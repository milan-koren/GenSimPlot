# -*- coding: utf-8 -*-
"""
Package:   GenSimPlot
File:      htuning.py
Version:   2.2
Author:    Milan Koren
Year:      2024
URL:       https://github.com/milan-koren/GenSimPlot
License:   EUPL v1.2 (European Union Public License), https://eupl.eu/          
           
The module for performing hyperparameter tuning for the GenSimPlot package. 
The class HTuning implements methods for management and statistics of hyperparameter tuning process.

Method overview:
    - HTuning.run(): Selects random hyperparameters from specified ranges, generates simulation plots,
                     and calculates performance statistics for each run. Results are stored in a CSV file.
    - HTuning.calculateStatistics(): Computes statistics on generated simulation plots.
    - HTuning.saveStatistics(): Saves computed statistics to a CSV file.
This script can be executed in a QGIS Python console or a script editor configured for QGIS.
"""

import datetime
import random
import math
import os
from qgis.core import *

from GenSimPlotLib import PlotGenerator, PointsGenerator, SimulationPlotVariables
from GenSimPlotUtilities import GenSimPlotUtilities, GProgressDialog


class HTuning:
    """    
    The HTuning class performs hyperparameter tuning for the GenSimPlot package.
    It defines default ranges for various hyperparameters number of iterations, translation percentage,
    angle limit, resize percentage, position, placement, and shape of the simulation plots, and provides
    methods to compute and record performance metrics.
    
    The HTuning class performs hyperparameter tuning for the GenSimPlot package. It defines default
    ranges for various hyperparameters (number of iterations, translation percentage, rotation angle
    limit, resize percentage, initial position, placement, and shape of simulation plots) and provides
    methods to compute and record performance metrics.
    
    Attributes:
        minIterations (int): Minimum number of iterations for the random search.
        maxIterations (int): Maximum number of iterations for the random search.
        minTranslatePerc (float): Minimum translation percentage used by the random search.
        maxTranslatePerc (float): Maximum translation percentage used by the random search.
        minAngleLimit (float): Minimum rotation angle used by the random search.
        maxAngleLimit (float): Maximum rotation angle used by the random search.
        minResizePerc (float): Minimum resize percentage used by the random search.
        maxResizePerc (float): Maximum resize percentage used by the random search.
        position (str): Initial positioning strategy for simulation plots (e.g., bounding box, centroid).
        placement (str): Placement strategy for simulation plots (e.g., fixed, resized, rotated, optimized).
        shape (str): Shape of the simulation plots (e.g., square, circle, rectangle, ellipse).
    """
    

    minIterations = 25          # Minimum number of iterations for random search.
    maxIterations = 1000        # Maximum number of iterations for random search.
    minTranslatePerc = 0.01     # Minimum translation percentage for random search.
    maxTranslatePerc = 0.25     # Maximum translation percentage for random search.
    minAngleLimit = 1.0         # Minimum rotation angle limit for random search.
    maxAngleLimit = 45.0        # Maximum rotation angle limit for random search.
    minResizePerc = 0.01        # Minimum resize percentage for random search.
    maxResizePerc = 0.25        # Maximum resize percentage for random search.
    position = "bounding box"   # Initial positioning strategy for the simulation plots.
    placement = "optimized"     # Placement strategy for the simulation plots.
    shape = "square"            # Shape of the simulation plots.
    

    def calculateStatistics(self, outputPlotFN: str, progressDlg: GProgressDialog):
        """       
        Calculates descriptive statistics on generated simulation plots.

        Reads the specified shapefile, verifies that its geometry type is polygonal, and computes
        descriptive statistics for an attribute named "perc," representing each feature's overlay
        percentage. Results are returned in a dictionary.
        
        Parameters:
            outputPlotFN (str): Path to the shapefile containing generated simulation plots.
            progressDlg (GProgressDialog): Progress dialog for displaying current progress.

        Returns:
            dict: A dictionary with the calculated statistics:
                  - nPolygons: Number of polygons in the layer.
                  - minPerc: Minimum overlay percentage.
                  - maxPerc: Maximum overlay percentage.
                  - avgPerc: Average overlay percentage.
                  - stdDevPerc: Standard deviation of overlay percentage.

        Raises:
            ValueError: If the input layer is not polygonal.            
        """
        inputLayer = QgsVectorLayer(outputPlotFN, "plots", "ogr")
        if inputLayer.geometryType() != Qgis.GeometryType.Polygon:
            GenSimPlotUtilities.raiseValueError(
                f"Geometry must be POLYGON ({inputFN}).", progressDlg
            )
        n = inputLayer.featureCount()
        GenSimPlotUtilities.startProgress(
            progressDlg,
            f"Calculating statistics of simulation plots {outputPlotFN} ...",
            n,
        )

        minPerc = 999.9
        maxPerc = 0.0
        sumPerc = 0.0
        sumPerc2 = 0.0

        for fid in range(0, n):
            inputFeature = inputLayer.getFeature(fid)
            perc = float(inputFeature["perc"])
            minPerc = min(minPerc, perc)
            maxPerc = max(maxPerc, perc)
            sumPerc += perc
            sumPerc2 += perc * perc
            GenSimPlotUtilities.incrementProgress(progressDlg)

        return {
            "nPolygons": n,
            "minPerc": minPerc,
            "maxPerc": maxPerc,
            "avgPerc": sumPerc / n,
            "stdDevPerc": math.sqrt(sumPerc2 / n - (sumPerc / n) ** 2),
        }


    def saveStatistics(
        self,
        outputStatisticsFN: str,
        polygonShpFN: str,
        randomIterations: int,
        percTranslate: float,
        maxAlpha: float,
        maxResizePerc: float,
        duration: datetime.timedelta,
        statistics: dict,
    ):
        """
        Appends hyperparameter tuning results to a CSV file.

        If the specified CSV file does not exist, creates it with an appropriate header.
        Otherwise, appends a row containing the following fields:
            ShpFN; nPolygons; position; placement; shape; randomIterations; percTranslate;
            maxAlpha; maxResizePerc; duration; minPerc; maxPerc; avgPerc; stdDevPerc

        Parameters:
            outputStatisticsFN (str): Path to the output CSV file for storing statistics.
            polygonShpFN (str): Path to the source polygon shapefile used for simulation.
            randomIterations (int): Number of random iterations used for generating plots.
            percTranslate (float): Translation percentage used for random search.
            maxAlpha (float): Maximum rotation limit used for random search.
            maxResizePerc (float): Maximum resize percentage used for random search.
            duration (timedelta): Elapsed time for the simulation process.
            statistics (dict): Dictionary of computed statistics from calculateStatistics().
        """
        if not os.path.exists(outputStatisticsFN):
            txtFile = open(outputStatisticsFN, "w")
            txtFile.write(
                "ShpFN;nPolygons;position;placement;shape;randomIterations;percTranslate;maxAlpha;maxResizePerc;duration;minPerc;maxPerc;avgPerc;stdDevPerc\n"
            )
        else:
            txtFile = open(outputStatisticsFN, "a+")
        txtFile.write(
            f"{polygonShpFN};{statistics['nPolygons']};{self.position};{self.placement};{self.shape};{randomIterations};{percTranslate};{maxAlpha};{maxResizePerc};{duration.total_seconds()};{statistics['minPerc']};{statistics['maxPerc']};{statistics['avgPerc']};{statistics['stdDevPerc']}\n"
        )
        txtFile.close()


    def run(
        self,
        workingFolder: str,
        polygonShpFN: str,
        idFieldName: str,
        outputPlotFNBase: str,
        outputStatisticsFN: str,
        progressDlg: GProgressDialog,
        minIterations:int = 25,
        maxIterations:int = 1000,
        minTranslatePerc:float = 0.01,
        maxTranslatePerc:float = 0.25,
        minAngleLimit:float = 1.0,
        maxAngleLimit:float = 45.0,
        minResizePerc:float = 0.01,
        maxResizePerc:float = 0.33,
        position:str = "bounding box",
        placement:str = "optimized",
        shape:str = "best",
        numberOfTests:int = 100,
    ):
        """
        Executes the hyperparameter tuning process.
       
        Combines a random search approach with the specified ranges of hyperparameters. 
        For each test iteration, the method selects random values for:
            - the number of random iterations,
            - translation percentage,
            - maximum rotation angle,
            - and maximum resize percentage.
          
        Once parameters are set, the method generates plots and calculates performance statistics. 
        It concludes by saving the results to the specified CSV file.

        Parameters:
            workingFolder (str): Directory containing the source shapefile and where outputs will be saved.
            polygonShpFN (str): Name of the source polygon shapefile.
            idFieldName (str): Name of the field identifying features in the source polygon shapefile.
            outputPlotFNBase (str): Base name for output simulation plot shapefiles.
            outputStatisticsFN (str): File name of the CSV to store statistical results.
            progressDlg (GProgressDialog): Dialog tracking progress.
            minIterations (int): Minimum number of iterations for random search.
            maxIterations (int): Maximum number of iterations for random search.
            minTranslatePerc (float): Minimum translation percentage for random search.
            maxTranslatePerc (float): Maximum translation percentage for random search.
            minAngleLimit (float): Minimum rotation angle for random search.
            maxAngleLimit (float): Maximum rotation angle for random search.
            minResizePerc (float): Minimum resize percentage for random search.
            maxResizePerc (float): Maximum resize percentage for random search.
            position (str): Initial plot position (e.g., bounding box, centroid).
            placement (str): Plot placement strategy (e.g., fixed, rotated, resized, translated, optimized).
            shape (str): Shape of the simulation plot (e.g., square, circle, rectangle, ellipse, best).
            numberOfTests (int): Number of random tuning runs.

        Raises:
            ValueError: If the requested plot shape is not recognized.
        """
        self.minIterations = minIterations
        self.maxIterations = maxIterations
        self.minTranslatePerc = minTranslatePerc
        self.maxTranslatePerc = maxTranslatePerc
        self.minAngleLimit = minAngleLimit
        self.maxAngleLimit = maxAngleLimit
        self.minResizePerc = minResizePerc
        self.maxResizePerc = maxResizePerc
        self.position = position
        self.placement = placement
        self.shape = shape

        polygonShpFN = workingFolder + polygonShpFN
        outputStatisticsFN = workingFolder + outputStatisticsFN

        plotGenerator = PlotGenerator()

        for iTest in range(0, numberOfTests):
            outputPlotFN = workingFolder + outputPlotFNBase + str(iTest + 1) + ".shp"
            print(f"Test {iTest + 1}/{numberOfTests} ...")
            randomIterations = random.randint(self.minIterations, self.maxIterations)
            percTranslate = (
                random.random() * (self.maxTranslatePerc - self.minTranslatePerc)
                + self.minTranslatePerc
            )
            maxAlpha = (
                random.random() * (self.maxAngleLimit - self.minAngleLimit)
                + self.minAngleLimit
            )
            maxResizePerc = (
                random.random() * (self.maxResizePerc - self.minResizePerc)
                + self.minResizePerc
            )
            plotGenerator.setup(randomIterations, percTranslate, maxAlpha, maxResizePerc)
            print(
                f"randomIterations={randomIterations}, percTranslate={percTranslate}, maxAlpha={maxAlpha}, maxResizePerc={maxResizePerc}"
            )

            startTime = datetime.datetime.now()
            if self.shape == "square":
                plotGenerator.generateSquarePlots(
                    polygonShpFN,
                    idFieldName,
                    outputPlotFN,
                    self.position,
                    self.placement,
                    progressDlg,
                )
            elif self.shape == "circle":
                plotGenerator.generateCirclePlots(
                    polygonShpFN,
                    idFieldName,
                    outputPlotFN,
                    self.position,
                    self.placement,
                    progressDlg,
                )
            elif self.shape == "rectangle":
                plotGenerator.generateRectanglePlots(
                    polygonShpFN,
                    idFieldName,
                    outputPlotFN,
                    self.position,
                    self.placement,
                    progressDlg,
                )
            elif self.shape == "ellipse":
                plotGenerator.generateEllipsePlots(
                    polygonShpFN,
                    idFieldName,
                    outputPlotFN,
                    self.position,
                    self.placement,
                    progressDlg,
                )
            elif self.shape == "best":
                plotGenerator.generateBestPlots(
                    polygonShpFN, idFieldName, outputPlotFN, progressDlg
                )
            else:
                GenSimPlotUtilities.raiseValueError(
                    f"Invalid plot shape ({self.shape}).",
                    progressDlg,
                )
            endTime = datetime.datetime.now()
            duration = endTime - startTime

            statistics = self.calculateStatistics(outputPlotFN, progressDlg)
            self.saveStatistics(
                outputStatisticsFN,
                polygonShpFN,
                randomIterations,
                percTranslate,
                maxAlpha,
                maxResizePerc,
                duration,
                statistics,
            )
            print(f"Duration: {duration}")
            print(statistics)
            #QgsVectorFileWriter.deleteShapeFile(outputPlotFN)
