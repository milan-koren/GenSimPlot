# -*- coding: utf-8 -*-
"""
Package:   GenSimPlot
File:      GenSimPlotLib.py
Version:   2.2
Author:    Milan Koren
Year:      2024
URL:       https://github.com/milan-koren/GenSimPlot
License:   EUPL v1.2 (European Union Public License), https://eupl.eu/

The implementation of various classes for creating different types of simulation plots, 
such as squares, circles, rectangles, and ellipses based on different criteria.
"""

import os
import json
import math
import random
from cmath import rect
from qgis.core import *
from PyQt5.QtCore import QVariant
from osgeo import gdal

from GenSimPlotUtilities import GProgressDialog
from GenSimPlotUtilities import GenSimPlotUtilities


#############################################################################
#   SIMULATION PLOTS
#############################################################################

class PolygonPlot:
    """
    The PolygonPlot class provides foundational functionality for creating and manipulating
    various types of simulation plots based on polygons.

    This class includes methods to set up the centroid, bounding box, and mean coordinates of a polygon,
    and supports generating different simulation plot geometries, including squares, circles, rectangles, and ellipses.

    Subclasses of PolygonPlot implement specific behaviors for creating each type of simulation plot
    through the following virtual methods:
        - createPlot(self, polygon: QgsGeometry): Initializes the plot based on the input polygon geometry.
        - createGeometry(self): Defines the geometry of the simulation plot.
        - clone(self): Creates a copy of the current plot instance.
        - resize(self, perc: float) Adjusts the size of the plot by a specified percentage.

    Attributes:
        sideRatioMax (float):        The maximum allowable ratio between the long and short sides of the bounding rectangle.
        ellipseNumPoints (int):      The number of points used to approximate an ellipse.
        originalPosition (QgsPoint): The initial position of the simulation plot.
        polygonArea (float):         The area of the polygon associated with the plot.
        polygonPerimeter (float):    The perimeter of the associated polygon.
        translatedPosition (QgsPoint): The current position of the simulation plot after translation.
        a (float):                   The length of the plot's long side.
        b (float):                   The length of the plot's short side.
        geom (QgsGeometry):          The geometry of the current simulation plot.
        tx (float):                  The translation distance in the x-direction.
        ty (float):                  The translation distance in the y-direction.
        alpha (float):               The rotation angle of the plot in degrees.
    """

    sideRatioMax = 4.0
    ellipseNumPoints = 100

    def __init__(self):
        self.gname = "geometry"
        self.gposition = "unknown"
        self.originalPosition = QgsPoint(0.0, 0.0)
        self.polygonArea = 0.0
        self.polygonPerimeter = 0.0
        self.translatedPosition = QgsPoint(0.0, 0.0)
        self.a = 0.0
        self.b = 0.0
        self.geom = None
        self.tx = 0.0
        self.ty = 0.0
        self.alpha = 0.0

    def setupCentroid(self, polygon: QgsGeometry):
        """
        Set the initial position of simulation plot to the centroid of the polygon.

        Parameters:
            polygon (QgsGeometry): The polygon for which the centroid is calculated.
        """
        self.originalPosition = polygon.centroid().asPoint()
        self.polygonArea = polygon.area()
        self.polygonPerimeter = polygon.length()
        self.translatedPosition = QgsPointXY(self.originalPosition)

    def setupBBox(self, polygon: QgsGeometry):
        """
        Set up the initial position of plot to centroid of the bounding box of the polygon.

        Parameters:
            polygon (QgsGeometry): The polygon for which the bounding box is calculated.
        """
        self.originalPosition = polygon.boundingBox().center()
        self.polygonArea = polygon.area()
        self.polygonPerimeter = polygon.length()
        self.translatedPosition = QgsPointXY(self.originalPosition)

    def setupMeanXY(self, polygon: QgsGeometry):
        """
        Set up the initial position of plot to the mean coordinates of the polygon.

        Parameters:
            polygon (QgsGeometry): The polygon for which the mean coordinates are calculated.
        """
        self.originalPosition = self.meanXY(polygon)
        self.polygonArea = polygon.area()
        self.polygonPerimeter = polygon.length()
        self.translatedPosition = QgsPointXY(self.originalPosition)

    def setupSquare(self):
        """
        Calculates the side length of a square simulation plot that has an area equal to the given polygon.
        This function ensures the simulation plot has equal long and short sides, resulting in a square plot.
        """
        self.a = math.sqrt(self.polygonArea)
        self.b = self.a

    def createSquare(self):
        """
        Creates a square simulation plot with predefined side length.
        """
        cx = self.originalPosition.x()
        cy = self.originalPosition.y()
        a2 = self.a / 2
        self.geom = QgsGeometry.fromRect(
            QgsRectangle(cx - a2, cy - a2, cx + a2, cy + a2)
        )

    def setupCircle(self):
        """
        Calculates the radius of a circular simulation plot with an area equal to the specified polygon.
        Set up the long and short sides of the simulation plot to be equal.
        """
        r = math.sqrt(self.polygonArea / math.pi)
        self.a = 2 * r
        self.b = self.a

    def createCircle(self):
        """
        Creates a circular simulation plot with predefined diameter and center.
        """
        c = QgsPoint(self.originalPosition.x(), self.originalPosition.y())
        r = self.a / 2.0
        self.geom = QgsGeometry(QgsCircle(c, r, 0.0).toPolygon())

    def setupRectangle(self):
        """
        Calculates the dimensions of a rectangular simulation plot with an area equal to that of the specified polygon.
        Determines the length of both the longer and shorter sides to achieve the specified area.
        """
        d = self.polygonPerimeter * self.polygonPerimeter - 16 * self.polygonArea
        if 0 < d:
            d = math.sqrt(d)
        else:
            d = 0
        self.a = (self.polygonPerimeter + d) / 4
        self.b = (self.polygonPerimeter - d) / 4
        if self.sideRatioMax is not None:
            if self.sideRatioMax < self.a / self.b:
                self.b = math.sqrt(self.polygonArea / self.sideRatioMax)
                self.a = self.polygonArea / self.b

    def createRectangle(self):
        """
        Creates a rectangular simulation plot with predefined dimensions.
        """
        cx = self.originalPosition.x()
        cy = self.originalPosition.y()
        a2 = self.a / 2
        b2 = self.b / 2
        self.geom = QgsGeometry.fromRect(
            QgsRectangle(cx - a2, cy - b2, cx + a2, cy + b2)
        )

    def setupEllipse(self):
        """
        Calculates the major and minor axis of the ellipse simulation plot of equal area of polygon.
        """
        d = self.polygonPerimeter * self.polygonPerimeter - 16 * self.polygonArea
        if 0.0 < d:
            d = math.sqrt(d)
            s = (self.polygonPerimeter + d) / (self.polygonPerimeter - d)
        else:
            d = 0.0
            s = 1.0
        a = math.sqrt(s * self.polygonArea / math.pi)
        b = a / s
        if self.sideRatioMax is not None:
            if self.sideRatioMax < a / b:
                a = math.sqrt(self.sideRatioMax * self.polygonArea / math.pi)
                b = a / self.sideRatioMax
        self.a = 2 * a
        self.b = 2 * b

    def createEllipse(self):
        """
        Creates an elliptical simulation plot with predefined major and minor axes.
        """
        cx = self.originalPosition.x()
        cy = self.originalPosition.y()
        semiMajor = self.a / 2
        semiMinor = self.b / 2
        points = []
        for i in range(self.ellipseNumPoints):
            angle = (2 * math.pi * i) / self.ellipseNumPoints
            x = semiMajor * math.cos(angle)
            y = semiMinor * math.sin(angle)
            p = QgsPointXY(cx + x, cy + y)
            points.append(p)
        points.append(points[0])
        self.geom = QgsGeometry(QgsPolygon(QgsLineString(points)))

    def setupFromPlot(self, plot):
        """
        Sets the parameters of the simulation plot based on an existing plot.
        """
        self.originalPosition = QgsPointXY(plot.originalPosition)
        self.polygonArea = plot.polygonArea
        self.polygonPerimeter = plot.polygonPerimeter
        self.translatedPosition = QgsPointXY(plot.translatedPosition)
        self.a = plot.a
        self.b = plot.b
        self.geom = QgsGeometry(plot.geom)
        self.tx = plot.tx
        self.ty = plot.ty
        self.alpha = plot.alpha

    def translate(self, dx, dy):
        """
        Translates the simulation plot by a given distance along the x and y axes.

        Parameters:
            dx (float): The distance to move the plot along the x-axix.
            dy (float): The distance to move the plot along the y-axis.

        Returns:
            A new simulation plot with the translated geometry.
        """
        nplot = self.clone()
        nplot.geom.translate(dx, dy)
        nplot.translatedPosition = QgsPointXY(
            nplot.translatedPosition.x() + dx, nplot.translatedPosition.y() + dy
        )
        nplot.tx += dx
        nplot.ty += dy
        return nplot

    def rotate(self, angle):
        """
        Rotates the simulation plot by a specified angle.

        Parameters:
            angle (float): The angle of rotation in degrees.

        Returns:
            A new simulation plot with the rotated geometry.
        """
        nplot = self.clone()
        nplot.geom.rotate(angle, nplot.translatedPosition)
        nplot.alpha += angle
        return nplot

    def randomTranslate(self, maxPerc):
        """
        Randomly translates the simulation plot within a specified percentage of its longest side length.

        The plot is shifted by a random distance along both the x and y axes, where the maximum shift is
        determined as a percentage of the plot's longest side.

        Parameters:
            maxPerc (float): The maximum percentage of the longest side length to translate the plot.

        Returns:
            A new simulation plot with the translated geometry.
        """
        dx = self.a * math.sin(math.radians(self.alpha)) + self.b * math.cos(
            math.radians(self.alpha)
        )
        dy = self.a * math.cos(math.radians(self.alpha)) + self.b * math.sin(
            math.radians(self.alpha)
        )
        tx = maxPerc * dx * (2.0 * random.random() - 1.0)
        ty = maxPerc * dy * (2.0 * random.random() - 1.0)
        return self.translate(tx, ty)

    def randomRotate(self, maxAngle):
        """
        Randomly rotates the simulation plot within a specified angle range.

        Parameters:
            maxAngle (float): The maximum angle, in degrees, by which the plot can be randomly rotated.

        Returns:
            A new simulation plot with rotated geometry.
        """
        angle = maxAngle * (2.0 * random.random() - 1.0)
        return self.rotate(angle)

    def resizeRectangle(self, perc):
        """
        Resizes the simulation plot by a given percentage.

        Parameters:
            perc (float): the percentage to scale the simulation plot by.
        """
        a = self.a * (1 + perc)
        b = self.b / (1 + perc)
        if a < b:
            c = b
            b = a
            a = c
        if self.sideRatioMax is not None:
            if a / b <= self.sideRatioMax:
                self.a = a
                self.b = b

    def resize(self, perc: float):
        """
        Resizes the simulation plot by a specified percentage.

        Parameters:
            perc (float): The percentage by which to resize the simulation plot.

        Returns:
            A new instance of the simulation plot with the adjusted geometry.
        """
        plot = self.clone()
        plot.resizeRectangle(perc)
        plot.createGeometry()
        plot.geom.translate(plot.tx, plot.ty)
        plot.geom.rotate(plot.alpha, plot.translatedPosition)
        return plot

    def randomResize(self, maxResizePerc: float):
        """
        Randomly resizes the simulation plot by a specified maximum percentage.

        Parameters:
            maxResizePerc (float): The maximum percentage variation to apply when randomly resizing the plot.

        Returns:
            A new instance of the simulation plot with randomly adjusted geometry.
        """
        perc = maxResizePerc * (2.0 * random.random() - 1.0)
        return self.resize(perc)

    def meanXY(self, polygon: QgsGeometry):
        """
        Calculate the mean coordinates of a polygon.

        Parameters:
            polygon (QgsGeometry): The polygon geometry for which the mean coordinates are calculated.

        Returns:
            QgsPoint: A point with the mean x and y coordinates of the polygon.
        """
        x = 0.0
        y = 0.0
        v = polygon.vertices()
        m = 0
        while v.hasNext():
            p = v.next()
            x += p.x()
            y += p.y()
            m += 1
        if 0 < m:
            x = x / m
            y = y / m
            return QgsPointXY(x, y)
        else:
            return None


