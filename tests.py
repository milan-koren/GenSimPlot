# -*- coding: utf-8 -*-
"""
Package:   GenSimPlot
File:      tests.py
Version:   2.2
Author:    Milan Koren
Year:      2024
URL:       https://github.com/milan-koren/GenSimPlot
License:   EUPL v1.2 (European Union Public License), https://eupl.eu/          
           
This script can be executed in a QGIS Python console or a script editor configured for QGIS.

The script performs batch testing of simulation plot generation and raster extraction for each generated plot's points.
The script initializes several configuration variables for setting up a working directory, polygon shapefile parameters, 
raster file paths, and options for point generation. It then generates various types of simulation plots (squares, circles,
rectangles, and ellipses), and calculates environmental values like elevation and slope for points within each plot.

Variables:
    workingDir (str): Specifies the directory path for input and output files.
    fstandFN (str): The filename for the polygon shapefile used as input for creating simulation plots.
    fstandID (str): Refers to the field name representing unique polygon IDs in the shapefile.
    nPoints (int): The number of points along the shorter side of each plot, defining grid density.
    clipPoints (bool): Specifies whether generated points should be clipped to the boundaries of each plot.

GenerateSquares, GenerateCircles, GenerateRectangles, and GenerateEllipses create simulation plots based on the input polygons 
in fstandFN. The output shapefiles are saved in the workingDir with default names based on the shape, initial position and
placement, such as rectangle_bbox_opt.shp for optimized rectangles.

valueFromPoints extracts values from raster files (demFN and slopeFN) to each point in pointsShpFN, which are then saved 
as simulation plot and point attributes. 

valueFromCentroid extracts raster values at each plot's centroid, storing the values in a field within the simulation plot 
attribute table.
"""

from GenSimPlotLib import PlotGenerator, PointsGenerator, SimulationPlotVariables
from GenSimPlotUtilities import GProgressDialog


def GenerateSquares(
    workingDir: str, polygonShpFN: str, idFieldName: str, nPoints: int, clipPoints: bool, progressDlg: GProgressDialog
):
    plotGen = PlotGenerator()
    pointsGen = SimulationPlotVariables()
    print("generating: square, centroid, fixed")
    plotGen.generateSquarePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "square_cen.shp",
        "centroid",
        "fixed",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "square_cen.shp",
        idFieldName,
        workingDir + "square_cen_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: square, bounding box, fixed")
    plotGen.generateSquarePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "square_bbox.shp",
        "bounding box",
        "fixed",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "square_bbox.shp",
        idFieldName,
        workingDir + "square_bbox_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: square, mean coordinates, fixed")
    plotGen.generateSquarePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "square_mxy.shp",
        "mean coordinates",
        "fixed",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "square_mxy.shp",
        idFieldName,
        workingDir + "square_mxy_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    
    print("generating: square, centroid, rotated")
    plotGen.generateSquarePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "square_cen_rot.shp",
        "centroid",
        "rotated",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "square_cen_rot.shp",
        idFieldName,
        workingDir + "square_cen_rot_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: square, bounding box, rotated")
    plotGen.generateSquarePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "square_bbox_rot.shp",
        "bounding box",
        "rotated",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "square_bbox_rot.shp",
        idFieldName,
        workingDir + "square_bbox_rot_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: square, mean coordinates, rotated")
    plotGen.generateSquarePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "square_mxy_rot.shp",
        "mean coordinates",
        "rotated",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "square_mxy_rot.shp",
        idFieldName,
        workingDir + "square_mxy_rot_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    
    print("generating: square, centroid, translated")
    plotGen.generateSquarePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "square_cen_trans.shp",
        "centroid",
        "translated",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "square_cen_trans.shp",
        idFieldName,
        workingDir + "square_cen_trans_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: square, bounding box, translated")
    plotGen.generateSquarePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "square_bbox_trans.shp",
        "bounding box",
        "translated",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "square_bbox_trans.shp",
        idFieldName,
        workingDir + "square_bbox_trans_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: square, mean coordinates, translated")
    plotGen.generateSquarePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "square_mxy_trans.shp",
        "mean coordinates",
        "translated",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "square_mxy_trans.shp",
        idFieldName,
        workingDir + "square_mxy_trans_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    
    print("generating: square, centroid, optimized")
    plotGen.generateSquarePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "square_cen_opt.shp",
        "centroid",
        "optimized",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "square_cen_opt.shp",
        idFieldName,
        workingDir + "square_cen_opt_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: square, bounding box, optimized")
    plotGen.generateSquarePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "square_bbox_opt.shp",
        "bounding box",
        "optimized",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "square_bbox_opt.shp",
        idFieldName,
        workingDir + "square_bbox_opt_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: square, mean coordinates, optimized")
    plotGen.generateSquarePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "square_mxy_opt.shp",
        "mean coordinates",
        "optimized",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "square_mxy_opt.shp",
        idFieldName,
        workingDir + "square_mxy_opt_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )


