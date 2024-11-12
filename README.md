# GenSimPlot
<b>GenSimPlot</b> is a QGIS plugin designed and developed for generating spatially optimized plots used in the simulation and analysis of geographic processes.
Plugin enable to create squared, circular, rectangular, and eliptical plots maximazing overlap with the source polygons, enhancing the accuracy and representativeness of simulations.
By automating plot generation, point grid creation, and raster data extraction, GenSimPlot enhances spatial analysis workflows within QGIS, making it a versatile tool for both research and applied geographic studies.

<b>GenSimPlot</b> is designed to support a wide range of spatial analysis and simulation tasks, including:
<ul>
    <li>Forest growth simulations.</li>
    <li>Habitat suitability simulations.</li>
    <li>Landscape planning.</li>
    <li>Environmental and ecological modeling</li>
</ul>
            
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

## Technical Requirements
GenSimPlot is developed as a QGIS plugin and requires QGIS version 3.0 or higher to run. The plugin is written in Python and uses the PyQt5 library for the user interface. The plugin is compatible with Windows, macOS, and Linux operating systems.

## Installation
<p>GenSimPlot can be installed from the QGIS Plugin Repository or by downloading the source code from the <a href="https://github.com/milan-koren/GenSimPlot" target="_blank">GitHub repository</a>.
The plugin will be available in the QGIS Vector menu after installation.</p>
<img src="help/qgis_vector_menu.png" width="720" />

## License
<p>The plugin is licensed under the <a href="https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12">EUPL v1.2 (European Union Public License)</a>.</p>

# Generate Point Grids for Simulation Plots
<p>The "Generate Point Grids for Simulation Plots" dialog enables creating a regular grid of points within the bounding rectangle of each simulation plot. The grid density, alignment, and clipping options ensure precise spatial accuracy within plot boundaries.</p>
<img src="help/form_generate_points.png" width="420" />
<p><b>Parameters</b></p>
<ul>
    <li><b><i>Simulation plots:</i></b> Shapefile containing polygon features representing the simulation plots.</li>
    <li><b><i>Plot ID:</i></b> Field name that identifies each simulation plot within the input shapefile.</li>
    <li><b><i>Output shape-file:</i></b> Path to the shapefile where the generated point grid will be saved.</li>
    <li><b><i>Number of points:</i></b> The number of points to generate along the shorter side of each plot's bounding box, controlling the grid density.</li>
    <li><b><i>Clip points by simulation plot:</i></b> Option to clip generated points to fit precisely within each plot's boundary, preserving spatial accuracy.</li>
</ul>
<p>Example of a regularly spaced point grid generated within square simulation plots:</p>
<img src="help/example_square_points.png" width="330" />
<p>Example of a point grid generated within simulation plots optimized using the 'best' option:</p>
<img src="help/example_best_points.png" width="330" />

