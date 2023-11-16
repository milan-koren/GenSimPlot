# -*- coding: utf-8 -*-

## @package   GenSimPlot
#  @version   1.1
#  @author    Milan Koren
#  @copyright EUPL v1.2, https://eupl.eu/
#  @remark    https://github.com/milan-koren/GenSimPlot

import math
import random
from qgis.core import *
from osgeo import gdal
   

#############################################################################
#   SIMULATION PLOTS
#############################################################################

class SimulationPlot:
    def __init__(self):
        self.setup()

    #  @param rotationSteps: Number of steps of rotation
    #  @param distanceStep: Maximal random translation in x and y direction
    #  @param alphaStep: Maximal random change of rotation angle.
    #  @param randomIterations: Number of random iterations
    #  @param sideRatioMax: Maximal ratio of the rectangle sides
    #  @param sideRatioStep: Change of side ratio from 1.0 to sideRatioMax
    #  @param sideRatioLimit: Upper limit of the side ratio for iteration
    def setup(self, 
              rotationSteps: int = 30, 
              distanceStep: float = 10.0, alphaStep: float = 3.0, randomIterations: int = 250,
              sideRatioMax: float = 4.0, sideRatioStep: float = 1.0, sideRatioLimit: float = 10.0):
        self.rotationSteps = rotationSteps
        self.distanceStep = distanceStep
        self.alphaStep = alphaStep
        self.randomIterations = randomIterations
        self.sideRatioMax = sideRatioMax
        self.sideRatioStep = sideRatioStep
        self.sideRatioLimit = sideRatioLimit

    ## Create QgsFields for simulation plots.
    #  @param outputIDField: Name of the forest stand ID field, e.g., fstand
    #  @param lengthIDField: Length of the forest stand ID field, e.g., 10
    #  @return QgsFields object
    def createSPlotFields(self, outputIDField: str, lengthIDField: int):
        outputFields = QgsFields()
        outputFields.append(QgsField(outputIDField, QVariant.String, "varchar", lengthIDField))
        outputFields.append(QgsField("a", QVariant.Double, "double", 6, 2))
        outputFields.append(QgsField("b", QVariant.Double, "double", 6, 2))
        outputFields.append(QgsField("alpha", QVariant.Double, "double", 6, 2))
        outputFields.append(QgsField("perc", QVariant.Double, "double", 6, 2))
        outputFields.append(QgsField("ishp", QVariant.Double, "double", 6, 2))
        return(outputFields)

    ## Create output vector thematic layer for simulation plots.
    #  @param outputFN: Name of the output vector file
    #  @param outputFields: List of output fields to be created (QgsFields object)
    #  @param crs: Coordinate reference system
    #  @return QgsVectorFileWriter object
    def createSPlotShapeFile(self, outputFN: str, outputFields: QgsFields, crs):
        svo = QgsVectorFileWriter.SaveVectorOptions()
        svo.driverName = "ESRI Shapefile"
        return(QgsVectorFileWriter.create(outputFN, outputFields, Qgis.WkbType.Polygon, crs, QgsCoordinateTransformContext(), svo, QgsFeatureSink.SinkFlags(), None, None))  

    ## Generate simulation plots.
    #  @param inputFN:       Input vector file
    #  @param inputIDField:  Input forest stand ID field
    #  @param outputFN:      Output vector file
    #  @param outputIDField: Output simulation plot ID field
    #  @param rplotFn:       Simulation plot creation function
    def generatePlots(self, inputFN, inputIDField, outputFN, outputIDField, rplotFn):
        random.seed()
        inputLayer = QgsVectorLayer(inputFN, "forest stands", "ogr")
        if (inputLayer.geometryType() != Qgis.GeometryType.Polygon):
            raise ValueError("Geometry must be POLYGON.")
        outputFields = self.createSPlotFields(outputIDField, 20)
        outputLayer = self.createSPlotShapeFile(outputFN, outputFields, inputLayer.crs())
        n = inputLayer.featureCount()
        for fid in range(0, n):
            inputFeature = inputLayer.getFeature(fid)
            geom = inputFeature.geometry().asGeometryCollection()[0]
            garea = geom.area()
            ishp = geom.length()/math.sqrt(garea)
            rgeom, a, b, alpha = rplotFn(geom)
            gr = geom.intersection(rgeom)
            outputFeature = QgsFeature(outputFields)
            outputFeature.setAttributes([inputFeature[inputIDField], a, b, alpha, 100.0*gr.area()/garea, ishp])
            outputFeature.setGeometry(rgeom)
            if (not outputLayer.addFeature(outputFeature)):
                raise ValueError("Cannnot save feature.")

    ## Find the rotation angle of the simulation plot to maximize overlap with a given polygon.
    #  The simulation plot is rotated in the range of 0 to 180 degrees by a given number of steps.
    #  @param geom: Polygon for which the simulation plot is generated, e.g., a forest stand
    #  @param rplot: Original simulation plot
    #  @remark A copy of the original simulation plot is used, so the original plot remains unchanged.
    #  @return (copy of the simulation plot, rotational angle)
    def rotateSPlot(self, geom: QgsGeometry, rplot: QgsGeometry):
        c = rplot.centroid().asPoint()
        areaMax = geom.intersection(rplot).area()
        alphaMax = 0.0
        d = 180.0 / self.rotationSteps
        alpha = d
        while (alpha < 180.0):
            nplot = QgsGeometry(rplot)
            nplot.rotate(alpha, c)
            a = geom.intersection(nplot).area()
            if (areaMax < a):
                areaMax = a
                alphaMax = alpha
            alpha += d
        nplot = QgsGeometry(rplot)
        if (0.0 < alphaMax):
            nplot.rotate(alphaMax, c)
        return(nplot, alphaMax)

    ## Rotate and move the simulation plot to enhance overlap with a given polygon.
    #  The simulation plot is rotated and translated multiple times with random displacements.
    #  @param geom: Polygon for which the simulation plot is generated, e.g., a forest stand
    #  @param rplot: Original simulation plot
    def rotateAndMoveSPlot(self, geom: QgsGeometry, rplot: QgsGeometry):
        nplot, alphaMax = self.rotateSPlot(geom, rplot)
        areaMax = geom.intersection(nplot).area()
        c = rplot.centroid().asPoint()
        txMax = 0.0
        tyMax = 0.0
        for i in range(self.randomIterations):
            nalpha = alphaMax + self.alphaStep*(2.0*random.random() - 1.0)
            tx = txMax + self.distanceStep*(2.0*random.random() - 1.0)
            ty = tyMax + self.distanceStep*(2.0*random.random() - 1.0)
            nplot = QgsGeometry(rplot)
            nplot.rotate(nalpha, c)
            nplot.translate(tx, ty)
            narea = geom.intersection(nplot).area()
            if (areaMax < narea):
                areaMax = narea
                alphaMax = nalpha
                txMax = tx
                tyMax = ty
        nplot = QgsGeometry(rplot)
        nplot.rotate(alphaMax, c)
        nplot.translate(txMax, tyMax)
        return(nplot, alphaMax)

    ## Calculate the mean coordinates of a polygon.
    #  @param geom: Polygon for which the mean coordinates are calculated
    #  @return (mean X coordinate, mean Y coordinate)
    def meanXY(self, geom: QgsGeometry):
        cx = 0.0
        cy = 0.0
        v = geom.vertices()
        m = 0
        while (v.hasNext()):
            p = v.next()
            cx += p.x()
            cy += p.y()
            m += 1
        if (0 < m):
            cx = cx / m
            cy = cy / m
            return(cx, cy)
        else:
            return(None)