def GenerateCircles(
    workingDir: str, polygonShpFN: str, idFieldName: str, nPoints: int, clipPoints: bool, progressDlg: GProgressDialog,
):
    plotGen = PlotGenerator()
    pointsGen = SimulationPlotVariables()
    print("generating: circle, centroid, fixed")
    plotGen.generateCirclePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "circle_cen.shp",
        "centroid",
        "fixed",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "circle_cen.shp",
        idFieldName,
        workingDir + "circle_cen_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: circle, bounding box, fixed")
    plotGen.generateCirclePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "circle_bbox.shp",
        "bounding box",
        "fixed",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "circle_bbox.shp",
        idFieldName,
        workingDir + "circle_bbox_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: circle, mean coordinates, fixed")
    plotGen.generateCirclePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "circle_mxy.shp",
        "mean coordinates",
        "fixed",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "circle_mxy.shp",
        idFieldName,
        workingDir + "circle_mxy_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    
    print("generating: circle, centroid, translated")
    plotGen.generateCirclePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "circle_cen_trans.shp",
        "centroid",
        "translated",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "circle_cen_trans.shp",
        idFieldName,
        workingDir + "circle_cen_trans_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: circle, bounding box, translated")
    plotGen.generateCirclePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "circle_bbox_trans.shp",
        "bounding box",
        "translated",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "circle_bbox_trans.shp",
        idFieldName,
        workingDir + "circle_bbox_trans_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: circle, mean coordinates, translated")
    plotGen.generateCirclePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "circle_mxy_trans.shp",
        "mean coordinates",
        "translated",
        progressDlg,
    )
    
    pointsGen.generatePoints(
        workingDir + "circle_mxy_trans.shp",
        idFieldName,
        workingDir + "circle_mxy_trans_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: circle, centroid, optimized")
    plotGen.generateCirclePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "circle_cen_opt.shp",
        "centroid",
        "optimized",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "circle_cen_opt.shp",
        idFieldName,
        workingDir + "circle_cen_opt_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )

    
