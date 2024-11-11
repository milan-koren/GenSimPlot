# -*- coding: utf-8 -*-
"""
Package:   GenSimPlot
File:      GenSimPlot_dialog.py
Version:   2.1
Author:    Milan Koren
Year:      2024
URL:       https://github.com/milan-koren/GenSimPlot
License:   EUPL v1.2 (European Union Public License), https://eupl.eu/
"""

import sys
import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

sys.path.append(os.path.dirname(__file__))
from qgis.core import *

from .GenSimPlotUtilities import GProgressDialog
from .GenSimPlotUtilities import GenSimPlotUtilities
import GenSimPlotLib

# This loads .ui file
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "GenSimPlot_dialog.ui"))


class GenSimPlotDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(GenSimPlotDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('Generator of Simulation Plots')
        self.btnBox.accepted.connect(self.OnOK)
        self.btnBrowseInputShp.clicked.connect(self.OnBrowseInputShp)
        self.btnBrowseOutputShp.clicked.connect(self.OnBrowseOutputShp)
        self.cmbShape.currentIndexChanged.connect(self.OnShapeChanged)
        

    def OnBrowseInputShp(self):
        GenSimPlotUtilities.browseInputPolygonShp(self, self.tbInputShpFN, self.cmbFields)


    def OnBrowseOutputShp(self):
        GenSimPlotUtilities.OnBrowseOutputShp(self, self.tbOutputShpFN)


    def OnShapeChanged(self):
        self.cmbPosition.setDisabled(self.cmbShape.currentText() == "best")
        self.cmbPlacement.setDisabled(self.cmbShape.currentText() == "best")


    def OnOK(self):
        inputShp = self.tbInputShpFN.text()
        outputShp = self.tbOutputShpFN.text()
        inputIDField = self.cmbFields.currentText()
        plotShape = self.cmbShape.currentText()
        plotPosition = self.cmbPosition.currentText()
        plotPlacement = self.cmbPlacement.currentText()
        progressDlg = GProgressDialog()
        progressDlg.show()
        if (plotShape == "circle"):
            GenSimPlotLib.PlotGenerator().generateCirclePlots(inputShp, inputIDField, outputShp, plotPosition, plotPlacement, progressDlg)
        elif (plotShape == "ellipse"):
            GenSimPlotLib.PlotGenerator().generateEllipsePlots(inputShp, inputIDField, outputShp, plotPosition, plotPlacement, progressDlg)
        elif (plotShape == "rectangle"):
            GenSimPlotLib.PlotGenerator().generateRectanglePlots(inputShp, inputIDField, outputShp, plotPosition, plotPlacement, progressDlg)
        elif (plotShape == "square"):
            GenSimPlotLib.PlotGenerator().generateSquarePlots(inputShp, inputIDField, outputShp, plotPosition, plotPlacement, progressDlg)
        else:
            GenSimPlotLib.PlotGenerator().generateBestPlots(inputShp, inputIDField, outputShp, progressDlg)
        progressDlg.close()
