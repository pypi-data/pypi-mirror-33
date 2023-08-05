.. _ref-release-notes:

===============
 Release Notes
===============

.. _ref-v0-1-1:

Version 0.1.1
~~~~~~~~~~~~~

- In conjunction with changes in support docs at Climate Data Center, the RADOLAN projection file used for ID raster creation (stored in sampledata module) has been replaced.
  The new file contains the stereographic RADOLAN projection in meters instead of kilometers. This guarantees compatibility with RADOLAN ASCII files from CDC.

- Accordingly, the unit of the output coordinates of :func: 'radproc.core.coordinates_degree_to_stereographic' has been changed to meter
  and the cellsize of :func: 'radproc.arcgis.create_idraster_germany' has been set to 1000 instead of 1.
  
- :func: 'radproc.raw.unzip_RW_binaries' and :func: 'radproc.raw.unzip_YW_binaries': outFolder will now be created if it doesn't exist, yet.

.. _ref-v0-1-0:

Version 0.1.0
~~~~~~~~~~~~~

First radproc release version.

www.pgweb.uni-hannover.de only hosts the docs for the latest release version.
If you need former versions, please check out the docs on https://radproc.readthedocs.io
Unfortunately, they don't contain the docs af the arcgis module due to technical problems with the installation of arcpy at readthedocs.