class SquareByCentroid(PolygonPlot):
    """
    This class represents a square simulation plot based on the centroid of a polygon.
    """

    def __init__(self):
        super().__init__()
        self.gname = "square"
        self.gposition = "centroid"

    def createPlot(self, polygon: QgsGeometry):
        plot = SquareByCentroid()
        plot.setupCentroid(polygon)
        plot.setupSquare()
        plot.createSquare()
        return plot

    def createGeometry(self):
        plot.createSquare()

    def clone(self):
        plot = SquareByCentroid()
        plot.setupFromPlot(self)
        return plot

    def resize(self, perc: float):
        return self.clone()


class SquareByBBox(PolygonPlot):
    """
    This class represents a square simulation plot based on the bounding box of a polygon.
    """

    def __init__(self):
        super().__init__()
        self.gname = "square"
        self.gposition = "bbox"

    def createPlot(self, polygon: QgsGeometry):
        plot = SquareByBBox()
        plot.setupBBox(polygon)
        plot.setupSquare()
        plot.createSquare()
        return plot

    def createGeometry(self):
        plot.createSquare()

    def clone(self):
        plot = SquareByBBox()
        plot.setupFromPlot(self)
        return plot

    def resize(self, perc: float):
        return self.clone()


class SquareByMeanXY(PolygonPlot):
    """
    This class represents a square simulation plot based on the mean coordinates of a polygon.
    """

    def __init__(self):
        super().__init__()
        self.gname = "square"
        self.gposition = "meanxy"

    def createPlot(self, polygon: QgsGeometry):
        plot = SquareByMeanXY()
        plot.setupMeanXY(polygon)
        plot.setupSquare()
        plot.createSquare()
        return plot

    def createGeometry(self):
        plot.createSquare()

    def clone(self):
        plot = SquareByMeanXY()
        plot.setupFromPlot(self)
        return plot

    def resize(self, perc: float):
        return self.clone()


class CircleByCentroid(PolygonPlot):
    """
    This class represents a circular simulation plot based on the centroid of a polygon.
    """

    def __init__(self):
        super().__init__()
        self.gname = "circle"
        self.gposition = "centroid"

    def createPlot(self, polygon: QgsGeometry):
        plot = CircleByCentroid()
        plot.setupCentroid(polygon)
        plot.setupCircle()
        plot.createCircle()
        return plot

    def createGeometry(self):
        plot.createCircle()

    def clone(self):
        plot = CircleByCentroid()
        plot.setupFromPlot(self)
        return plot

    def resize(self, perc: float):
        return self.clone()

    def rotate(self, angle):
        return self.clone()


class CircleByBBox(PolygonPlot):
    """
    This class represents a circular simulation plot based on the bounding box.
    """

    def __init__(self):
        super().__init__()
        self.gname = "circle"
        self.gposition = "bbox"

    def createPlot(self, polygon: QgsGeometry):
        plot = CircleByBBox()
        plot.setupBBox(polygon)
        plot.setupCircle()
        plot.createCircle()
        return plot

    def createGeometry(self):
        plot.createCircle()

    def clone(self):
        plot = CircleByBBox()
        plot.setupFromPlot(self)
        return plot

    def resize(self, perc: float):
        return self.clone()

    def rotate(self, angle):
        return self.clone()


class CircleByMeanXY(PolygonPlot):
    """
    This class represents a circular simulation plot based on the mean coordinates of a polygon.
    """

    def __init__(self):
        super().__init__()
        self.gname = "circle"
        self.gposition = "meanxy"

    def createPlot(self, polygon: QgsGeometry):
        plot = CircleByMeanXY()
        plot.setupMeanXY(polygon)
        plot.setupCircle()
        plot.createCircle()
        return plot

    def createGeometry(self):
        plot.createCircle()

    def clone(self):
        plot = CircleByMeanXY()
        plot.setupFromPlot(self)
        return plot

    def resize(self, perc: float):
        return self.clone()

    def rotate(self, angle):
        return self.clone()


class RectangleByCentroid(PolygonPlot):
    """
    This class represents a rectangular simulation plot based on the centroid of a polygon.
    """

    def __init__(self):
        super().__init__()
        self.gname = "rectangle"
        self.gposition = "centroid"

    def createPlot(self, polygon: QgsGeometry):
        plot = RectangleByCentroid()
        plot.setupCentroid(polygon)
        plot.setupRectangle()
        plot.createRectangle()
        return plot

    def createGeometry(self):
        self.createRectangle()

    def clone(self):
        plot = RectangleByCentroid()
        plot.setupFromPlot(self)
        return plot


class RectangleByBBox(PolygonPlot):
    """
    This class represents a rectangular simulation plot based on the bounding box.
    """

    def __init__(self):
        super().__init__()
        self.gname = "rectangle"
        self.gposition = "bbox"

    def createPlot(self, polygon: QgsGeometry):
        plot = RectangleByBBox()
        plot.setupBBox(polygon)
        plot.setupRectangle()
        plot.createRectangle()
        return plot

    def createGeometry(self):
        self.createRectangle()

    def clone(self):
        plot = RectangleByBBox()
        plot.setupFromPlot(self)
        return plot


class RectangleByMeanXY(PolygonPlot):
    """
    This class represents a rectangular simulation plot based on the mean coordinates.
    """

    def __init__(self):
        super().__init__()
        self.gname = "rectangle"
        self.gposition = "meanxy"

    def createPlot(self, polygon: QgsGeometry):
        plot = RectangleByMeanXY()
        plot.setupMeanXY(polygon)
        plot.setupRectangle()
        plot.createRectangle()
        return plot

    def createGeometry(self):
        self.createRectangle()

    def clone(self):
        plot = RectangleByMeanXY()
        plot.setupFromPlot(self)
        return plot


class EllipseByCentroid(PolygonPlot):
    """
    This class represents an elliptical simulation plot based on the centroid of a polygon.
    """

    def __init__(self):
        super().__init__()
        self.gname = "ellipse"
        self.gposition = "centroid"

    def createPlot(self, polygon: QgsGeometry):
        plot = EllipseByCentroid()
        plot.setupCentroid(polygon)
        plot.setupEllipse()
        plot.createEllipse()
        return plot

    def createGeometry(self):
        self.createEllipse()

    def clone(self):
        plot = EllipseByCentroid()
        plot.setupFromPlot(self)
        return plot


class EllipseByBBox(PolygonPlot):
    """
    This class represents an elliptical simulation plot based on the bounding box.
    """

    def __init__(self):
        super().__init__()
        self.gname = "ellipse"
        self.gposition = "bbox"

    def createPlot(self, polygon: QgsGeometry):
        plot = EllipseByBBox()
        plot.setupBBox(polygon)
        plot.setupEllipse()
        plot.createEllipse()
        return plot

    def createGeometry(self):
        self.createEllipse()

    def clone(self):
        plot = EllipseByBBox()
        plot.setupFromPlot(self)
        return plot


class EllipseByMeanXY(PolygonPlot):
    """
    This class represents an elliptical simulation plot based on the mean coordinates.
    """

    def __init__(self):
        super().__init__()
        self.gname = "ellipse"
        self.gposition = "meanxy"

    def createPlot(self, polygon: QgsGeometry):
        plot = EllipseByMeanXY()
        plot.setupMeanXY(polygon)
        plot.setupEllipse()
        plot.createEllipse()
        return plot

    def createGeometry(self):
        self.createEllipse()

    def clone(self):
        plot = EllipseByMeanXY()
        plot.setupFromPlot(self)
        return plot



#############################################################################
#   PLOT GENERATOR
#############################################################################