def GenerateRectangles(
    workingDir: str, polygonShpFN: str, idFieldName: str, nPoints: int, clipPoints: bool, progressDlg: GProgressDialog
):
    plotGen = PlotGenerator()
    pointsGen = SimulationPlotVariables()
    print("generating: rectangle, centroid, fixed")
    plotGen.generateRectanglePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "rectangle_cen.shp",
        "centroid",
        "fixed",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "rectangle_cen.shp",
        idFieldName,
        workingDir + "rectangle_cen_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: rectangle, bounding box, fixed")
    plotGen.generateRectanglePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "rectangle_bbox.shp",
        "bounding box",
        "fixed",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "rectangle_bbox.shp",
        idFieldName,
        workingDir + "rectangle_bbox_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: rectangle, mean coordinates, fixed")
    plotGen.generateRectanglePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "rectangle_mxy.shp",
        "mean coordinates",
        "fixed",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "rectangle_mxy.shp",
        idFieldName,
        workingDir + "rectangle_mxy_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )

    print("generating: rectangle, centroid, resized")
    plotGen.generateRectanglePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "rectangle_cen_rsiz.shp",
        "centroid",
        "resized",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "rectangle_cen_rsiz.shp",
        idFieldName,
        workingDir + "rectangle_cen_rsiz_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: rectangle, bounding box, resized")
    plotGen.generateRectanglePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "rectangle_bbox_rsiz.shp",
        "bounding box",
        "resized",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "rectangle_bbox_rsiz.shp",
        idFieldName,
        workingDir + "rectangle_bbox_rsiz_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: rectangle, mean coordinates, resized")
    plotGen.generateRectanglePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "rectangle_mxy_rsiz.shp",
        "mean coordinates",
        "resized",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "rectangle_mxy_rsiz.shp",
        idFieldName,
        workingDir + "rectangle_mxy_rsiz_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )  

    print("generating: rectangle, centroid, rotated")
    plotGen.generateRectanglePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "rectangle_cen_rot.shp",
        "centroid",
        "rotated",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "rectangle_cen_rot.shp",
        idFieldName,
        workingDir + "rectangle_cen_rot_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: rectangle, bounding box, rotated")
    plotGen.generateRectanglePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "rectangle_bbox_rot.shp",
        "bounding box",
        "rotated",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "rectangle_bbox_rot.shp",
        idFieldName,
        workingDir + "rectangle_bbox_rot_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: rectangle, mean coordinates, rotated")
    plotGen.generateRectanglePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "rectangle_mxy_rot.shp",
        "mean coordinates",
        "rotated",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "rectangle_mxy_rot.shp",
        idFieldName,
        workingDir + "rectangle_mxy_rot_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    
    print("generating: rectangle, centroid, translated")
    plotGen.generateRectanglePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "rectangle_cen_trans.shp",
        "centroid",
        "translated",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "rectangle_cen_trans.shp",
        idFieldName,
        workingDir + "rectangle_cen_trans_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: rectangle, bounding box, translated")
    plotGen.generateRectanglePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "rectangle_bbox_trans.shp",
        "bounding box",
        "translated",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "rectangle_bbox_trans.shp",
        idFieldName,
        workingDir + "rectangle_bbox_trans_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: rectangle, mean coordinates, translated")
    plotGen.generateRectanglePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "rectangle_mxy_trans.shp",
        "mean coordinates",
        "translated",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "rectangle_mxy_trans.shp",
        idFieldName,
        workingDir + "rectangle_mxy_trans_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )

    print("generating: rectangle, centroid, optimized")
    plotGen.generateRectanglePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "rectangle_cen_opt.shp",
        "centroid",
        "optimized",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "rectangle_cen_opt.shp",
        idFieldName,
        workingDir + "rectangle_cen_opt_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: rectangle, bounding box, optimized")
    plotGen.generateRectanglePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "rectangle_bbox_opt.shp",
        "bounding box",
        "optimized",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "rectangle_bbox_opt.shp",
        idFieldName,
        workingDir + "rectangle_bbox_opt_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: rectangle, mean coordinates, optimized")
    plotGen.generateRectanglePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "rectangle_mxy_opt.shp",
        "mean coordinates",
        "optimized",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "rectangle_mxy_opt.shp",
        idFieldName,
        workingDir + "rectangle_mxy_opt_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )

        
def GenerateEllipses(
    workingDir: str, polygonShpFN: str, idFieldName: str, nPoints: int, clipPoints: bool, progressDlg: GProgressDialog
):
    plotGen = PlotGenerator()
    pointsGen = SimulationPlotVariables()
    print("generating: ellipse, centroid, fixed")
    plotGen.generateEllipsePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "ellipse_cen.shp",
        "centroid",
        "fixed",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "ellipse_cen.shp",
        idFieldName,
        workingDir + "ellipse_cen_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: ellipse, bounding box, fixed")
    plotGen.generateEllipsePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "ellipse_bbox.shp",
        "bounding box",
        "fixed",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "ellipse_bbox.shp",
        idFieldName,
        workingDir + "ellipse_bbox_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: ellipse, mean coordinates, fixed")
    plotGen.generateEllipsePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "ellipse_mxy.shp",
        "mean coordinates",
        "fixed",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "ellipse_mxy.shp",
        idFieldName,
        workingDir + "ellipse_mxy_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )

    print("generating: ellipse, centroid, resized")
    plotGen.generateEllipsePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "ellipse_cen_rsiz.shp",
        "centroid",
        "resized",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "ellipse_cen_rsiz.shp",
        idFieldName,
        workingDir + "ellipse_cen_rsiz_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: ellipse, bounding box, resized")
    plotGen.generateEllipsePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "ellipse_bbox_rsiz.shp",
        "bounding box",
        "resized",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "ellipse_bbox_rsiz.shp",
        idFieldName,
        workingDir + "ellipse_bbox_rsiz_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: ellipse, mean coordinates, resized")
    plotGen.generateEllipsePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "ellipse_mxy_rsiz.shp",
        "mean coordinates",
        "resized",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "ellipse_mxy_rsiz.shp",
        idFieldName,
        workingDir + "ellipse_mxy_rsiz_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )

    print("generating: ellipse, centroid, rotated")
    plotGen.generateEllipsePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "ellipse_cen_rot.shp",
        "centroid",
        "rotated",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "ellipse_cen_rot.shp",
        idFieldName,
        workingDir + "ellipse_cen_rot_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: ellipse, bounding box, rotated")
    plotGen.generateEllipsePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "ellipse_bbox_rot.shp",
        "bounding box",
        "rotated",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "ellipse_bbox_rot.shp",
        idFieldName,
        workingDir + "ellipse_bbox_rot_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: ellipse, mean coordinates, rotated")
    plotGen.generateEllipsePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "ellipse_mxy_rot.shp",
        "mean coordinates",
        "rotated",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "ellipse_mxy_rot.shp",
        idFieldName,
        workingDir + "ellipse_mxy_rot_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    
    print("generating: ellipse, centroid, translated")
    plotGen.generateEllipsePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "ellipse_cen_trans.shp",
        "centroid",
        "translated",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "ellipse_cen_trans.shp",
        idFieldName,
        workingDir + "ellipse_cen_trans_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: ellipse, bounding box, translated")
    plotGen.generateEllipsePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "ellipse_bbox_trans.shp",
        "bounding box",
        "translated",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "ellipse_bbox_trans.shp",
        idFieldName,
        workingDir + "ellipse_bbox_trans_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: ellipse, mean coordinates, translated")
    plotGen.generateEllipsePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "ellipse_mxy_trans.shp",
        "mean coordinates",
        "translated",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "ellipse_mxy_trans.shp",
        idFieldName,
        workingDir + "ellipse_mxy_trans_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )

    print("generating: ellipse, centroid, optimized")
    plotGen.generateEllipsePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "ellipse_cen_opt.shp",
        "centroid",
        "optimized",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "ellipse_cen_opt.shp",
        idFieldName,
        workingDir + "ellipse_cen_opt_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: ellipse, bounding box, optimized")
    plotGen.generateEllipsePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "ellipse_bbox_opt.shp",
        "bounding box",
        "optimized",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "ellipse_bbox_opt.shp",
        idFieldName,
        workingDir + "ellipse_bbox_opt_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )
    print("generating: ellipse, mean coordinates, optimized")
    plotGen.generateEllipsePlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "ellipse_mxy_opt.shp",
        "mean coordinates",
        "optimized",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "ellipse_mxy_opt.shp",
        idFieldName,
        workingDir + "ellipse_mxy_opt_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )


def GenerateBestPlots(
    workingDir: str, 
    polygonShpFN: str, 
    idFieldName: str, 
    nPoints: int, 
    clipPoints: bool, 
    progressDlg: GProgressDialog,
):
    plotGen = PlotGenerator()
    pointsGen = SimulationPlotVariables()
    print("generating: best")
    plotGen.generateBestPlots(
        workingDir + polygonShpFN,
        idFieldName,
        workingDir + "best_plot.shp",
        progressDlg,
    )
    pointsGen.generatePoints(
        workingDir + "best_plot.shp",
        idFieldName,
        workingDir + "best_plot_points.shp",
        nPoints,
        clipPoints,
        progressDlg,
    )


# Open progress dialog.
progressDlg = GProgressDialog()
progressDlg.show()

try:
    # Set configuration variables for batch testing.
    workingDir = "C:\\data\\"
    fstandFN = "forest_stands.shp"
    fstandID = "id"
    nPoints = 5
    clipPoints = True

    # Generate simulation plots and points for each plot type.
    GenerateSquares(workingDir, fstandFN, fstandID, nPoints, clipPoints, progressDlg)
    GenerateCircles(workingDir, fstandFN, fstandID, nPoints, clipPoints, progressDlg)
    GenerateRectangles(workingDir, fstandFN, fstandID, nPoints, clipPoints, progressDlg)
    GenerateEllipses(workingDir, fstandFN, fstandID, nPoints, clipPoints, progressDlg)
    GenerateBestPlots(workingDir, fstandFN, fstandID, nPoints, clipPoints, progressDlg)

    # Set configuration variables for raster extraction.
    demFN = "dem\\dem"
    slopeFN = "dem\\slope_perc"
    plotShpFN = "best_plot.shp" # created by GenerateBestPlots
    pointsShpFN = "best_plot_points.shp" # created by GenerateBestPlots

    # Extract elevation and slope values for each point in the simulation plot.
    points = SimulationPlotVariables()
    points.valueFromPoints(workingDir + fstandFN, fstandID, workingDir + pointsShpFN, "elev", workingDir + demFN, progressDlg)
    points.valueFromPoints(workingDir + fstandFN, fstandID, workingDir + pointsShpFN, "slope", workingDir + slopeFN, progressDlg)
    points.valueFromCentroid(workingDir + plotShpFN, "slope", workingDir + slopeFN, progressDlg)

except Exception as e:
    print(e)

else:
    print("Testing completed.")

finally:
    progressDlg.close()
