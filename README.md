# holo-gridgen
WIP: GUI interface to pygridgen using the [Holoviz](holoviz.org) tool suite, using panel, holoviews and geoviews

![holoviz fig](https://github.com/pygridgen/holo-gridgen/blob/master/images/holo-gridgen.png)
## The Plan: 

### Interface
GUI with control points plotted in the context of coastlines, bathymetry

### Persistence
The final output that goes to the simulation is just the actual grid
Also want to persist the various control points and matrices that the user manipulates so that a user can re-generate grids later with some modifications

### Focusing
Probably will need an extensible class hierarchy with some focus spacing functions, each with their own parameterization
See the Focus class https://github.com/hetland/pygridgen/blob/master/pygridgen/grid.py#L512, which is a callable that can be configured to add local Gaussian distortions

### Coastlines
Need to display coastlines, which aren't necessarily just Cartopy's coastline files; often it will be a high-res local creekbed shapefile.
UI should allow user to input their own coastline shapefile

### Projections
Points will need to be projected for display.
The projection needs to preserve orthogonality, so actual grid generation needs to use a conformal projection like Mercator or Lambert Conformal
Display will thus ideally will also use a conformal projection, but maybe it's not that important

Q: Is Web Mercator conformal? A: No, but almost; maybe ok?

### Nested grids:
Needed eventually, but not urgent
Should work fine to postpone worrying about that until near the end or after this project completes, as it should slot in to whatever we do.
