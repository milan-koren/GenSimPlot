# GenSimPlot
<b>GenSimPlot</b> is a QGIS plugin designed and developed for generating spatially optimized plots used in the simulation and analysis of geographic processes.
Plugin enable to create squared, circular, rectangular, and eliptical plots maximazing overlap with the source polygons, enhancing the accuracy and representativeness of simulations.
By automating plot generation, point grid creation, and raster data extraction, GenSimPlot enhances spatial analysis workflows within QGIS, making it a versatile tool for both research and applied geographic studies.

## Key Features
<b>Plot Shape Generation</b>
<uL>
  <li>Generate spatially optimized plots in square, circular, rectangular, or elliptical shapes.</li>
  <li>Configurable positioning options, including alignment with the bounding box, centroid, or mean coordinates of source polygons.</li>
  <li>Optimized placement to maximize coverage and overlap with the original polygon, improving spatial simulation outcomes.</li>
</uL>
<b>Regular Point Grid Creation</b>
<uL>
  <li>Generate regular grids of points within each simulation plot.</li>
  <li>Configure grid density, making it suitable for high-resolution sampling within plots.</li>
  <li>Optional clipping of grid points to ensure they remain within the defined plot boundaries.</li>
</uL>
<b>Raster Data Extraction</b>
<uL>
  <li>Extract values from environmental raster layers, such as DEM or slope, and assign these values to simulation plots or individual grid points within plots.</li>
  <li>Options to calculate aggregate statistics (e.g., mean, min, max) of raster values across grid points for each plot.</li>
</uL>

## License
The plugin is licensed under the <a href="https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12">EUPL v1.2 (European Union Public License)</a>.

## Technical Requirements
GenSimPlot is developed as a QGIS plugin and requires QGIS version 3.0 or higher to run. The plugin is written in Python and uses the PyQt5 library for the user interface. The plugin is compatible with Windows, macOS, and Linux operating systems.

## Installation
GenSimPlot can be installed from the QGIS Plugin Repository or by downloading the source code from the <a href="https://github.com/milan-koren/GenSimPlot" target="_blank">GitHub repository</a>.
The plugin will be available in the QGIS Vector menu after installation.
<img src="help/qgis_vector_menu.png" width="720" />
