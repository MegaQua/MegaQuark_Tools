# -*- coding: utf-8 -*-
# MotionBuilder 2023+ - HumanIK Pin Presets Tool (PySide2)
#
# Auto-saves presets to:
#   <User Documents>/MB/<MobuVersion>/config/hik_pin_presets.json
#
# - 智能识别 namespace（GetOwnerNamespace + 名字拆分）
# - JSON 带版本号，版本不匹配时自动丢弃旧数据
# - 仅对当前角色上“实际存在”的 Effector 做 Pin 读写
# - 窗口挂在 Mobu 主窗口下：在 Mobu 前置时浮在其上，切到别的软件时不会置顶

import os
import json

from pyfbsdk import FBSystem, FBEffectorId, FBGetMainWindow
from PySide2 import QtWidgets, QtCore
import shiboken2


# ===== DB 版本 =====
DB_VERSION = 2


# ===== Auto preset path =====
def get_mobu_user_config_path():
    """自动定位用户的 MotionBuilder config 目录."""
    try:
        ver = FBSystem().ApplicationVersion  # e.g., 2023.0.0.0
        ver_year = str(ver)[:4]
    except:
        ver_year = "2023"  # fallback

    documents = os.path.join(os.path.expanduser("~"), "Documents")
    config_dir = os.path.join(documents, "MB", ver_year, "config")

    try:
        os.makedirs(config_dir, exist_ok=True)
    except:
        pass

    return os.path.join(config_dir, "hik_pin_presets.json")


PRESET_FILE = get_mobu_user_config_path()


# ===== 获取 Mobu 主窗口 =====
def get_main_window():
    """返回 MotionBuilder 主窗口对应的 QWidget."""
    try:
        ptr = FBGetMainWindow()
    except:
        return None
    if not ptr:
        return None
    try:
        return shiboken2.wrapInstance(ptr, QtWidgets.QWidget)
    except:
        return None


# ===== Namespace / Character 工具 =====
def split_namespace(name):
    """返回 (namespace, base_name)，尽量规避双重 namespace."""
    if not name:
        return "", ""
    parts = name.split(":")
    if len(parts) <= 1:
        return "", name
    ns = ":".join(parts[:-1])
    base = parts[-1]
    return ns, base


def get_namespace(comp):
    """优先用 OwnerNamespace，失败再从名字拆 ':'."""
    if comp is None:
        return ""
    ns = ""
    try:
        ns_obj = comp.GetOwnerNamespace()
        if ns_obj and ns_obj.Name:
            ns = ns_obj.Name
    except:
        ns = ""

    if ns:
        return ns

    # fallback：从名字解析
    name = getattr(comp, "LongName", "") or getattr(comp, "Name", "")
    ns, _ = split_namespace(name)
    return ns


def get_characters():
    try:
        return list(FBSystem().Scene.Characters)
    except:
        return []


def get_character_by_name(name):
    try:
        for c in get_characters():
            if c.Name == name:
                return c
    except:
        pass
    return None


def get_char_key(char):
    """用 LongName 作为 key，尽量包含 namespace 信息."""
    try:
        ln = char.LongName
        if ln:
            return ln
    except:
        pass
    return char.Name


# ===== Effector 映射 =====
def _build_effector_table():
    """构造 {label -> eff_id} 映射，label 例如 'Hips'、'LeftWrist' 等."""
    table = {}
    for attr in dir(FBEffectorId):
        if not attr.startswith("kFB"):
            continue
        if attr in ("kFBInvalidEffectorId", "kFBLastEffectorId"):
            continue

        eff_id = getattr(FBEffectorId, attr)
        label = attr
        if label.startswith("kFB"):
            label = label[3:]
        if label.endswith("EffectorId"):
            label = label[:-10]
        table[label] = eff_id
    return table


EFF_TABLE = _build_effector_table()


# ===== Pin 读写：基于 Character + FBEffectorId =====
def collect_pin_data(char):
    """
    返回 (pins, controllers)

    pins: {
        "Hips": {"t": True/False, "r": True/False},
        ...
    }

    controllers: {
        "Hips": {
            "model_name": str,
            "model_long": str,
            "namespace": str
        },
        ...
    }

    仅收集“当前角色上实际存在 EffectorModel”的项。
    """
    pins = {}
    ctrls = {}

    if not char:
        return pins, ctrls

    for label, eff_id in EFF_TABLE.items():
        try:
            mdl = char.GetEffectorModel(eff_id)
        except:
            mdl = None

        # 没有对应模型，说明这个 effector 在当前角色上无效，跳过
        if not mdl:
            continue

        # 控制器信息（带 namespace）
        try:
            mdl_ns = get_namespace(mdl)
        except:
            mdl_ns = ""

        mdl_name = getattr(mdl, "Name", "")
        mdl_long = getattr(mdl, "LongName", "") or mdl_name
        ctrls[label] = {
            "model_name": mdl_name,
            "model_long": mdl_long,
            "namespace": mdl_ns,
        }

        # 当前 pin 状态
        try:
            t_pin = bool(char.IsTranslationPin(eff_id))
        except:
            t_pin = False
        try:
            r_pin = bool(char.IsRotationPin(eff_id))
        except:
            r_pin = False

        pins[label] = {"t": t_pin, "r": r_pin}

    return pins, ctrls