class PlotGenerator:
    """
    The PlotGenerator class facilitates the generation of simulation plots from input polygon geometries.

    This class provides methods to create various simulation plot shapes, including squares, circles, rectangles,
    and ellipses, with flexible positioning options based on attributes such as bounding box, centroid, and mean
    coordinates of the polygon. Additionally, the class supports random transformations - translations, rotations,
    and reshaping - to maximize overlap with source polygons.

    Attributes:
        randomIterations (int): The number of random generation attempts to apply when creating each simulation plot.
                                Higher values can improve accuracy but may increase computation time. Default is 750.
        percTranslate (float):  The maximum allowable percentage for random translation in both x and y directions
                                relative to plot size. Default is 0.1.
        maxAlpha (float):       The maximum rotation angle, in degrees, for random plot rotations to enhance positional
                                variation. Default is 25 degrees.
        maxResizePerc (float):  The maximum percentage by which the plot size can be altered for reshaping, aiding
                                flexibility in adapting plot geometry to source data. Default is 0.15.
        sideRatioMax (float):   The maximum allowable ratio between the longer and shorter sides of a rectangular plot,
                                which constrains plot shape. Default is 4.
    """

   
    def __init__(self):
        """
        Initializes the PlotGenerator class with default values for the simulation plot generation parameters.
        """
        random.seed()
        self.setup()
        self.readHyperparameters("gensimplot.cnf")


    def setup(
        self,
        randomIterations: int = 750,
        percTranslate: float = 0.10,
        maxAlpha: float = 25.00,
        maxResizePerc: float = 0.15,
        sideRatioMax: float = 4.00,
    ):
        """
        Configures the parameters for the simulation plot generation process.

        This method allows customization of the key parameters influencing how simulation plots are generated, including
        the number of random iterations, maximum translation, rotation angle, aspect ratio limits, and reshaping percentage.

        Parameters:
            randomIterations (int): Specifies the number of random iterations for each simulation plot generation. 
            percTranslate (float):  Defines the maximum percentage for random translations in the x and y directions.
            maxAlpha (float):       Sets the maximum allowable rotation angle, in degrees, for random plot rotations. 
            maxResizePerc (float):  Determines the maximum percentage by which a plot's size can be altered. 
            sideRatioMax (float):   Limits the maximum ratio between the long and short sides of a rectangular plot. 
        """
        self.randomIterations = randomIterations
        self.percTranslate = percTranslate
        self.maxAlpha = maxAlpha
        self.sideRatioMax = sideRatioMax
        self.maxResizePerc = maxResizePerc


    def saveHyperparameters(self, configFN: str):
        """
        Saves the current hyperparameters to a JSON file.

        Parameters:
            configFN (str): The path to the JSON file where hyperparameters will be saved.
        """
        configPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), configFN)
        data = {
            "randomIterations": self.randomIterations,
            "percTranslate": self.percTranslate,
            "maxAlpha": self.maxAlpha,
            "maxResizePerc": self.maxResizePerc,
            "sideRatioMax": self.sideRatioMax
        }
        with open(configPath, "w") as f:
            json.dump(data, f, indent=3)

    
    def readHyperparameters(self, configFN: str):
        """
        Reads hyperparameters from a JSON file and updates the class attributes accordingly.

        Parameters:
            configFN (str): The path to the JSON file where hyperparameters will be read.
        """
        configPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), configFN)

        if not os.path.exists(configPath):
            return
            
        with open(configPath, "r") as f:
            data = json.load(f)
        
        self.randomIterations = data.get("randomIterations", self.randomIterations)
        self.percTranslate = data.get("percTranslate", self.percTranslate)
        self.maxAlpha = data.get("maxAlpha", self.maxAlpha)
        self.maxResizePerc = data.get("maxResizePerc", self.maxResizePerc)
        self.sideRatioMax = data.get("sideRatioMax", self.sideRatioMax)
        
        
    def createSPlotFields(self, idField: QgsField):
        """
        Generates a 'QgsFields' object containing fields for simulation plot attributes.

        This function creates a set of fields used to store simulation plot metadata, specifically designed for associating
        plots with unique forest stand IDs. The fields include identifiers essential for organizing and identifying
        simulation plots within a forest management or research dataset.

        Parameters:
            idField (QgsField): The field containing the unique ID for each simulation plot.

        Returns:
            QgsFields: A 'QgsFields' object with the defined field structure for use in simulation plot layers.
        """
        outputFields = QgsFields()
        outputFields.append(idField)
        outputFields.append(QgsField("a", QVariant.Double, "double", 6, 2))
        outputFields.append(QgsField("b", QVariant.Double, "double", 6, 2))
        outputFields.append(QgsField("alpha", QVariant.Double, "double", 6, 2))
        outputFields.append(QgsField("perc", QVariant.Double, "double", 6, 2))
        outputFields.append(QgsField("ishp", QVariant.Double, "double", 6, 2))
        return outputFields

    
    def createSPlotShapeFile(self, outputFN: str, outputFields: QgsFields, crs):
        """
        Creates a new ESRI Shapefile for storing simulation plot geometries.

        This function generates a vector file specifically formatted as an ESRI Shapefile to store simulation plot geometries.
        The output file is initialized with a defined structure of fields and a specified Coordinate Reference System (CRS),
        making it suitable for GIS analysis and visualization.

        Parameters:
            outputFN (str):           The file path and name for the output vector file to be created.
            outputFields (QgsFields): A 'QgsFields' object defining the structure of fields to include in the output file,
                                      typically for storing simulation plot metadata.
            crs (QgsCoordinateReferenceSystem): The CRS in which to save the output file, ensuring spatial accuracy and consistency.

        Returns:
            QgsVectorFileWriter: A 'QgsVectorFileWriter' instance associated with the newly created Shapefile, enabling
                                 further data insertion and manipulation.
        """
        svo = QgsVectorFileWriter.SaveVectorOptions()
        svo.driverName = "ESRI Shapefile"
        return QgsVectorFileWriter.create(
            outputFN,
            outputFields,
            Qgis.WkbType.Polygon,
            crs,
            QgsCoordinateTransformContext(),
            svo,
            QgsFeatureSink.SinkFlags(),
            None,
            None,
        )
      
    
    def createSPlot(self, polygon: QgsGeometry, plotFactory):
        """
        Generates a simulation plot using the geometry of an input polygon.

        This function creates a simulation plot by utilizing the specified 'plotFactory' object, which contains
        the logic to generate plot geometries based on the input polygon. It calls the 'createPlot' method
        of the provided simulation plot object, ensuring that the generated plot aligns with the spatial properties
        of the input polygon geometry.

        Parameters:
            polygon (QgsGeometry): The input polygon geometry that defines the area and shape used for generating
                                   the simulation plot.
            plotFactory:           An instance of the simulation plot class (e.g. RectangleByBBox) that contains
                                   the 'createPlot' method, responsible for creating the plot geometry.

        Returns:
            QgsGeometry: The generated geometry of the simulation plot.
        """
        splot = plotFactory.createPlot(polygon)
        sarea = polygon.intersection(splot.geom).area()
        return (splot, sarea)

    
    def createTranslatedPlot(self, polygon: QgsGeometry, plotFactory):
        """
        Generates a randomly translated simulation plot to maximize overlap with an input polygon.

        This function creates a simulation plot based on the provided polygon geometry. It then iteratively translates
        the plot within a specified percentage ('percTranslate') to maximize the area of overlap between the plot and
        the input polygon.

        Parameters:
            polygon (QgsGeometry): The input polygon geometry that serves as the reference for generating
                                   and aligning the simulation plot.
            plotFactory:           An instance of the simulation plot class that provides the 'createPlot' and 'randomTranslate'
                                   methods to generate and translate the plot geometry.

        Returns:
            SimulationPlot: The randomly translated simulation plot with the maximum overlap area with the input polygon.
        """
        splot = plotFactory.createPlot(polygon)
        sarea = polygon.intersection(splot.geom).area()
        for i in range(self.randomIterations):
            nplot = splot.randomTranslate(self.percTranslate)
            narea = polygon.intersection(nplot.geom).area()
            if sarea < narea:
                sarea = narea
                splot = nplot
        return (splot, sarea)

    
    def createRotatedSPlot(self, polygon: QgsGeometry, plotFactory):
        """
        Generates a randomly rotated simulation plot to maximize overlap with an input polygon.

        This function creates an initial simulation plot based on the provided polygon geometry. It then iteratively
        rotates the plot within a specified maximum angle ('maxAlpha') to maximize the area of overlap between the plot
        and the input polygon.

        Parameters:
            polygon (QgsGeometry): The input polygon geometry that serves as the reference for generating and aligning
                                   the simulation plot.
            plotFactory:           An instance of the simulation plot class that provides the 'createPlot' and 'randomRotate'
                                   methods to generate and rotate the plot geometry.

        Returns:
            SimulationPlot: The randomly rotated simulation plot with the maximum overlap area with the input polygon.
        """
        splot = plotFactory.createPlot(polygon)
        sarea = polygon.intersection(splot.geom).area()
        for i in range(self.randomIterations):
            nplot = splot.randomRotate(self.maxAlpha)
            narea = polygon.intersection(nplot.geom).area()
            if sarea < narea:
                sarea = narea
                splot = nplot
        return (splot, sarea)


    def createResizedSPlot(self, polygon: QgsGeometry, plotFactory):
        """
        Generates a resized simulation plot by applying random size adjustments to maximize overlap with an input polygon.

        This function initializes a simulation plot based on the provided polygon geometry and iteratively applies random
        reshaping transformations. After each reshaping, the overlap area between the resized plot and the input polygon
        is calculated, with the plot configuration that yields the maximum overlap being retained as the final output.

        Parameters:
            polygon (QgsGeometry): The input polygon geometry used as a reference for generating and optimizing the simulation plot.
            plotFactory:           An instance of a simulation plot class providing the 'randomResize' method for performing resize transformation.

        Returns:
            SimulationPlot: The resized simulation plot with the highest achieved overlap area relative to the input polygon.
        """
        splot = plotFactory.createPlot(polygon)
        sarea = polygon.intersection(splot.geom).area()
        for i in range(self.randomIterations):
            nplot = splot.randomResize(self.maxResizePerc)
            narea = polygon.intersection(nplot.geom).area()
            if sarea < narea:
                sarea = narea
                splot = nplot
        return (splot, sarea)

    
    def createOptimizedSPlot(self, polygon: QgsGeometry, plotFactory):
        """
        Generates an optimized simulation plot by applying random transformations to maximize overlap with an input polygon.

        This function creates an initial simulation plot based on the given polygon geometry and iteratively applies random
        reshaping, translation, and rotation transformations to the plot. Each transformation sequence is evaluated for its
        overlap area with the input polygon, and the plot configuration yielding the maximum overlap area is retained.

        Parameters:
            polygon (QgsGeometry): The input polygon geometry used as a reference for generating and optimizing the simulation plot.
            plotFactory:           An instance of a simulation plot class that provides 'createPlot', 'randomResize',
                                   'randomTranslate', and 'randomRotate' methods to perform the transformations.

        Returns:
            SimulationPlot: The optimized simulation plot with the highest overlap area with the input polygon.
        """
        splot = plotFactory.createPlot(polygon)
        sarea = polygon.intersection(splot.geom).area()
        for i in range(self.randomIterations):
            nplot = splot.randomResize(self.maxResizePerc)
            nplot = nplot.randomTranslate(self.percTranslate)
            nplot = nplot.randomRotate(self.maxAlpha)
            narea = polygon.intersection(nplot.geom).area()
            if sarea < narea:
                sarea = narea
                splot = nplot
        return (splot, sarea)

    
    def createBestSPlot(self, polygon: QgsGeometry, plotFactory):
        """
        Generates the most optimal simulation plot that maximizes overlap with the input polygon.

        This function iterates through various shapes (square, circle, rectangle, and ellipse) and different
        positioning methods (aligned with the bounding box, centered on the centroid, or centered on the mean coordinates)
        to generate a simulation plot. For each combination, it applies random spatial transformations to achieve maximum
        overlap area with the input polygon. The resulting plot with the highest overlap is returned.

        Parameters:
            polygon (QgsGeometry): The input polygon geometry used as a reference for generating and optimizing the simulation plot.
            plotFactory:           An instance of a simulation plot class that provides methods such as 'createPlot',
                                   'randomResize', 'randomTranslate', and 'randomRotate' for performing transformations.

        Returns:
            The optimized simulation plot that achieves the maximum overlap area with the input polygon.
        """
        bplot, barea = self.createOptimizedSPlot(polygon, SquareByBBox())
        splot, sarea = self.createOptimizedSPlot(polygon, SquareByCentroid())
        if barea < sarea:
            bplot = splot
            barea = sarea
        splot, sarea = self.createOptimizedSPlot(polygon, SquareByMeanXY())
        if barea < sarea:
            bplot = splot
            barea = sarea

        splot, sarea = self.createOptimizedSPlot(polygon, CircleByBBox())
        if barea < sarea:
            bplot = splot
            barea = sarea
        splot, sarea = self.createOptimizedSPlot(polygon, CircleByCentroid())
        if barea < sarea:
            bplot = splot
            barea = sarea
        splot, sarea = self.createOptimizedSPlot(polygon, CircleByMeanXY())
        if barea < sarea:
            bplot = splot
            barea = sarea

        splot, sarea = self.createOptimizedSPlot(polygon, RectangleByBBox())
        if barea < sarea:
            bplot = splot
            barea = sarea
        splot, sarea = self.createOptimizedSPlot(polygon, RectangleByCentroid())
        if barea < sarea:
            bplot = splot
            barea = sarea
        splot, sarea = self.createOptimizedSPlot(polygon, RectangleByMeanXY())
        if barea < sarea:
            bplot = splot
            barea = sarea

        splot, sarea = self.createOptimizedSPlot(polygon, EllipseByBBox())
        if barea < sarea:
            bplot = splot
            barea = sarea
        splot, sarea = self.createOptimizedSPlot(polygon, EllipseByCentroid())
        if barea < sarea:
            bplot = splot
            barea = sarea
        splot, sarea = self.createOptimizedSPlot(polygon, EllipseByMeanXY())
        if barea < sarea:
            bplot = splot
            barea = sarea

        return (bplot, barea)

    
    def createPlots(
        self,
        inputFN: str,
        idFieldName: str,
        outputFN: str,
        plotFactory: PolygonPlot,
        createFn,
        progressDlg: GProgressDialog,
    ):
        """
        Generates and saves simulation plots for each polygon feature in an input vector file, saving them to an output vector file.

        This function reads polygon geometries from an input vector file, uses the specified simulation plot factory and creation
        function to generate individual simulation plots, and writes these plots to an output vector file. The output includes
        calculated attributes, such as area ratio, shape index, and rotation angle for each plot.

        Parameters:
            inputFN (str):       Path to the input vector file containing polygon features.
            idFieldName (str):   Field name for the polygon ID in the input file.
            outputFN (str):      Path to the output vector file for saving the generated simulation plots.
            plotFactory (SimulationPlotFactory): Instance of the plot factory used to generate plot geometries.
            createFn (function): Function reference to create simulation plots based on polygons.
            progressDlg (GProgressDialog): Optional parameter for displaying a progress dialog during the process.

        Raises:
            ValueError: If the input layer does not contain polygon geometries or if there is an issue saving a plot to the output layer.
            Exception: If feature cannot be saved to the output layer.
            Exception: If process was canceled by the user.

        Process:
            1. Initializes random seed and loads the input vector layer.
            2. Ensures that the input layer geometry type is polygon.
            3. Sets up output fields and creates the output vector file with specified fields and CRS.
            4. Iterates through each feature in the input layer, generating a simulation plot with 'createFn'.
            5. Calculates plot-specific metrics, including overlap percentage and shape index.
            6. Saves each plot with its attributes to the output vector layer.

        Returns:
            None: The function writes output directly to the specified file path.

        Output Attributes:
            - Polygon ID.
            - Simulation plot dimensions ('a', 'b'), rotation angle ('alpha'), and overlap area percentage with the original polygon.
            - Shape index computed from the perimeter-to-area ratio of the input polygon.

        Usage:
            This function is ideal for creating detailed simulation plots for each polygon in the input data, storing all relevant
            geometry and metrics in a new output file.
        """

        inputLayer = QgsVectorLayer(inputFN, "input polygons", "ogr")
        if inputLayer.geometryType() != Qgis.GeometryType.Polygon:
            GenSimPlotUtilities.raiseValueError(f"Geometry must be POLYGON ({inputFN}).", progressDlg)
        inputIDField = inputLayer.fields().field(idFieldName)
        
        outputFields = self.createSPlotFields(QgsField(inputIDField))
        outputLayer = self.createSPlotShapeFile(
            outputFN, outputFields, inputLayer.crs()
        )
        
        n = inputLayer.featureCount()
        GenSimPlotUtilities.startProgress(
            progressDlg, f"Generating simulation plots to {outputFN} ...", n
        )

        for fid in range(0, n):
            inputFeature = inputLayer.getFeature(fid)
            polygon = inputFeature.geometry().asGeometryCollection()[0]
            garea = polygon.area()
            ishp = polygon.length() / math.sqrt(garea)
            splot, sarea = createFn(polygon, plotFactory)
            outputFeature = QgsFeature(outputFields)
            outputFeature.setAttributes(
                [
                    inputFeature[idFieldName],
                    splot.a,
                    splot.b,
                    splot.alpha,
                    100.0 * sarea / garea,
                    ishp,
                ]
            )
            outputFeature.setGeometry(splot.geom)
            if not outputLayer.addFeature(outputFeature):
                GenSimPlotUtilities.raiseException("Cannnot save feature.", progressDlg)
            GenSimPlotUtilities.incrementProgress(progressDlg)

        del(outputLayer)


    def generateFixedPlots(
        self, 
        inputFN: str, 
        idFieldName: str, 
        outputFN: str, 
        plotFactory: PolygonPlot,
        progressDlg: GProgressDialog,
    ):
        """
        Generates fixed simulation plots for each polygon feature in the input vector file and saves them to an output vector file.

        This function iterates over each polygon in the input vector file, creating a fixed simulation plot based on a predefined
        configuration provided by the 'plotFactory'. Each generated plot is saved to an output vector file, complete with attributes
        linking back to the original polygon and containing simulation-specific details.

        Parameters:
            inputFN (str):     Path to the input vector file containing polygon geometries.
            idFieldName (str): Field name for the polygon ID in the input vector file.
            outputFN (str):    Path to the output vector file where the generated simulation plots will be saved.
            plotFactory (PolygonPlot): Instance of simulation plot class responsible for generating the plot geometries.
            progressDlg (GProgressDialog): Optional parameter for displaying a progress dialog during the process.

        Details:
            - This function uses 'self.createPlots', a generalized method for plot creation, along with a specific plot-creation
              instance of the simulation plot class.
            - A fixed simulation plot is generated for each polygon feature in the input vector file and saved to the output vector file.
            - The output file includes attributes for the original polygon ID and additional information related to the generated plot.

        Returns:
            None: The function directly writes the generated simulation plots to the specified output file.

        Usage:
            'generateFixedPlots' is suitable when a consistent, non-randomized plot shape is needed for each polygon in the input data.
        """
        self.createPlots(
            inputFN, 
            idFieldName, 
            outputFN, 
            plotFactory, 
            self.createSPlot, 
            progressDlg
        )


    def generateTranslatedPlots(
        self,
        inputFN: str, 
        idFieldName: str, 
        outputFN: str, 
        plotFactory: PolygonPlot,
        progressDlg: GProgressDialog,
    ):
        """
        Generates simulation plots by applying random translations to each polygon feature in the input vector file
        and saves the results to an output vector file.

        This function processes each polygon in the input vector file, creating simulation plots with randomized
        translations based on the specified parameters in the 'plotFactory'. The translated plots are saved to an
        output vector file.

        Parameters:
            inputFN (str):     Path to the input vector file containing polygon features.
            idFieldName (str): Field name for the polygon ID in the input vector file.
            outputFN (str):    Path to the output vector file for saving the generated translated simulation plots.
            plotFactory (PolygonPlot): An instance of the simulation plot class responsible for creating the plot geometry and managing translations.
            progressDlg (GProgressDialog): Optional parameter for displaying a progress dialog during the process.

        Details:
            - For each polygon feature in the input vector file, a new plot is created with random translations.
            - This function leverages 'self.createPlots', a generalized plot-creation method, with 'self.createTranslatedPlot'
              as the creation function to apply translation to each simulation plot.
            - The output vector file records attributes that associate each plot with its original polygon ID, alongside details
              specific to the translation.

        Returns:
            None: This function directly saves the output to the specified file path.

        Usage:
           'generateTranslatedPlots' is ideal for scenarios requiring spatial variation in plot positioning with alignment
            along coordinate axes, such as ecological or spatial sampling simulations where greater overlap improves representativeness.
        """
        self.createPlots(
            inputFN,
            idFieldName,
            outputFN,
            plotFactory,
            self.createTranslatedPlot,
            progressDlg,
        )

    
    def generateResizedPlots(
        self, 
        inputFN: str, 
        idFieldName: str, 
        outputFN: str, 
        plotFactory: PolygonPlot,
        progressDlg: GProgressDialog,
    ):
        """
        Generates simulation plots with randomized size adjustments for each polygon feature in the input vector file, saving them to an output file.

        This function reads polygon geometries from the specified input vector file, applies random resizing transformations to create simulation 
        plots with variable dimensions. It uses the given 'plotFactory' instance and the 'createResizedSPlot' method to control the resizing process
        and save the plots to the specified output file.

        Parameters:
            inputFN (str): Path to the input vector file containing polygon features.
            idFieldName (str): Name of the field representing a unique identifier for each polygon in the input file.
            outputFN (str): Path to the output vector file where the resized simulation plots will be saved.
            plotFactory (PolygonPlot): An instance of the plot class responsible for generating and resizing plot geometries.
            progressDlg (GProgressDialog): Instance of a progress dialog to display updates throughout the resizing operation.

        Details:
            - Processes each polygon feature in the input vector file to create a resized simulation plot using random size variations.
            - Calls 'self.createPlots', a generalized method for plot generation, and 'self.createResizedSPlot' for applying size adjustments 
              that maintain area constraints and improve spatial alignment within each polygon.
            - Attributes in the output vector file link each resized plot to its original polygon ID and include additional plot-specific data.

        Raises:
            ValueError: If the input layer's geometry is not a polygon or if there is an error saving a plot to the output layer.

        Returns:
            None: The function directly writes the resized simulation plots to the specified output file.

        Usage:
            'generateResizedPlots' is suitable for tasks requiring simulation plots with variable sizes for enhanced spatial alignment 
            and coverage. It is ideal for scenarios where adaptive plot sizes are necessary to improve overlap with source polygons 
            for detailed spatial analysis.
        """
        self.createPlots(
            inputFN,
            idFieldName,
            outputFN,
            plotFactory,
            self.createResizedSPlot,
            progressDlg,
        )


    def generateRotatedPlots(
        self, 
        inputFN: str, 
        idFieldName: str, 
        outputFN: str, 
        plotFactory: PolygonPlot,
        progressDlg: GProgressDialog,
    ):
        """
        Generates randomly rotated simulation plots for each polygon feature in the input vector file and saves them to an output vector file.

        This function processes polygons from an input vector file, applies random rotational transformations to create simulation plots
        using the specified 'plotFactory' instance and the 'createRotatedSPlot' function, and saves each generated plot to the specified
        output file.

        Parameters:
            inputFN (str):     Path to the input vector file containing polygon features.
            idFieldName (str): Field name representing the polygon ID in the input file.
            outputFN (str):    Path to the output vector file where rotated simulation plots will be saved.
            plotFactory (PolygonPlot): An instance of the simulation plot class responsible for generating plot geometries.
            progressDlg (GProgressDialog): Optional parameter for displaying a progress dialog during the process.

        Details:
            - Each polygon feature in the input vector file is processed to create a randomly rotated simulation plot.
            - Uses 'self.createPlots', a generalized plot-creation method, with 'self.createRotatedSPlot' to apply
              random rotations to each plot.
            - The output vector file records attributes that associate each plot with its original polygon ID, alongside details
              specific to the rotation.

        Raises:
            ValueError: Raised if the input layer geometry is not a polygon or if there is an error saving a plot to the output layer.

        Returns:
            None: This function directly writes output to the specified file path.

        Usage:
            'generateRotatedPlots' is ideal for applications requiring rotated simulation plots, such as spatial sampling or ecological
            studies, where randomly rotated plots can improve the spatial overlap and alignment with the original polygon.
        """
        self.createPlots(
            inputFN,
            idFieldName,
            outputFN,
            plotFactory,
            self.createRotatedSPlot,
            progressDlg,
        )


    def generateOptimizedPlots(
        self, 
        inputFN: str, 
        idFieldName: str, 
        outputFN: str, 
        plotFactory: PolygonPlot,
        progressDlg: GProgressDialog,
    ):
        """
        Generates optimized simulation plots for each polygon feature in the input vector file and saves them to an output vector file.

        This function processes polygons from an input vector file and applies a series of transformation - such as random
        translations, rotations, and reshaping - using the 'plotFactory' instance and the 'createOptimizedSPlot' function
        to maximize spatial overlap with the input polygons. The resulting plots are saved to the specified output file.

        Parameters:
            inputFN (str):     Path to the input vector file containing polygon features.
            idFieldName (str): Field name representing the polygon ID in the input file.
            outputFN (str):    Path to the output vector file where the optimized simulation plots will be saved.
            plotFactory (PolygonPlot): An instance of the simulation plot class responsible for generating plot geometries.
            progressDlg (GProgressDialog): Optional parameter for displaying a progress dialog during the process.

        Details:
            - Utilizes 'self.createPlots', a generalized plot-creation method, with 'self.createOptimizedSPlot' to apply iterative
              transformations aimed at maximizing area overlap with the original polygon.
            - Each plot undergoes randomized adjustments in position, rotation, and size to achieve optimal alignment
              with the input polygons.

        Raises:
            ValueError: Raised if the input layer geometry is not a polygon or if a plot cannot be saved to the output layer.

        Returns:
            None: The function directly writes the output to the specified file path.

        Usage:
            'generateOptimizedPlots' is particularly useful for spatial simulations or sampling studies where high overlap
            between simulation plots and source polygons is essential, providing a tailored fit to complex polygon geometries.
        """
        self.createPlots(
            inputFN,
            idFieldName,
            outputFN,
            plotFactory,
            self.createOptimizedSPlot,
            progressDlg,
        )


    def generatePlots(
        self, 
        inputFN: str, 
        idFieldName: str, 
        outputFN: str, 
        plotFactory: PolygonPlot,
        plotPlacement: str,
        progressDlg: GProgressDialog,):
        """
        Generates simulation plots for each polygon feature in the input vector file and saves them to an output vector file,
        based on the specified placement strategy.

        This function provides a high-level interface for generating simulation plots with various spatial configurations,
        including fixed, translated, rotated, and optimized placements. Depending on the 'plotPlacement' parameter, the function
        directs to specific plot-generation methods that apply unique transformations to the simulation plots, leveraging the
        'plotFactory' to create the geometry and attributes.

        Parameters:
            inputFN (str):       Path to the input vector file containing polygon features.
            idFieldName (str):   Field name representing the polygon ID in the input file.
            outputFN (str):      Path to the output vector file to save the generated simulation plots.
            plotFactory (SimulationPlotFactory): An instance of the simulation plot class responsible for generating plot geometries.
            plotPlacement (str): Specifies the placement strategy for the plots. Options include:
                                 - "fixed": Generates plots with a fixed position.
                                 - "resized": Randomly alters plot size while preserving area.
                                 - "rotated": Applies random rotations to plot orientation.
                                 - "translated": Applies random translations to plot positions.
                                 - "optimized": Iteratively adjusts placement to maximize plot overlap with the polygon.
            progressDlg (GProgressDialog): Optional parameter for displaying a progress dialog during the process.

        Raises:
            ValueError: Raised if 'plotPlacement' is not one of the accepted options.

        Returns:
            None: The function directly saves the generated simulation plots to the specified output file.

        Usage:
            'generatePlots' is suitable for scenarios where multiple spatial configuration options are required, allowing users to
            select between fixed, translated, rotated, resized, and optimized placements based on analysis needs. This function simplifies
            the plot generation process by selecting the appropriate method based on the 'plotPlacement' parameter.
        """
        if plotPlacement == "fixed":
            self.generateFixedPlots(inputFN, idFieldName, outputFN, plotFactory, progressDlg)
        elif plotPlacement == "translated":
            self.generateTranslatedPlots(inputFN, idFieldName, outputFN, plotFactory, progressDlg)
        elif plotPlacement == "rotated":
            self.generateRotatedPlots(inputFN, idFieldName, outputFN, plotFactory, progressDlg)
        elif plotPlacement == "resized":
            self.generateResizedPlots(inputFN, idFieldName, outputFN, plotFactory, progressDlg)
        elif plotPlacement == "optimized":
            self.generateOptimizedPlots(inputFN, idFieldName, outputFN, plotFactory, progressDlg)
        else:
            GenSimPlotUtilities.raiseValueError(
                f"Invalid plot placement option ({plotPlacement}).", 
                progressDlg,
            )


    def generateSquarePlots(
        self, inputFN, idFieldName, outputFN, plotPosition, plotPlacement, progressDlg
    ):
        """
        Generates square simulation plots based on input polygon geometries, with configurable positioning and placement options.

        This function reads polygon geometries from an input vector file and creates square simulation plots according to
        specified positioning and placement strategies. Positioning options (such as aligning with the bounding box, centroid,
        or mean coordinates) determine where the square plot is centered within each polygon. The placement strategy
        applies additional transformations, such as fixed, rotated, translated, or optimized placements,
        to control plot orientation and spatial adjustments.

        Parameters:
            inputFN (str):       Path to the input vector file containing polygon features.
            idFieldName (str):   Field name representing the polygon ID in the input file.
            outputFN (str):      Path to the output vector file to save the generated square plots.
            plotPosition (str):  Specifies how to position the square plot within each polygon. Options include:
                                 - "bounding box": Aligns the square with the bounding box of the polygon.
                                 - "centroid": Centers the square at the polygon's centroid.
                                 - "mean coordinates": Centers the square at the mean x and y coordinates of the polygon.
            plotPlacement (str): Specifies the placement strategy for the square plots. Options include:
                                 - "fixed": Generates plots with a fixed position.
                                 - "resized": Randomly alters plot size while preserving area; does not affect square plots.
                                 - "rotated": Applies random rotations to plot orientation.
                                 - "translated": Applies random translations to plot positions.
                                 - "optimized": Iteratively adjusts placement to maximize plot overlap with the polygon.
            progressDlg (GProgressDialog): Optional parameter for displaying a progress dialog during the process.

        Raises:
            ValueError: If 'plotPosition' is not one of the accepted options.

        Returns:
            None: The function directly writes the generated plots to the specified output vector file.

        Usage:
            'generateSquarePlots' is ideal for creating square-shaped simulation plots where specific alignment with polygon
            features is required, such as aligning with bounding boxes or centering on mean coordinates. Combined with
            the 'plotPlacement' options, this function offers flexibility for ecological sampling or spatial analyses where
            varying alignment and positioning are necessary.
        """
        if plotPosition == "bounding box":
            self.generatePlots(
                inputFN, idFieldName, outputFN, SquareByBBox(), plotPlacement, progressDlg
            )
        elif plotPosition == "centroid":
            self.generatePlots(
                inputFN, idFieldName, outputFN, SquareByCentroid(), plotPlacement, progressDlg
            )
        elif plotPosition == "mean coordinates":
            self.generatePlots(
                inputFN, idFieldName, outputFN, SquareByMeanXY(), plotPlacement, progressDlg
            )
        else:
            GenSimPlotUtilities.raiseValueError(
                f"Invalid plot position option ({plotPosition}).",
                progressDlg,
            )


    def generateCirclePlots(
        self, inputFN, idFieldName, outputFN, plotPosition, plotPlacement, progressDlg
    ):
        """
        Generates circular simulation plots based on input polygon geometries, configured by specified position and placement criteria.

        This function reads polygon geometries from an input vector file and generates circular simulation plots according to
        the desired positioning within each polygon and placement strategy. The 'plotPosition' parameter determines the center
        point of the circle, while the 'plotPlacement' parameter defines spatial transformations like fixed positioning,
        random rotation, translation, or optimized placement for enhanced overlap with the polygon.

        Parameters:
            inputFN (str):       Path to the input vector file containing polygon features.
            idFieldName (str):   Field name representing the polygon ID in the input file.
            outputFN (str):      Path to the output vector file to store the generated circular plots.
            plotPosition (str):  Specifies the positioning approach for centering the circle within each polygon. Options include:
                                 - "bounding box": Aligns the circle with the bounding box of the polygon.
                                 - "centroid": Centers the circle at the polygon's centroid.
                                 - "mean coordinates": Centers the circle at the mean x and y coordinates of the polygon.
            plotPlacement (str): Specifies the placement strategy for the circle plots, offering additional spatial adjustments:
                                 - "fixed": Generates plots with a fixed position.
                                 - "resized": Randomly alters plot size while preserving area; does not affect circular plots.
                                 - "rotated": Applies random rotations to plot orientation.
                                 - "translated": Applies random translations to plot positions.
                                 - "optimized": Iteratively adjusts placement to maximize plot overlap with the polygon.
            progressDlg (GProgressDialog): Optional parameter for displaying a progress dialog during the process.
            
        Raises:
            ValueError: If 'plotPosition' is not one of the accepted options.

        Returns:
            None: The function directly writes the generated circular plots to the specified output vector file.

        Usage:
            'generateCirclePlots' is useful for creating circular simulation plots where specific alignment within polygon
            features is needed. It is particularly beneficial in spatial analyses and sampling applications where consistent
            positioning combined with flexible spatial adjustments enhances data representativeness.
        """
        if plotPosition == "bounding box":
            self.generatePlots(
                inputFN, idFieldName, outputFN, CircleByBBox(), plotPlacement, progressDlg
            )
        elif plotPosition == "centroid":
            self.generatePlots(
                inputFN, idFieldName, outputFN, CircleByCentroid(), plotPlacement, progressDlg
            )
        elif plotPosition == "mean coordinates":
            self.generatePlots(
                inputFN, idFieldName, outputFN, CircleByMeanXY(), plotPlacement, progressDlg
            )
        else:
            GenSimPlotUtilities.raiseValueError(
                f"Invalid plot position option ({plotPosition}).",
                progressDlg,
            )


    def generateRectanglePlots(
        self, inputFN, idFieldName, outputFN, plotPosition, plotPlacement, progressDlg
    ):
        """
        Generates rectangular simulation plots based on input polygon geometries, configured by specified positioning and placement criteria.

        This function reads polygons from an input vector file and creates rectangular simulation plots for each polygon feature.
        Positioning criteria determine where the rectangle is placed within the polygon, while placement strategies apply spatial
        transformations, such as fixed placement, reshaping, rotations, translations, and optimized positioning.

        Parameters:
            inputFN (str):       Path to the input vector file containing polygon features.
            idFieldName (str):   Field name representing the polygon ID in the input file.
            outputFN (str):      Path to the output vector file to store the generated rectangular plots.
            plotPosition (str):  Specifies the alignment method for positioning the rectangle within each polygon. Options include:
                                 - "bounding box": Aligns the rectangle to the polygon's bounding box dimensions.
                                 - "centroid": Centers the rectangle on the polygon's centroid.
                                 - "mean coordinates": Centers the rectangle at the mean x and y coordinates of the polygon.
            plotPlacement (str): Specifies the placement strategy for the rectangle plots, providing spatial flexibility:
                                 - "fixed": Generates plots with a fixed position within the polygon.
                                 - "resized": Randomly alters plot size while preserving area.
                                 - "rotated": Applies random rotations to adjust plot orientation.
                                 - "translated": Applies random translations to adjust plot positioning.
                                 - "optimized": Iteratively optimizes placement to maximize plot overlap with the polygon.
            progressDlg (GProgressDialog): Optional parameter for displaying a progress dialog during the process.

        Raises:
            ValueError: If 'plotPosition' is not one of the accepted options.

        Returns:
            None: The function directly writes the generated rectangular plots to the specified output vector file.

        Usage:
            'generateRectanglePlots' is ideal for applications requiring rectangular plots with specific spatial alignment within
            polygon features, such as habitat sampling or environmental monitoring tasks.
        """
        if plotPosition == "bounding box":
            self.generatePlots(
                inputFN, idFieldName, outputFN, RectangleByBBox(), plotPlacement, progressDlg
            )
        elif plotPosition == "centroid":
            self.generatePlots(
                inputFN, idFieldName, outputFN, RectangleByCentroid(), plotPlacement, progressDlg
            )
        elif plotPosition == "mean coordinates":
            self.generatePlots(
                inputFN, idFieldName, outputFN, RectangleByMeanXY(), plotPlacement, progressDlg
            )
        else:
            GenSimPlotUtilities.raiseValueError(
                f"Invalid plot position option ({plotPosition}).",
                progressDlg,
            )


    def generateEllipsePlots(
        self, inputFN, idFieldName, outputFN, plotPosition, plotPlacement, progressDlg
    ):
        """
        Generates elliptical simulation plots for each polygon feature in the input vector file, based on the specified
        plot positioning and placement options, and saves them to an output vector file.

        This function reads polygons from the input vector file, generates elliptical plots according to the selected
        position criteria (bounding box, centroid, or mean coordinates), and applies the specified placement (fixed, resized, rotated,
        translated, or optimized). Each generated plot is saved to an output file with attributes that identify the original polygon
        and store relevant simulation details.

        Parameters:
            inputFN (str):       Path to the input vector file containing polygon features.
            idFieldName (str):   Field name in the input file for identifying each polygon.
            outputFN (str):      Path to the output vector file for storing the generated elliptical plots.
            plotPosition (str):  Specifies the positioning of the plot within each polygon; options include:
                                 - "bounding box": Aligns the ellipse with the polygon's bounding box.
                                 - "centroid": Centers the ellipse on the polygon's centroid.
                                 - "mean coordinates": Positions the ellipse at the mean x and y coordinates of the polygon.
            plotPlacement (str): Specifies how the plot is placed within the polygon:
                                 - "fixed": Generates plots with a fixed position within the polygon.
                                 - "resized": Randomly alters plot size while preserving area.
                                 - "rotated": Applies random rotations to adjust plot orientation.
                                 - "translated": Applies random translations to adjust plot positioning.
                                 - "optimized": Iteratively optimizes placement to maximize plot overlap with the polygon.
            progressDlg (GProgressDialog): Optional parameter for displaying a progress dialog during the process.

        Raises:
            ValueError: If an invalid plot position is specified.

        Usage:
            generateEllipsePlots' is suitable for creating elliptical simulation plots that align with specific polygon
            attributes, such as bounding box dimensions or centroid location. This function is valuable for applications
            like spatial analysis or ecological studies where elliptical plot shapes are necessary to represent area coverage
            consistently across varying polygon features.
        """
        if plotPosition == "bounding box":
            self.generatePlots(
                inputFN, idFieldName, outputFN, EllipseByBBox(), plotPlacement, progressDlg
            )
        elif plotPosition == "centroid":
            self.generatePlots(
                inputFN, idFieldName, outputFN, EllipseByCentroid(), plotPlacement, progressDlg
            )
        elif plotPosition == "mean coordinates":
            self.generatePlots(
                inputFN, idFieldName, outputFN, EllipseByMeanXY(), plotPlacement, progressDlg
            )
        else:
            GenSimPlotUtilities.raiseValueError(
                f"Invalid plot position option ({plotPosition}).",
                progressDlg,
            )


    def generateBestPlots(
        self,
        inputFN: str,
        idFieldName: str,
        outputFN: str,
        progressDlg: GProgressDialog,
    ):
        """
        Generates simulation plots for each polygon feature in the input vector file, maximizing overlap
        with the original polygon, and saves them to an output vector file.

        This function reads polygon features from an input vector file, applies an optimization process to create
        simulation plots that maximize spatial overlap with each original polygon feature, and saves the results
        to an output file. The output includes each plot with relevant attributes and ID associations for
        tracking and analysis.

        Parameters:
            inputFN (str):     Path to the input vector file containing polygon features.
            idFieldName (str): Field name representing the polygon ID in the input file.
            outputFN (str):    Path to the output vector file where the simulation plots will be stored.
            progressDlg (GProgressDialog): A dialog window to display the progress of the plot generation process.

        Returns:
            None: The function directly writes the generated simulation plots to the specified output file.

        Usage:
            Use 'generateBestPlots' in scenarios that demand maximum spatial representativeness, where optimal alignment
            and coverage of each simulation plot with its corresponding polygon are essential. This function is ideal for
            applications in spatial analysis, ecological modeling, or sampling simulations that benefit from enhanced
            plot-polygon overlap.
        """
        self.createPlots(
            inputFN,
            idFieldName,
            outputFN,
            None,
            self.createBestSPlot,
            progressDlg,
        )



