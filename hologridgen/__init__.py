import numpy as np
import pandas as pd
from io import BytesIO

import param
import geopandas
import holoviews as hv
import geoviews as gv
import panel as pn
import pygridgen as pgg

from holoviews.plotting.bokeh.callbacks import Link, LinkCallback


class PolaritySwap(Link):
    """
    Link to be applied to a Points object with a polarity column to
    allow toggling of the polarity (beta) value client-side.
    """
    _requires_target = False


class PolarityCallback(LinkCallback):
    """
    Client side JavaScript to toggle the node polarity (beta) value of
    nodes tapped using the Tap tool
    """
    source_model = 'selected'
    on_source_changes = ['indices']
    source_handles = ['cds', 'draw_tool']
    source_code = """
    if (source_draw_tool.active) { return }
    var index = source_selected.indices[0]
    if (index == undefined)
      return
    var polarity = source_cds.get_column('color')
    if (polarity[index] == '+')
      polarity[index] = '0'
    else if (polarity[index] == '0')
      polarity[index] = '-'
    else
      polarity[index] = '+'
    source_cds.data['color'] = polarity
    source_cds.data['polarity'] = polarity
    source_selected.indices = []
    source_cds.properties.data.change.emit()
    source_cds.change.emit()
    """


# Registering Link callback
callbacks = Link._callbacks['bokeh']
callbacks[PolaritySwap] = PolarityCallback


# Dictionary of possible tile sources to make available via the background dropdown menu
TILE_SOURCES = {k:v.opts(global_extent=True)
                for k,v in gv.tile_sources.tile_sources.items()}
TILE_SOURCES['None'] = None