#############################################################################
#   SQUARE SIMULATION PLOTS
#############################################################################

## Class SquareSimulationPlot
#  @remark Functions return long and short side of square, due to compatibility with functions for rectangles.
class SquareSimulationPlot(SimulationPlot):

    ## Create a square simulation plot by centroid.
    #  @param geom: Polygon for plot generation
    #  @return (QgsGeometry, side length, side length, rotation angle)
    def squareByCentroid(self, geom: QgsGeometry):
        garea = geom.area()
        a = math.sqrt(garea)
        a2 = a/2
        c = geom.centroid().asPoint()
        cx = c.x()
        cy = c.y()
        rgeom = QgsGeometry.fromRect(QgsRectangle(cx-a2, cy-a2, cx+a2, cy+a2))
        return(rgeom, a, a, 0.0)

    ## Create a square simulation plot by bounding box.
    #  @param geom: Polygon for plot generation
    #  @return (QgsGeometry, side length, side length, rotation angle)
    def squareByBBox(self, geom: QgsGeometry):
        garea = geom.area()
        a = math.sqrt(garea)
        a2 = a/2
        c = geom.boundingBox().center()
        cx = c.x()
        cy = c.y()
        rgeom = QgsGeometry.fromRect(QgsRectangle(cx-a2, cy-a2, cx+a2, cy+a2))
        return(rgeom, a, a, 0.0)

    ## Create a square simulation plot by mean coordinates.
    #  @param geom: Polygon for plot generation
    #  @return (QgsGeometry, side length, side length, rotation angle)
    def squareByMeanXY(self, geom: QgsGeometry):
        garea = geom.area()
        a = math.sqrt(garea)
        a2 = a/2
        cx, cy = self.meanXY(geom)
        rgeom = QgsGeometry.fromRect(QgsRectangle(cx-a2, cy-a2, cx+a2, cy+a2))
        return(rgeom, a, a, 0.0)

    ## Create and rotate a square simulation plot by centroid.
    #  @param geom: Polygon for plot generation
    #  @return (QgsGeometry, side length, side length, rotation angle)
    def rotatedSquareByCentroid(self, geom: QgsGeometry):
        rplot, a, b, alpha = self.squareByCentroid(geom)
        rplot, alpha = self.rotateSPlot(geom, rplot)
        return(rplot, a, a, alpha)

    ## Create and rotate a square simulation plot by mean coordinates.
    #  @param geom: Polygon for plot generation
    #  @return (QgsGeometry, side length, side length, rotation angle)
    def rotatedSquareByBBox(self, geom: QgsGeometry):
        rplot, a, b, alpha = self.squareByBBox(geom)
        rplot, alpha = self.rotateSPlot(geom, rplot)
        return(rplot, a, a, alpha)

    ## Create, rotate, and move a square simulation plot by centroid.
    #  @param geom: Polygon for plot generation
    #  @return (QgsGeometry, side length, side length, rotation angle)
    def rotatedSquareByMeanXY(self, geom: QgsGeometry):
        rplot, a, b, alpha = self.squareByMeanXY(geom)
        rplot, alpha = self.rotateSPlot(geom, rplot)
        return(rplot, a, a, alpha)

    ## Create, rotate, and move a square simulation plot by centroid.
    #  @param geom: Polygon for plot generation
    #  @return (QgsGeometry, side length, side length, rotation angle)
    def rotatedAndMovedSquareByCentroid(self, geom: QgsGeometry):
        rplot, a, b, alpha = self.squareByCentroid(geom)
        rplot, alpha = self.rotateAndMoveSPlot(geom, rplot)
        return(rplot, a, a, alpha)

    ## Create, rotate, and move a square simulation plot by bounding box.
    #  @param geom: Polygon for plot generation
    #  @return (QgsGeometry, side length, side length, rotation angle)
    def rotatedAndMovedSquareByBBox(self, geom: QgsGeometry):
        rplot, a, b, alpha = self.squareByBBox(geom)
        rplot, alpha = self.rotateAndMoveSPlot(geom, rplot)
        return(rplot, a, a, alpha)

    ## Create, rotate, and move a square simulation plot by mean coordinates.
    #  @param geom: Polygon for plot generation
    #  @return (QgsGeometry, side length, side length, rotation angle)
    def rotatedAndMovedSquareByMeanXY(self, geom: QgsGeometry):
        rplot, a, b, alpha = self.squareByMeanXY(geom)
        rplot, alpha = self.rotateAndMoveSPlot(geom, rplot)
        return(rplot, a, a, alpha)

    ## Generate square simulation plots by centroid.
    #  @param inputFN:       Input vector file
    #  @param inputIDField:  Input forest stand ID field
    #  @param outputFN:      Output vector file
    #  @param outputIDField: Output simulation plot ID field
    def generateSquaresByCentroid(self, inputFN: str, inputIDField: str, outputFN: str, outputIDField: str):
        self.generatePlots(inputFN, inputIDField, outputFN, outputIDField, self.squareByCentroid)

    ## Generate square simulation plots by bounding box.
    #  @param inputFN:       Input vector file
    #  @param inputIDField:  Input forest stand ID field
    #  @param outputFN:      Output vector file
    #  @param outputIDField: Output simulation plot ID field
    def generateSquaresByBBox(self, inputFN: str, inputIDField: str, outputFN: str, outputIDField: str):
        self.generatePlots(inputFN, inputIDField, outputFN, outputIDField, self.squareByBBox)

    ## Generate square simulation plots by bounding box.
    #  @param inputFN:       Input vector file
    #  @param inputIDField:  Input forest stand ID field
    #  @param outputFN:      Output vector file
    #  @param outputIDField: Output simulation plot ID field
    def generateSquaresByMeanXY(self, inputFN: str, inputIDField: str, outputFN: str, outputIDField: str):
        self.generatePlots(inputFN, inputIDField, outputFN, outputIDField, self.squareByMeanXY)

    ## Generate rotated square simulation plots by centroid.
    #  @param inputFN:       Input vector file
    #  @param inputIDField:  Input forest stand ID field
    #  @param outputFN:      Output vector file
    #  @param outputIDField: Output simulation plot ID field
    #  @param rotationSteps: Number of steps of square rotation
    def generateRotatedSquaresByCentroid(self, inputFN: str, inputIDField: str, outputFN: str, outputIDField: str, 
                                         rotationSteps: int = 30):
        self.setup(rotationSteps)
        self.generatePlots(inputFN, inputIDField, outputFN, outputIDField, self.rotatedSquareByCentroid)

    ## Generate rotated square simulation plots by bounding box.
    #  @param inputFN:       Input vector file
    #  @param inputIDField:  Input forest stand ID field
    #  @param outputFN:      Output vector file
    #  @param outputIDField: Output simulation plot ID field
    #  @param rotationSteps: Number of steps of square rotation
    def generateRotatedSquaresByBBox(self, inputFN: str, inputIDField: str, outputFN: str, outputIDField: str, 
                                     rotationSteps: int = 30):
        self.setup(rotationSteps)
        self.generatePlots(inputFN, inputIDField, outputFN, outputIDField, self.rotatedSquareByBBox)

    ## Generate rotated square simulation plots by mean coordinates.
    #  @param inputFN:       Input vector file
    #  @param inputIDField:  Input forest stand ID field
    #  @param outputFN:      Output vector file
    #  @param outputIDField: Output simulation plot ID field
    #  @param rotationSteps: Number of steps of square rotation
    def generateRotatedSquaresByMeanXY(self, inputFN: str, inputIDField: str, outputFN: str, outputIDField: str, 
                                       rotationSteps: int = 30):
        self.setup(rotationSteps)
        self.generatePlots(inputFN, inputIDField, outputFN, outputIDField, self.rotatedSquareByMeanXY)

    ## Generate rotated and moved square simulation plots by centroid.
    #  @param inputFN:       Input vector file
    #  @param inputIDField:  Input forest stand ID field
    #  @param outputFN:      Output vector file
    #  @param outputIDField: Output simulation plot ID field
    #  @param rotationSteps: Number of steps of square rotation
    #  @param distanceStep: Maximal random translation in x and y direction
    #  @param alphaStep: Maximal random change of rotation angle.
    #  @param randomIterations: Number of random iterations
    def generateRotatedAndMovedSquaresByCentroid(self, inputFN: str, inputIDField: str, outputFN: str, outputIDField: str, 
                                                 rotationSteps: int = 30,
                                                 distanceStep: float = 10.0, alphaStep: float = 3.0, randomIterations: int = 250):
        self.setup(rotationSteps, distanceStep, alphaStep, randomIterations)
        self.generatePlots(inputFN, inputIDField, outputFN, outputIDField, self.rotatedAndMovedSquareByCentroid)

    ## Generate rotated and moved square simulation plots by bounding box.
    #  @param inputFN:       Input vector file
    #  @param inputIDField:  Input forest stand ID field
    #  @param outputFN:      Output vector file
    #  @param outputIDField: Output simulation plot ID field
    #  @param rotationSteps: Number of steps of square rotation
    #  @param distanceStep: Maximal random translation in x and y direction
    #  @param alphaStep: Maximal random change of rotation angle.
    #  @param randomIterations: Number of random iterations
    def generateRotatedAndMovedSquaresByBBox(self, inputFN: str, inputIDField: str, outputFN: str, outputIDField: str, 
                                             rotationSteps: int = 30,
                                             distanceStep: float = 10.0, alphaStep: float = 3.0, randomIterations: int = 250):
        self.setup(rotationSteps, distanceStep, alphaStep, randomIterations)
        self.generatePlots(inputFN, inputIDField, outputFN, outputIDField, self.rotatedAndMovedSquareByBBox)

    ## Generate rotated and moved square simulation plots by mean coordinates.
    #  @param inputFN:       Input vector file
    #  @param inputIDField:  Input forest stand ID field
    #  @param outputFN:      Output vector file
    #  @param outputIDField: Output simulation plot ID field
    #  @param rotationSteps: Number of steps of square rotation
    #  @param distanceStep: Maximal random translation in x and y direction
    #  @param alphaStep: Maximal random change of rotation angle.
    #  @param randomIterations: Number of random iterations
    def generateRotatedAndMovedSquaresByMeanXY(self, inputFN: str, inputIDField: str, outputFN: str, outputIDField: str, 
                                               rotationSteps: int = 30,
                                               distanceStep: float = 10.0, alphaStep: float = 3.0, randomIterations: int = 250):
        self.setup(rotationSteps, distanceStep, alphaStep, randomIterations)
        self.generatePlots(inputFN, inputIDField, outputFN, outputIDField, self.rotatedAndMovedSquareByMeanXY)



