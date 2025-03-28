# -*- coding: utf-8 -*-
"""
Package:   GenSimPlot
File:      ExtractByCentroid_dialog.py
Version:   2.2
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
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "ExtractByCentroid_dialog.ui"))


class ExtractByCentroidDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(ExtractByCentroidDialog, self).__init__(parent)
        self.setupUi(self)
        self.btnBox.accepted.connect(self.OnOK)
        self.btnBrowseInputShp.clicked.connect(self.OnBrowseInputShp)
        self.btnBrowseInputRaster.clicked.connect(self.OnBrowseInputRaster)
        

    def OnBrowseInputShp(self):
        GenSimPlotUtilities.browseInputPolygonShp(self, self.tbInputShpFN, None)


    def OnBrowseInputRaster(self):
        GenSimPlotUtilities.browseInputRaster(self, self.tbInputRasterFN)


    def OnOK(self):
        inputPlotsShpFN = self.tbInputShpFN.text()
        outputFieldName = self.tbOutputFieldName.text()
        inputRasterFN = self.tbInputRasterFN.text()
        progressDlg = GProgressDialog()
        progressDlg.show()
        SimulationPlotVariables().valueFromCentroid(inputPlotsShpFN, outputFieldName, inputRasterFN, progressDlg)
        progressDlg.close()
        
