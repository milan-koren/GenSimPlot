# -*- coding: utf-8 -*-
"""
Package:   GenSimPlot
File:      example_script.py
Version:   2.2
Author:    Milan Koren
Year:      2024
URL:       https://github.com/milan-koren/GenSimPlot
License:   EUPL v1.2 (European Union Public License), https://eupl.eu/          

GenSimPlot Scripting Example

This script demonstrates the use of GenSimPlot to automate the generation of spatially optimized simulation plots,
creation of point grids within those plots, and extraction of raster values for environmental variables. 

Example Steps:
    1. Use PlotGenerator to create optimized plots from the source polygon shapefile.
    2. Generate a grid of points within each simulation plot.
    3. Extract raster data for each point, compute plot-level statistics, and store the results.
    4. Extract additional raster values (e.g., slope) at the centroid of each plot.

The script can be executed in the QGIS Python console or in a script editor configured for QGIS.

Requirements:
- GenSimPlot plugin and libraries
- An input shapefile with polygon features (e.g., forest_stands.shp)
- One or more raster files for environmental data (e.g., a DEM and slope raster)
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