#############################################################################
#   POINTS ON SIMULATION PLOTS
#############################################################################

class PointsGenerator:
    """
    Generates a grid of points over the bounding rectangle of each simulation plot.

    This class provides functionality for generating a regularly spaced grid of points within the rectangular bounds
    of simulation plots. Each generated point can optionally be clipped to fit within the simulation plot's boundaries.
    The class supports varying grid densities by adjusting the number of points along the shorter side of the bounding rectangle,
    and aligns the grid according to the plot's rotation.

    Attributes:
        bufPerc (float):        A percentage defining the buffer size for clipping points within the plot boundary.
        bufQCirclePoints (int): Number of points used to define circular buffers when clipping points to plot boundaries.
    """

    bufPerc = 0.005
    bufQCirclePoints = 6

    def createSPointsFields(self, idField: QgsField):
        """
        Creates the QgsFields structure for storing simulation plot points.

        This method sets up a field schema for the output vector file containing points. Each point has an ID
        and positional attributes (row and column) within the grid.

        Parameters:
            idField (QgsField): The field representing the simulation plot ID.

        Returns:
            QgsFields: A list of fields to be included in the output vector file for storing simulation plot points.
        """
        outputFields = QgsFields()
        outputFields.append(idField)
        outputFields.append(QgsField("row", QVariant.Int, "int", 4))
        outputFields.append(QgsField("column", QVariant.Int, "int", 4))
        return outputFields

    def createSPointsShapeFile(self, outputFN, outputFields, crs):
        """
        Creates an output shapefile to store simulation plot points.

        This method initializes an output vector file for storing point geometries representing simulation plot points.
        The file is structured according to the specified fields and CRS.

        Parameters:
            outputFN (str):           Path to the output vector file.
            outputFields (QgsFields): The fields to include in the output file.
            crs (QgsCoordinateReferenceSystem): The coordinate reference system for the output file.

        Returns:
            QgsVectorFileWriter: A writer object for the newly created vector file.


        Usage:
            This method is used to create a new vector file for storing simulation plot points. It is typically called before
            generating and writing points to the output file.
        """
        svo = QgsVectorFileWriter.SaveVectorOptions()
        svo.driverName = "ESRI Shapefile"
        return QgsVectorFileWriter.create(
            outputFN,
            outputFields,
            Qgis.WkbType.Point,
            crs,
            QgsCoordinateTransformContext(),
            svo,
            QgsFeatureSink.SinkFlags(),
            None,
            None,
        )

    def generatePointsX(
        self,
        polygon: QgsMultiPolygon,
        inputID: str,
        alpha: float,
        a: float,
        b: float,
        nPoints: int,
        outputLayer: QgsVectorFileWriter,
        outputFields: QgsFields,
        clipPoints: bool,
    ):
        """
        Generates a grid of points within a simulation plot when the x-side is shorter than the y-side.

        Creates a grid where points are aligned along the shorter side (a <= b), ensuring the specified number of points
        along the shorter side of the rectangle. Points are optionally clipped to fit within the plot boundaries and
        rotated to align with the plot's orientation.

        Parameters:
            polygon (QgsMultiPolygon): Input polygon geometry representing the simulation plot.
            inputID (str):             Simulation plot ID.
            alpha (float):             Rotation angle of the plot.
            a (float):                 Length of the long side of the plot.
            b (float):                 Length of the short side of the plot.
            nPoints (int):             Number of points along the long side.
            outputLayer (QgsVectorFileWriter): The output layer for storing generated points.
            outputFields (QgsFields):  Field schema for the output vector file.
            clipPoints (bool):         Flag to clip points within plot boundaries.

        Returns:
            None: The method writes the generated points to the output vector file.
        """
        cen = polygon.centroid().asPoint()
        x0 = cen.x() - a / 2.0
        y0 = cen.y() - b / 2.0
        x1 = cen.x() + a / 2.0
        y1 = cen.y() + b / 2.0
        dx = a / (nPoints - 1)
        row = 0
        y = y1
        if clipPoints:
            pbuf = polygon.buffer(self.bufPerc * a, self.bufQCirclePoints)
        while (y0 - dx / 2) <= y:
            x = x0
            for col in range(nPoints):
                g = QgsGeometry.fromPointXY(QgsPointXY(x, y))
                g.rotate(alpha, cen)
                if (not clipPoints) or g.within(pbuf):
                    outputFeature = QgsFeature(outputFields)
                    outputFeature.setAttributes([inputID, row + 1, col + 1])
                    outputFeature.setGeometry(g)
                    outputLayer.addFeature(outputFeature)
                x = x + dx
            y = y - dx
            row += 1

    def generatePointsY(
        self,
        polygon: QgsMultiPolygon,
        inputID: str,
        alpha: float,
        a: float,
        b: float,
        nPoints: int,
        outputLayer: QgsVectorFileWriter,
        outputFields: QgsFields,
        clipPoints: bool,
    ):
        """
        Generates a grid of points within a simulation plot when the y-side is shorter than the x-side.

        Creates a grid where points are aligned along the shorter side (a > b), ensuring the specified number of points
        along the shorter side of the rectangle. Points are optionally clipped to fit within the plot boundaries and
        rotated to align with the plot's orientation.

        Parameters:
            polygon (QgsMultiPolygon): Input polygon geometry representing the simulation plot.
            inputID (str):             Simulation plot ID.
            alpha (float):             Rotation angle of the plot.
            a (float):                 Length of the long side of the plot.
            b (float):                 Length of the short side of the plot.
            nPoints (int):             Number of points along the short side.
            outputLayer (QgsVectorFileWriter): The output layer for storing generated points.
            outputFields (QgsFields):  Field schema for the output vector file.
            clipPoints (bool):         Flag to clip points within plot boundaries.

        Returns:
            None: The method writes the generated points to the output vector file.
        """
        cen = polygon.centroid().asPoint()
        x0 = cen.x() - a / 2.0
        y0 = cen.y() - b / 2.0
        x1 = cen.x() + a / 2.0
        y1 = cen.y() + b / 2.0
        dy = b / (nPoints - 1)
        col = 0
        x = x0
        if clipPoints:
            pbuf = polygon.buffer(self.bufPerc * a, self.bufQCirclePoints)
        while x < (x1 + dy / 2):
            y = y1
            for row in range(nPoints):
                g = QgsGeometry.fromPointXY(QgsPointXY(x, y))
                g.rotate(alpha, cen)
                if (not clipPoints) or g.within(pbuf):
                    outputFeature = QgsFeature(outputFields)
                    outputFeature.setAttributes([inputID, row + 1, col + 1])
                    outputFeature.setGeometry(g)
                    outputLayer.addFeature(outputFeature)
                y = y - dy
            x = x + dy
            col += 1

    def generatePoints(
        self,
        inputFN: str,
        idFieldName: str,
        outputFN: str,
        nPoints: int,
        clipPoints: bool,
        progressDlg: GProgressDialog,
    ):
        """
        Generates a complete grid of points for each simulation plot's bounding rectangle.

        This method reads input polygon geometries, determines the optimal grid orientation, and generates a
        grid of points that follow the plot's position and rotation. Points are optionally clipped to remain
        within each plot's boundaries. The grid density is specified by the number of points along the shorter
        side of each plot.

        Parameters:
            inputFN (str):     Path to the input file containing simulation plot polygons.
            idFieldName (str): Field name representing the plot ID in the input file.
            outputFN (str):    Path to the output vector file for storing generated points.
            nPoints (int):     Number of points along the shorter side of the rectangle.
            clipPoints (bool): Flag to indicate whether points should be clipped to the plot boundary.
            progressDlg (GProgressDialog): A dialog to display the progress of the operation.

        Raises:
            ValueError: If the input layer's geometry is not of polygon type.

        Returns:
            None: Directly writes the generated points to the output vector file.
        """
        inputLayer = QgsVectorLayer(inputFN, "forest stands", "ogr")
        if inputLayer.geometryType() != Qgis.GeometryType.Polygon:
            GenSimPlotUtilities.raiseValueError(f"Geometry must be POLYGON ({inputFN}).", progressDlg)
        inputIDField = inputLayer.fields().field(idFieldName)
        outputFields = self.createSPointsFields(QgsField(inputIDField))
        outputLayer = self.createSPointsShapeFile(
            outputFN, outputFields, inputLayer.crs()
        )
        n = inputLayer.featureCount()
        GenSimPlotUtilities.startProgress(
            progressDlg, f"Generating simulation plot points to {outputFN} ...", n
        )
        for fid in range(0, n):
            inputFeature = inputLayer.getFeature(fid)
            # polygon = inputFeature.geometry()
            polygon = inputFeature.geometry().asGeometryCollection()[0]
            a = inputFeature["a"]
            b = inputFeature["b"]
            alpha = inputFeature["alpha"]
            inputID = inputFeature[idFieldName]
            if b < a:
                self.generatePointsY(
                    polygon,
                    inputID,
                    alpha,
                    a,
                    b,
                    nPoints,
                    outputLayer,
                    outputFields,
                    clipPoints,
                )
            else:
                self.generatePointsX(
                    polygon,
                    inputID,
                    alpha,
                    a,
                    b,
                    nPoints,
                    outputLayer,
                    outputFields,
                    clipPoints,
                )
            GenSimPlotUtilities.incrementProgress(progressDlg)



