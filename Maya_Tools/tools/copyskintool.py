# -*- coding: utf-8 -*-
import maya.cmds as cmds
try:
    from PySide6 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide2 import QtWidgets, QtCore, QtGui
from maya import OpenMayaUI as omui
import shiboken2


def maya_main_window():
    ptr = omui.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(int(ptr), QtWidgets.QWidget)


class CrossDragList(QtWidgets.QListWidget):

    orderChanged = QtCore.Signal()
    drag_source = None
    drag_row = None
    drag_text = None

    def __init__(self):
        super(CrossDragList, self).__init__()
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)

    def startDrag(self, actions):
        item = self.currentItem()
        if item:
            CrossDragList.drag_source = self
            CrossDragList.drag_row = self.currentRow()
            CrossDragList.drag_text = item.text()
        super(CrossDragList, self).startDrag(actions)

    def dropEvent(self, event):
        target = self
        if CrossDragList.drag_text is None:
            super(CrossDragList, self).dropEvent(event)
            self.orderChanged.emit()
            return

        source = CrossDragList.drag_source
        src_row = CrossDragList.drag_row
        text = CrossDragList.drag_text

        if source is target:
            super(CrossDragList, self).dropEvent(event)
            self.orderChanged.emit()
        else:
            insert_row = target.indexAt(event.pos()).row()
            if insert_row < 0:
                insert_row = target.count()
            target.insertItem(insert_row, QtWidgets.QListWidgetItem(text))
            source.takeItem(src_row)
            self.orderChanged.emit()

        CrossDragList.drag_source = None
        CrossDragList.drag_row = None
        CrossDragList.drag_text = None

    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace):
            for item in self.selectedItems():
                self.takeItem(self.row(item))
            self.orderChanged.emit()
        else:
            super(CrossDragList, self).keyPressEvent(event)


