# Yeoda DC Loader
QGIS Plugin using TUW GEO packages to load raster files of a Data Cube from a pre-defined folder structure and naming conventions.

The plugin is aimed at querying, filtering, and loading of raster files to QGIS using specific folder and file naming schemes found in [geopathfinder](https://github.com/TUW-GEO/geopathfinder). Aside from loading the data its primary function is to set the temporal parameters for each file as discerned from the filenaming conventions. It also allows for layer titles to be set based on the filename keys ex. date, polarization, grid system, etc. and common styling to be applied. Primary use case is to ease spatio-temporal viewing of (subsets of) data cubes using temporal controller function in QGIS.

## Installation instructions
Copy the yeoda_dc_loader folder from src and paste this in your QGIS python plugin directory e.g. /home/'user'/.local/share/QGIS/QGIS3/profiles/default/python/plugins .

### Geopathfinder Requirement
1. The plugin currently requires [geopathfinder](https://github.com/TUW-GEO/geopathfinder).
2. Initial run of the plugin may take a long time if geopathfinder is not currently installed, as the plugin will attempt to (pip) install geopathfinder automatically.
3. Should this fail, manual installation of geopathfinder to a location acccessible by PyQGIS is required e.g. pip install geopathfinder then setting system path.
