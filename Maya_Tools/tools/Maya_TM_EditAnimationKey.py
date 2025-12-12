# -*- coding: utf-8 -*-
import maya.cmds as cmds
from PySide2 import QtWidgets, QtCore
from maya import OpenMayaUI as omui
import shiboken2

class _UndoChunk(object):
    def __init__(self, name="TM_EditAnimationKey"):
        self.name = name
    def __enter__(self):
        try:
            cmds.undoInfo(openChunk=True)
        except Exception:
            pass
    def __exit__(self, exc_type, exc, tb):
        try:
            cmds.undoInfo(closeChunk=True)
        except Exception:
            pass

class TMEditAnimationKey(QtWidgets.QDialog):
    def __init__(self, parent=None):
        if not parent:
            ptr = omui.MQtUtil.mainWindow()
            parent = shiboken2.wrapInstance(int(ptr), QtWidgets.QWidget)
        super(TMEditAnimationKey, self).__init__(parent)

        self.setWindowTitle("TM_Edit Animation Key ver 0.9")
        self.setObjectName("TM_EditAnimationKey")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        # 内存中的关键帧集合：{name: {curve: [times...]}}
        self.key_sets = {}

        self.build_ui()

    def build_ui(self):
        root = QtWidgets.QVBoxLayout(self)

        self.tabs = QtWidgets.QTabWidget(self)
        self.build_move_tab()
        self.build_scale_tab()   # 更新：小写“mode”
        self.build_reverse_tab()

        root.addWidget(self.tabs)

        # ===== 独立面板：Keyframe Sets & 选择操作 =====
        sets_box = QtWidgets.QGroupBox("Key Sets")
        vb = QtWidgets.QVBoxLayout(sets_box)

        # 保存/应用行
        row1 = QtWidgets.QHBoxLayout()
        self.btn_save_set = QtWidgets.QPushButton("Save key set")
        self.btn_save_set.clicked.connect(self.on_save_key_set)
        row1.addWidget(self.btn_save_set)

        row1.addWidget(QtWidgets.QLabel("Saved:"))
        self.combo_sets = QtWidgets.QComboBox()
        row1.addWidget(self.combo_sets)

        self.chk_append = QtWidgets.QCheckBox("Append select")
        self.chk_append.setChecked(False)  # 默认单独选择
        row1.addWidget(self.chk_append)

        self.btn_apply_set = QtWidgets.QPushButton("select set")
        self.btn_apply_set.clicked.connect(self.on_apply_key_set)
        row1.addWidget(self.btn_apply_set)

        row1.addStretch(1)
        vb.addLayout(row1)

        # 关键帧选择操作
        row2 = QtWidgets.QHBoxLayout()
        self.btn_select_ops = QtWidgets.QPushButton("key Select SP")
        self.btn_select_ops.clicked.connect(self.on_select_ops_execute)
        row2.addWidget(self.btn_select_ops)

        self.combo_select_ops = QtWidgets.QComboBox()
        self.combo_select_ops.addItems([
            "①: keep left one key",
            "②: keep right one key",
            "③: right add one key",
            "④: left add one key",
        ])

        row2.addWidget(self.combo_select_ops)
        row2.addStretch(1)
        vb.addLayout(row2)

        root.addWidget(sets_box)
    # ================= Move =================
    def build_move_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)

        value_layout = QtWidgets.QHBoxLayout()
        value_layout.addWidget(QtWidgets.QLabel("Value"))
        self.move_value = QtWidgets.QDoubleSpinBox()
        self.move_value.setRange(0, 10000)
        self.move_value.setValue(1)
        self.move_value.setDecimals(3)
        value_layout.addWidget(self.move_value)
        reset_btn = QtWidgets.QPushButton("0")
        reset_btn.setMaximumWidth(30)
        reset_btn.clicked.connect(lambda: self.move_value.setValue(0))
        value_layout.addWidget(reset_btn)
        layout.addLayout(value_layout)

        quick_values = [100, 10, 1, 0.1, 0.01]
        quick_layout = QtWidgets.QHBoxLayout()
        quick_layout.addWidget(QtWidgets.QLabel("Quick Add:"))
        for val in quick_values:
            btn = QtWidgets.QPushButton(str(val))
            btn.setMaximumWidth(30)
            btn.clicked.connect(self.make_value_adder(val))
            quick_layout.addWidget(btn)
        layout.addLayout(quick_layout)

        btn_layout = QtWidgets.QGridLayout()
        btn_layout.addWidget(QtWidgets.QLabel(""), 0, 0)
        btn_layout.addWidget(self.create_btn("Up",   lambda: self.move_animation_key("Up",   self.move_value.value())), 0, 1)
        btn_layout.addWidget(QtWidgets.QLabel(""), 0, 2)
        btn_layout.addWidget(self.create_btn("Left", lambda: self.move_animation_key("Left", self.move_value.value())), 1, 0)
        btn_layout.addWidget(self.create_btn("Down", lambda: self.move_animation_key("Down", self.move_value.value())), 1, 1)
        btn_layout.addWidget(self.create_btn("Right",lambda: self.move_animation_key("Right",self.move_value.value())), 1, 2)
        layout.addLayout(btn_layout)

        #layout.addWidget(self.create_btn("Close", self.close))
        self.tabs.addTab(tab, "Move")

    def move_animation_key(self, move_type, move_value):
        with _UndoChunk("Move Keys"):
            if move_type == "Up":
                cmds.keyframe(e=True, iub=True, animation='keys', r=True, o='over', vc=move_value)
            elif move_type == "Down":
                cmds.keyframe(e=True, iub=True, animation='keys', r=True, o='over', vc=-move_value)
            elif move_type == "Right":
                cmds.keyframe(e=True, iub=True, animation='keys', r=True, o='move', timeChange=move_value)
            elif move_type == "Left":
                cmds.keyframe(e=True, iub=True, animation='keys', r=True, o='move', timeChange=-move_value)

    def make_value_adder(self, val):
        return lambda checked=False, v=val: self.move_value.setValue(self.move_value.value() + v)

    def make_value_setter(self, val):
        return lambda checked=False, v=val: self.move_value.setValue(v)

    # ================= Scale（小写“mode” + 单一执行按钮） =================
    def build_scale_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)

        mode_row = QtWidgets.QHBoxLayout()
        mode_row.addWidget(QtWidgets.QLabel("mode"))
        self.scale_mode = QtWidgets.QComboBox()
        self.scale_mode.addItems([
            "① Time (with pivot)",
            "② Value (with pivot)",
            "③ curve root base (keep left)",
            "④ curve root base (keep right)",
        ])
        self.scale_mode.setCurrentIndex(0)
        mode_row.addWidget(self.scale_mode)
        layout.addLayout(mode_row)

        # Pivot/Scale 参数
        piv_row = QtWidgets.QHBoxLayout()
        self.time_pivot = QtWidgets.QDoubleSpinBox(); self.time_pivot.setDecimals(3); self.time_pivot.setRange(-1e12, 1e12)
        self.value_pivot = QtWidgets.QDoubleSpinBox(); self.value_pivot.setDecimals(3); self.value_pivot.setRange(-1e12, 1e12)
        piv_row.addWidget(QtWidgets.QLabel("Time Pivot"))
        piv_row.addWidget(self.time_pivot)
        piv_row.addWidget(QtWidgets.QLabel("Value Pivot"))
        piv_row.addWidget(self.value_pivot)
        layout.addLayout(piv_row)

        scale_row = QtWidgets.QHBoxLayout()
        scale_row.addWidget(QtWidgets.QLabel("Scale"))
        self.scale_value = QtWidgets.QDoubleSpinBox()
        self.scale_value.setRange(-1000, 10000)
        self.scale_value.setDecimals(3)
        self.scale_value.setValue(1.0)
        scale_row.addWidget(self.scale_value)
        layout.addLayout(scale_row)

        quick_values = [1.5, 1.1, 1, 0.9, 0.5, 0.1]
        quick_layout = QtWidgets.QHBoxLayout()
        quick_layout.addWidget(QtWidgets.QLabel("Quick Set:"))
        for val in quick_values:
            btn = QtWidgets.QPushButton(str(val))
            btn.setMaximumWidth(40)
            btn.clicked.connect(self.make_scale_setter(val))
            quick_layout.addWidget(btn)
        layout.addLayout(quick_layout)

        # 单一执行按钮
        layout.addWidget(self.create_btn("Scale", self.execute_scale))

        self.tabs.addTab(tab, "Scale")

    def make_scale_setter(self, val):
        return lambda checked=False, v=val: self.scale_value.setValue(v)

    def execute_scale(self):
        with _UndoChunk("Scale Keys"):
            mode = self.scale_mode.currentIndex()
            s = self.scale_value.value()
            if mode == 0:
                self.scale_animation_key("TimeScale", self.time_pivot.value(), s)
            elif mode == 1:
                self.scale_animation_key("ValueScale", self.value_pivot.value(), s)
            elif mode == 2:
                self._time_scale_by_per_curve_anchor(scale=s, use_left=True)
            elif mode == 3:
                self._time_scale_by_per_curve_anchor(scale=s, use_left=False)

    def scale_animation_key(self, scale_type, pivot, value):
        if scale_type == "ValueScale":
            cmds.scaleKey(scaleSpecifiedKeys=True, valueScale=value, valuePivot=pivot)
        elif scale_type == "TimeScale":
            cmds.scaleKey(scaleSpecifiedKeys=True, timeScale=value, timePivot=pivot)

    # --- 每条曲线锚点缩放（仅作用于所选关键帧） ---
    def _time_scale_by_per_curve_anchor(self, scale=1.0, use_left=True):
        """
        仅缩放“所选关键帧”：
        - 每条曲线以所选最左( use_left=True ) / 最右( use_left=False )关键为 pivot
        - 仅缩放 pivot 一侧、且被选中的关键帧；未选中的不动
        - 不足2个已选关键则跳过该曲线
        """
        curves = cmds.keyframe(q=True, sl=True, name=True) or []
        if not curves:
            return
        eps = 1e-8
        unique = sorted(set(curves))

        cmds.undoInfo(openChunk=True)
        try:
            for crv in unique:
                sel_times = cmds.keyframe(crv, q=True, sl=True, tc=True) or []
                if len(sel_times) < 2:
                    continue

                pivot = min(sel_times) if use_left else max(sel_times)
                if use_left:
                    targets = [t for t in sel_times if t > pivot + eps]
                else:
                    targets = [t for t in sel_times if t < pivot - eps]

                if not targets:
                    continue

                # 扩张(>1)先移动离pivot更远的，收缩(<1)从近到远，降低碰撞概率
                targets.sort(key=lambda t: abs(t - pivot), reverse=(scale >= 1.0))

                for t in targets:
                    new_t = pivot + (t - pivot) * float(scale)
                    if abs(new_t - t) < eps:
                        continue
                    # 仅精确命中该时间点的关键帧
                    cmds.keyframe(crv, e=True, time=(t, t), timeChange=new_t)
        finally:
            cmds.undoInfo(closeChunk=True)

    # ================= Reverse =================
    def build_reverse_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)

        self.reverse_pivot = QtWidgets.QDoubleSpinBox()
        self.reverse_pivot.setRange(-1000, 10000)
        layout.addWidget(QtWidgets.QLabel("Pivot"))
        layout.addWidget(self.reverse_pivot)

        reverse_btn_layout = QtWidgets.QHBoxLayout()
        reverse_btn_layout.addWidget(self.create_btn("Time Reverse", self.on_reverse_time))
        reverse_btn_layout.addWidget(self.create_btn("Value Reverse", self.on_reverse_value))
        layout.addLayout(reverse_btn_layout)

        offset_up_layout = QtWidgets.QHBoxLayout()
        offset_up_layout.addWidget(QtWidgets.QLabel("Move Up:"))
        offset_up_layout.addWidget(self.create_btn("+180", lambda: self.move_animation_key("Up", 180)))
        offset_up_layout.addWidget(self.create_btn("+360", lambda: self.move_animation_key("Up", 360)))
        layout.addLayout(offset_up_layout)

        offset_down_layout = QtWidgets.QHBoxLayout()
        offset_down_layout.addWidget(QtWidgets.QLabel("Move Down:"))
        offset_down_layout.addWidget(self.create_btn("-180", lambda: self.move_animation_key("Down", 180)))
        offset_down_layout.addWidget(self.create_btn("-360", lambda: self.move_animation_key("Down", 360)))
        layout.addLayout(offset_down_layout)

        self.tabs.addTab(tab, "Reverse")

    def on_reverse_time(self):
        with _UndoChunk("Reverse Time"):
            self.reverse_animation_key("TimeReverse", self.reverse_pivot.value())

    def on_reverse_value(self):
        with _UndoChunk("Reverse Value"):
            self.reverse_animation_key("ValueReverse", self.reverse_pivot.value())

    def reverse_animation_key(self, reverse_type, pivot):
        if reverse_type == "ValueReverse":
            cmds.scaleKey(scaleSpecifiedKeys=True, valueScale=-1, valuePivot=pivot)
        elif reverse_type == "TimeReverse":
            cmds.scaleKey(scaleSpecifiedKeys=True, timeScale=-1, timePivot=pivot)

    # ================== Keyframe Sets & 选择操作 ==================
    def _collect_selected_keys_per_curve(self):
        """返回 {curve: sorted_times}，并附带当前选中曲线列表。"""
        curve_names = cmds.keyframe(q=True, sl=True, name=True) or []
        data = {}
        for crv in set(curve_names):
            times = cmds.keyframe(crv, q=True, sl=True, tc=True) or []
            if times:
                data[crv] = sorted(set(times))
        # 把曲线集合一并返回
        return {"curves": sorted(set(curve_names)), "keys": data}

    def _apply_key_set(self, data, append=False):
        """应用关键帧集合（包含曲线）。append=False 时清空当前选择。"""
        if not data:
            return

        curves = data.get("curves", [])
        keys = data.get("keys", {})

        if not append:
            try:
                cmds.select(cl=True)
                cmds.selectKey(clear=True)
            except Exception:
                pass

        # 先选中曲线节点
        if curves:
            try:
                if append:
                    cmds.select(curves, add=True)
                else:
                    cmds.select(curves, r=True)
            except Exception:
                pass

        # 再选中关键帧
        for crv, times in keys.items():
            for t in times:
                cmds.selectKey(crv, time=(t, t), add=True)

    def _next_unused_set_name(self):
        i = 1
        existing = set(self.key_sets.keys())
        while True:
            name = "set{}".format(i)
            if name not in existing:
                return name
            i += 1

    def on_save_key_set(self):
        # 保存只是内存状态，不包 undo（不影响场景），可以按需改
        data = self._collect_selected_keys_per_curve()
        if not data:
            QtWidgets.QMessageBox.information(self, "Info", "未检测到被选择的关键帧。")
            return
        default_name = self._next_unused_set_name()
        name, ok = QtWidgets.QInputDialog.getText(self, "Save keyframe set", "Name:", text=default_name)
        if not ok or not name.strip():
            return
        name = name.strip()
        self.key_sets[name] = data
        if self.combo_sets.findText(name) == -1:
            self.combo_sets.addItem(name)
        self.combo_sets.setCurrentText(name)

    def on_apply_key_set(self):
        with _UndoChunk("Apply Keyframe Set"):
            name = self.combo_sets.currentText()
            if not name or name not in self.key_sets:
                return
            self._apply_key_set(self.key_sets[name], append=self.chk_append.isChecked())

    def on_select_ops_execute(self):
        with _UndoChunk("Keyframe Select Ops"):
            op = self.combo_select_ops.currentIndex()
            data = self._collect_selected_keys_per_curve()
            if not data:
                return

            if op == 0:
                # keep left
                new_data = {crv: [min(ts)] for crv, ts in data.items() if ts}
                self._apply_key_set(new_data, append=False)

            elif op == 1:
                # keep right
                new_data = {crv: [max(ts)] for crv, ts in data.items() if ts}
                self._apply_key_set(new_data, append=False)

            elif op == 2:
                # right add 1 key：每曲线在当前最右选择之后追加一个
                for crv, sel_ts in data.items():
                    all_ts = cmds.keyframe(crv, q=True, tc=True) or []
                    if not all_ts:
                        continue
                    sel_right = max(sel_ts)
                    candidates = sorted(t for t in set(all_ts) if t > sel_right)
                    if candidates:
                        cmds.selectKey(crv, time=(candidates[0], candidates[0]), add=True)

            elif op == 3:
                # left add 1 key：每曲线在当前最左选择之前追加一个
                for crv, sel_ts in data.items():
                    all_ts = cmds.keyframe(crv, q=True, tc=True) or []
                    if not all_ts:
                        continue
                    sel_left = min(sel_ts)
                    candidates = sorted((t for t in set(all_ts) if t < sel_left))
                    if candidates:
                        left_neighbor = candidates[-1]
                        cmds.selectKey(crv, time=(left_neighbor, left_neighbor), add=True)

    # ================= Utils =================
    def create_btn(self, label, command):
        btn = QtWidgets.QPushButton(label)
        btn.clicked.connect(command)
        return btn

# === 唤起窗口（保证唯一） ===
for w in QtWidgets.QApplication.allWidgets():
    if w.objectName() == "TM_EditAnimationKey":
        w.close()
        w.deleteLater()

TMEditAnimationKey = TMEditAnimationKey()
TMEditAnimationKey.show()