#############################################################################
#   RECTANGULAR SIMULATION PLOTS
#############################################################################

class RectangularSimulationPlot(SquareSimulationPlot):

    ## Create, rotate, and move a square simulation plot by mean coordinates.
    #  @param geom: Polygon for rectangular plot generation
    #  @return (longer side length, shorter side length)
    def rectangleSize(self, geom: QgsGeometry):
        garea = geom.area()
        gperim = geom.length()
        d = gperim*gperim - 16*garea
        if (0 < d):
            d = math.sqrt(d)
        else:
            d = 0;
        a = (gperim + d)/4
        b = (gperim - d)/4
        if (self.sideRatioMax is not None):
            if (self.sideRatioMax < a/b):
                b = math.sqrt(garea/self.sideRatioMax)
                a = garea/b
        return(a, b)

    ## Create a rectangular simulation plot by centroid.
    #  @param geom: Polygon for rectangular plot generation
    #  @return (QgsGeometry, long side length, short side length, rotation angle)  
    def rectangleByCentroid(self, geom: QgsGeometry):
        c = geom.centroid().asPoint()
        cx = c.x()
        cy = c.y()
        a, b = self.rectangleSize(geom)
        a2 = a/2
        b2 = b/2
        rgeom = QgsGeometry.fromRect(QgsRectangle(cx-a2, cy-b2, cx+a2, cy+b2))
        return(rgeom, a, b, 0.0)

    ## Create a rectangular simulation plot by bounding box.
    #  @param geom: Polygon for rectangular plot generation
    #  @return (QgsGeometry, long side length, short side length, rotation angle)  
    def rectangleByBBox(self, geom):
        c = geom.boundingBox().center()
        cx = c.x()
        cy = c.y()
        a, b = self.rectangleSize(geom)
        a2 = a/2
        b2 = b/2
        rgeom = QgsGeometry.fromRect(QgsRectangle(cx-a2, cy-b2, cx+a2, cy+b2))
        return(rgeom, a, b, 0.0)


    ## Create a rectangular simulation plot by mean coordinates.
    #  @param geom: Polygon for rectangular plot generation
    #  @return (QgsGeometry, long side length, short side length, rotation angle)  
    def rectangleByMeanXY(self, geom: QgsGeometry):
        cx, cy = self.meanXY(geom)
        a, b = self.rectangleSize(geom)
        a2 = a/2
        b2 = b/2
        rgeom = QgsGeometry.fromRect(QgsRectangle(cx-a2, cy-b2, cx+a2, cy+b2))
        return(rgeom, a, b, 0.0)

    ## Create and rotate a rectanglar simulation plot by centroid.
    #  @param geom: Polygon for rectangular plot generation
    #  @return (QgsGeometry, long side length, short side length, rotation angle)  
    def rotatedRectangleByCentroid(self, geom: QgsGeometry):
        rplot, a, b, alpha = self.rectangleByCentroid(geom)
        rplot, alpha = self.rotateSPlot(geom, rplot)
        return(rplot, a, b, alpha)

    ## Create and rotate a rectanglar simulation plot by bounding box.
    #  @param geom: Polygon for rectangular plot generation
    #  @return (QgsGeometry, long side length, short side length, rotation angle)  
    def rotatedRectangleByBBox(self, geom: QgsGeometry):
        rplot, a, b, alpha = self.rectangleByBBox(geom)
        rplot, alpha = self.rotateSPlot(geom, rplot)
        return(rplot, a, b, alpha)

    ## Create and rotate a rectanglar simulation plot by mean coordinates.
    #  @param geom: Polygon for rectangular plot generation
    #  @return (QgsGeometry, long side length, short side length, rotation angle)  
    def rotatedRectangleByMeanXY(self, geom: QgsGeometry):
        rplot, a, b, alpha = self.rectangleByMeanXY(geom)
        rplot, alpha = self.rotateSPlot(geom, rplot)
        return(rplot, a, b, alpha)

    ## Create, rotate, and move a rectagular simulation plot by centroid.
    #  @param geom: Polygon for rectangular plot generation
    #  @return (QgsGeometry, long side length, short side length, rotation angle)  
    def rotatedAndMovedRectangleByCentroid(self, geom: QgsGeometry):
        rplot, a, b, alpha = self.rectangleByCentroid(geom)
        rplot, alpha = self.rotateAndMoveSPlot(geom, rplot)
        return(rplot, a, b, alpha)

    ## Create, rotate, and move a rectagular simulation plot by bounding box.
    #  @param geom: Polygon for rectangular plot generation
    #  @return (QgsGeometry, long side length, short side length, rotation angle)
    def rotatedAndMovedRectangleByBBox(self, geom: QgsGeometry):
        rplot, a, b, alpha = self.rectangleByBBox(geom)
        rplot, alpha = self.rotateAndMoveSPlot(geom, rplot)
        return(rplot, a, b, alpha)

    ## Create, rotate, and move a rectagular simulation plot by mean coordinates.
    #  @param geom: Polygon for rectangular plot generation
    #  @return (QgsGeometry, long side length, short side length, rotation angle)      
    def rotatedAndMovedRectangleByMeanXY(self, geom: QgsGeometry):
        rplot, a, b, alpha = self.rectangleByMeanXY(geom)
        rplot, alpha = self.rotateAndMoveSPlot(geom, rplot)
        return(rplot, a, b, alpha)

    ## Create square and rectangular simulation plots, returns the one with better overlap.
    #  @brief Selects from square and rectangular simulation plot optimized by position and rotation.
    #  @param geom: Polygon for plot generation
    #  @return (QgsGeometry, long side length, short side length, rotation angle)      
    def splotByPosition(self, geom: QgsGeometry):
        splot, sa, sb, salpha = self.squareByCentroid(geom)
        splot, salpha = self.rotateAndMoveSPlot(geom, splot)
        rplot, ra, rb, ralpha = self.rotatedAndMovedRectangleByCentroid(geom)
        sarea = geom.intersection(splot).area()
        rarea = geom.intersection(rplot).area()
        if (rarea < sarea):
            return(splot, sa, sb, salpha)
        else:
            return(rplot, ra, rb, ralpha)

    ## Create square and rectangular simulation plots with different ratio of sides, returns the one with best overlap.
    #  @brief Simulation plot optimized by shape, position, and rotation.
    #  @param geom: Polygon for plot generation
    #  @return (QgsGeometry, long side length, short side length, rotation angle)      
    def splotByPositionAndShape(self, geom: QgsGeometry):
        splot, sa, sb, salpha = self.squareByCentroid(geom)
        splot, salpha = self.rotateAndMoveSPlot(geom, splot)
        rplot, ra, rb, ralpha = self.rotatedAndMovedRectangleByCentroid(geom)
        sarea = geom.intersection(splot).area()
        rarea = geom.intersection(rplot).area()
        if (sarea < rarea):
            splot = rplot
            sa = ra
            sb = rb
            salpha = ralpha
            sarea = rarea
        self.sideRatioMax = 1.0 + self.sideRatioStep
        while (self.sideRatioMax < self.sideRatioLimit):            
            rplot, ra, rb, ralpha = self.rectangleByCentroid(geom)
            rplot, ralpha = self.rotateAndMoveSPlot(geom, rplot)
            rarea = geom.intersection(rplot).area()
            if (sarea < rarea):
                splot = rplot
                sa = ra
                sb = rb
                salpha = ralpha
                sarea = rarea
            self.sideRatioMax += self.sideRatioStep
        return(splot, sa, sb, salpha)

    ## Generate rectangular simulation plots by centroid.
    #  @param inputFN:       Input vector file
    #  @param inputIDField:  Input forest stand ID field
    #  @param outputFN:      Output vector file
    #  @param outputIDField: Output simulation plot ID field
    def generateRectanglesByCentroid(self, inputFN: str, inputIDField: str, outputFN: str, outputIDField: str):
        self.generatePlots(inputFN, inputIDField, outputFN, outputIDField, self.rectangleByCentroid)

    ## Generate rectangular simulation plots by bounding box.
    #  @param inputFN:       Input vector file
    #  @param inputIDField:  Input forest stand ID field
    #  @param outputFN:      Output vector file
    #  @param outputIDField: Output simulation plot ID field
    def generateRectanglesByBBox(self, inputFN: str, inputIDField: str, outputFN: str, outputIDField: str):
        self.generatePlots(inputFN, inputIDField, outputFN, outputIDField, self.rectangleByBBox)

    ## Generate rectangular simulation plots by bounding box.
    #  @param inputFN:       Input vector file
    #  @param inputIDField:  Input forest stand ID field
    #  @param outputFN:      Output vector file
    #  @param outputIDField: Output simulation plot ID field
    def generateRectanglesByMeanXY(self, inputFN: str, inputIDField: str, outputFN: str, outputIDField: str):
        self.generatePlots(inputFN, inputIDField, outputFN, outputIDField, self.rectangleByMeanXY)

    ## Generate rotated rectangular simulation plots by centroid.
    #  @param inputFN:       Input vector file
    #  @param inputIDField:  Input forest stand ID field
    #  @param outputFN:      Output vector file
    #  @param outputIDField: Output simulation plot ID field
    #  @param rotationSteps: Number of steps of square rotation
    def generateRotatedRectanglesByCentroid(self, inputFN: str, inputIDField: str, outputFN: str, outputIDField: str, 
                                            rotationSteps: int = 30):
        self.setup(rotationSteps)
        self.generatePlots(inputFN, inputIDField, outputFN, outputIDField, self.rotatedRectangleByCentroid)

    ## Generate rotated rectangular simulation plots by bounding box.
    #  @param inputFN:       Input vector file
    #  @param inputIDField:  Input forest stand ID field
    #  @param outputFN:      Output vector file
    #  @param outputIDField: Output simulation plot ID field
    #  @param rotationSteps: Number of steps of square rotation
    def generateRotatedRectanglesByBBox(self, inputFN: str, inputIDField: str, outputFN: str, outputIDField: str, 
                                        rotationSteps: int = 30):
        self.setup(rotationSteps)
        self.generatePlots(inputFN, inputIDField, outputFN, outputIDField, self.rotatedRectangleByBBox)

    ## Generate rotated rectangular simulation plots by mean coordinates.
    #  @param inputFN:       Input vector file
    #  @param inputIDField:  Input forest stand ID field
    #  @param outputFN:      Output vector file
    #  @param outputIDField: Output simulation plot ID field
    #  @param rotationSteps: Number of steps of square rotation
    def generateRotatedRectanglesByMeanXY(self, inputFN: str, inputIDField: str, outputFN: str, outputIDField: str, 
                                          rotationSteps: int = 30):
        self.setup(rotationSteps)
        self.generatePlots(inputFN, inputIDField, outputFN, outputIDField, self.rotatedRectangleByMeanXY)

    ## Generate rotated and moved rectangular simulation plots by centroid.
    #  @param inputFN:       Input vector file
    #  @param inputIDField:  Input forest stand ID field
    #  @param outputFN:      Output vector file
    #  @param outputIDField: Output simulation plot ID field
    #  @param rotationSteps: Number of steps of square rotation
    #  @param distanceStep: Maximal random translation in x and y direction
    #  @param alphaStep: Maximal random change of rotation angle.
    #  @param randomIterations: Number of random iterations
    def generateRotatedAndMovedRectanglesByCentroid(self, inputFN: str, inputIDField: str, outputFN: str, outputIDField: str, 
                                                    rotationSteps: int = 30,
                                                    distanceStep: float = 10.0, alphaStep: float = 3.0, randomIterations: int = 250):
        self.setup(rotationSteps, distanceStep, alphaStep, randomIterations)
        self.generatePlots(inputFN, inputIDField, outputFN, outputIDField, self.rotatedAndMovedRectangleByCentroid)

    ## Generate rotated and moved rectangular simulation plots by bounding box.
    #  @param inputFN:       Input vector file
    #  @param inputIDField:  Input forest stand ID field
    #  @param outputFN:      Output vector file
    #  @param outputIDField: Output simulation plot ID field
    #  @param rotationSteps: Number of steps of square rotation
    #  @param distanceStep: Maximal random translation in x and y direction
    #  @param alphaStep: Maximal random change of rotation angle.
    #  @param randomIterations: Number of random iterations
    def generateRotatedAndMovedRectanglesByBBox(self, inputFN: str, inputIDField: str, outputFN: str, outputIDField: str, 
                                                rotationSteps: int = 30,
                                                distanceStep: float = 10.0, alphaStep: float = 3.0, randomIterations: int = 250):
        self.setup(rotationSteps, distanceStep, alphaStep, randomIterations)
        self.generatePlots(inputFN, inputIDField, outputFN, outputIDField, self.rotatedAndMovedRectangleByBBox)

    ## Generate rotated and moved rectangular simulation plots by mean coordinates.
    #  @param inputFN:       Input vector file
    #  @param inputIDField:  Input forest stand ID field
    #  @param outputFN:      Output vector file
    #  @param outputIDField: Output simulation plot ID field
    #  @param rotationSteps: Number of steps of square rotation
    #  @param distanceStep: Maximal random translation in x and y direction
    #  @param alphaStep: Maximal random change of rotation angle.
    #  @param randomIterations: Number of random iterations
    def generateRotatedAndMovedRectanglesByMeanXY(self, inputFN: str, inputIDField: str, outputFN: str, outputIDField: str, 
                                                  rotationSteps: int = 30,
                                                  distanceStep: float = 10.0, alphaStep: float = 3.0, randomIterations: int = 250):
        self.setup(rotationSteps, distanceStep, alphaStep, randomIterations)
        self.generatePlots(inputFN, inputIDField, outputFN, outputIDField, self.rotatedAndMovedRectangleByMeanXY)

    ## Generate rotated and moved square or rectangular simulation plots.
    #  @param inputFN:       Input vector file
    #  @param inputIDField:  Input forest stand ID field
    #  @param outputFN:      Output vector file
    #  @param outputIDField: Output simulation plot ID field
    #  @param rotationSteps: Number of steps of square rotation
    #  @param distanceStep: Maximal random translation in x and y direction
    #  @param alphaStep: Maximal random change of rotation angle.
    #  @param randomIterations: Number of random iterations
    def generatePlotsByPosition(self, inputFN: str, inputIDField: str, outputFN: str, outputIDField: str, 
                                rotationSteps: int = 30,
                                distanceStep: float = 10.0, alphaStep: float = 3.0, randomIterations: int = 250):
        self.setup(rotationSteps, distanceStep, alphaStep, randomIterations)
        self.generatePlots(inputFN, inputIDField, outputFN, outputIDField, self.splotByPosition)

    ## Generate rotated and moved rectangular simulation plots, test for different ratio of rectangle's sides.
    #  @param inputFN:       Input vector file
    #  @param inputIDField:  Input forest stand ID field
    #  @param outputFN:      Output vector file
    #  @param outputIDField: Output simulation plot ID field
    #  @param rotationSteps: Number of steps of square rotation
    #  @param distanceStep: Maximal random translation in x and y direction
    #  @param alphaStep: Maximal random change of rotation angle.
    #  @param randomIterations: Number of random iterations
    #  @param sideRatioStep: Change of side ratio from 1.0 to sideRatioMax
    #  @param sideRatioMax: Maximal ratio of the rectangle sides
    def generatePlotsByPositionAndShape(self, inputFN: str, inputIDField: str, outputFN: str, outputIDField: str, 
                                        rotationSteps: int = 30,
                                        distanceStep: float = 10.0, alphaStep: float = 3.0, randomIterations: int = 250,
                                        sideRatioStep: float = 1.0, sideRatioMax: float = 4.0):
        self.setup(rotationSteps, distanceStep, alphaStep, randomIterations, sideRatioStep, sideRatioMax)
        self.generatePlots(inputFN, inputIDField, outputFN, outputIDField, self.splotByPositionAndShape)



