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

import os

from qgis.utils import iface
from qgis.core import QgsProject, QgsApplication #, QgsFeature, QgsGeometry, QgsPointXY, QgsVectorLayer, QgsPoint, QgsField

from qgis.PyQt import uic, QtWidgets
# from qgis.PyQt.QtCore import QVariant

from PyQt5.QtGui import QIntValidator

# from .utils.pyqgisA import get_request_box
# from .utils.pyqgisA import get_bounding_feats_from_lyr
from .utils.Connector import Connector

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'LinkerDialog.ui'))


class LinkerDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        
        super().__init__()
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.iface = iface
        self.current_qpj = QgsProject.instance()
        
        self.refresh_dialog()
        
        onlyInt = QIntValidator()
        onlyInt.setRange(1, 10000)
        self.le_bufsize.setValidator(onlyInt)
        
        try:
            self.cbx_pnt_changed()
            self.cbx_link_changed()
        except:
            print('Selection might be vacant.')
        
        self.btn_submit.clicked.connect(self.btn_submit_clicked)
        self.btn_cancel.clicked.connect(self.btn_cancel_clicked)
        self.cbx_pnt.currentTextChanged.connect(self.cbx_pnt_changed)
        self.cbx_link.currentTextChanged.connect(self.cbx_link_changed)
        
    def refresh_dialog(self):
        all_lyrs = [i for i in self.iface.mapCanvas().layers()]
        pnt_lyrs = ['{}'.format(i.id()) for i in all_lyrs if i.geometryType() == 0]
        line_lyrs = ['{}'.format(i.id()) for i in all_lyrs if i.geometryType() == 1]
        
        self.cbx_pnt.addItems(pnt_lyrs)
        self.cbx_link.addItems(line_lyrs)
        
    def btn_submit_clicked(self):
        '''
        tmp_lyr = QgsVectorLayer('LineString', 'relations', 'memory')
        
        p_lyr = self.current_qpj.mapLayer(self.cbx_pnt.currentText())
        processing.run("native:createspatialindex", {'INPUT':p_lyr})
        l_lyr = self.current_qpj.mapLayer(self.cbx_link.currentText())
        processing.run("native:createspatialindex", {'INPUT':l_lyr})
        
        tmp_lyr.setCrs(p_lyr.crs())
        
        # tmp_lyr = QgsMapLayerRegistry.instance().mapLayersByName('dist')[0]
        
        tmp_lyr_dp = tmp_lyr.dataProvider()
        attrs = [QgsField("distance", QVariant.Double)]
        value_cbx_pnt_col= self.cbx_pnt_col.currentText()
        value_cbx_link_col= self.cbx_link_col.currentText()
        if value_cbx_link_col:
            attrs.insert(0, QgsField("id_link",  QVariant.String))
        if value_cbx_pnt_col:
            attrs.insert(0, QgsField("id_node", QVariant.String))

        tmp_lyr_dp.addAttributes(attrs)
        tmp_lyr.updateFields() 
        
        feats = [] 
        fails = []
        bufsize = int(self.le_bufsize.text())
        for p in p_lyr.getFeatures():
            lyr_clipped = get_bounding_feats_from_lyr(p.geometry(), l_lyr, bufsize) 
            if lyr_clipped:
                candidates = [l.geometry().closestSegmentWithContext(QgsPointXY(p.geometry().asPoint())) for l in lyr_clipped]
                _minDistPoint = min(candidates)
                target_line_feat = lyr_clipped[candidates.index(_minDistPoint)]
                # print(target_line_feat)
                minDistPoint = _minDistPoint[1]
                # closestSegmentWithContext's sample return: (24.521728385751178, <QgsPointXY: POINT(968737.81815429532434791 1949835.58028465695679188)>, 2, -1)
                geom = QgsGeometry.fromPolyline([QgsPoint(p.geometry().asPoint()), QgsPoint(minDistPoint[0], minDistPoint[1])])
                
                if geom.length() <= bufsize:
                    feat = QgsFeature()
                    feat.setGeometry(geom)
                    cattrs = [feat.geometry().length()]
                    if value_cbx_link_col:
                        lcol_idx = l_lyr.fields().indexFromName(value_cbx_link_col) 
                        cattrs.insert(0, target_line_feat.attribute(lcol_idx))
                    if value_cbx_pnt_col:
                        pcol_idx = p_lyr.fields().indexFromName(value_cbx_pnt_col)
                        cattrs.insert(0, p.attribute(pcol_idx))
                    # print(p.attribute(pcol_idx))
                    # print(_minDistPoint[2])
                    feat.setAttributes(cattrs)
                    feats.append(feat)
                else:
                    fails.append(p.id())
            else:
                fails.append(p.id())
    
        tmp_lyr_dp.addFeatures(feats)
        # epsg_crs = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)

        self.current_qpj.addMapLayer(tmp_lyr)
        # tmp_lyr.updateExtents()
        # tmp_lyr.triggerRepaint()
        query  = 'fid in ({})'.format(','.join([str(i) for i in fails]))
        # print(query)
        if self.cb_filter.isChecked():
            p_lyr.setSubsetString(query)
            # p_lyr.selectByExpression( query )
        '''
        
        self.connector = Connector()
        self.connector.toss_params(plyr = self.current_qpj.mapLayer(self.cbx_pnt.currentText()),
                                llyr = self.current_qpj.mapLayer(self.cbx_link.currentText()),
                                value_cbx_pnt_col = self.cbx_pnt_col.currentText(),
                                value_cbx_link_col = self.cbx_link_col.currentText(),
                                bf_unit = int(self.le_bufsize.text()))
        self.connector.toss_btns(pbar = self.pgbar, 
                                    chkbox = self.cb_filter)
        
        QgsApplication.taskManager().addTask(self.connector)
    
    def btn_cancel_clicked(self):
        if self.connector:
            self.connector.cancel()
    
    def cbx_pnt_changed(self):
        self.cbx_pnt_col.clear()
        p_lyr = self.current_qpj.mapLayer(self.cbx_pnt.currentText())
        self.cbx_pnt_col.addItems(['']+[i.name() for i in p_lyr.fields()])

    def cbx_link_changed(self):
        self.cbx_link_col.clear()
        l_lyr = self.current_qpj.mapLayer(self.cbx_link.currentText())
        self.cbx_link_col.addItems(['']+[i.name() for i in l_lyr.fields()])
