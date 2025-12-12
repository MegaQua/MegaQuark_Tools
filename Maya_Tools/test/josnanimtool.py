# -*- coding: utf-8 -*-
# Maya TR per-frame exporter/importer with simple UI (PySide2)
# 说明：UI英文；代码注释中文且简短

import json
import os
import maya.cmds as cmds
from PySide2 import QtWidgets, QtCore

# ===== 小工具 =====
def long_name(n):
    """取长名；不存在返回None"""
    if not cmds.objExists(n):
        return None
    return cmds.ls(n, l=True)[0]

def short_name(n):
    """短名"""
    return n.split('|')[-1]

def is_locked_attr(node, attr):
    """判断属性是否锁定"""
    plug = f"{node}.{attr}"
    return cmds.getAttr(plug, l=True) if cmds.objExists(plug) else True

def playback_range_int():
    """返回当前播放范围（整数帧，含端点）"""
    start = int(round(cmds.playbackOptions(q=True, minTime=True)))
    end   = int(round(cmds.playbackOptions(q=True, maxTime=True)))
    if end < start:
        start, end = end, start
    return start, end

def ensure_dir(path):
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d)

def find_match(name_in_json, prefer_short=False):
    """按名称在场景中寻找对象
    prefer_short=True 时用短名匹配（第一个命中返回）
    """
    if prefer_short:
        target_short = short_name(name_in_json)
        cands = cmds.ls(target_short, l=True) or []
        return cands[0] if cands else None
    # 先按长名精确
    if cmds.objExists(name_in_json):
        return long_name(name_in_json)
    # 退化为短名匹配
    cands = cmds.ls(short_name(name_in_json), l=True) or []
    return cands[0] if cands else None

