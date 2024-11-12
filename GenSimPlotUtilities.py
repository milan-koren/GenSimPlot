# -*- coding: utf-8 -*-
"""
Package:   GenSimPlot
File:      GenSimPlotUtilities.py
Version:   2.1
Author:    Milan Koren
Year:      2024
URL:       https://github.com/milan-koren/GenSimPlot
License:   EUPL v1.2 (European Union Public License), https://eupl.eu/
"""

import os.path

from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QProgressDialog
from PyQt5.QtCore import Qt
from qgis.core import *
from qgis.PyQt.QtWidgets import QApplication


class GProgressDialog:
    """
    This class provides a simple progress dialog with a progress bar and a label.
    """

    def __init__(self):
        """
        Initializes the progress dialog with the specified parent widget.

        Parameters:
            parent (QWidget): The parent widget

        Raises:
            Exception: If the user cancels the operation
        """
        title = "GenSimPlot Progress"
        self.progress = QProgressDialog(title, "Cancel", 0, 100)
        self.progress.setWindowModality(Qt.WindowModal)
        self.progress.setWindowTitle(title)
        self.progress.setLabelText("Processing...")
        self.progress.setMinimumDuration(0)
        self.progress.setAutoClose(False)
        self.progress.setAutoReset(False)
        QApplication.processEvents()


    def show(self):
        """
        Displays the progress dialog.
        """
        self.progress.show()
        QApplication.processEvents()


    def restart(self, label: str, maximum: int):
        """
        Resets the value of the progress bar to 0.

        Parameters:
            label (str): The label to set.
            maximum (int): The maximum value to set.
        """
        self.progress.setLabelText(label)
        self.progress.setMaximum(maximum)
        self.progress.setValue(0)
        QApplication.processEvents()


    def setLabel(self, label: str):
        """
        Sets the label of the progress dialog.

        Parameters:
            label (str): The label to set.
        """
        self.progress.setLabelText(label)
        QApplication.processEvents()


    def setMaximum(self, maximum: int):
        """
        Sets the maximum value of the progress bar.

        Parameters:
            maximum (int): The value to set.
        """
        self.progress.setMaximum(maximum)
        self.progress.setValue(0)
        QApplication.process


    def setProgress(self, val: int):
        """
        Sets the value of the progress bar.

        Parameters:
            val (int): The value to set
        """
        self.progress.setValue(val)
        QApplication.processEvents()
        if self.progress.wasCanceled():
            raise Exception("User cancelled operation.")


    def increment(self):
        """
        Increments the value of the progress bar by 1.
        """
        if self.progress.value() < self.progress.maximum():
            self.progress.setValue(self.progress.value() + 1)
        else:
            self.progress.setValue(0)
        QApplication.processEvents()
        if self.progress.wasCanceled():
            raise Exception("User cancelled operation.")


    def wasCanceled(self):
        """
        Returns True if the user has clicked the cancel button, otherwise False.
        """
        return self.progress.wasCanceled()


    def close(self):
        """
        Closes the progress dialog.
        """
        self.progress.close()



