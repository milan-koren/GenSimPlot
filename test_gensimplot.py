# -*- coding: utf-8 -*-

## @package   GenSimPlot
#  @version   1.1
#  @author    Milan Koren
#  @copyright EUPL v1.2, https://eupl.eu/
#  @remark    github.com/

import sys
sys.path.append("D:\\python\\gensimplot\\")
import gensimplot

def test():
    workingDir = "D:\\shp\\"
    #workingDir = "C:\\Users\\koren\\Documents\\shp\\"
    fstandShapeFile = "lp.shp"
    fstandIDField = "idps"
    splotIDField = "fstand"

    splots = gensimplot.SquareSimulationPlot()
    splots.generateSquaresByCentroid(workingDir + fstandShapeFile, fstandIDField, workingDir + "sq_cen.shp", splotIDField)
    splots.generateSquaresByBBox(workingDir + fstandShapeFile, fstandIDField, workingDir + "sq_bbox.shp", splotIDField)
    splots.generateSquaresByMeanXY(workingDir + fstandShapeFile, fstandIDField, workingDir + "sq_meanxy.shp", splotIDField)
    splots.generateRotatedSquaresByCentroid(workingDir + fstandShapeFile, fstandIDField, workingDir + "sq_rot_cen.shp", splotIDField)
    splots.generateRotatedSquaresByBBox(workingDir + fstandShapeFile, fstandIDField, workingDir + "sq_rot_bbox.shp", splotIDField)
    splots.generateRotatedSquaresByMeanXY(workingDir + fstandShapeFile, fstandIDField, workingDir + "sq_rot_meanxy.shp", splotIDField)
    splots.generateRotatedAndMovedSquaresByCentroid(workingDir + fstandShapeFile, fstandIDField, workingDir + "sq_rmov_cen.shp", splotIDField)
    splots.generateRotatedAndMovedSquaresByBBox(workingDir + fstandShapeFile, fstandIDField, workingDir + "sq_rmov_bbox.shp", splotIDField)
    splots.generateRotatedAndMovedSquaresByMeanXY(workingDir + fstandShapeFile, fstandIDField, workingDir + "sq_rmov_meanxy.shp", splotIDField)

    rplots = gensimplot.RectangularSimulationPlot()
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

    points = gensimplot.SimulationPlotVariables()
    points.generatePoints(workingDir + "sp_shape.shp", splotIDField, workingDir + "sp_shape_points.shp", splotIDField, 5)
    points.demPoints(workingDir + "sp_shape.shp", splotIDField, workingDir + "sp_shape_points.shp", splotIDField, workingDir + "dmr\\dmr")
    points.valueFromPoints(workingDir + "sp_shape.shp", splotIDField, "slopemin", "slopemax", "slopemean", workingDir + "sp_shape_points.shp", splotIDField, "slope", workingDir + "dmr\\dmr")
    points.valueFromCentroid(workingDir + "sp_shape.shp", "temperatur", workingDir + "dmr\\dmr")

test()
