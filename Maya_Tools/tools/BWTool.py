# -*- coding: utf-8 -*-
import maya.cmds as cmds
from PySide2 import QtWidgets, QtCore
import re

class BWTool(QtWidgets.QWidget):
    """B/W + Binary tool (unified controller; per-material brightness; final monochrome override)"""

    # ===== config =====
    MATERIAL_COLOR_MAP = {
        "lambert": ["color", "Color"],
        "blinn": ["color"],
        "phong": ["color"],
        "phongE": ["color"],
        "aiStandardSurface": ["baseColor"],
    }

    # Controller attrs (identified by hidden enum tag; no name dependency)
    TAG_ATTR   = "bwControllerTag"
    TAG_ENUM   = "BW_CTRL"

    # Ordered main attrs: Base Color, Monochrome, Threshold, Binarize
    ATTR_BASE  = "baseColor"   # 0..1 original vs processed
    ATTR_MONO  = "monochrome"  # 0..1 color -> final grayscale (1=BW, 0=unchanged)
    ATTR_THR   = "threshold"   # 0..1 binary threshold
    ATTR_BIN   = "binarize"    # 0..1 grayscale vs binary (0 gray, 1 binary)

    ATTR_SEP   = "sep"         # visual separator (displayable)
    SEP_TEXT   = "__________________________________"

    PER_MAT_PREFIX = "brightness__"  # per-material brightness (double, no range)
    MARK_ATTR = "bwProcessed"

    def __init__(self):
        super(BWTool, self).__init__()
        self.setObjectName("BWTool_UniqueWindow")
        self.setWindowTitle("B/W & Binary Material Tool")
        self.resize(820, 520)

        main = QtWidgets.QHBoxLayout(self)

        left = QtWidgets.QVBoxLayout()
        left.addWidget(QtWidgets.QLabel("Unprocessed (supported types & no mark)"))
        self.list_un = QtWidgets.QListWidget()
        self.list_un.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        left.addWidget(self.list_un)

        mid = QtWidgets.QVBoxLayout()
        self.btn_refresh = QtWidgets.QPushButton("Refresh")
        self.btn_proc    = QtWidgets.QPushButton("→ Process Selected")
        self.btn_unproc  = QtWidgets.QPushButton("← Revert Selected")
        self.btn_fix     = QtWidgets.QPushButton("Fix/Find Controller")
        mid.addWidget(self.btn_refresh)
        mid.addSpacing(8)
        mid.addWidget(self.btn_proc)
        mid.addWidget(self.btn_unproc)
        mid.addSpacing(8)
        mid.addWidget(self.btn_fix)
        mid.addStretch()

        right = QtWidgets.QVBoxLayout()
        right.addWidget(QtWidgets.QLabel("Processed (has mark)"))
        self.list_pr = QtWidgets.QListWidget()
        self.list_pr.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        right.addWidget(self.list_pr)

        main.addLayout(left, 1)
        main.addLayout(mid)
        main.addLayout(right, 1)

        self.btn_refresh.clicked.connect(self.refresh_lists)
        self.btn_proc.clicked.connect(self._on_process)
        self.btn_unproc.clicked.connect(self._on_unprocess)
        self.btn_fix.clicked.connect(self.ensure_ctrl)

        self.refresh_lists()

    # ===== helpers =====
    @staticmethod
    def _short(n): return n.split('|')[-1]
    @staticmethod
    def _has_attr(n, a): return cmds.attributeQuery(a, n=n, exists=True)

    @classmethod
    def _sanitize_attr(cls, name):
        s = cls._short(name)
        s = re.sub(r'[:|\s]+', '_', s)
        s = re.sub(r'[^A-Za-z0-9_]', '_', s)
        if re.match(r'^\d', s): s = '_' + s
        return s

    # ===== controller =====
    def find_ctrl(self):
        for t in (cmds.ls(type='transform') or []):
            if self._has_attr(t, self.TAG_ATTR):
                try:
                    if cmds.addAttr(f'{t}.{self.TAG_ATTR}', q=True, at=True) == 'enum':
                        enums = cmds.addAttr(f'{t}.{self.TAG_ATTR}', q=True, enumName=True) or ""
                        if self.TAG_ENUM in enums.split(':'):
                            return t
                except:
                    pass
        return None

    def ensure_ctrl(self):
        ctrl = self.find_ctrl() or cmds.createNode("transform", name="BW_Controller#")

        def _add_double(n, ln, dv, mn=None, mx=None, keyable=True, cb=None):
            if not self._has_attr(n, ln):
                kw = dict(ln=ln, at='double', dv=dv, k=keyable)
                if mn is not None: kw['min'] = mn
                if mx is not None: kw['max'] = mx
                cmds.addAttr(n, **kw)
                if cb is not None:
                    cmds.setAttr(f"{n}.{ln}", e=True, cb=cb)

        # hidden tag
        if not self._has_attr(ctrl, self.TAG_ATTR):
            cmds.addAttr(ctrl, ln=self.TAG_ATTR, at='enum', enumName=self.TAG_ENUM, k=False)
        # hide tag (not keyable, not in CB, locked)
        try:
            cmds.setAttr(f"{ctrl}.{self.TAG_ATTR}", e=True, k=False, cb=False)
            cmds.setAttr(f"{ctrl}.{self.TAG_ATTR}", l=True)
        except: pass

        # --- add in required order: Base Color, Monochrome, Threshold, Binarize ---
        _add_double(ctrl, self.ATTR_BASE, 0.0, 0.0, 1.0, keyable=True)   # 0 original — 1 processed
        _add_double(ctrl, self.ATTR_MONO, 0.0, 0.0, 1.0, keyable=True)   # 0 unchanged — 1 grayscale (final)
        _add_double(ctrl, self.ATTR_THR,  0.5, 0.0, 1.0, keyable=True)   # threshold
        _add_double(ctrl, self.ATTR_BIN,  0.0, 0.0, 1.0, keyable=True)   # 0 gray — 1 binary

        # separator as displayable (channelBox-only)
        if not self._has_attr(ctrl, self.ATTR_SEP):
            cmds.addAttr(ctrl, ln=self.ATTR_SEP, at='enum', enumName=self.SEP_TEXT, k=False)
        try:
            cmds.setAttr(f"{ctrl}.{self.ATTR_SEP}", e=True, k=False, cb=True)  # displayable
        except: pass

        # lock TRSV
        for a in ('tx','ty','tz','rx','ry','rz','sx','sy','sz','v'):
            try: cmds.setAttr(f'{ctrl}.{a}', l=True, k=False, cb=False)
            except: pass
        try:
            cmds.setAttr(ctrl + '.overrideEnabled', 1)
            cmds.setAttr(ctrl + '.overrideDisplayType', 2)
        except: pass
        return ctrl

    def per_mat_brightness_attr(self, ctrl, mat):
        suffix = self._sanitize_attr(mat)
        attr = self.PER_MAT_PREFIX + suffix
        if not self._has_attr(ctrl, attr):
            cmds.addAttr(ctrl, ln=attr, at='double', dv=1.0, k=True)  # no range
        return f'{ctrl}.{attr}'

    # ===== material queries =====
    def color_plug_of(self, mat):
        t = cmds.nodeType(mat)
        for a in self.MATERIAL_COLOR_MAP.get(t, []):
            p = f'{mat}.{a}'
            if cmds.objExists(p): return p
        return None

    def is_processed(self, mat):
        return cmds.attributeQuery(self.MARK_ATTR, node=mat, exists=True)

    def set_flag(self, mat, v=True):
        if not cmds.attributeQuery(self.MARK_ATTR, node=mat, exists=True):
            cmds.addAttr(mat, ln=self.MARK_ATTR, at="bool")
        cmds.setAttr(f"{mat}.{self.MARK_ATTR}", bool(v))

    def incoming_src_plug(self, dest_plug):
        cons = cmds.listConnections(dest_plug, s=True, d=False, p=True) or []
        return cons[0] if cons else None

    def lock_attrs(self, node, attrs):
        for a in attrs:
            try: cmds.setAttr(f'{node}.{a}', l=True, k=False, cb=False)
            except: pass

    # ===== listing =====
    def materials_by_state(self):
        un, pr, mats = [], [], []
        for t in self.MATERIAL_COLOR_MAP.keys():
            mats.extend(cmds.ls(type=t) or [])
        for m in sorted(set(mats)):
            (pr if self.is_processed(m) else un).append(m)
        return un, pr

    def refresh_lists(self):
        self.list_un.clear(); self.list_pr.clear()
        un, pr = self.materials_by_state()
        self.list_un.addItems(un); self.list_pr.addItems(pr)

    # ===== build network =====
    def process_one(self, mat):
        cplug = self.color_plug_of(mat)
        if not cplug:
            print("[Skip]", mat, ": no color attribute"); return False
        src_plug = self.incoming_src_plug(cplug)
        if not src_plug:
            print("[Skip]", mat, ": color has no upstream"); return False

        ctrl = self.ensure_ctrl()
        A_base = f'{ctrl}.{self.ATTR_BASE}'
        A_mono = f'{ctrl}.{self.ATTR_MONO}'
        A_thr  = f'{ctrl}.{self.ATTR_THR}'
        A_bin  = f'{ctrl}.{self.ATTR_BIN}'
        A_bri  = self.per_mat_brightness_attr(ctrl, mat)

        base   = mat + "_bw"
        lum    = cmds.shadingNode("luminance",       asUtility=True, name=base + "_Lum")
        mul    = cmds.shadingNode("multiplyDivide",  asUtility=True, name=base + "_Mul")     # brightness
        cond   = cmds.shadingNode("condition",       asUtility=True, name=base + "_Cond")    # binary
        bMode  = cmds.shadingNode("blendColors",     asUtility=True, name=base + "_BlendMode")   # gray vs binary
        bFin   = cmds.shadingNode("blendColors",     asUtility=True, name=base + "_BlendFinal")  # original vs processed
        finLum = cmds.shadingNode("luminance",       asUtility=True, name=base + "_FinalLum")    # final luminance
        bMono  = cmds.shadingNode("blendColors",     asUtility=True, name=base + "_BlendMono")   # final color vs grayscale

        # condition: GT -> white/black
        cmds.setAttr(cond + ".operation", 2)
        for ch in "RGB":
            cmds.setAttr(f"{cond}.colorIfTrue{ch}", 1)
            cmds.setAttr(f"{cond}.colorIfFalse{ch}", 0)

        # disconnect original
        try: cmds.disconnectAttr(src_plug, cplug)
        except: pass

        # original -> final blend color1
        cmds.connectAttr(src_plug, bFin + ".color1", f=True)

        # src -> luminance
        src_node = src_plug.split(".")[0]
        if cmds.objExists(src_node + ".outColor"):
            cmds.connectAttr(src_node + ".outColor", lum + ".value", f=True)
        else:
            cmds.connectAttr(src_plug, lum + ".value", f=True)

        # luminance * brightness -> mul.outputX
        cmds.connectAttr(lum + ".outValue", mul + ".input1X", f=True)
        cmds.connectAttr(A_bri,             mul + ".input2X", f=True)

        # gray path -> bMode.color1 (RGB from mul.outputX)
        for ch in "RGB":
            cmds.connectAttr(mul + ".outputX", f"{bMode}.color1{ch}", f=True)

        # binary path from mul.outputX vs threshold
        cmds.connectAttr(mul + ".outputX", cond + ".firstTerm", f=True)
        cmds.connectAttr(A_thr,            cond + ".secondTerm", f=True)

        # gray vs binary
        cmds.connectAttr(cond + ".outColor", bMode + ".color2", f=True)
        cmds.connectAttr(A_bin,             bMode + ".blender", f=True)

        # processed vs original
        cmds.connectAttr(bMode + ".output", bFin + ".color2", f=True)
        cmds.connectAttr(A_base,            bFin + ".blender", f=True)

        # === final monochrome override (independent; 1=BW, 0=unchanged) ===
        cmds.connectAttr(bFin + ".output", finLum + ".value", f=True)
        cmds.connectAttr(bFin + ".output", bMono + ".color1", f=True)         # unchanged color
        for ch in "RGB":
            cmds.connectAttr(finLum + ".outValue", f"{bMono}.color2{ch}", f=True)  # grayscale
        cmds.connectAttr(A_mono, bMono + ".blender", f=True)

        # back to material
        cmds.connectAttr(bMono + ".output", cplug, f=True)

        # locks
        self.lock_attrs(lum,    ['nodeState'])
        self.lock_attrs(mul,    ['nodeState','input1Y','input1Z','input2Y','input2Z','operation'])
        self.lock_attrs(cond,   ['nodeState','colorIfTrueR','colorIfTrueG','colorIfTrueB',
                                 'colorIfFalseR','colorIfFalseG','colorIfFalseB','operation'])
        self.lock_attrs(bMode,  ['nodeState'])
        self.lock_attrs(bFin,   ['nodeState'])
        self.lock_attrs(finLum, ['nodeState'])
        self.lock_attrs(bMono,  ['nodeState'])

        self.set_flag(mat, True)
        print("[OK] Processed:", mat)
        return True

    def unprocess_one(self, mat):
        cplug = self.color_plug_of(mat)
        if not cplug:
            if self.is_processed(mat):
                try: cmds.deleteAttr(f"{mat}.{self.MARK_ATTR}")
                except: pass
            return False

        src_plug = self.incoming_src_plug(cplug)  # should be bMono.output
        if not src_plug:
            if self.is_processed(mat):
                try: cmds.deleteAttr(f"{mat}.{self.MARK_ATTR}")
                except: pass
            return False

        bMono = src_plug.split(".")[0]
        if cmds.nodeType(bMono) != "blendColors":
            if self.is_processed(mat):
                try: cmds.deleteAttr(f"{mat}.{self.MARK_ATTR}")
                except: pass
            return False

        bFin_in  = cmds.listConnections(bMono + ".color1", s=True, d=False, p=True)
        bFin     = bFin_in[0].split(".")[0] if bFin_in else None
        finLum_in= cmds.listConnections(bMono + ".color2R", s=True, d=False, p=True)
        finLum   = finLum_in[0].split(".")[0] if finLum_in else None

        orig_src = cmds.listConnections(bFin + ".color1", s=True, d=False, p=True) if bFin else None
        bMode_in = cmds.listConnections(bFin + ".color2", s=True, d=False, p=True) if bFin else None
        bMode    = bMode_in[0].split(".")[0] if bMode_in else None
        mul_in   = cmds.listConnections(bMode + ".color1R", s=True, d=False, p=True) if bMode else None
        mul      = mul_in[0].split(".")[0] if mul_in else None
        cond_in  = cmds.listConnections(bMode + ".color2", s=True, d=False, p=True) if bMode else None
        cond     = cond_in[0].split(".")[0] if cond_in else None
        lum_in   = cmds.listConnections(mul + ".input1X", s=True, d=False, p=True) if mul else None
        lum      = lum_in[0].split(".")[0] if lum_in else None

        try: cmds.disconnectAttr(src_plug, cplug)
        except: pass
        if orig_src:
            cmds.connectAttr(orig_src[0], cplug, f=True)

        for n in (bMono, finLum, bFin, bMode, cond, mul, lum):
            if n and cmds.objExists(n):
                try: cmds.delete(n)
                except: pass

        try: cmds.deleteAttr(f"{mat}.{self.MARK_ATTR}")
        except: pass

        print("[OK] Reverted:", mat)
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

    # ===== single-instance window =====
    @classmethod
    def show_window(cls):
        for w in QtWidgets.QApplication.topLevelWidgets():
            if isinstance(w, BWTool) or w.objectName() == "BWTool_UniqueWindow":
                try: w.close()
                except: pass
        cls._win = BWTool()
        cls._win.show()
        return cls._win


# Run
BWTool.show_window()