class SkinWeightCopier(QtWidgets.QWidget):

    def __init__(self):
        super(SkinWeightCopier, self).__init__(maya_main_window())
        self.setObjectName("JCQ_SkinWeightCopier_UI")
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.Tool)
        self.setWindowTitle("Batch Weight Copy Tool")
        self.resize(560, 380)

        main = QtWidgets.QVBoxLayout(self)

        btn_copy = QtWidgets.QPushButton("Copy Skin Weights")
        btn_copy.clicked.connect(self.process_pairs)
        main.addWidget(btn_copy)

        self.cb_per_vertex = QtWidgets.QCheckBox("Per-Vertex Copy (if same vertex count)")
        self.cb_per_vertex.setChecked(False)
        main.addWidget(self.cb_per_vertex)

        lists_layout = QtWidgets.QHBoxLayout()

        self.left_list = CrossDragList()
        self.right_list = CrossDragList()

        self.left_list.orderChanged.connect(self.mark_invalid_pairs)
        self.right_list.orderChanged.connect(self.mark_invalid_pairs)

        arrow = QtWidgets.QLabel("➡")
        arrow.setAlignment(QtCore.Qt.AlignCenter)
        arrow.setStyleSheet("font-size:28px;")

        lists_layout.addWidget(self.left_list, 1)
        lists_layout.addWidget(arrow)
        lists_layout.addWidget(self.right_list, 1)
        main.addLayout(lists_layout)

        bl = QtWidgets.QHBoxLayout()

        btn_env = QtWidgets.QPushButton("skinCluster.envelope_SW")
        btn_env.clicked.connect(self.switchEnvelope)

        btn_pose = QtWidgets.QPushButton("reset dagPose")
        btn_pose.clicked.connect(self.resetdagpose)

        btn_reload = QtWidgets.QPushButton("Reload From Selection")
        btn_reload.clicked.connect(self.reload_from_selection)

        bl.addWidget(btn_env)
        bl.addWidget(btn_pose)
        bl.addWidget(btn_reload)
        main.addLayout(bl)

        self.reload_from_selection()
        self.show()

    def reload_from_selection(self):
        sel = cmds.ls(selection=True) or []
        self.left_list.clear()
        self.right_list.clear()

        for i, obj in enumerate(sel):
            item = QtWidgets.QListWidgetItem(obj)
            if i % 2 == 0:
                self.left_list.addItem(item)
            else:
                self.right_list.addItem(QtWidgets.QListWidgetItem(obj))

        self.mark_invalid_pairs()

    def mark_invalid_pairs(self):
        n = max(self.left_list.count(), self.right_list.count())

        for i in range(n):
            l = self.left_list.item(i)
            r = self.right_list.item(i)

            if not l or not r:
                if l: self._set_bad(l)
                if r: self._set_bad(r)
                continue

            obj = l.text()
            his = cmds.listHistory(obj) or []
            has_skin = any(cmds.nodeType(n) == "skinCluster" for n in his)

            if has_skin:
                self._set_good(l)
                self._set_good(r)
            else:
                self._set_bad(l)
                self._set_bad(r)

    def _set_good(self, item):
        item.setBackground(QtGui.QColor(0,0,0,0))
        item.setForeground(QtGui.QColor(255,255,255))

    def _set_bad(self, item):
        item.setBackground(QtGui.QColor(120,0,0))
        item.setForeground(QtGui.QColor(255,220,220))

    def switchEnvelope(self):
        scs = cmds.ls(type="skinCluster") or []
        if not scs:
            return
        all_zero = all(cmds.getAttr(s + ".envelope") == 0 for s in scs)
        new_val = 1 if all_zero else 0
        for s in scs:
            cmds.setAttr(s + ".envelope", new_val)

    def resetdagpose(self):
        nodes = cmds.ls(type="dagPose") or []
        if nodes:
            cmds.delete(nodes)
        cmds.dagPose(cmds.ls(), bindPose=True, save=True)

    def _copy_weights_per_vertex(self, source, target, skc_src, skc_tgt):
        v_src = cmds.polyEvaluate(source, v=True)
        v_tgt = cmds.polyEvaluate(target, v=True)
        if v_src != v_tgt:
            return False

        joints = cmds.skinCluster(skc_src, q=True, inf=True)
        tgt_infs = cmds.skinCluster(skc_tgt, q=True, inf=True)

        for j in joints:
            if j not in tgt_infs:
                cmds.skinCluster(skc_tgt, e=True, ai=j, lw=False, wt=0.0)

        for j in joints:
            for idx in range(v_src):
                vtx_s = f"{source}.vtx[{idx}]"
                vtx_t = f"{target}.vtx[{idx}]"
                try:
                    w = cmds.skinPercent(skc_src, vtx_s, q=True, t=j)
                except:
                    continue
                cmds.skinPercent(skc_tgt, vtx_t, transformValue=[(j, float(w))], normalize=False)

        cmds.skinPercent(skc_tgt, f"{target}.vtx[0:{v_tgt - 1}]", normalize=True)
        return True

    def copy_skin_weights(self, source, target):
        skc_src = None
        for n in cmds.listHistory(source) or []:
            if cmds.nodeType(n) == "skinCluster":
                skc_src = n
                break
        if not skc_src:
            return

        joints = cmds.skinCluster(skc_src, q=True, inf=True)

        for n in cmds.listHistory(target) or []:
            if cmds.nodeType(n) == "skinCluster":
                cmds.delete(n)

        cmds.skinCluster(joints, target, tsb=True)

        skc_tgt = None
        for n in cmds.listHistory(target) or []:
            if cmds.nodeType(n) == "skinCluster":
                skc_tgt = n
                break

        if self.cb_per_vertex.isChecked():
            ok = self._copy_weights_per_vertex(source, target, skc_src, skc_tgt)
            if ok:
                return

        cmds.copySkinWeights(
            source, target,
            noMirror=True,
            surfaceAssociation="closestPoint",
            influenceAssociation="oneToOne"
        )

    def process_pairs(self):
        self.mark_invalid_pairs()
        n = max(self.left_list.count(), self.right_list.count())
        for i in range(n):
            l = self.left_list.item(i)
            r = self.right_list.item(i)
            if not l or not r:
                continue
            if l.background().color().red() > 100:
                continue
            self.copy_skin_weights(l.text(), r.text())


def show_skin_weight_copier():
    app = QtWidgets.QApplication.instance()
    for w in app.allWidgets():
        if w.objectName() == "JCQ_SkinWeightCopier_UI":
            w.show()
            w.raise_()
            w.activateWindow()
            return w
    return SkinWeightCopier()


tool = show_skin_weight_copier()