# ===== 主窗口 =====
class TR_IO_Window(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(TR_IO_Window, self).__init__(parent)
        self.setWindowTitle("TR Export / Import (per-frame JSON)")
        self.setMinimumWidth(420)

        tabs = QtWidgets.QTabWidget(self)

        # --- Export tab ---
        tab_export = QtWidgets.QWidget()
        v1 = QtWidgets.QVBoxLayout(tab_export)

        self.sel_label = QtWidgets.QLabel("Selected Objects: 0")
        self.range_label = QtWidgets.QLabel("Playback Range: -")
        btn_refresh = QtWidgets.QPushButton("Refresh Selection && Range")
        btn_refresh.clicked.connect(self._refresh_status)

        self.cb_export_shortname = QtWidgets.QCheckBox("Store short names instead of long DAG paths")
        self.cb_export_shortname.setChecked(False)

        self.cb_sample_step = QtWidgets.QSpinBox()
        self.cb_sample_step.setMinimum(1)
        self.cb_sample_step.setMaximum(1000)
        self.cb_sample_step.setValue(1)
        self.cb_sample_step.setSuffix(" frame(s)")
        step_row = self._hrow("Sampling step:", self.cb_sample_step)

        self.btn_export = QtWidgets.QPushButton("Export TR to JSON")
        self.btn_export.clicked.connect(self._on_export)

        v1.addWidget(self.sel_label)
        v1.addWidget(self.range_label)
        v1.addWidget(btn_refresh)
        v1.addWidget(self.cb_export_shortname)
        v1.addLayout(step_row)
        v1.addStretch(1)
        v1.addWidget(self.btn_export)

        # --- Import tab ---
        tab_import = QtWidgets.QWidget()
        v2 = QtWidgets.QVBoxLayout(tab_import)

        self.ed_json_path = QtWidgets.QLineEdit()
        self.ed_json_path.setReadOnly(True)
        btn_browse = QtWidgets.QPushButton("Browse JSON...")
        btn_browse.clicked.connect(self._on_browse)

        row_file = QtWidgets.QHBoxLayout()
        row_file.addWidget(self.ed_json_path, 1)
        row_file.addWidget(btn_browse)

        self.cb_match_short = QtWidgets.QCheckBox("Prefer short-name matching")
        self.cb_match_short.setChecked(False)

        self.cb_skip_locked = QtWidgets.QCheckBox("Skip locked attributes on import")
        self.cb_skip_locked.setChecked(True)

        self.cb_apply_ro = QtWidgets.QCheckBox("Apply recorded rotateOrder before import")
        self.cb_apply_ro.setChecked(True)

        self.cb_set_keys = QtWidgets.QCheckBox("Set keyframes while importing")
        self.cb_set_keys.setChecked(True)

        self.btn_import = QtWidgets.QPushButton("Import from JSON")
        self.btn_import.clicked.connect(self._on_import)

        v2.addLayout(row_file)
        v2.addWidget(self.cb_match_short)
        v2.addWidget(self.cb_skip_locked)
        v2.addWidget(self.cb_apply_ro)
        v2.addWidget(self.cb_set_keys)
        v2.addStretch(1)
        v2.addWidget(self.btn_import)

        tabs.addTab(tab_export, "Export")
        tabs.addTab(tab_import, "Import")

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(tabs)

        self._refresh_status()

    # —— UI 辅助 ——
    def _hrow(self, label_text, widget):
        lab = QtWidgets.QLabel(label_text)
        row = QtWidgets.QHBoxLayout()
        row.addWidget(lab)
        row.addWidget(widget, 1)
        return row

    def _refresh_status(self):
        sel = cmds.ls(sl=True, l=True) or []
        self.sel_label.setText("Selected Objects: {}".format(len(sel)))
        s, e = playback_range_int()
        self.range_label.setText("Playback Range: {} .. {}".format(s, e))

    # —— Export 逻辑 ——
    def _on_export(self):
        sel = cmds.ls(sl=True, l=True) or []
        if not sel:
            cmds.warning(u"[Export] No objects selected.")
            return

        start, end = playback_range_int()
        step = max(1, int(self.cb_sample_step.value()))
        name_mode_short = self.cb_export_shortname.isChecked()

        # 选择文件
        out_path = cmds.fileDialog2(fileMode=0, caption="Save JSON", fileFilter="JSON (*.json)")
        if not out_path:
            return
        out_path = out_path[0]
        ensure_dir(out_path)

        # 采样
        data = {
            "frame_start": start,
            "frame_end": end,
            "step": step,
            "objects": {},
            "meta": {
                "version": "1.0",
                "stored_name": "short" if name_mode_short else "long",
            }
        }

        # 记录每个对象 rotateOrder
        ro_map = {}
        for o in sel:
            ro_map[o] = cmds.getAttr(o + ".rotateOrder")
        data["rotateOrder"] = { (short_name(o) if name_mode_short else long_name(o)): ro_map[o] for o in sel }

        frames = list(range(start, end + 1, step))
        total_ops = len(sel) * len(frames)
        print("[Export] Objects: {}, Frames: {}, Step: {}, Total samples: {}".format(len(sel), len(frames), step, total_ops))

        for o in sel:
            key = short_name(o) if name_mode_short else long_name(o)
            rec_t = []
            rec_r = []
            for f in frames:
                cmds.currentTime(f, edit=True)
                tx = cmds.getAttr(o + ".translateX")
                ty = cmds.getAttr(o + ".translateY")
                tz = cmds.getAttr(o + ".translateZ")
                rx = cmds.getAttr(o + ".rotateX")
                ry = cmds.getAttr(o + ".rotateY")
                rz = cmds.getAttr(o + ".rotateZ")
                rec_t.append([tx, ty, tz])
                rec_r.append([rx, ry, rz])
            data["objects"][key] = {"t": rec_t, "r": rec_r}

        # 写文件
        with open(out_path, "w") as f:
            json.dump(data, f, indent=2)
        print(u"[Export] Done → {}".format(out_path))
        QtWidgets.QMessageBox.information(self, "Export", "Export completed:\n{}".format(out_path))

    # —— Import 逻辑 ——
    def _on_browse(self):
        paths = cmds.fileDialog2(fileMode=1, caption="Open JSON", fileFilter="JSON (*.json)")
        if not paths:
            return
        self.ed_json_path.setText(paths[0])

    def _on_import(self):
        path = self.ed_json_path.text().strip()
        if not path or not os.path.isfile(path):
            cmds.warning(u"[Import] Please choose a valid JSON file.")
            return

        with open(path, "r") as f:
            data = json.load(f)

        objs = data.get("objects", {})
        if not objs:
            cmds.warning(u"[Import] No objects in JSON.")
            return

        start = int(data.get("frame_start", playback_range_int()[0]))
        end   = int(data.get("frame_end", playback_range_int()[1]))
        step  = int(data.get("step", 1))
        frames = list(range(start, end + 1, step))

        prefer_short = self.cb_match_short.isChecked()
        skip_locked  = self.cb_skip_locked.isChecked()
        apply_ro     = self.cb_apply_ro.isChecked()
        set_keys     = self.cb_set_keys.isChecked()

        # 尝试恢复 rotateOrder
        ro_map = data.get("rotateOrder", {})
        if apply_ro and ro_map:
            for json_name, ro in ro_map.items():
                scene_node = find_match(json_name, prefer_short=prefer_short)
                if scene_node and cmds.objExists(scene_node + ".rotateOrder"):
                    try:
                        cmds.setAttr(scene_node + ".rotateOrder", int(ro))
                    except Exception as e:
                        print("[Import][rotateOrder] Skip {}: {}".format(scene_node, e))

        print("[Import] Objects in JSON:", len(objs))
        print("[Import] Frames: {}..{} step {}".format(start, end, step))

        # 导入每帧TR并可选打关键帧
        for json_name, rec in objs.items():
            scene_node = find_match(json_name, prefer_short=prefer_short)
            if not scene_node:
                print("[Import] Not found in scene ->", json_name)
                continue

            t_list = rec.get("t", [])
            r_list = rec.get("r", [])
            if len(t_list) != len(frames) or len(r_list) != len(frames):
                print("[Import] Frame count mismatch for", json_name)
                continue

            # 属性列表
            attrs_t = ["translateX", "translateY", "translateZ"]
            attrs_r = ["rotateX", "rotateY", "rotateZ"]

            # 锁定过滤
            locked_t = [is_locked_attr(scene_node, a) for a in attrs_t] if skip_locked else [False, False, False]
            locked_r = [is_locked_attr(scene_node, a) for a in attrs_r] if skip_locked else [False, False, False]

            for idx, f in enumerate(frames):
                cmds.currentTime(f, edit=True)

                # set T
                for i, a in enumerate(attrs_t):
                    if not locked_t[i]:
                        try:
                            cmds.setAttr("{}.{}".format(scene_node, a), float(t_list[idx][i]))
                        except Exception as e:
                            print("[Import][T] {}.{} @ {} -> {}".format(scene_node, a, f, e))

                # set R
                for i, a in enumerate(attrs_r):
                    if not locked_r[i]:
                        try:
                            cmds.setAttr("{}.{}".format(scene_node, a), float(r_list[idx][i]))
                        except Exception as e:
                            print("[Import][R] {}.{} @ {} -> {}".format(scene_node, a, f, e))

                if set_keys:
                    try:
                        cmds.setKeyframe(scene_node, at=attrs_t + attrs_r, t=(f,))
                    except Exception as e:
                        print("[Import][Key] {} @ {} -> {}".format(scene_node, f, e))

        QtWidgets.QMessageBox.information(self, "Import", "Import completed:\n{}".format(path))
        print("[Import] Done.")

# ===== 入口函数 =====
def show_tr_io_window():
    """显示窗口（单例）"""
    global _TR_IO_WIN
    try:
        _TR_IO_WIN.close()
        _TR_IO_WIN.deleteLater()
    except:
        pass
    _TR_IO_WIN = TR_IO_Window()
    _TR_IO_WIN.show()

# 直接运行
if __name__ == "__main__":
    show_tr_io_window()