def apply_pin_states(char, pins):
    """根据 pins 字典设置当前角色的 pin 状态（仅作用于存在的 effector）。"""
    if not char or not pins:
        return

    for label, state in pins.items():
        eff_id = EFF_TABLE.get(label)
        if eff_id is None:
            continue

        try:
            mdl = char.GetEffectorModel(eff_id)
        except:
            mdl = None
        if not mdl:
            continue

        t_pin = bool(state.get("t", False))
        r_pin = bool(state.get("r", False))
        try:
            char.SetTranslationPin(eff_id, t_pin)
        except:
            pass
        try:
            char.SetRotationPin(eff_id, r_pin)
        except:
            pass


def clear_all_pins(char):
    """将当前角色上所有存在的 Effector 的 pin 全部关闭。"""
    if not char:
        return

    for label, eff_id in EFF_TABLE.items():
        try:
            mdl = char.GetEffectorModel(eff_id)
        except:
            mdl = None
        if not mdl:
            continue
        try:
            char.SetTranslationPin(eff_id, False)
        except:
            pass
        try:
            char.SetRotationPin(eff_id, False)
        except:
            pass


# ===== DB 读写 =====
def empty_db():
    return {"_version": DB_VERSION, "characters": {}}


def load_db():
    try:
        if not os.path.exists(PRESET_FILE):
            return empty_db()

        with open(PRESET_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 版本不一致，丢弃旧数据
        if data.get("_version") != DB_VERSION or "characters" not in data:
            return empty_db()

        return data
    except:
        return empty_db()


def save_db(db):
    try:
        if not isinstance(db, dict):
            db = empty_db()

        db["_version"] = DB_VERSION
        if "characters" not in db:
            db["characters"] = {}

        with open(PRESET_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
    except:
        pass


def get_or_create_char_entry(db, char):
    """
    返回 db 中当前角色的 entry:
    {
        "char_name": "...",   # 带 namespace 的名字
        "base_name": "...",   # 去 namespace 的短名
        "namespace": "...",
        "controllers": {...}, # 最新一次采集到的 effector 控制器信息
        "presets": [...]
    }
    """
    if not char:
        return None

    chars = db.setdefault("characters", {})
    key = get_char_key(char)

    entry = chars.get(key)
    if entry is None:
        ns = get_namespace(char)
        _, base = split_namespace(char.Name)
        entry = {
            "char_name": char.Name,
            "base_name": base,
            "namespace": ns,
            "controllers": {},
            "presets": [],
        }
        chars[key] = entry

    return entry


# ===== UI =====
class PinPresetTool(QtWidgets.QDialog):
    def __init__(self, parent=None):
        # 让对话框挂在 Mobu 主窗口下面
        super().__init__(parent)

        self.setWindowTitle("HumanIK Pin Presets")
        self.resize(380, 300)

        # 去掉问号按钮，不使用 AlwaysOnTop
        flags = self.windowFlags()
        flags &= ~QtCore.Qt.WindowContextHelpButtonHint
        self.setWindowFlags(flags)

        self.db = empty_db()
        self._build_ui()
        self.reload_all()

    # ---------------- UI ----------------
    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Character row
        top = QtWidgets.QHBoxLayout()
        top.addWidget(QtWidgets.QLabel("Character"))

        self.combo_char = QtWidgets.QComboBox()
        top.addWidget(self.combo_char, 1)

        self.btn_refresh = QtWidgets.QPushButton("Reload")
        self.btn_refresh.setFixedWidth(70)
        top.addWidget(self.btn_refresh)

        layout.addLayout(top)

        # Preset list
        layout.addWidget(QtWidgets.QLabel("Presets"))

        self.list_presets = QtWidgets.QListWidget()
        self.list_presets.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        layout.addWidget(self.list_presets, 1)

        # Bottom buttons
        btns = QtWidgets.QHBoxLayout()

        self.btn_save = QtWidgets.QPushButton("Save Set")
        self.btn_update = QtWidgets.QPushButton("Overwrite set")
        self.btn_clear = QtWidgets.QPushButton("Clear Chr Pins")
        self.btn_delete = QtWidgets.QPushButton("Delete set")

        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_update)
        btns.addWidget(self.btn_clear)
        btns.addWidget(self.btn_delete)
        btns.addStretch(1)

        layout.addLayout(btns)

        # Signals
        self.btn_refresh.clicked.connect(self.reload_all)
        self.combo_char.currentIndexChanged.connect(self._refresh_presets)
        self.btn_save.clicked.connect(self.on_save)
        self.btn_update.clicked.connect(self.on_update)
        self.btn_clear.clicked.connect(self.on_clear_all)
        self.btn_delete.clicked.connect(self.on_delete)
        self.list_presets.itemDoubleClicked.connect(self.on_apply)

    # ---------------- Data ----------------
    def reload_all(self):
        try:
            self.db = load_db()
            self._refresh_characters()
            self._refresh_presets()
        except:
            pass

    def _refresh_characters(self):
        try:
            self.combo_char.blockSignals(True)
            self.combo_char.clear()
            for c in get_characters():
                # 这里直接显示角色的 Name（一般已带 namespace）
                self.combo_char.addItem(c.Name)
        except:
            pass
        finally:
            self.combo_char.blockSignals(False)

    def _current_char(self):
        try:
            name = self.combo_char.currentText()
            if not name:
                return None
            return get_character_by_name(name)
        except:
            return None

    def _current_char_entry(self):
        char = self._current_char()
        if not char:
            return None
        return get_or_create_char_entry(self.db, char)

    def _refresh_presets(self):
        self.list_presets.clear()

        try:
            char = self._current_char()
            if not char or not isinstance(self.db, dict):
                return

            chars = self.db.get("characters", {})
            key = get_char_key(char)
            entry = chars.get(key)
            if not entry:
                return

            preset_list = entry.get("presets", [])
            for i, preset in enumerate(preset_list):
                label = preset.get("label", "Preset %d" % (i + 1))
                item = QtWidgets.QListWidgetItem(label)
                item.setData(QtCore.Qt.UserRole, i)
                self.list_presets.addItem(item)
        except:
            pass

    # ---------------- Actions ----------------
    def on_save(self):
        try:
            char = self._current_char()
            if not char:
                return

            pins, ctrls = collect_pin_data(char)
            if not pins:
                # 没有任何可 pin 控制器
                return

            text, ok = QtWidgets.QInputDialog.getText(self, "Save Preset", "Name")
            if not ok:
                return

            label = (text or "").strip() or "Preset"

            entry = get_or_create_char_entry(self.db, char)
            if entry is None:
                return

            # 更新 controllers 信息为当前场景实际可 pin 控制器
            entry["controllers"] = ctrls

            preset_list = entry.setdefault("presets", [])
            preset_list.append({"label": label, "pins": pins})

            save_db(self.db)
            self._refresh_presets()
        except:
            pass

    def on_update(self):
        """Overwrite selected preset."""
        try:
            char = self._current_char()
            if not char:
                return

            item = self.list_presets.currentItem()
            if not item:
                return

            idx = item.data(QtCore.Qt.UserRole)

            entry = self._current_char_entry()
            if not entry:
                return

            preset_list = entry.get("presets", [])
            if idx < 0 or idx >= len(preset_list):
                return

            pins, ctrls = collect_pin_data(char)
            if not pins:
                return

            # 覆盖 pins，并刷新 controllers 信息
            preset_list[idx]["pins"] = pins
            entry["controllers"] = ctrls

            save_db(self.db)
        except:
            pass

    def on_apply(self, *args):
        try:
            char = self._current_char()
            if not char:
                return

            item = self.list_presets.currentItem()
            if not item:
                return

            idx = item.data(QtCore.Qt.UserRole)

            entry = self._current_char_entry()
            if not entry:
                return

            preset_list = entry.get("presets", [])
            if idx < 0 or idx >= len(preset_list):
                return

            pins = preset_list[idx].get("pins", {})
            apply_pin_states(char, pins)
        except:
            pass

    def on_clear_all(self):
        try:
            char = self._current_char()
            if not char:
                return
            clear_all_pins(char)
        except:
            pass

    def on_delete(self):
        try:
            char = self._current_char()
            if not char:
                return

            item = self.list_presets.currentItem()
            if not item:
                return

            idx = item.data(QtCore.Qt.UserRole)

            entry = self._current_char_entry()
            if not entry:
                return

            preset_list = entry.get("presets", [])
            if idx < 0 or idx >= len(preset_list):
                return

            preset_list.pop(idx)
            save_db(self.db)
            self._refresh_presets()
        except:
            pass


# ===== Entry =====
g_pin_tools = []


def show_tool():
    parent = get_main_window()
    try:
        dlg = PinPresetTool(parent)
        dlg.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        dlg.show()
        g_pin_tools.append(dlg)
        return dlg
    except:
        return None


show_tool()
