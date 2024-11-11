# -*- coding: utf-8 -*-
"""
Package:   GenSimPlot
File:      GenPoints_dialog.py
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
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "GenPoints_dialog.ui"))


class GenPointsDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(GenPointsDialog, self).__init__(parent)
        self.setupUi(self)
        self.btnBox.accepted.connect(self.OnOK)
        self.btnBrowseInputShp.clicked.connect(self.OnBrowseInputShp)
        self.btnBrowseOutputShp.clicked.connect(self.OnBrowseOutputShp)
        

    def OnBrowseInputShp(self):
        GenSimPlotUtilities.browseInputPolygonShp(self, self.tbInputShpFN, self.cmbFields)


    def OnBrowseOutputShp(self):
        GenSimPlotUtilities.OnBrowseOutputShp(self, self.tbOutputShpFN)


    def OnOK(self):
        inputShp = self.tbInputShpFN.text()
        inputIDField = self.cmbFields.currentText()
        outputShp = self.tbOutputShpFN.text()
        nPoints = int(self.tbOutputNPoints.text())
        clipPoints = self.chbOutputClipPoints.isChecked()
        points = GenSimPlotLib.SimulationPlotVariables()
        progressDlg = GProgressDialog()
        progressDlg.show()
        points.generatePoints(inputShp, inputIDField, outputShp, nPoints, clipPoints, progressDlg)
        progressDlg.close()

