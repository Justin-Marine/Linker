# -*- coding: utf-8 -*-
"""

/***************************************************************************

################################
Linker plugin.
begin     : 2023-01-12
copyright : (C) 2023 by Justin
email     : justin901203@gmail.com

Plugin generates relations between Point Layer's features and shortest vertex of a Line Layer.
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
    """Load class_name class from file class_name.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .Linker import Linker
    return Linker(iface)
