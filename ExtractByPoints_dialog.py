# -*- coding: utf-8 -*-
"""
Package:   GenSimPlot
File:      ExtractByPoints_dialog.py
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

from .GenSimPlotUtilities import GProgressDialog
from .GenSimPlotUtilities import GenSimPlotUtilities
from .GenSimPlotLib import SimulationPlotVariables

# This loads .ui file
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "ExtractByPoints_dialog.ui"))


class ExtractByPointsDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(ExtractByPointsDialog, self).__init__(parent)
        self.setupUi(self)
        self.btnBox.accepted.connect(self.OnOK)
        self.btnBrowseInputPlotShp.clicked.connect(self.OnBrowseInputPlotShp)
        self.btnBrowseInputPointsShp.clicked.connect(self.OnBrowseInputPointsShp)
        self.btnBrowseInputRaster.clicked.connect(self.OnBrowseInputRaster)
        

    def OnBrowseInputPlotShp(self):
        GenSimPlotUtilities.browseInputPolygonShp(self, self.tbInputPlotsShpFN, self.cmbFields)


    def OnBrowseInputPointsShp(self):
        GenSimPlotUtilities.browseInputPointShp(self, self.tbInputPointsShpFN)
    

    def OnBrowseInputRaster(self):
        GenSimPlotUtilities.browseInputRaster(self, self.tbInputRasterFN)


    def OnOK(self):
        inputPlotsShpFN = self.tbInputPlotsShpFN.text()
        inputIDFieldName = self.cmbFields.currentText()
        inputPointsShpFN = self.tbInputPointsShpFN.text()
        outputFieldName = self.tbOutputFieldName.text()
        inputRasterFN = self.tbInputRasterFN.text()
        progressDlg = GProgressDialog()
        progressDlg.show()
        SimulationPlotVariables().valueFromPoints(inputPlotsShpFN, inputIDFieldName, inputPointsShpFN, outputFieldName, inputRasterFN, progressDlg)
        progressDlg.close()
