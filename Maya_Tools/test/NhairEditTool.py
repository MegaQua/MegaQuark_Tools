# -*- coding: utf-8 -*-
# NhairEditTool — nHair 列表 / 动态属性面板 / Replace Caches / 预设库(JSON单文件)
import os, json
import maya.cmds as cmds, maya.mel as mel
try:
    from PySide2 import QtCore, QtWidgets
    import shiboken2 as shiboken
except:
    from PySide6 import QtCore, QtWidgets
    import shiboken6 as shiboken


class NhairEditTool(QtWidgets.QDialog):
    _inst = None
    _WIN_OBJECT_NAME = "NhairEditToolWindow"
    _REPLACE_MEL = 'doCreateNclothCache 5 { "2","1","10","OneFilePerFrame","1","","0","","0","replace","0","1","1","0","1","mcx" };'
    # 首选目录与预设库文件名
    _PREFERRED_DIR = r"S:\Public\qiu_yi\JCQ_Tool\data"
    _PRESET_FILENAME = "NhairEditTool_presets.json"

    # ---------- lifecycle ----------
    @classmethod
    def show_unique(cls):
        app = QtWidgets.QApplication.instance()
        if app:
            for w in app.topLevelWidgets():
                try:
                    if w.objectName() == cls._WIN_OBJECT_NAME:
                        w.close(); w.deleteLater()
                except Exception:
                    pass
        if cls._inst:
            try: cls._inst.close(); cls._inst.deleteLater()
            except Exception: pass
            cls._inst = None

        cls._inst = cls(cls._maya_main_window())
        cls._inst.show(); cls._inst.raise_(); cls._inst.activateWindow()
        return cls._inst

    @staticmethod
    def _maya_main_window():
        try:
            import maya.OpenMayaUI as omui
            return shiboken.wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)
        except:
            return None

    # ---------- utils ----------
    @staticmethod
    def _short(n):
        s = n.split('|')[-1]; return s.split(':')[-1]

    @staticmethod
    def _all_hairsystems():
        hs = cmds.ls(type='hairSystem', long=True) or []
        seen, out = set(), []
        for n in hs:
            ln = (cmds.ls(n, long=True) or [n])[0]
            if ln not in seen: seen.add(ln); out.append(ln)
        return out

    @staticmethod
    def _connected_nucleus(hair):
        nodes = cmds.listConnections(hair, s=True, d=False) or []
        for n in nodes:
            if cmds.nodeType(n) == 'nucleus': return n
        for a in ('currentState','startState'):
            src = cmds.listConnections(f'{hair}.{a}', s=True, d=False) or []
            for n in src:
                if cmds.nodeType(n) == 'nucleus': return n
        return None

    @staticmethod
    def _timeline_start():
        return cmds.playbackOptions(q=True, min=True)

    @staticmethod
    def _attr_readable(plug):
        if not cmds.objExists(plug): return False
        try: cmds.getAttr(plug); return True
        except: return False

    @staticmethod
    def _set_attr(node, attr, v):
        plug = f'{node}.{attr}'
        if not cmds.objExists(plug): return False
        try:
            try:
                if cmds.getAttr(plug, l=True): cmds.setAttr(plug, l=False)
            except: pass
            if isinstance(v,bool): cmds.setAttr(plug, v)
            elif isinstance(v,int): cmds.setAttr(plug, int(v))
            elif isinstance(v,float): cmds.setAttr(plug, float(v))
            else:
                try: cmds.setAttr(plug, float(v))
                except: cmds.setAttr(plug, v, type='string')
            return True
        except: return False

    @staticmethod
    def _parent_transform(shape):
        p = cmds.listRelatives(shape, p=True, f=True) or []
        return p[0] if p else None

    # ---------- init ----------
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName(self._WIN_OBJECT_NAME)
        self.setWindowTitle("NhairEditTool")


        self._fields = {}
        self._is_custom = False
        self._last_loaded_node = None

        # 预设库：路径与可用性
        self._preset_dir = None
        self._preset_path = None
        self._presets_enabled = False
        self._preset_store = {"tool":"NhairEditTool","version":1,"presets":{}}  # name -> {attr:val}

        self._build_ui()
        self._wire()
        self._resolve_preset_dir_and_store()  # 目录与文件创建/加载/禁用逻辑
        self._refresh_list()
        self._set_header_none()
        self._refresh_presets_ui()

    # ---------- preset dir & store ----------
    def _resolve_preset_dir_and_store(self):
        # 1) 目标目录：优先固定路径，否则回退到“我的文档\NhairEditTool”
        target_dir = self._PREFERRED_DIR
        try:
            if not os.path.isdir(target_dir):
                os.makedirs(target_dir, exist_ok=True)
        except Exception:
            # 回退
            docs = os.path.join(os.path.expanduser("~"), "Documents")
            target_dir = os.path.join(docs, "NhairEditTool")
            try:
                if not os.path.isdir(target_dir):
                    os.makedirs(target_dir, exist_ok=True)
            except Exception:
                # 彻底失败，禁用预设功能
                self._preset_dir = None
                self._preset_path = None
                self._presets_enabled = False
                self._set_presets_enabled(False, why="Preset directory cannot be created.")
                return

        self._preset_dir = target_dir
        self._preset_path = os.path.join(self._preset_dir, self._PRESET_FILENAME)

        # 2) 预设库文件：没有就创建；失败则禁用
        if not os.path.isfile(self._preset_path):
            try:
                with open(self._preset_path, "w", encoding="utf-8") as f:
                    json.dump(self._preset_store, f, indent=2, ensure_ascii=False)
            except Exception as e:
                self._presets_enabled = False
                self._set_presets_enabled(False, why=f"Preset file cannot be created:\n{e}")
                return

        # 3) 读取库；失败则禁用
        try:
            with open(self._preset_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict) or "presets" not in data:
                raise ValueError("Bad preset store format.")
            self._preset_store = data
            self._presets_enabled = True
            self._set_presets_enabled(True)
        except Exception as e:
            self._presets_enabled = False
            self._set_presets_enabled(False, why=f"Preset file cannot be read:\n{e}")

    def _save_preset_store(self):
        if not (self._presets_enabled and self._preset_path):
            return False
        try:
            with open(self._preset_path, "w", encoding="utf-8") as f:
                json.dump(self._preset_store, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self._warn(f"Save preset store failed:\n{e}")
            return False

    def _set_presets_enabled(self, enabled, why=None):
        self.group_presets.setEnabled(bool(enabled))
        if not enabled and why:
            self._warn(why)

    # ---------- UI ----------
    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8); root.setSpacing(6)

        # 顶部按钮（顺序/文案按你要求）
        top = QtWidgets.QHBoxLayout()
        self.btn_refresh        = self._btn("Refresh List", 110)
        self.btn_select_tr      = self._btn("Select from scene", 140)
        self.btn_read_from_list = self._btn("Get values from select", 180)
        self.btn_apply_to_sel   = self._btn("Apply to Selected", 150)
        self.btn_replace        = self._btn("Replace Caches", 150); self.btn_replace.setStyleSheet("font-weight:700;")
        top.addWidget(self.btn_refresh); top.addWidget(self.btn_select_tr)
        top.addWidget(self.btn_read_from_list); top.addWidget(self.btn_apply_to_sel)
        top.addWidget(self.btn_replace); top.addStretch(1)
        root.addLayout(top)

        # 分栏
        self.split = QtWidgets.QSplitter(QtCore.Qt.Horizontal); self.split.setHandleWidth(6)

        # 左：列表
        left = QtWidgets.QWidget(); l_lay = QtWidgets.QVBoxLayout(left)
        l_lay.setContentsMargins(0,0,0,0); l_lay.setSpacing(0)
        lbl = QtWidgets.QLabel("hairSystems in Scene (shape nodes)")
        lbl.setStyleSheet("color:#aaa; padding:4px;")
        self.list_hs = QtWidgets.QListWidget()
        self.list_hs.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        l_lay.addWidget(lbl); l_lay.addWidget(self.list_hs)
        self.split.addWidget(left)

        # 右：预设区 + 属性区
        right = QtWidgets.QWidget(); r_lay = QtWidgets.QVBoxLayout(right)
        r_lay.setContentsMargins(0,0,0,0); r_lay.setSpacing(6)

        # Presets（改为下拉，数据来自单一 JSON）
        self.group_presets = QtWidgets.QGroupBox("Presets")
        presets_lay = QtWidgets.QGridLayout(self.group_presets)
        presets_lay.setContentsMargins(6,6,6,6); presets_lay.setHorizontalSpacing(6); presets_lay.setVerticalSpacing(4)

        self.preset_combo = QtWidgets.QComboBox()
        self.btn_preset_refresh = QtWidgets.QPushButton("Refresh")
        self.btn_preset_load    = QtWidgets.QPushButton("Load")
        self.btn_preset_save    = QtWidgets.QPushButton("Save Current")

        presets_lay.addWidget(QtWidgets.QLabel("Preset:"), 0, 0)
        presets_lay.addWidget(self.preset_combo,           0, 1, 1, 3)
        presets_lay.addWidget(self.btn_preset_refresh,     1, 1)
        presets_lay.addWidget(self.btn_preset_load,        1, 2)
        presets_lay.addWidget(self.btn_preset_save,        1, 3)

        r_lay.addWidget(self.group_presets)

        # Header + 属性区
        self.header = QtWidgets.QLabel("")  # none / loaded / custom
        r_lay.addWidget(self.header)

        self.scroll = QtWidgets.QScrollArea(); self.scroll.setWidgetResizable(True)
        self.inner  = QtWidgets.QWidget()
        self.form   = QtWidgets.QFormLayout(self.inner)
        self.form.setLabelAlignment(QtCore.Qt.AlignRight)
        self.form.setFormAlignment(QtCore.Qt.AlignTop)
        self.form.setHorizontalSpacing(10); self.form.setVerticalSpacing(4)
        self.scroll.setWidget(self.inner)
        r_lay.addWidget(self.scroll)

        self.status = QtWidgets.QLabel("Ready."); self.status.setStyleSheet("color:#6cf;")
        r_lay.addWidget(self.status)

        self.split.addWidget(right)
        self.split.setStretchFactor(0, 1); self.split.setStretchFactor(1, 2)
        self._tighten_scrollbar(self.split); self._tighten_scrollbar(self.scroll)
        root.addWidget(self.split)

    def _wire(self):
        self.btn_refresh.clicked.connect(self._refresh_list)
        self.btn_select_tr.clicked.connect(self._select_transforms_of_checked)
        self.btn_read_from_list.clicked.connect(self._read_from_list)
        self.btn_apply_to_sel.clicked.connect(self._apply_to_sel)
        self.btn_replace.clicked.connect(self._on_replace_caches)

        self.btn_preset_refresh.clicked.connect(self._refresh_presets_ui)
        self.btn_preset_load.clicked.connect(self._load_selected_preset_to_panel)
        self.btn_preset_save.clicked.connect(self._save_current_as_named_preset)

    # ---------- helpers (UI) ----------
    def _btn(self, text, minw=None):
        b = QtWidgets.QPushButton(text)

        b.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        return b

    def _tighten_scrollbar(self, widget):
        widget.setStyleSheet("QScrollBar:vertical { width:10px; } QScrollBar:horizontal { height:10px; }")

    def _warn(self, msg):
        self.status.setText(msg); self.status.setStyleSheet("color:#f66;")
        QtWidgets.QMessageBox.warning(self, "NhairEditTool", msg)

    def _info(self, msg):
        self.status.setText(msg); self.status.setStyleSheet("color:#6cf;")

    # ---------- header states ----------
    def _set_header_none(self):
        self.header.setText("Values: (none)"); self.header.setStyleSheet("font-weight:600; color:#999;")
        self._is_custom = False

    def _set_header_loaded(self):
        self.header.setText("Values: Loaded"); self.header.setStyleSheet("font-weight:600; color:#bbb;")
        self._is_custom = False

    def _set_header_custom(self):
        self.header.setText("Values: Custom"); self.header.setStyleSheet("font-weight:700; color:#f0a500;")
        self._is_custom = True

    # ---------- 列表 ----------
    def _refresh_list(self):
        self.list_hs.clear()
        for n in self._all_hairsystems():
            it = QtWidgets.QListWidgetItem(self._short(n)); it.setData(QtCore.Qt.UserRole, n)
            self.list_hs.addItem(it)
        self._info(f"Found {self.list_hs.count()} hairSystems.")

    def _select_transforms_of_checked(self):
        items = self.list_hs.selectedItems()
        if not items: return self._warn("Please select hairSystems in the list.")
        trans = []
        for it in items:
            shape = it.data(QtCore.Qt.UserRole)
            t = self._parent_transform(shape)
            if t: trans.append(t)
        if not trans: return self._warn("No parent transforms found.")
        try:
            cmds.select(trans, r=True); self._info(f"Selected {len(trans)} transform(s).")
        except Exception as e:
            self._warn(f"Select failed: {e}")

    # ---------- Replace Caches ----------
    def _on_replace_caches(self):
        items = self.list_hs.selectedItems()
        if not items: return self._warn("No hairSystem selected in the list.")
        nodes = [it.data(QtCore.Qt.UserRole) for it in items]

        tl = self._timeline_start(); bad = []
        for h in nodes:
            nuc = self._connected_nucleus(h)
            if not nuc: bad.append((h, 'no connected nucleus')); continue
            ns = cmds.getAttr(nuc + '.startFrame') if cmds.objExists(nuc + '.startFrame') else None
            if ns is None: bad.append((h, 'nucleus.startFrame missing')); continue
            if float(ns) != float(tl): bad.append((h, f'startFrame={ns} ≠ timelineMin={tl}'))
        if bad:
            msg = "Replace Caches aborted due to startFrame mismatch:\n\n" + "\n".join(f"- {self._short(h)} : {r}" for h,r in bad)
            return QtWidgets.QMessageBox.warning(self, "Start Frame Mismatch", msg)

        try: cmds.select(nodes, r=True)
        except: pass
        try:
            mel.eval(self._REPLACE_MEL); self._info("Replace Caches executed.")
        except Exception as e:
            self._warn(f"Replace Caches failed: {e}")

    # ---------- 动态属性 ----------
    def _clear_fields(self):
        while self.form.count():
            it = self.form.takeAt(0); w = it.widget()
            if w: w.deleteLater()
        self._fields.clear()

    def _make_field(self, val):
        def mark_custom():
            if not self._is_custom: self._set_header_custom()
        if isinstance(val, bool):
            w = QtWidgets.QCheckBox(); w.setChecked(val); w.setMaximumWidth(18); w.stateChanged.connect(mark_custom)
        elif isinstance(val, int):
            w = QtWidgets.QSpinBox(); w.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
            w.setRange(-999999, 999999); w.setValue(val); w.setMaximumWidth(120); w.valueChanged.connect(lambda *_: mark_custom())
        elif isinstance(val, float):
            w = QtWidgets.QDoubleSpinBox(); w.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
            w.setDecimals(6); w.setRange(-1e8, 1e8); w.setValue(val); w.setMaximumWidth(160); w.valueChanged.connect(lambda *_: mark_custom())
        else:
            w = QtWidgets.QLineEdit(str(val)); w.setMaximumWidth(220); w.textEdited.connect(lambda *_: mark_custom())
        return w

    def _build_fields_from_node(self, node):
        self._last_loaded_node = node
        self._clear_fields()
        attrs = cmds.listAttr(node, k=True) or []
        count = 0
        for a in attrs:
            plug = f"{node}.{a}"
            if not self._attr_readable(plug): continue
            try: val = cmds.getAttr(plug)
            except: continue
            if isinstance(val, (list, tuple)): continue
            w = self._make_field(val)
            lbl = QtWidgets.QLabel(a);
            self.form.addRow(lbl, w)
            self._fields[a] = w; count += 1
        self._set_header_loaded(); self._info(f"Loaded {count} attribute(s).")

    def _read_from_list(self):
        items = self.list_hs.selectedItems()
        if not items: return self._warn("Select at least one hairSystem in the list.")
        node = items[0].data(QtCore.Qt.UserRole)
        self._build_fields_from_node(node)

    def _apply_to_sel(self):
        sels = cmds.ls(sl=True, long=True) or []
        targets = []
        for n in sels:
            if cmds.nodeType(n) == 'hairSystem': targets.append(n)
            else:
                sh = cmds.listRelatives(n, s=True, ni=True, fullPath=True) or []
                targets += [s for s in sh if cmds.nodeType(s) == 'hairSystem']
        targets = list(dict.fromkeys(targets))
        if not targets: return self._warn("Select target hairSystem(s) in the scene (shape or transform).")

        changed = 0
        for node in targets:
            for a, w in self._fields.items():
                if isinstance(w, QtWidgets.QCheckBox): v = w.isChecked()
                elif isinstance(w, QtWidgets.QSpinBox): v = int(w.value())
                elif isinstance(w, QtWidgets.QDoubleSpinBox): v = float(w.value())
                else:
                    t = w.text()
                    try: v = float(t)
                    except: v = t
                if self._set_attr(node, a, v): changed += 1
        self._info(f"Applied to {len(targets)} node(s), wrote {changed} field(s).")

    # ---------- 预设：UI与读写（单一JSON库） ----------
    def _refresh_presets_ui(self):
        self.preset_combo.clear()
        if not self._presets_enabled:
            self.preset_combo.addItem("(presets disabled)")
            return
        names = sorted((self._preset_store.get("presets") or {}).keys())
        if not names:
            self.preset_combo.addItem("(no presets)")
        else:
            self.preset_combo.addItems(names)

    def _collect_current_values(self):
        data = {}
        for attr, w in self._fields.items():
            if isinstance(w, QtWidgets.QCheckBox):
                v = bool(w.isChecked())
            elif isinstance(w, QtWidgets.QSpinBox):
                v = int(w.value())
            elif isinstance(w, QtWidgets.QDoubleSpinBox):
                v = float(w.value())
            else:
                txt = w.text()
                try:
                    if "." in txt: v = float(txt)
                    else: v = int(txt)
                except: v = txt
            data[attr] = v
        return data

    def _save_current_as_named_preset(self):
        if not self._presets_enabled:
            return self._warn("Preset feature is disabled.")
        if not self._fields:
            return self._warn("No values to save. Load or edit attributes first.")

        # 默认名：最近载入节点名或左侧第一个选中项
        default_name = None
        if self._last_loaded_node:
            default_name = self._short(self._last_loaded_node)
        else:
            items = self.list_hs.selectedItems()
            if items:
                default_name = self._short(items[0].data(QtCore.Qt.UserRole))
        if not default_name:
            default_name = "nhair_preset"

        name, ok = QtWidgets.QInputDialog.getText(self, "Save Preset",
                                                  "Preset name:", QtWidgets.QLineEdit.Normal,
                                                  default_name)
        if not ok or not name.strip():
            return
        name = name.strip()

        # 覆盖确认
        presets = self._preset_store.get("presets", {})
        if name in presets:
            ret = QtWidgets.QMessageBox.question(self, "Overwrite?",
                                                 f"Preset '{name}' exists. Overwrite?",
                                                 QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                 QtWidgets.QMessageBox.No)
            if ret != QtWidgets.QMessageBox.Yes:
                return

        presets[name] = self._collect_current_values()
        self._preset_store["presets"] = presets
        if self._save_preset_store():
            self._info(f"Preset saved: {name}")
            self._refresh_presets_ui()
            # 自动选中刚保存的项
            idx = self.preset_combo.findText(name)
            if idx >= 0: self.preset_combo.setCurrentIndex(idx)

    def _load_selected_preset_to_panel(self):
        if not self._presets_enabled:
            return self._warn("Preset feature is disabled.")
        name = self.preset_combo.currentText().strip()
        if not name or name.startswith("("):
            return self._warn("No preset selected.")
        presets = self._preset_store.get("presets", {})
        data = presets.get(name, {})
        if not data:
            return self._warn(f"Preset '{name}' is empty or missing.")

        applied = 0
        for a, v in data.items():
            w = self._fields.get(a)
            if not w: continue
            try:
                if isinstance(w, QtWidgets.QCheckBox): w.setChecked(bool(v))
                elif isinstance(w, QtWidgets.QSpinBox): w.setValue(int(v))
                elif isinstance(w, QtWidgets.QDoubleSpinBox): w.setValue(float(v))
                else: w.setText(str(v))
                applied += 1
            except Exception:
                pass
        self._set_header_loaded()
        self._info(f"Preset loaded: {name} — filled {applied} field(s).")


# run
NhairEditTool.show_unique()