class GridEditor(param.Parameterized):
    """
    Interactive boundary editor for previewing and generating pygridgen grids.

    Core features:
       * Add, drag and delete nodes interactively with the PointsDraw tool
       * Toggle their polarity (beta) value with the Tap Tool
       * Insert nodes into selected edges after selecting them with the Tap Tool.
       * Set a focus function and update the grid
       * Pythonic access to the geopandas boundary DataFrame.
       * Serializable state to capture editor state between sessions
       * Customizable background tile sources or background tile elements.

    For more information please visit https://github.com/pygridgen/hologridgen
    """

    # Algorithmic parameters hidden from the GUI

    max_nodes = param.Integer(default=1000, precedence=-1,
                              doc = "Maximum number of nodes in a boundary")

    ul_idx=param.Integer(default=0, precedence=-1,
                         doc='Upper left index: parameter of grid generation')

    polarity_value = param.Dict(default={'+':1, '0':0, '-':-1}, precedence=-1, doc="""
      Beta values to associate with the three node polarities (positive
      '+', neutral '0' and negative '-'). Setting '+':4/3 for instance
      enables grid generation with only three positive nodes.""")

    # Parameters not in the GUI for Pythonic data access

    focus = param.ClassSelector(default=None, class_=pgg.Focus,
                                allow_None=True, precedence=-1, doc="""
      Parameter that can be set to a pygridgen Focus object (or None).
      When set, mesh generation will apply the specified Focus
      function.""")

    grid = param.ClassSelector(default=None, class_=pgg.grid.Gridgen,
                               allow_None=True, precedence=-1, doc="""
      Parameter that exposes the pygridgen Gridgen object that will be
      set after mesh generation """)

    ready = param.Boolean(default=False, precedence=-1, doc="""
      Boolean predicate indicating readiness for mesh generation: mesh generation
      can be executed when the sum of the polarity in the boundary is 4.""")

    # User settings hidden from the GUI, settable in the constructor (precedence= -1)

    width = param.Integer(default=600, precedence=-1, bounds=(200, 1000),
        doc="Width of the HoloViews object corresponding to the editor view area")

    height = param.Integer(default=600, precedence=-1, bounds=(200, 1000),
        doc="Height of the HoloViews object corresponding to the editor view area")

    custom_background = param.Parameter(default=None, precedence=-1, doc="""
      Custom HoloViews element to use as the background when the
      background parameter is set to 'Custom'.""")

    background = param.ObjectSelector('None', objects=TILE_SOURCES.keys(), doc="""
      Selector of available default tile sources which can also be set
      to 'None' for no background or 'Custom' in which case the
      HoloViews/GeoViews element set in the custom_background parameter
      (if any) is used as the background.""")

    # Customizable HoloViews styles (hidden from the GUI, settable in the constructor)

    node_style = param.Dict(dict(cmap={'+': 'red', '-': 'blue', '0':'black'}),
                            precedence=-1, doc="""
      Style options for nodes. Note that the size is overidden by the
      node_size param controllable in the GUI and the polarity colors
      can be changed by setting the cmap dictionary.""")

    mesh_style = param.Dict(dict(line_width=2, line_alpha=1, line_color='blue'),
                            precedence=-1, doc="Style options for displayed mesh.")


    edge_style = param.Dict(dict(line_width=2, line_alpha=1, line_color='green',
                                nonselection_color='green', nonselection_alpha=0.5),
                            precedence=-1, doc="""
      Style options for displayed boundary edges. The nonselection_*
      options set how deselected edges appear when the Tap tool is used
      to insert new nodes into edges""")

    start_indicator_style = param.Dict(
        dict(marker='triangle', angle=30, fill_alpha=0, size=30, color='black'),
        precedence=-1, doc="""
      Style of the start marker indicating the first boundary
      point. Default is a triangle that can be rotated by setting the
      'angle' keyword.""")

    # GUI controllable parameters

    node_size = param.Integer(default=10, bounds=(1,200),
                              doc="Size of nodes used to mark the boundary.")

    edge_width = param.Integer(default=2, bounds=(1,50), doc="Width of the boundary edges")

    xres = param.Integer(default=50,  bounds=(2, None), doc="""
       X resolution of the generated grid""")

    yres = param.Integer(default=50,  bounds=(2, None), doc="""
       Y resolution of the generated grid""")

    generate_mesh = param.Event(doc='Event that runs mesh generation')

    hide_mesh = param.Event(doc='Event that clears displayed mesh')

    insert_points = param.Event(
        doc='Event that inserts a new node into an edge selected with the Tap tool')

    _columns = ['color', 'polarity', 'x', 'y']


    def __init__(self, data=None, **params):
        data_params = {} if data is None else {k:v for k,v in data.items()
                                               if k not in self._columns}
        params = dict(data_params, **params)
        data = {k:[] for k in self._columns} if (data is None) else data
        super().__init__(**params)

        def install_handle(plot, element):
            "Handle needed to make the draw_tool available in the JS callback"
            plot.handles['draw_tool'] = plot.state.tools[-1]

        node_style = dict(self.node_style,
                           tools=['tap'],
                           color=hv.dim('polarity'),
                           fill_alpha=hv.dim('polarity').categorize({'0':0, '+':1, '-':1 }),
                           show_legend=False, hooks=[install_handle])

        # PointDraw Stream that enables the PointDraw Bokeh tool
        self._node_stream = hv.streams.PointDraw(data=data,
                                                 num_objects=self.max_nodes,
                                                 empty_value = '+')

        # Nodes is a DynamicMap returning hv.Points along the boundary
        self.nodes = hv.DynamicMap(self.points,
                                  streams=[self._node_stream,
                                           self.param.insert_points,
                                           self.param.node_size]).opts(**node_style)
        # DynamicMap drawing the boundary as a hv.Path element
        self.boundary_dmap = hv.DynamicMap(self._boundary,
                                         streams=[self._node_stream,
                                                  hv.streams.Selection1D()])
        # DynamicMap placing the start indicator
        self.start_marker = hv.DynamicMap(self._start_marker,
                                          streams=[self._node_stream]
                                          ).opts(**self.start_indicator_style)

        # Initial, empty mesh
        self.qmesh = hv.QuadMesh((np.zeros((2,2)), np.zeros((2,2)), np.zeros((2,2))))

        self._selected_edge_index = None

    @classmethod
    def from_geopandas(cls, df):
        """
        Classmethod that allows a GridEditor to be initialized from a
        boundary geopandas DataFrame (such as the one available from the
        .boundary property).
        """
        if len(df) == 0:
            return GridEditor()
        allowed = [el for el in cls._columns if el != 'geometry']
        color_vals = {v:k for k,v in cls.polarity_value.items()}
        data = {k:list(v) for k,v in df.to_dict(orient='list').items() if k in allowed}
        data['color'] = [color_vals[p] for p in data['polarity']]
        data['polarity'] = data['color']
        return GridEditor(data)

    @property
    def boundary(self):
        "Property returning the boundary GeoDataFrame"
        exclude = ['color', 'fill_alpha']
        data = self._node_stream.data
        polarity = [self.polarity_value[c] for c in data['color']]
        df_data = {c:[el for el in v] for c,v in data.items() if c not in exclude}
        df_data['polarity'] = polarity
        df = pd.DataFrame(df_data)
        return geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df.x, df.y))


    @property
    def data(self, exclude=['name', 'fill_alpha', 'grid']):
        """
        Propery exposing serializable state of the editor that can be
        passed into the GridEditor constructor to restore that state
        """
        data = {k:[el for el in v] for k,v in self._node_stream.data.items()}
        param_data = {p:getattr(self, p) for p in self.param}
        data.update(param_data)
        return {k:v for k,v in data.items() if k not in exclude}

    def _ready(self):
        "Predicate method indicating current readiness for mesh generation"
        data = self._node_stream.data

        if len(data['x']) > 3:
            summed = sum(self.polarity_value[el] for el in data['color'])
            return (summed == 4)
        else:
            return False


    @pn.depends('ready', watch=True)
    def _check_readiness(self):
        "Callback used to disable generate mesh button till ready"
        for widget in self.widgets:
            if isinstance(widget, pn.widgets.button.Button) and (widget.name == 'Generate mesh'):
                button = widget
                break
        button.disabled = not self.ready


    @pn.depends('_node_stream.data')
    def _geojson(self):
        "Callback to generate GeoJSON file when download button is clicked"
        boundary = self.boundary
        bio = BytesIO()
        if len(boundary) != 0:
            boundary.to_file(bio, driver='GeoJSON')
        bio.seek(0)
        return bio

    # DynamicMap callbacks

    def points(self, data, insert_points, node_size):
        "DynamicMap callback returns Points representing boundary nodes"
        new_data = {'x': data['x'], 'y': data['y'],
                    'polarity' : np.array(data['color'], dtype='U1')}
        if insert_points and len(self._selected_edge_index)==1:
            point_index = self._selected_edge_index[0] + 1
            sx, ex = new_data['x'][point_index-1], new_data['x'][point_index]
            sy, ey = new_data['y'][point_index-1], new_data['y'][point_index]

            new_data['x'] = np.insert(new_data['x'], point_index, (sx+ex) / 2.)
            new_data['y'] = np.insert(new_data['y'], point_index, (sy+ey) / 2.)
            new_data['polarity'] = np.insert(new_data['polarity'], point_index, '+')
        return hv.Points(new_data, vdims=['polarity']).opts(size=node_size)


    def _generate_mesh(self, generate_mesh=False, hide_mesh=False):
        "Callback returning generated QuadMesh element"
        if not self.ready:
            return self.qmesh.opts(fill_alpha=0, line_alpha=0)

        elif hide_mesh or (not generate_mesh):
            return self.qmesh.opts(fill_alpha=0, line_alpha=0)

        if self.ready:
            gdf = self.boundary
            kwargs = dict(shape=(self.xres, self.yres), ul_idx=self.ul_idx)
            if self.focus is not None:
                kwargs['focus'] = self.focus
            self.grid = pgg.Gridgen(gdf.geometry.x, gdf.geometry.y, gdf.polarity, **kwargs)
            xdim, ydim = self.grid.x.shape
            zs = np.ones((xdim-1, ydim-1))
            self.qmesh = hv.QuadMesh((np.array(self.grid.x), np.array(self.grid.y), zs))
            return self.qmesh.opts(**self.mesh_style, fill_alpha=0)


    def _boundary(self, data,  index):
        "Callback drawing Path element defining boundary"
        self._selected_edge_index = index
        xs, ys = data['x'], data['y']
        lines = []
        for i in range(len(xs)-1):
            s, e = i, (i+1)
            lines.append([(xs[s], ys[s]), (xs[e], ys[e])])
        self.ready = self._ready()
        return hv.Path(lines).opts(**self.edge_style)

    def _start_marker(self, data):
        "Callback to draw the start marker"
        if len(data['x']) == 0:
            return hv.Points(None)
        return hv.Points((data['x'][0], data['y'][0]))


    def _background(self, background):
        """
        Callback that allows the background to be switched between tile
        sources, a custom background element or None for no
        background
        """
        elements = []
        if background != 'None':
            elements = [TILE_SOURCES[background].opts(global_extent=True, alpha=1)]
        elif background == 'None':
            if self.custom_background:
                elements = [self.custom_background]
            else:
                elements = [TILE_SOURCES[list(TILE_SOURCES.keys())[0]].opts(alpha=0)]
        return hv.Overlay(elements)


    def view(self):
        "Main entry point for using the GridEditor after construction"
        self.polarity_link =  PolaritySwap(self.nodes)
        param_stream = hv.streams.Params(self,
                                         ['generate_mesh', 'hide_mesh'],
                                         transient=True)

        elements = [hv.DynamicMap(self._background, streams=[self.param.background]),
                    self.boundary_dmap.apply.opts(line_width=self.param.edge_width),
                    self.start_marker,
                    self.nodes,
                    hv.DynamicMap(self._generate_mesh,
                    streams=[param_stream])]

        hvobj = hv.Overlay(elements).collate()
        self.widgets = pn.Param(self.param,
                                widgets={'edge_select_mode': pn.widgets.Toggle})
        obj = pn.Row(pn.Column(self.widgets,
                               pn.widgets.FileDownload(callback=self._geojson,
                                                       filename='boundary.geojson')),
                     hvobj.opts(width=self.width, height=self.height))
        self.param.trigger('ready')
        return obj
