# -*- coding: utf-8 -*-
"""
Package:   GenSimPlot
File:      htuning_example.py
Version:   2.2
Author:    Milan Koren
Year:      2024
URL:       https://github.com/milan-koren/GenSimPlot
License:   EUPL v1.2 (European Union Public License), https://eupl.eu/          

GenSimPlot Hyperparameters Tuning Example

This script demonstrates how to use the HTuning class in GenSimPlot to automate hyperparameter
tuning for simulation plot generation. By specifying a range of values for key parameters, it
randomly selects settings and evaluates how well the resulting plots match the input polygons.

The script can be run in the QGIS Python console or in a script editor configured for QGIS.

Requirements:
    - GenSimPlot plugin and its libraries
    - An input shapefile with polygon features (e.g., forest stands)

Usage Overview:
    1. An instance of the HTuning class is created.
    2. The .run() method is called with paths to the input shapefile and an output statistics CSV.
    3. Ranges for hyperparameters such as iterations, translation percentage, angle limit, and resize
       percentage are specified. The script then runs multiple tests, generating simulation plots and
       recording outcomes.
    4. Results, including overlay statistics and run durations, are appended to the designated CSV file.
"""

from htuning import HTuning
from GenSimPlotUtilities import GProgressDialog


#Initialize the progress dialog
progressDlg = GProgressDialog()
progressDlg.show()

ht = HTuning()

ht.run(
    workingFolder = "C:\\data\\",
    polygonShpFN = "polygons.shp",
    idFieldName = "id",
    outputPlotFNBase = "splots",
    outputStatisticsFN = "statistics_best.csv",
    progressDlg = progressDlg,
    minIterations = 50,
    maxIterations = 500,
    minTranslatePerc = 0.01,
    maxTranslatePerc = 0.25,
    minAngleLimit = 1.0,
    maxAngleLimit = 45.0,
    minResizePerc = 0.01,
    maxResizePerc = 0.25,
    position = "bounding box",
    placement = "optimized",
    shape = "best",
    numberOfTests = 25,
)
    
#Close the progress dialog
progressDlg.close()
