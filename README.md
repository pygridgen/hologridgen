# holo-gridgen
WIP: GUI interface for configuring pygridgen using the [HoloViz](holoviz.org) tool suite, including Panel, HoloViews, and GeoViews

<img src="https://github.com/pygridgen/holo-gridgen/blob/master/images/holo-gridgen.png" width="450"/>

## The Plan: 

### Interface
GUI with control points plotted in the context of coastlines, bathymetry

### Persistence
- The final output that goes to the simulation is just the actual grid
- Also want to persist the various control points and matrices that the user manipulates so that a user can re-generate grids later with some modifications

### Focusing
- Probably will need an extensible class hierarchy with some focus spacing functions, each with their own parameterization
-See the [Focus class](https://github.com/pygridgen/pygridgen/blob/master/pygridgen/grid.py#L120), which is a callable that can be configured to add local Gaussian distortions

### Coastlines
- Need to display coastlines, which aren't necessarily just Cartopy's coastline files; often it will be a high-res local creekbed shapefile.
- UI should allow user to input their own coastline shapefile

### Projections
- Points will need to be projected for display.
- The projection needs to preserve orthogonality, so actual grid generation needs to use a conformal projection like Mercator or Lambert Conformal
- Display will thus ideally will also use a conformal projection, but maybe it's not that important; a nearly conformal projection like [Web Mercator](https://en.wikipedia.org/wiki/Web_Mercator_projection#:~:text=Unlike%20the%20ellipsoidal%20Mercator%2C%20however,to%20be%20noticeable%20by%20eye.) may be ok.

### Nested grids:
- Needed eventually, but not urgent
- Should work fine to postpone worrying about that until near the end or after this project completes, as it should slot in to whatever we do.