#############################################################################
#   POINTS ON SIMULATION PLOTS
#############################################################################

## Class SimulationPlotPoints
#  @brief Generate points on rectangular simulation plots.
class SimulationPlotPoints:  
   
    ## Create QgsFields for simulation plot points.
    #  @param outputIDField: Name of the forest stand ID field, e.g., fstand
    #  @param lengthIDField: Length of the forest stand ID field, e.g., 10
    #  @return QgsFields object
    def createSPointsFields(self, outputIDField, fieldLength):
        outputFields = QgsFields()
        outputFields.append(QgsField(outputIDField, QVariant.String, "varchar", fieldLength))
        outputFields.append(QgsField("row", QVariant.Int, "int", 4)) 
        outputFields.append(QgsField("column", QVariant.Int, "int", 4))
        return(outputFields)
    
    ## Create output vector thematic layer for points.
    #  @param outputFN:     Name of the output vector file
    #  @param outputFields: List of output fields to be created (QgsFields object)
    #  @param crs:          Coordinate reference system
    #  @return QgsVectorFileWriter object
    def createSPointsShapeFile(self, outputFN, outputFields, crs):
        svo = QgsVectorFileWriter.SaveVectorOptions()
        svo.driverName = "ESRI Shapefile"
        return(QgsVectorFileWriter.create(outputFN, outputFields, Qgis.WkbType.Point, crs, QgsCoordinateTransformContext(), svo, QgsFeatureSink.SinkFlags(), None, None))  
   
    ## Generate points for simulation plot when a < b.
    #  @param inputID:      Simulation plot ID
    #  @param alpha:        Rotation angle of simulation plot
    #  @param c:            Centroid of the simulation plot
    #  @param a:            Long side of the simulation plot
    #  @param b:            Short side of the simulation plot
    #  @param nPoints:      Number of points at the long side of the rectangle (a)
    #  @param outputLayer:  Output vector writer
    #  @param outputFields: List of output fields
    def generatePointsX(self, inputID: str, c: QgsPoint, alpha: float, a: float, b: float, nPoints: int, outputLayer: QgsVectorFileWriter, outputFields: QgsFields):
        x0 = c.x() - a/2.0
        y0 = c.y() - b/2.0
        x1 = c.x() + a/2.0
        y1 = c.y() + b/2.0
        dx = a/(nPoints - 1)
        row = 0
        y = y1
        while ((y0-dx/2) <= y):
            x = x0
            for col in range(nPoints):
                g = QgsGeometry.fromPointXY(QgsPointXY(x, y))
                g.rotate(alpha, c)
                outputFeature = QgsFeature(outputFields)
                outputFeature.setAttributes([inputID, row+1, col+1])
                outputFeature.setGeometry(g)
                outputLayer.addFeature(outputFeature)
                x = x + dx
            y = y - dx
            row += 1
    
    ## Generate points for simulation plot when a > b.
    #  @param inputID:      Simulation plot ID
    #  @param alpha:        Rotation angle of simulation plot
    #  @param c:            Centroid of the simulation plot
    #  @param a:            Long side of the simulation plot
    #  @param b:            Short side of the simulation plot
    #  @param nPoints:      Number of points at the short side of the rectangle (b)
    #  @param outputLayer:  Output vector writer
    #  @param outputFields: List of output fields
    def generatePointsY(self, inputID, c, alpha, a, b, nPoints, outputLayer, outputFields):
        x0 = c.x() - a/2.0
        y0 = c.y() - b/2.0
        x1 = c.x() + a/2.0
        y1 = c.y() + b/2.0
        dy = b/(nPoints - 1)
        col = 0
        x = x0
        while (x < (x1+dy/2)):
            y = y1
            for row in range(nPoints):
                g = QgsGeometry.fromPointXY(QgsPointXY(x, y))
                g.rotate(alpha, c)
                outputFeature = QgsFeature(outputFields)
                outputFeature.setAttributes([inputID, row+1, col+1])
                outputFeature.setGeometry(g)
                outputLayer.addFeature(outputFeature)
                y = y - dy
            x = x + dy
            col += 1   
    
    ## Generate points for simulation plot.
    #  @param inputFN:       Input simulation plot file (polygon)
    #  @param inputIDField:  Input simulation plot ID field
    #  @param outputFN:      Output vector layer (point)
    #  @param outputIDField: Output simulation plot ID field
    #  @param nPoints:       Number of points on the shorter side of the rectangular simulation plot
    def generatePoints(self, inputFN, inputIDField, outputFN, outputIDField, nPoints):
        inputLayer = QgsVectorLayer(inputFN, "forest stands", "ogr")
        if (inputLayer.geometryType() != Qgis.GeometryType.Polygon):
            raise ValueError("Geometry must be POLYGON.")
        outputFields = self.createSPointsFields(outputIDField, 20)
        outputLayer = self.createSPointsShapeFile(outputFN, outputFields, inputLayer.crs())
        n = inputLayer.featureCount()
        for fid in range(0, n):
            inputFeature = inputLayer.getFeature(fid)
            geom = inputFeature.geometry()
            c = geom.centroid().asPoint()
            a = inputFeature["a"]
            b = inputFeature["b"]
            alpha = inputFeature["alpha"]
            inputID = inputFeature[inputIDField]
            if (b < a):
                self.generatePointsY(inputID, c, alpha, a, b, nPoints, outputLayer, outputFields)
            else:
                self.generatePointsX(inputID, c, alpha, a, b, nPoints, outputLayer, outputFields)



