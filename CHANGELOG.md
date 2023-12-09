# Changelog

## UNTAGGED
### Added
 - egs_env36.yml as archive of python 3.16 conda env
 - reproject_raster returns the reprojected path
 - resampling method to geotiff_to_cog.reproject_raster
### Changed
 - egs_env.yml now python 310 and only packages required for cogification and publcation
 - README.md added conda env creation instructions based on yml
 - COG_creation into an importable package (added __init__.py)
 - input is converted to pathlib.Path
 - file name and datetime conversions using pathlib fxns
 - upstream repo is a fork of github EGS-publish-to-datacube
 - merged datacube/pipeline/egs repo with EGS-publish-to-datacube
### Removed
### Fixed