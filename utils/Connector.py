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

from qgis.core import (QgsFeature, QgsGeometry, QgsPointXY, QgsVectorLayer, QgsFeatureRequest,
                    QgsProject, QgsPoint, QgsField, QgsTask, QgsMessageLog)
from qgis.PyQt.QtCore import QVariant

import processing
from .pyqgisA import get_bounding_feats_from_lyr

class Connector(QgsTask):
    """Task thread for Linking layers."""

    def __init__(self):
        super().__init__()
        self.exception = None

    def toss_params(self, plyr, llyr, value_cbx_pnt_col, value_cbx_link_col, bf_unit):
        self.p_lyr = plyr
        self.l_lyr = llyr
        self.value_cbx_pnt_col = value_cbx_pnt_col
        self.value_cbx_link_col = value_cbx_link_col
        self.bufsize = bf_unit
    
    def toss_btns(self, pbar, chkbox):
        self.pbar = pbar
        self.chkbox = chkbox
        
    def run(self):
        self.pbar.setValue(0)
        tmp_lyr = QgsVectorLayer('LineString', 'relations', 'memory')
        
        processing.run("native:createspatialindex", {'INPUT':self.p_lyr})
        processing.run("native:createspatialindex", {'INPUT':self.l_lyr})
        tmp_lyr.setCrs(self.p_lyr.crs())
        
        # tmp_lyr = QgsMapLayerRegistry.instance().mapLayersByName('dist')[0]
        
        tmp_lyr_dp = tmp_lyr.dataProvider()
        attrs = [QgsField("distance", QVariant.Double)]
        if self.value_cbx_link_col:
            attrs.insert(0, QgsField("id_link",  QVariant.String))
        if self.value_cbx_pnt_col:
            attrs.insert(0, QgsField("id_node", QVariant.String))

        tmp_lyr_dp.addAttributes(attrs)
        tmp_lyr.updateFields() 
        
        feats = [] 
        fails = []
        idx = 0
        for p in self.p_lyr.getFeatures():
            idx += 1
            lyr_clipped = get_bounding_feats_from_lyr(p.geometry(), self.l_lyr, self.bufsize) 
            if lyr_clipped:
                candidates = [l.geometry().closestSegmentWithContext(QgsPointXY(p.geometry().asPoint())) for l in lyr_clipped]
                _minDistPoint = min(candidates)
                target_line_feat = lyr_clipped[candidates.index(_minDistPoint)]
                # print(target_line_feat)
                minDistPoint = _minDistPoint[1]
                # closestSegmentWithContext's sample return: (24.521728385751178, <QgsPointXY: POINT(968737.81815429532434791 1949835.58028465695679188)>, 2, -1)
                geom = QgsGeometry.fromPolyline([QgsPoint(p.geometry().asPoint()), QgsPoint(minDistPoint[0], minDistPoint[1])])
                
                if geom.length() <= self.bufsize:
                    feat = QgsFeature()
                    feat.setGeometry(geom)
                    cattrs = [feat.geometry().length()]
                    if self.value_cbx_link_col:
                        lcol_idx = self.l_lyr.fields().indexFromName(self.value_cbx_link_col) 
                        cattrs.insert(0, target_line_feat.attribute(lcol_idx))
                    if self.value_cbx_pnt_col:
                        pcol_idx = self.p_lyr.fields().indexFromName(self.value_cbx_pnt_col)
                        cattrs.insert(0, p.attribute(pcol_idx))
                    # print(p.attribute(pcol_idx))
                    # print(_minDistPoint[2])
                    feat.setAttributes(cattrs)
                    feats.append(feat)
                else:
                    fails.append(p.id())
            else:
                fails.append(p.id())
            
            self.pbar.setValue(int((idx/len(self.p_lyr))*100))
            if self.isCanceled():
                return False
            
        tmp_lyr_dp.addFeatures(feats)
        # epsg_crs = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)

        QgsProject.instance().addMapLayer(tmp_lyr)
        # tmp_lyr.updateExtents()
        # tmp_lyr.triggerRepaint()
        # query  = 'fid in ({})'.format(','.join([str(i) for i in fails]))
        if self.chkbox.isChecked() and fails:
            # self.p_lyr.setSubsetString(query)
            self.p_lyr.removeSelection()
            self.p_lyr.select( fails )
            new_layer = self.p_lyr.materialize(QgsFeatureRequest().setFilterFids(self.p_lyr.selectedFeatureIds()))
            self.p_lyr.removeSelection()
            new_layer.setName(f'{new_layer.name()}_rel_failed')
            QgsProject.instance().addMapLayer(new_layer)
        
            # # simulate exceptions to show how to abort task
            # if arandominteger == 42:
            #     # DO NOT raise Exception('bad value!')
            #     # this would crash QGIS
            #     self.exception = Exception('bad value!')
            #     return False
        return True
    
    
    def finished(self, result):
        if result:
            pass
        else:
            if self.exception is None:
                QgsMessageLog.logMessage(
                    'Task not successful but without '\
                    'exception (probably the task was manually '\
                    'canceled by the user)')
            else:
                QgsMessageLog.logMessage('Exception')
                raise self.exception
    
    def cancel(self):
        super().cancel()