#############################################################################
#   ENVIRONMENTAL VARIABLES
#############################################################################

## Class SimulationPlotVariables
#  @brief Assign environmental variables to simulation plots.
class SimulationPlotVariables(SimulationPlotPoints):    

    ## Extract values at the centroid of simulation plots.
    #  @brief Create a new field to store environmental variable values. Extract values at the centroid of each simulation plot.
    #  @param spFN:        Input simulation plot file (polygon)
    #  @param spDataField: Field to store environmental variable (double)
    #  @param rasterFN:    Input raster layer (environmental variable)
    def valueFromCentroid(self, spFN: str, spDataField: str, rasterFN: str):
        dataLayer = QgsRasterLayer(rasterFN, "data")
        rdata = dataLayer.dataProvider()
        spLayer = QgsVectorLayer(spFN, "plots", "ogr")
        if (spLayer.geometryType() != Qgis.GeometryType.Polygon):
            raise ValueError("Geometry must be POLYGON.")
        if (spLayer.fields().indexFromName(spDataField) < 0):
            #add data field to plots layer
            spLayer.dataProvider().addAttributes([QgsField(spDataField, QVariant.Double),])
            spLayer.updateFields()
        n = spLayer.featureCount()
        spLayer.startEditing()
        for fid in range(0, n):
            inputSP = spLayer.getFeature(fid)
            cen = inputSP.geometry().centroid()
            val = rdata.identify(cen.asPoint(), QgsRaster.IdentifyFormatValue).results()[1]
            if (val is not None):
                inputSP[spDataField] = val
                spLayer.updateFeature(inputSP)
        spLayer.commitChanges()
    
    ## Extract values for points on simulation plot and calculate statistics for simulation plot.
    #  @brief Create new fields to store values of environmental variables. Extract values at the centroids of each simulation plot.
    #  @param spFN:            Input simulation plot file (polygon)
    #  @param spIDField:       Simulation plot ID field (e.g., fstand)
    #  @param spMinField:      Field of simulation plot to store minimal value of environmental variable calculated from points
    #  @param spMaxField:      Field of simulation plot to store maximal value of environmental variable calculated from points
    #  @param spMeanField:     Field of simulation plot to store mean value of environmental variable calculated from points
    #  @param pointsFN:        Input points vector layer
    #  @param pointsIDField:   Simulation plot ID field in points layer (e.g., fstand)
    #  @param pointsDataField: Field to store environmental variable in points layer (double)
    #  @param rasterFN:        Input raster layer (environmental variable)
    def valueFromPoints(self, 
                        spFN: str, spIDField: str, spMinField: str, spMaxField: str, spMeanField: str, 
                        pointsFN: str, pointsIDField: str, pointsDataField: str, rasterFN: str):
        dataLayer = QgsRasterLayer(rasterFN, "data")
        rdata = dataLayer.dataProvider()
        pointsLayer = QgsVectorLayer(pointsFN, "points", "ogr")
        if (pointsLayer.geometryType() != Qgis.GeometryType.Point):
            raise ValueError("Geometry must be POINT.")
        if (pointsLayer.fields().indexFromName(pointsDataField) < 0):
            #add data field to points layer
            pointsLayer.dataProvider().addAttributes([QgsField(pointsDataField, QVariant.Double),])
            pointsLayer.updateFields()
        n = pointsLayer.featureCount()
        spDict = dict()
        pointsLayer.startEditing()
        for fid in range(0, n):
            inputFeature = pointsLayer.getFeature(fid)
            geom = inputFeature.geometry()
            spId = inputFeature[pointsIDField]
            val = rdata.identify(geom.asPoint(), QgsRaster.IdentifyFormatValue).results()[1]
            if (val is not None):
                inputFeature[pointsDataField] = val
                pointsLayer.updateFeature(inputFeature)
                if (spId in spDict):
                    valmin = min(val, spDict[spId]["min"])
                    valmax = max(val, spDict[spId]["max"])
                    valsum = val + spDict[spId]["sum"]
                    valn = spDict[spId]["n"] + 1
                    spDict[spId] = {"min": valmin, "max": valmax, "sum": valsum, "n": valn}
                else:
                    spDict[spId] = {"min": val, "max": val, "sum": val, "n": 1}
            if ((fid % 5000) == 0):
                # partial commit
                pointsLayer.commitChanges(stopEditing=False)
        pointsLayer.commitChanges()
        # calculate the mean of point data
        for spId in spDict:
            spDict[spId]["mean"] = spDict[spId]["sum"]/spDict[spId]["n"]
        # update simulation plots
        spLayer = QgsVectorLayer(spFN, "plots", "ogr")
        if (spMinField is not None):
            if (spLayer.fields().indexFromName(spMinField) < 0):
                spLayer.dataProvider().addAttributes([QgsField(spMinField, QVariant.Double),])
        if (spMaxField is not None):
            if (spLayer.fields().indexFromName(spMaxField) < 0):
                spLayer.dataProvider().addAttributes([QgsField(spMaxField, QVariant.Double),])
        if (spMeanField is not None):
            if (spLayer.fields().indexFromName(spMeanField) < 0):
                spLayer.dataProvider().addAttributes([QgsField(spMeanField, QVariant.Double),])
        spLayer.updateFields()
        n = spLayer.featureCount()
        spLayer.startEditing()
        for fid in range(0, n):
            inputSP = spLayer.getFeature(fid)
            spId = inputSP[spIDField]
            if (spId in spDict):
                if (spMinField is not None):
                    inputSP[spMinField] = spDict[spId]["min"]
                if (spMaxField is not None):
                    inputSP[spMaxField] = spDict[spId]["max"]
                if (spMeanField is not None):
                    inputSP[spMeanField] = spDict[spId]["mean"]
                spLayer.updateFeature(inputSP)
        spLayer.commitChanges()
   
    ## Assign elevation to simulation plot points.
    #  @brief Create points representing terrain on each simulation plot.
    #  @param spFN:            Input simulation plot file (polygon)
    #  @param spIDField:       Simulation plot ID field (e.g., fstand)
    #  @param pointsFN:        Input points vector layer
    #  @param pointsIDField:   Simulation plot ID field in points layer (e.g., fstand)
    #  @param demFN:           Input raster DEM
    #  @remark Standard fields to store elevation for simulation plots are elevmin, elevmax, elevmean (double).
    def demPoints(self, spFN: str, spIDField: str, pointsFN: str, pointsIDField: str, demFN: str):
        self.valueFromPoints(spFN, spIDField, "elevmin", "elevmax", "elevmean", pointsFN, pointsIDField, "elev", demFN)


