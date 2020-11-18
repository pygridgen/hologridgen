# hologrid

Interactive tool for the generation of orthonormal grids using
[pygridgen](https://github.com/pygridgen/pygridgen) and the
[HoloViz](holoviz.org) tool suite for use within [Jupyter
notebooks](https://jupyter.org/) or deployable with
[Panel](panel.pyviz.org).

## Installation

You can install it as follows in an existing Python 3.7 conda environment:

```
conda install  -c conda-forge hologridgen
```

If you need a new, blank Python 3.7 conda environment, you can create it
and activate it using:

```
conda create -n hologridgriden -c conda-forge python=3.7 hologridgen
conda activate hologridgen
```


## Core features

* Add, move and delete nodes. First node indicated with a special marker (triangle by default)

<img width=400 src="https://github.com/pygridgen/holo-gridgen/blob/master/images/add-mode-delete.gif"></img>

* Toggle node polarity (beta) with the Tap Tool. Generate Mesh button indicates when mesh generation is possible. Hide button to hide current grid/mesh.

<img width=400 src="https://github.com/pygridgen/hologridgen/blob/master/images/polarity-toggle.gif"></img>

* Easy insertion of new nodes into edges selected with the Tap Tool (which can then be easily moved):

<img width=400 src="https://github.com/pygridgen/hologridgen/blob/master/images/edge_insertion.gif"></img>

* Pythonic access of boundary as it is drawn and the grid once it is generated:

<img width=400 src="https://github.com/pygridgen/hologridgen/blob/master/images/pythonic-access.gif"></img>

* Easy adjustment of node size and edge width via the GUI. Easy regeneration with different x- and y-resolutions:

<img width=400 src="https://github.com/pygridgen/hologridgen/blob/master/images/node-edge-size.gif"></img>

* Easy selection between a predefined set of tile sources in the background:

<img width=400 src="https://github.com/pygridgen/hologridgen/blob/master/images/tilesources.gif"></img>

* Easy use of a custom element (e.g a different tile source) as the background:

<img width=400 src="https://github.com/pygridgen/hologridgen/blob/master/images/custom_background.gif"></img>

* Download boundary as GeoJSON:

<img width=400 src="https://github.com/pygridgen/hologridgen/blob/master/images/geojson_download.gif"></img>

* Capture serializable editor state and restore from it (can also be restored from a geopandas boundary DataFrame):

<img width=400 src="https://github.com/pygridgen/hologridgen/blob/master/images/save_restore_state.gif"></img>

* Set a focus function and update mesh accordingly:

<img width=400 src="https://github.com/pygridgen/hologridgen/blob/master/images/focus_edit.gif"></img>

* Highly customizable styling of boundary, nodes and start marker:

<img width=400 src="https://github.com/pygridgen/hologridgen/blob/master/images/customizable_style.gif"></img>

* Can be served as a Panel dashboard using the `serveable()` method.
