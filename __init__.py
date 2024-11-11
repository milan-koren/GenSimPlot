# -*- coding: utf-8 -*-
"""
Package:   GenSimPlot
File:      __init__.py
Version:   2.1
Author:    Milan Koren
Year:      2024
URL:       https://github.com/milan-koren/GenSimPlot
License:   EUPL v1.2 (European Union Public License), https://eupl.eu/          

This script initializes the plugin, making it known to QGIS.
"""

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """
    Load GenSimPlot class from file GenSimPlot.

    Parameters:
        iface (QgsInterface): A QGIS interface instance.
    """
    from .GenSimPlot import GenSimPlot
    return GenSimPlot(iface)
