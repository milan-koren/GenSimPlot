# -*- coding: utf-8 -*-
"""
Package:   GenSimPlot
File:      example_script.py
Version:   2.1
Author:    Milan Koren
Year:      2024
URL:       https://github.com/milan-koren/GenSimPlot
License:   EUPL v1.2 (European Union Public License), https://eupl.eu/          

GenSimPlot Scripting Example

This script demonstrates the use of GenSimPlot to automate the generation of spatially optimized simulation plots,
creation of point grids within plots, and extraction of raster values. The example includes generating plots,
grid of points within plots, and extracting elevation and slope data from raster layers.

Requirements:
- GenSimPlot plugin and libraries
- Input shapefile with polygon features (e.g., forest stands)
- Raster files for environmental data (elevation and slope)

Steps:
1. Generates optimized simulation plots.
2. Creates a regular grid of points within each plot.
3. Extracts raster values at each point within the plots and calculates plot-level statistics.
4. Extracts raster values at the centroid of each plot.
"""

from GenSimPlotLib import PlotGenerator, PointsGenerator, SimulationPlotVariables
from GenSimPlotUtilities import GProgressDialog

#Initialize the progress dialog
progressDlg = GProgressDialog()
progressDlg.show()

#Define input parameters
workingFolder = "c:\\data\\"
inputShp = workingFolder + "forest_stands.shp"
polygonID = "id"
plotsShp = workingFolder + "plots.shp"
pointsShp = workingFolder + "points.shp"
nPoints = 10
clipPoints = True
demRaster = workingFolder + "dem\\dem"
slopeRaster = workingFolder + "dem\\slope"

#Generate optimized simulation plots
plotGen = PlotGenerator()
plotGen.generateBestPlots(inputShp, polygonID, plotsShp, progressDlg)

#Generate a grid of points within the plots
pointsGen = SimulationPlotVariables()
pointsGen.generatePoints(plotsShp, polygonID, pointsShp, nPoints, clipPoints, progressDlg)

#Extract raster values for each point within plots and calculate plot-level statistics
rasterStats = SimulationPlotVariables()
rasterStats.valueFromPoints(plotsShp, polygonID, pointsShp, "elev", demRaster, progressDlg)

#Extract raster values for each plot centroid
rasterCentroid = SimulationPlotVariables()
rasterCentroid.valueFromCentroid(plotsShp, "slope", slopeRaster, progressDlg)

#Close the progress dialog
progressDlg.close()