#############################################################################
#   ENVIRONMENTAL VARIABLES
#############################################################################

class SimulationPlotVariables(PointsGenerator):
    """
    A class to assign environmental variables to simulation plots by extracting data from raster layers.

    This class provides methods to extract environmental variable values from raster layers, either at the centroid
    of each simulation plot or at multiple points within each plot. The extracted values are stored in new fields
    in the simulation plot's attribute table for further spatial analysis or visualization.

    Attributes:
        maxFieldNameLength (int): The maximum allowable length for field names in the simulation plot attribute table.

    Methods:
        valueFromCentroid(spFN: str, spDataFieldName: str, rasterFN: str):
            Extracts environmental variable values at the centroid of each simulation plot and saves them in a specified field.

        valueFromPoints(spFN: str, spIDField: str, pointsFN: str, pointsDataField: str, rasterFN: str):
            Extracts environmental variable values for multiple points on each simulation plot, calculates summary statistics
            (minimum, maximum, mean), and saves them in the simulation plot attribute table.
    """

    maxFieldNamePrefixLength = 5
    maxValueFieldNameLength = 10

    def valueFromCentroid(
        self,
        shpFN: str,
        shpValueFieldName: str,
        rasterFN: str,
        progressDlg: GProgressDialog,
    ):
        """
        Extracts environmental variable values at the centroid of each simulation plot.

        Reads simulation plot polygons from an input vector file, retrieves the environmental variable values at the centroid
        of each plot from a raster layer, and saves the values in a specified field within the simulation plot attribute table.

        Parameters:
            shpFN (str):             Path to the input vector file containing simulation plot polygons.
            shpValueFieldName (str): Field name for storing the extracted environmental variable values.
            rasterFN (str):          Path to the input raster file containing environmental data.
            progressDlg (GProgressDialog): A dialog to display the progress of the operation.

        Raises:
            ValueError: If the input layer's geometry is not of type polygon.
            ValueError: If the input raster is invalid.
            Exception: If the process was canceled by the user.

        Returns:
            None: The function directly updates the attribute table with extracted values.

        Usage:
            Ideal for scenarios where environmental data from raster layers is represented at the centroid of each simulation plot,
            such as in studies focusing on spatially explicit ecological factors within plot geometries.

        """
        dataLayer = QgsRasterLayer(rasterFN, "data")
        rdata = dataLayer.dataProvider()
        if not QgsRasterLayer.isValidRasterFileName(rasterFN):
            GenSimPlotUtilities.raiseValueError(f"The input raster is invalid ({rasterFN}).", progressDlg)
        spLayer = QgsVectorLayer(shpFN, "plots", "ogr")
        if spLayer.geometryType() != Qgis.GeometryType.Polygon:
            GenSimPlotUtilities.raiseValueError("Geometry must be POLYGON ({shpFN}).", progressDlg)
        if spLayer.fields().indexFromName(shpValueFieldName) < 0:
            # add data field to plots layer
            if self.maxValueFieldNameLength < len(shpValueFieldName):
                shpValueFieldName = shpValueFieldName[0 : self.maxValueFieldNameLength]
            if spLayer.fields().indexFromName(shpValueFieldName) < 0:
                spLayer.dataProvider().addAttributes(
                    [
                        QgsField(shpValueFieldName, QVariant.Double),
                    ]
                )
            spLayer.updateFields()
        n = spLayer.featureCount()
        GenSimPlotUtilities.startProgress(
            progressDlg, f"Extracting centroid values for plots from {shpFN} ...", n
        )
        spLayer.startEditing()
        for fid in range(0, n):
            inputSP = spLayer.getFeature(fid)
            cen = inputSP.geometry().centroid()
            val = rdata.identify(
                cen.asPoint(), QgsRaster.IdentifyFormatValue
            ).results()[1]
            if val is not None:
                inputSP[shpValueFieldName] = val
                spLayer.updateFeature(inputSP)
            GenSimPlotUtilities.incrementProgress(progressDlg)
        spLayer.commitChanges()

    def valueFromPoints(
        self,
        spFN: str,
        spIDField: str,
        pointsFN: str,
        valueFieldName: str,
        rasterFN: str,
        progressDlg: GProgressDialog,
    ):
        """
        Extracts environmental variable values for multiple points on each simulation plot and calculates statistics.

        Reads polygons and points from vector files, extracts environmental values at each point location from a raster layer,
        and calculates summary statistics (minimum, maximum, and mean) for each simulation plot. The computed statistics are
        stored as new fields in the simulation plot attribute table.

        Parameters:
            spFN (str):           Path to the input vector file containing simulation plot polygons.
            spIDField (str):      Field name identifying each simulation plot.
            pointsFN (str):       Path to the input vector file containing points within simulation plots.
            valueFieldName (str): Field name for storing extracted environmental variable values in the points layer.
            rasterFN (str):       Path to the input raster file containing environmental data.
            progressDlg (GProgressDialog): A dialog to display the progress of the operation.

        Raises:
            ValueError: If the points layer's geometry is not of type point.

        Returns:
            None: The function directly updates both the points and simulation plot attribute tables with extracted values
            and calculated statistics.

        Usage:
            'valueFromPoints' is ideal for applications needing detailed environmental data representation across multiple
            points in each simulation plot, such as spatial analyses that consider within-plot variability in ecological studies.

        """
        if self.maxFieldNamePrefixLength < len(valueFieldName):
            valueFieldName = valueFieldName[0 : self.maxFieldNamePrefixLength]
        spMinFieldName = valueFieldName + "_min"
        spMaxFieldName = valueFieldName + "_max"
        spMeanFieldName = valueFieldName + "_mean"
        dataLayer = QgsRasterLayer(rasterFN, "data")
        rdata = dataLayer.dataProvider()
        if not QgsRasterLayer.isValidRasterFileName(rasterFN):
            GenSimPlotUtilities.raiseValueError(f"The input raster is invalid ({rasterFN}).", progressDlg)
        pointsLayer = QgsVectorLayer(pointsFN, "points", "ogr")
        if pointsLayer.geometryType() != Qgis.GeometryType.Point:
            GenSimPlotUtilities.raiseValueError(f"Geometry must be POINT ({pointsFN}).", progressDlg)
        if pointsLayer.fields().indexFromName(valueFieldName) < 0:
            # add data field to points layer
            pointsLayer.dataProvider().addAttributes(
                [
                    QgsField(valueFieldName, QVariant.Double),
                ]
            )
            pointsLayer.updateFields()
        n = pointsLayer.featureCount()
        GenSimPlotUtilities.startProgress(
            progressDlg, f"Extracting point values for plots from {spFN} ...", n
        )
        spDict = dict()
        pointsLayer.startEditing()
        for fid in range(0, n):
            inputPoint = pointsLayer.getFeature(fid)
            geom = inputPoint.geometry()
            spId = inputPoint[spIDField]
            val = rdata.identify(
                geom.asPoint(), QgsRaster.IdentifyFormatValue
            ).results()[1]
            if val is not None:
                inputPoint[valueFieldName] = val
                pointsLayer.updateFeature(inputPoint)
                if spId in spDict:
                    valmin = min(val, spDict[spId]["min"])
                    valmax = max(val, spDict[spId]["max"])
                    valsum = val + spDict[spId]["sum"]
                    valn = spDict[spId]["n"] + 1
                    spDict[spId] = {
                        "min": valmin,
                        "max": valmax,
                        "sum": valsum,
                        "n": valn,
                    }
                else:
                    spDict[spId] = {"min": val, "max": val, "sum": val, "n": 1}
            if (fid % 5000) == 0:
                # partial commit
                pointsLayer.commitChanges(stopEditing=False)
            GenSimPlotUtilities.incrementProgress(progressDlg)
        pointsLayer.commitChanges()
        # calculate the mean of point data
        for spId in spDict:
            spDict[spId]["mean"] = spDict[spId]["sum"] / spDict[spId]["n"]
        # update simulation plots
        spLayer = QgsVectorLayer(spFN, "plots", "ogr")
        if spMinFieldName is not None:
            if spLayer.fields().indexFromName(spMinFieldName) < 0:
                spLayer.dataProvider().addAttributes(
                    [
                        QgsField(spMinFieldName, QVariant.Double),
                    ]
                )
        if spMaxFieldName is not None:
            if spLayer.fields().indexFromName(spMaxFieldName) < 0:
                spLayer.dataProvider().addAttributes(
                    [
                        QgsField(spMaxFieldName, QVariant.Double),
                    ]
                )
        if spMeanFieldName is not None:
            if spLayer.fields().indexFromName(spMeanFieldName) < 0:
                spLayer.dataProvider().addAttributes(
                    [
                        QgsField(spMeanFieldName, QVariant.Double),
                    ]
                )
        spLayer.updateFields()
        n = spLayer.featureCount()
        spLayer.startEditing()
        for fid in range(0, n):
            inputSP = spLayer.getFeature(fid)
            spId = inputSP[spIDField]
            if spId in spDict:
                if spMinFieldName is not None:
                    inputSP[spMinFieldName] = spDict[spId]["min"]
                if spMaxFieldName is not None:
                    inputSP[spMaxFieldName] = spDict[spId]["max"]
                if spMeanFieldName is not None:
                    inputSP[spMeanFieldName] = spDict[spId]["mean"]
                spLayer.updateFeature(inputSP)
            GenSimPlotUtilities.incrementProgress(progressDlg)
        spLayer.commitChanges()