class GenSimPlotUtilities:
    """
    This class provides several static methods that offer various functionalities related to generating simulation plots
    within a QGIS plugin.

    These methods provide convenient functionality for interacting with file dialogs, validating shapefile geometries,
    displaying error messages, and updating UI elements within the QGIS plugin.
    """

    @staticmethod
    def showErrorMessage(msg, progressDlg = None):
        """
        This method displays an error message dialog box with the specified message.

        Parameters:
            msg (str): The error message
            progressDlg (GProgressDialog): The progress dialog
        """
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Critical)
        msgBox.setText(msg)
        msgBox.setWindowTitle("Error")
        msgBox.exec_()
        if progressDlg != None:
            progressDlg.close()


    @staticmethod
    def raiseException(msg, progressDlg):
        """
        Raises exception and closes the progress dialog.

        Parameters:
            msg (str): The exception message
            progressDlg (GProgressDialog): The progress dialog
        """
        GenSimPlotUtilities.showErrorMessage(msg, progressDlg)
        raise Exception(msg)


    @staticmethod
    def raiseValueError(msg, progressDlg):
        """
        Raises value exception and closes the progress dialog.

        Parameters:
            msg (str): The exception message
            progressDlg (GProgressDialog): The progress dialog
        """
        GenSimPlotUtilities.showErrorMessage(msg, progressDlg)
        raise ValueError(msg)


    @staticmethod
    def browseInputPolygonShp(parent, tbInputShpFN, cmbFields):
        """
        This method opens a file dialog for selecting an input polygon shapefile.

        It checks if the selected shapefile contains polygon geometries and
        retrieves the available fields. If a valid shapefile is selected, it updates
        the input shapefile text box (tbInputShpFN) and, if provided, the combo box
        (cmbFields) with the available text and integer fields.

        Parameters:
            parent (QWidget): The parent widget
            tbInputShpFN (QLineEdit): The input shapefile text box
            cmbFields (QComboBox): The combo box for field names
        """
        shpName, _ = QtWidgets.QFileDialog.getOpenFileName(
            parent, "Input Polygon Shape-file", "", "Shape-files (*.shp)"
        )
        if shpName:
            try:
                fieldList = []
                inputLayer = QgsVectorLayer(shpName, "fpoly", "ogr")
                if inputLayer.geometryType() != Qgis.GeometryType.Polygon:
                    GenSimPlotUtilities.showErrorMessage(
                        "Invalid geometry type: The input shapefile must consist of POLYGON geometries only. Please verify and select an appropriate file."
                    )
                    shpName = None
                else:
                    for field in inputLayer.fields():
                        if (
                            field.typeName() == "Integer"
                            or field.typeName() == "Integer64"
                            or field.typeName() == "String"
                        ):
                            fieldList.append(field.name())
                    if len(fieldList) < 1:
                        shpName = None
                        GenSimPlotUtilities.showErrorMessage(
                            "No valid ID field found in the input shapefile. Please check and select a shapefile with a defined ID field."
                        )
            except:
                shpName = None
            if cmbFields != None:
                cmbFields.clear()
            if shpName != None and 0 < len(fieldList):
                tbInputShpFN.setText(shpName)
                if cmbFields != None:
                    cmbFields.addItems(fieldList)
            else:
                tbInputShpFN.setText("")

    
    @staticmethod
    def browseInputPointShp(parent, tbInputShpFN):
        """
        This method opens a file dialog for selecting an input point shapefile.

        It checks if the selected shapefile contains only point geometries.
        If a valid shapefile is selected, it updates the input shapefile text box (tbInputShpFN).

        Parameters:
            parent (QWidget): The parent widget
            tbInputShpFN (QLineEdit): The input shapefile text box
        """
        shpName, _ = QtWidgets.QFileDialog.getOpenFileName(
            parent, "Input Point Shape-file", "", "Shape-files (*.shp)"
        )
        if shpName:
            inputLayer = QgsVectorLayer(shpName, "fpoints", "ogr")
            if inputLayer.geometryType() != Qgis.GeometryType.Point:
                GenSimPlotUtilities.showErrorMessage(
                    "Invalid geometry type: The input shapefile must consist of POINT geometries only. Please verify and select an appropriate file."
                )
                shpName = None
            tbInputShpFN.setText(shpName)


    @staticmethod
    def OnBrowseOutputShp(parent, tbOutputShpFN):
        """
        This method opens a file dialog for selecting the output shapefile path.

        It updates the output shapefile text box (tbOutputShpFN) with the selected path.

        Parameters:
            parent (QWidget): The parent widget
            tbOutputShpFN (QLineEdit): The output shapefile
        """
        shpName, _ = QtWidgets.QFileDialog.getSaveFileName(
            parent, "Output Shape-file", "", "Shape-files (*.shp)"
        )
        if shpName:
            tbOutputShpFN.setText(shpName)


    @staticmethod
    def browseInputRaster(parent, tbInputRasterFN):
        """
        This method opens a directory dialog for selecting an input raster directory.

        It updates the input raster text box (tbInputRasterFN) with the selected directory path.

        Parameters:
            parent (QWidget): The parent widget
            tbInputRasterFN (QLineEdit): The input raster text
        """
        rasterFN = QtWidgets.QFileDialog.getExistingDirectory(
            parent,
            "Select Raster",
            "",
            QtWidgets.QFileDialog.ShowDirsOnly
            | QtWidgets.QFileDialog.DontResolveSymlinks,
        )
        if rasterFN:
            if QgsRasterLayer.isValidRasterFileName(rasterFN):
                tbInputRasterFN.setText(rasterFN)
            else:
                GenSimPlotUtilities.showErrorMessage(
                    "Invalid raster: Please verify and select an appropriate Arc/Info binary raster."
                )
                tbInputRasterFN.setText("")


    @staticmethod
    def startProgress(progressDlg: GProgressDialog, label: str, maximum: int):
        """
        This method displays the progress dialog with the specified label and maximum value.

        If the progress dialog is not None, it restarts the progress dialog with the specified label and maximum value.

        Parameters:
            progressDlg (GProgressDialog): The progress dialog.
            label (str): The label.
            maximum (int): The maximum value.
        """
        if progressDlg != None:
            progressDlg.restart(label, maximum)
    
    
    @staticmethod
    def incrementProgress(progressDlg: GProgressDialog):
        """
        This method increments the progress dialog by 1.

        If the progress dialog is not None, it increments the progress dialog by 1.

        Parameters:
            progressDlg (GProgressDialog): The progress dialog.
        """
        if progressDlg != None:
            progressDlg.increment()


    @staticmethod
    def setProgressMaximum(progressDlg: GProgressDialog, maximum: int):
        """
        This method sets the maximum value of the progress dialog.

        If the progress dialog is not None, it sets the maximum value of the progress dialog.

        Parameters:
            progressDlg (GProgressDialog): The progress dialog.
            maximum (int): The maximum value.
        """
        if progressDlg != None:
            progressDlg.setMaximum(maximum)


    @staticmethod
    def setProgressLabel(progressDlg: GProgressDialog, label: str):
        """
        This method sets the label of the progress dialog.

        If the progress dialog is not None, it sets the label of the progress dialog.

        Parameters:
            progressDlg (GProgressDialog): The progress dialog.
            label (str): The label.
        """
        if progressDlg != None:
            progressDlg.setLabel(label)