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
"""

'''
Pyqgis related functions.
'''

from qgis.core import QgsFeatureRequest # QgsFeature, QgsGeometry, QgsPointXY, QgsVectorLayer, QgsProject, QgsPoint, 


def set_attr_by_fld_name( feature, fieldname, value):
    """ 피처와 필드명칭을 입력하면 해당 필드명의 속성값을 리턴.
        get attribute by field name. (from feature)
    """
    fld_idx = feature.fields().indexFromName(fieldname)
    feature.setAttribute(fld_idx, value)

def get_request_box(input_geom, input_dist):    
    req = QgsFeatureRequest()
    req.setFilterRect(input_geom.buffer(input_dist, 5).boundingBox())
    req.setFlags(QgsFeatureRequest.ExactIntersect)
    return req

def get_bounding_feats_from_lyr(input_geom, input_lyr, input_dist):   
    req = get_request_box(input_geom, input_dist) 
    intersecting_pnts = input_lyr.getFeatures(req)
    return [pnt for pnt in intersecting_pnts]
