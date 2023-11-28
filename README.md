# GenSimPlot
GenSimPlot: Simulation Plot Generator for QGIS

GenSimPlot is a Python script collection designed for QGIS, aimed at generating simulation plots for various applications, particularly in the context of forestry and environmental modeling. This repository contains scripts for creating and manipulating simulation plots, enhancing their visualization and analysis within the QGIS environment.


# Instructions for Using GenSimPlot Script Library

## Environment Setup:
1. Open QGIS Desktop v. 3.30.1 or later.
2. Open the Python console from the toolbar or use Ctrl+Alt+P.
3. Use the "Show Editor" button to open the script editor.
4. Open "gensimplot.py" in the script editor.

## Modify the Script:
Modify the script to automate the generation of your simulation plots.

# Python
### Setup Working Environment
workingDir = "C:\\simulation\\"
fstandShapeFile = "fstand.shp"
fstandIDField = "fstand_id"
simplotIDField = "fstand_id"

### Generate Optimized Simulation Plots into "simplot.shp"
rplots = gensimplot.RectangularSimulationPlot()
rplots.generatePlotsByPositionAndShape(workingDir + fstandShapeFile, fstandIDField, workingDir + "simplot.shp", simplotIDField)

### Extract DEM Points for the Simulation Plots (elevation stored in raster "dem")
points = gensimplot.SimulationPlotVariables()
points.generatePoints(workingDir + "simplot.shp", simplotIDField, workingDir + "simplot_points.shp", simplotIDField, 5)
points.demPoints(workingDir + "simplot.shp", simplotIDField, workingDir + "simplot_points.shp", simplotIDField, workingDir + "dem")

### Extract Slope for Simulation Plot Points and Calculate Mean Slope for Simulation Plot
### Slope is extracted from the raster "slope"
points.valueFromPoints(workingDir + "simplot.shp", simplotIDField, "slopemin", "slopemax", "slopemean", workingDir + "simplot_points.shp", simplotIDField, "slope", workingDir + "slope")

### Extract Temperature at Centroids of Simulation Plots and Assign it to Corresponding Simulation Plot
### Mean temperature is extracted from the raster "mtemper"
points.valueFromCentroid(workingDir + "simplot.shp", "temperature", workingDir + "mtemper")

# Assign Other Required Environmental Variables to Simulation Plots (e.g., aspect, precipitation, solar radiation)
