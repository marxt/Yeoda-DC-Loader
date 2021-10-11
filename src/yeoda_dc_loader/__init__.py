# -*- coding: utf-8 -*-
"""
/***************************************************************************
 YeodaDCLoader
                                 A QGIS plugin
 Loads a Yeoda filenamed directory to QGIS, sets time element
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-10-09
        copyright            : (C) 2021 by TUW GEO
        email                : mark.tupas@geo.tuwien.ac.at
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load YeodaDCLoader class from file YeodaDCLoader.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .yeoda_dc_loader import YeodaDCLoader
    return YeodaDCLoader(iface)
