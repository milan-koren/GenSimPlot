# -*- coding: utf-8 -*-
"""
Package:   GenSimPlot
File:      GenSimPlot.py
Version:   2.1
Author:    Milan Koren
Year:      2024
URL:       https://github.com/milan-koren/GenSimPlot
License:   EUPL v1.2 (European Union Public License), https://eupl.eu/
"""

import os.path

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .resources import *
from .GenSimPlot_dialog import GenSimPlotDialog
from .GenPoints_dialog import GenPointsDialog
from .ExtractByPoints_dialog import ExtractByPointsDialog
from .ExtractByCentroid_dialog import ExtractByCentroidDialog


class GenSimPlot:
    def __init__(self, iface):
        """
        Constructor.

        Parameters
            iface (QgsInterface): An interface instance that will be passed to this class which provides the hook 
                                  by which you can manipulate the QGIS application at run time.
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # Declare instance attributes
        self.actions = []
        self.menu = "&GenSimPlot"


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """
        Add a toolbar icon to the toolbar.

        Parameters:
            icon_path (str): Path to the icon for this action. Can be a resource or a normal file system path.
            text (str): Text that should be shown in menu items for this action.
            callback (function): Function to be called when the action is triggered.
            param enabled_flag (bool): A flag indicating if the action should be enabled by default. Defaults to True.
            param add_to_menu (bool): Flag indicating whether the action should also be added to the menu. Defaults to True.
            param add_to_toolbar (bool): Flag indicating whether the action should also be added to the toolbar. Defaults to True.
            param status_tip (str): Optional text to show in a popup when mouse pointer hovers over the action.
            param parent (QWidget): Parent widget for the new action. Defaults None.
            param whats_this (str): Optional text to show in the status bar when the mouse pointer hovers over the action.

         Returns:
            (QAction): The action that was created. Note that the action is also added to self.actions list.
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        icon_generatePlots = ':/plugins/GenSimPlot/icon01.png'
        icon_generatePoints = ':/plugins/GenSimPlot/icon02.png'
        icon_extractByPoints = ':/plugins/GenSimPlot/icon03.png'
        icon_extractByCentroid = ':/plugins/GenSimPlot/icon04.png'
        self.add_action(
            icon_generatePlots,
            text="Generate Plots",
            callback=self.runGenSimPlot,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False)

        self.add_action(
            icon_generatePoints,
            text="Generate Points",
            callback=self.runGenPoints,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False)
        
        self.add_action(
            icon_extractByPoints,
            text="Extract Values by Points",
            callback=self.runExtractByPoints,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False)
        
        self.add_action(
            icon_extractByCentroid,
            text="Extract Values by Centroid",
            callback=self.runExtractByCentroid,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False)


    def unload(self):
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                "&GenSimPlot",
                action)
            self.iface.removeToolBarIcon(action)


    def runGenSimPlot(self):
        if (not hasattr(self, "dlgGenSimPlot")):
            self.dlgGenSimPlot = GenSimPlotDialog()
        self.dlgGenSimPlot.show()


    def runGenPoints(self):
        if (not hasattr(self, "dlgGenPoints")):
            self.dlgGenPoints = GenPointsDialog()
        self.dlgGenPoints.show()


    def runExtractByPoints(self):
        if (not hasattr(self, "dlgExtractByPoints")):
            self.dlgExtractByPoints = ExtractByPointsDialog()
        self.dlgExtractByPoints.show()


    def runExtractByCentroid(self):
        if (not hasattr(self, "dlgExtractByCentroid")):
            self.dlgExtractByCentroid = ExtractByCentroidDialog()
        self.dlgExtractByCentroid.show()
    