def test(workingDir, fstandShapeFile = "lp.shp", fstandIDField = "fstand", splotIDField = "fstand"):
    splots = SquareSimulationPlot()
    splots.generateSquaresByCentroid(workingDir + fstandShapeFile, fstandIDField, workingDir + "sq_cen.shp", splotIDField)
    splots.generateSquaresByBBox(workingDir + fstandShapeFile, fstandIDField, workingDir + "sq_bbox.shp", splotIDField)
    splots.generateSquaresByMeanXY(workingDir + fstandShapeFile, fstandIDField, workingDir + "sq_meanxy.shp", splotIDField)
    splots.generateRotatedSquaresByCentroid(workingDir + fstandShapeFile, fstandIDField, workingDir + "sq_rot_cen.shp", splotIDField)
    splots.generateRotatedSquaresByBBox(workingDir + fstandShapeFile, fstandIDField, workingDir + "sq_rot_bbox.shp", splotIDField)
    splots.generateRotatedSquaresByMeanXY(workingDir + fstandShapeFile, fstandIDField, workingDir + "sq_rot_meanxy.shp", splotIDField)
    splots.generateRotatedAndMovedSquaresByCentroid(workingDir + fstandShapeFile, fstandIDField, workingDir + "sq_rmov_cen.shp", splotIDField)
    splots.generateRotatedAndMovedSquaresByBBox(workingDir + fstandShapeFile, fstandIDField, workingDir + "sq_rmov_bbox.shp", splotIDField)
    splots.generateRotatedAndMovedSquaresByMeanXY(workingDir + fstandShapeFile, fstandIDField, workingDir + "sq_rmov_meanxy.shp", splotIDField)

    rplots = RectangularSimulationPlot()
    rplots.generateRectanglesByCentroid(workingDir + fstandShapeFile, fstandIDField, workingDir + "rc_cen.shp", splotIDField)
    rplots.generateRectanglesByBBox(workingDir + fstandShapeFile, fstandIDField, workingDir + "rc_bbox.shp", splotIDField)
    rplots.generateRectanglesByMeanXY(workingDir + fstandShapeFile, fstandIDField, workingDir + "rc_meanxy.shp", splotIDField)
    rplots.generateRotatedRectanglesByCentroid(workingDir + fstandShapeFile, fstandIDField, workingDir + "rc_rot_cen.shp", splotIDField)
    rplots.generateRotatedRectanglesByBBox(workingDir + fstandShapeFile, fstandIDField, workingDir + "rc_rot_bbox.shp", splotIDField)
    rplots.generateRotatedRectanglesByMeanXY(workingDir + fstandShapeFile, fstandIDField, workingDir + "rc_rot_meanxy.shp", splotIDField)
    rplots.generateRotatedAndMovedRectanglesByCentroid(workingDir + fstandShapeFile, fstandIDField, workingDir + "rc_rmov_cen.shp", splotIDField)
    rplots.generateRotatedAndMovedRectanglesByBBox(workingDir + fstandShapeFile, fstandIDField, workingDir + "rc_rmov_bbox.shp", splotIDField)
    rplots.generateRotatedAndMovedRectanglesByMeanXY(workingDir + fstandShapeFile, fstandIDField, workingDir + "rc_rmov_meanxy.shp", splotIDField)
    rplots.generatePlotsByPosition(workingDir + fstandShapeFile, fstandIDField, workingDir + "sp_position.shp", splotIDField)
    rplots.generatePlotsByPositionAndShape(workingDir + fstandShapeFile, fstandIDField, workingDir + "sp_shape.shp", splotIDField)

    points = SimulationPlotVariables()
    points.generatePoints(workingDir + "sp_shape.shp", splotIDField, workingDir + "sp_shape_terrain.shp", splotIDField, 5)
    points.demPoints(workingDir + "sp_shape.shp", splotIDField, workingDir + "sp_shape_terrain.shp", splotIDField, workingDir + "dtm\\dtm")
    points.valueFromPoints(workingDir + "sp_shape.shp", splotIDField, "slopemin", "slopemax", "slopemean", workingDir + "sp_shape_terrain.shp", splotIDField, "slope", workingDir + "dtm\\slope")
    points.valueFromPoints(workingDir + "sp_shape.shp", splotIDField, "solarmin", "solarmax", "solarmean", workingDir + "sp_shape_terrain.shp", splotIDField, "solar", workingDir + "dtm\\solar")
    points.valueFromCentroid(workingDir + "sp_shape.shp", "temperatur", workingDir + "climate\\meantemp")
    points.valueFromCentroid(workingDir + "sp_shape.shp", "precipitat", workingDir + "climate\\meanprecip")
