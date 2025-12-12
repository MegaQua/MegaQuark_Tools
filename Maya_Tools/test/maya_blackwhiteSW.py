# -*- coding: utf-8 -*-
import maya.cmds as cmds
from PySide2 import QtWidgets, QtCore

class BWTool(QtWidgets.QWidget):
    """材质黑白控制工具（类封装版，尝试式 + 上游扫描）"""

    def __init__(self):
        super(BWTool, self).__init__()
        self.setWindowTitle(u"材质黑白控制工具")
        self.resize(760, 480)

        # ===== 可扩展：材质类型 → 颜色属性名 =====
        self.material_color_map = {
            "lambert": ["color", "Color"],
            "blinn": ["color"],
            "phong": ["color"],
            "phongE": ["color"],
            "aiStandardSurface": ["baseColor"],
        }

        # ===== 常量 =====
        self.ctrl_name = "BW_Controller"
        self.ctrl_attr = "bwBlend"
        self.mark_attr = "bwProcessed"

        # ===== UI =====
        main = QtWidgets.QHBoxLayout(self)

        # 未处理
        left = QtWidgets.QVBoxLayout()
        left.addWidget(QtWidgets.QLabel(u"未处理（支持类型 & 无标记）"))
        self.list_un = QtWidgets.QListWidget()
        self.list_un.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        left.addWidget(self.list_un)

        # 中间按钮
        mid = QtWidgets.QVBoxLayout()
        self.btn_refresh = QtWidgets.QPushButton(u"刷新")
        self.btn_proc = QtWidgets.QPushButton(u"→ 处理所选")
        self.btn_unproc = QtWidgets.QPushButton(u"← 逆向所选")
        self.btn_fix = QtWidgets.QPushButton(u"修复控制器")
        mid.addWidget(self.btn_refresh)
        mid.addSpacing(8)
        mid.addWidget(self.btn_proc)
        mid.addWidget(self.btn_unproc)
        mid.addSpacing(8)
        mid.addWidget(self.btn_fix)
        mid.addStretch()

        # 已处理
        right = QtWidgets.QVBoxLayout()
        right.addWidget(QtWidgets.QLabel(u"已处理（有标记）"))
        self.list_pr = QtWidgets.QListWidget()
        self.list_pr.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        right.addWidget(self.list_pr)

        main.addLayout(left, 1)
        main.addLayout(mid)
        main.addLayout(right, 1)

        # 事件
        self.btn_refresh.clicked.connect(self.refresh_lists)
        self.btn_proc.clicked.connect(self._on_process)
        self.btn_unproc.clicked.connect(self._on_unprocess)
        self.btn_fix.clicked.connect(self.ensure_ctrl)

        self.refresh_lists()

    # ===== 基础 =====
    def ensure_ctrl(self):
        if not cmds.objExists(self.ctrl_name):
            ctrl = cmds.createNode("transform", name=self.ctrl_name)
            cmds.addAttr(ctrl, ln=self.ctrl_attr, at="double", min=0, max=1, dv=0, k=True)
        elif not cmds.attributeQuery(self.ctrl_attr, node=self.ctrl_name, exists=True):
            cmds.addAttr(self.ctrl_name, ln=self.ctrl_attr, at="double", min=0, max=1, dv=0, k=True)
        return "{}.{}".format(self.ctrl_name, self.ctrl_attr)

    def color_plug_of(self, mat):
        t = cmds.nodeType(mat)
        for a in self.material_color_map.get(t, []):
            p = "{}.{}".format(mat, a)
            if cmds.objExists(p):
                return p
        return None

    def is_processed(self, mat):
        return cmds.attributeQuery(self.mark_attr, node=mat, exists=True)

    def set_flag(self, mat, v=True):
        if not cmds.attributeQuery(self.mark_attr, node=mat, exists=True):
            cmds.addAttr(mat, ln=self.mark_attr, at="bool")
        cmds.setAttr("{}.{}".format(mat, self.mark_attr), bool(v))

    # ===== 上游扫描 =====
    def find_incoming_to(self, node, target_plug):
        if not cmds.objExists(node) or not cmds.objExists(target_plug):
            return None
        nodes = cmds.listHistory(node, pruneDagObjects=True) or []
        nodes = sorted(set(nodes + [node]))
        for n in [node] + [x for x in nodes if x != node]:
            pairs = cmds.listConnections(n, s=True, d=False, p=True, c=True) or []
            for i in range(0, len(pairs), 2):
                dest_plug = pairs[i]
                src_plug  = pairs[i + 1]
                if dest_plug == target_plug:
                    return src_plug
        return None

    # ===== 列表收集 =====
    def materials_by_state(self):
        un, pr = [], []
        mats = []
        for t in self.material_color_map.keys():
            mats.extend(cmds.ls(type=t) or [])
        for m in sorted(set(mats)):
            if self.is_processed(m):
                pr.append(m)
            else:
                un.append(m)
        return un, pr

    def refresh_lists(self):
        self.list_un.clear()
        self.list_pr.clear()
        un, pr = self.materials_by_state()
        self.list_un.addItems(un)
        self.list_pr.addItems(pr)

    # ===== 处理 =====
    def process_one(self, mat):
        cplug = self.color_plug_of(mat)
        if not cplug:
            print(u"[跳过] {}：无颜色属性".format(mat)); return False
        src_plug = self.find_incoming_to(mat, cplug)
        if not src_plug:
            print(u"[跳过] {}：颜色口无来线".format(mat)); return False

        ctrl_attr = self.ensure_ctrl()
        prefix = mat + "_bw"
        lum = cmds.shadingNode("luminance", asUtility=True, name=prefix + "Lum")
        blend = cmds.shadingNode("blendColors", asUtility=True, name=prefix + "Blend")

        cmds.connectAttr(src_plug, blend + ".color1", f=True)
        src_node = src_plug.split(".")[0]
        if cmds.objExists(src_node + ".outColor"):
            cmds.connectAttr(src_node + ".outColor", lum + ".value", f=True)
        else:
            cmds.connectAttr(src_plug, lum + ".value", f=True)
        for ch in "RGB":
            cmds.connectAttr(lum + ".outValue", "{}.color2{}".format(blend, ch), f=True)
        cmds.connectAttr(ctrl_attr, blend + ".blender", f=True)

        try: cmds.disconnectAttr(src_plug, cplug)
        except: pass
        cmds.connectAttr(blend + ".output", cplug, f=True)

        self.set_flag(mat, True)
        print(u"[OK] 已处理：{}".format(mat))
        return True

    # ===== 逆向 =====
    def unprocess_one(self, mat):
        cplug = self.color_plug_of(mat)
        if not cplug:
            if self.is_processed(mat):
                try: cmds.deleteAttr("{}.{}".format(mat, self.mark_attr))
                except: pass
            return False
        src_plug = self.find_incoming_to(mat, cplug)
        if not src_plug:
            if self.is_processed(mat):
                try: cmds.deleteAttr("{}.{}".format(mat, self.mark_attr))
                except: pass
            return False
        blend = src_plug.split(".")[0]
        if cmds.nodeType(blend) != "blendColors":
            if self.is_processed(mat):
                try: cmds.deleteAttr("{}.{}".format(mat, self.mark_attr))
                except: pass
            return False

        orig_src = cmds.listConnections(blend + ".color1", s=True, d=False, p=True)
        lum_in = cmds.listConnections(blend + ".color2R", s=True, d=False, p=True)
        lum = lum_in[0].split(".")[0] if lum_in else None
        try: cmds.disconnectAttr(src_plug, cplug)
        except: pass
        if orig_src:
            cmds.connectAttr(orig_src[0], cplug, f=True)
        if lum and cmds.objExists(lum): cmds.delete(lum)
        if cmds.objExists(blend): cmds.delete(blend)
        try: cmds.deleteAttr("{}.{}".format(mat, self.mark_attr))
        except: pass
        print(u"[OK] 已逆向：{}".format(mat))
        return True

    # ===== UI handlers =====
    def _on_process(self):
        items = self.list_un.selectedItems()
        if not items: return
        cmds.undoInfo(openChunk=True)
        try:
            for it in items:
                self.process_one(it.text())
        finally:
            cmds.undoInfo(closeChunk=True)
        self.refresh_lists()

    def _on_unprocess(self):
        items = self.list_pr.selectedItems()
        if not items: return
        cmds.undoInfo(openChunk=True)
        try:
            for it in items:
                self.unprocess_one(it.text())
        finally:
            cmds.undoInfo(closeChunk=True)
        self.refresh_lists()

    # ===== 启动窗口 =====
    @classmethod
    def show_window(cls):
        try:
            cls._win.close()
        except:
            pass
        cls._win = BWTool()
        cls._win.show()
        return cls._win


# 运行
BWTool.show_window()
