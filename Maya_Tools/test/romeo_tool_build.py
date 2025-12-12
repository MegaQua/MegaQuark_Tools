# ==== Retarget FBX to Metahuman Controls (handles existing animation) ====
from PySide2 import QtWidgets, QtGui, QtCore
import maya.cmds as cmds
import maya.mel as mel
import os, re
import time

try:
    import metahuman_api as mh_api
except Exception as e:
    mh_api = None
    _mh_api_import_error = str(e)
else:
    _mh_api_import_error = ""



class RomeoTool(QtWidgets.QWidget):
    def __init__(self):
        super(RomeoTool, self).__init__(None)

        self.setWindowTitle("RomeoTool")
        self.tabs = QtWidgets.QTabWidget()

        # === Tab: Retarget FBX ===
        tab = QtWidgets.QWidget()
        self.tabs.addTab(tab, "Facial")

        # Namespace row
        ns_label = QtWidgets.QLabel("Namespace:")
        self.ns_combo = QtWidgets.QComboBox()
        self.btn_refresh_ns = QtWidgets.QPushButton("⟳")
        self.btn_select_ctrls = QtWidgets.QPushButton("Select Face Controls")
        self.btn_select_ctrls_zero = QtWidgets.QPushButton("zero Controls")
        ns_row = QtWidgets.QHBoxLayout()
        ns_row.addWidget(ns_label)
        ns_row.addWidget(self.ns_combo, 1)
        ns_row.addWidget(self.btn_refresh_ns)
        ns_row.addWidget(self.btn_select_ctrls)
        ns_row.addWidget(self.btn_select_ctrls_zero)

        # Start frame row (playback start)
        start_label = QtWidgets.QLabel("import Start Frame:")
        self.start_edit = QtWidgets.QLineEdit()
        self.start_edit.setValidator(QtGui.QIntValidator(-9999999, 9999999, self))
        self.btn_set_playback = QtWidgets.QPushButton("Set to Playback Start")
        self.btn_import = QtWidgets.QPushButton("Import FBX animation")
        start_row = QtWidgets.QHBoxLayout()
        start_row.addWidget(start_label)
        start_row.addWidget(self.start_edit)
        start_row.addWidget(self.btn_set_playback)
        start_row.addWidget(self.btn_import)

        # —— 在 start_row 下面追加一行含 A/B/C 三个按钮 ——
        tool_row = QtWidgets.QHBoxLayout()
        self.btn_a = QtWidgets.QPushButton("CTRL_CustomRigCubeGUI")
        self.btn_b = QtWidgets.QPushButton("CTRL_CustomRigEyeBrowsGUI")
        self.btn_c = QtWidgets.QPushButton("CTRL_CustomRigTweakGUI")
        tool_row.addWidget(self.btn_a)
        tool_row.addWidget(self.btn_b)
        tool_row.addWidget(self.btn_c)

        # Log box
        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(100)

        # Layout
        v = QtWidgets.QVBoxLayout(tab)
        v.addLayout(ns_row)
        v.addLayout(start_row)
        v.addLayout(tool_row)  # ⬅️ 新增
        v.addWidget(self.log)

        main = QtWidgets.QVBoxLayout()
        main.addWidget(self.tabs)
        self.setLayout(main)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        # Signals
        self.btn_refresh_ns.clicked.connect(self._refresh_namespaces)
        self.btn_select_ctrls.clicked.connect(self.select_face_controls)
        self.btn_select_ctrls_zero.clicked.connect(self.zero_out_face_controls)
        self.btn_set_playback.clicked.connect(self._apply_playback_start)
        self.btn_import.clicked.connect(self._on_import_clicked)
        self.btn_a.clicked.connect(lambda: self.toggle_translate("CTRL_CustomRigCubeGUI"))
        self.btn_b.clicked.connect(lambda: self.toggle_translate("CTRL_CustomRigEyeBrowsGUI"))
        self.btn_c.clicked.connect(lambda: self.toggle_translate("CTRL_CustomRigTweakGUI"))

        # Init
        self._refresh_namespaces()
        self._apply_playback_start()
        if mh_api is None:
            self._log(f"⚠️ Failed to import metahuman_api: {_mh_api_import_error}")
        self.add_dropframe_tab()
        self.show()

    # ===== Helpers =====
    def select_face_controls(self):
        """Select face controls from namespace in dropdown."""
        ns = self.ns_combo.currentText().strip()
        if not ns:
            QtWidgets.QMessageBox.critical(
                self,
                "Metahuman: Selection Error",
                "No namespace selected in dropdown."
            )
            return

        try:
            ok = mh_api.select_face_controls(ns)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Operation Failed",
                f"Exception while selecting face controls:\n{e}"
            )
            return

        if not ok:
            QtWidgets.QMessageBox.critical(
                self,
                "Operation Failed",
                "Missing Face Controls or invalid namespace.\nMake sure your Metahuman is in the scene."
            )
        else:
            self._log(f"Face controls selected for namespace: {ns}")

    def zero_out_face_controls(self):
        """Zero out face controls from namespace in dropdown."""
        ns = self.ns_combo.currentText().strip()
        if not ns:
            QtWidgets.QMessageBox.critical(
                self,
                "Metahuman: Selection Error",
                "No namespace selected in dropdown."
            )
            return

        try:
            ok = mh_api.zero_out_face_controls(ns)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Operation Failed",
                f"Exception while zeroing face controls:\n{e}"
            )
            return

        if not ok:
            QtWidgets.QMessageBox.critical(
                self,
                "Operation Failed",
                "Missing Face Controls or invalid namespace.\nMake sure your Metahuman is in the scene."
            )
            return

        self._log(f"Zeroed face controls for namespace: {ns}")

    def toggle_translate(self, attr, translate_axis="Y"):
        """切换 namespace 下指定对象的 translateX/Y/Z 在 0 和 1 之间"""
        ns = self._current_namespace()
        if ns is None:
            self._log("⚠️ No namespace selected", clear=False)
            return

        node = ns + attr
        plug = f"{node}.translate{translate_axis}"

        if not cmds.objExists(node):
            self._log(f"❌ Node not found: {node}", clear=False)
            return

        try:
            val = cmds.getAttr(plug)
            new_val = 1 if abs(val) < 1e-6 else 0
            cmds.setAttr(plug, new_val)
            self._log(f"✔ {plug} set to {new_val}", clear=False)
        except Exception as e:
            self._log(f"⚠️ Failed to toggle {plug}: {e}", clear=False)

    def _log(self, msg="", clear=False):
        cursor = self.log.textCursor()
        cursor.beginEditBlock()

        if clear:
            # 清空内容
            cursor.select(QtGui.QTextCursor.Document)
            cursor.removeSelectedText()
            cursor.deletePreviousChar()  # 去掉多余空行
        else:
            # 原逻辑
            cursor.movePosition(QtGui.QTextCursor.Start)
            cursor.movePosition(QtGui.QTextCursor.End, QtGui.QTextCursor.KeepAnchor)
            fmt_g = QtGui.QTextCharFormat();
            fmt_g.setForeground(QtGui.QColor("#888888"))
            cursor.setCharFormat(fmt_g)
            cursor.movePosition(QtGui.QTextCursor.End)
            fmt_w = QtGui.QTextCharFormat();
            fmt_w.setForeground(QtGui.QColor("#ffffff"))
            cursor.setCharFormat(fmt_w)
            cursor.insertText(f"> {msg}\n")

        cursor.endEditBlock()
        self.log.moveCursor(QtGui.QTextCursor.End)

    def _find_namespaces(self, only_with_facial_grp=True):
        """List namespaces (include ':' for no-namespace).
        当 only_with_facial_grp=True 时，仅保留场景里确实存在 <ns>facial_Grp 的命名空间（支持层级里短名匹配）。
        """
        # 1) 基础 ns 列表
        ns_list = [':']
        try:
            all_ns = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True) or []
        except Exception:
            all_ns = cmds.namespaceInfo(listOnlyNamespaces=True) or []
        for ns in all_ns:
            ns_list.append(ns if ns.endswith(':') else (ns + ':'))
        ns_list = sorted(list(dict.fromkeys(ns_list)), key=lambda x: (x != ':', x))

        if not only_with_facial_grp:
            return ns_list

        # 2) 采集实际有 facial_Grp 的命名空间集合（根据短名判断）
        has_facial = set()

        # 找到所有名字以 facial_Grp 结尾的节点（含层级、含命名空间）
        nodes = cmds.ls('*facial_Grp', r=True, long=True) or []
        for n in nodes:
            leaf = n.split('|')[-1]  # 去层级，得到形如 "ns1:ns2:facial_Grp" 或 "facial_Grp"
            base = leaf.split(':')[-1]  # 去命名空间，得到短名
            if base != 'facial_Grp':
                continue
            # 提取命名空间部分（可能是 "ns1:ns2:"，也可能没有命名空间）
            if ':' in leaf:
                ns_part = leaf[:leaf.rfind(':') + 1]  # 包含最后一个 ':'，如 "ns1:ns2:"
            else:
                ns_part = ':'  # 无命名空间用 ':'

            has_facial.add(ns_part)

        # 3) 过滤只保留实际存在 facial_Grp 的命名空间
        filtered = [ns for ns in ns_list if ns in has_facial]
        return filtered

    def _apply_playback_start(self):
        s = int(round(float(cmds.playbackOptions(q=True, minTime=True))))
        self.start_edit.setText(str(s))
        self._log(f"Start frame set to playback start: {s}")

    def _refresh_namespaces(self):
        self.ns_combo.clear()
        ns_list = self._find_namespaces()
        self.ns_combo.addItems(ns_list)
        self._log("Namespaces refreshed: " + ", ".join(ns_list))

    def _current_namespace(self):
        txt = self.ns_combo.currentText().strip()
        if not txt:
            return None
        return txt if txt.endswith(':') else (txt + ':')

    def _clear_existing_on_controls(self, namespace):
        """
        Disconnect incoming connections and clear keys on translate X/Y/Z
        for face controls in the selected namespace.
        """
        try:
            ctrls = mh_api.get_face_controls(namespace)
        except Exception as e:
            return False, f"Failed to get face controls: {e}"

        if not ctrls:
            return False, "No face controls found."

        bw_to_check = set()
        chans = ("translateX", "translateY", "translateZ")
        for c in ctrls:
            name = str(c)
            for ch in chans:
                attr = f"{name}.{ch}"
                if not cmds.objExists(attr):
                    continue
                # disconnect incoming
                plugs = cmds.listConnections(attr, s=True, d=False, p=True) or []
                for src in plugs:
                    try:
                        # record bw for cleanup
                        n = src.split(".")[0]
                        try:
                            if cmds.nodeType(n) == "blendWeighted":
                                bw_to_check.add(n)
                        except Exception:
                            pass
                        cmds.disconnectAttr(src, attr)
                    except Exception:
                        pass
                # clear keys
                try:
                    cmds.cutKey(attr, cl=True)  # remove keys from this attr
                except Exception:
                    pass

        # delete orphan blendWeighted created by previous retargets
        for n in list(bw_to_check):
            try:
                outs = cmds.listConnections(n + ".output", s=False, d=True, p=False) or []
                if not outs:
                    cmds.delete(n)
            except Exception:
                pass

        return True, "Existing keys & connections cleared."

    def _shift_animation_to_start(self, namespace, desired_start):
        """Shift keys to desired_start and update playback range."""
        try:
            face_controls = mh_api.get_face_controls(namespace)
        except Exception as e:
            return False, f"Failed to get face controls: {e}"
        if not face_controls:
            return False, "No face controls found."

        try:
            start_frame, end_frame = mh_api.get_key_frame_ranges(face_controls)
        except Exception as e:
            return False, f"Failed to read key ranges: {e}"
        if start_frame is None or end_frame is None:
            return False, "No keys detected."

        s = int(round(start_frame))
        e = int(round(end_frame))
        delta = int(desired_start) - s
        if delta == 0:
            cmds.playbackOptions(minTime=s, maxTime=e)
            return True, "Retarget done. No time shift needed."

        # shift only for nodes that actually have curves
        ctrl_names = []
        for n in face_controls:
            name = str(n)
            if cmds.listConnections(name, type="animCurve"):
                ctrl_names.append(name)
        if not ctrl_names:
            return False, "No animated keys on controls."

        try:
            cmds.keyframe(ctrl_names, e=True, r=True, tc=delta, t=(s, e))
            cmds.playbackOptions(minTime=s + delta, maxTime=e + delta)
        except Exception as ex:
            return False, f"Time shift failed: {ex}"

        return True, f"Shifted {delta} frames ({s} -> {s + delta})."

    def mh_anim_io(self,data=None, namespace=':'):
        """
        用法1：无参 -> 采集动画并返回字典
            snap = mh_anim_io(namespace='mh_001:')

        用法2：传入字典 -> 按字典写回动画（已有关键帧的时刻跳过）
            stats = mh_anim_io(snap)  # snap 为上面返回的字典

        字典结构（示例）：
        {
          'namespace': 'mh_001:',
          'channels': [
            {'node':'mh_001:CTRL_C_jaw','attr':'translateX','times':[1,2,3],'values':[0.0,0.5,1.0]},
            ...
          ]
        }
        """

        # ---- 辅助 ----
        def _exists_attr(node_attr):
            return cmds.objExists(node_attr)

        def _free_and_keyable(node_attr):
            try:
                if cmds.getAttr(node_attr, lock=True):
                    return False
                # 若不可设置也视为不可写
                cmds.getAttr(node_attr)
                return True
            except Exception:
                return False

        def _has_time(existing_times, t, eps=1e-4):
            if not existing_times:
                return False
            for x in existing_times:
                if abs(float(x) - float(t)) < eps:
                    return True
            return False

        # ================= 用法1：采集 =================
        if data is None:
            chans = []
            # 利用 API 获取控制器
            ctrls = mh_api.get_face_controls(namespace)
            if not ctrls:
                return {'namespace': namespace, 'channels': []}

            for c in ctrls:
                name = str(c)
                for attr in ('translateX', 'translateY', 'translateZ'):
                    plug = f"{name}.{attr}"
                    if not _exists_attr(plug):
                        continue
                    # 仅当有动画曲线或已有关键帧时采集
                    if cmds.listConnections(plug, type='animCurve') or cmds.keyframe(plug, q=True, kc=True):
                        times = cmds.keyframe(plug, q=True, tc=True) or []
                        values = cmds.keyframe(plug, q=True, vc=True) or []
                        if times and values and len(times) == len(values):
                            chans.append({'node': name, 'attr': attr,
                                          'times': list(map(float, times)),
                                          'values': list(map(float, values))})
            return {'namespace': namespace, 'channels': chans}

        # ================= 用法2：写回 =================
        stats = {'written': 0, 'skipped_existing': 0, 'missing_attrs': 0, 'locked': 0, 'total': 0}
        ns_in = data.get('namespace', namespace)
        channels = data.get('channels', [])
        for ch in channels:
            node = ch.get('node', '')
            attr = ch.get('attr', '')
            times = ch.get('times', []) or []
            vals = ch.get('values', []) or []
            if not node or not attr or len(times) != len(vals):
                continue
            plug = f"{node}.{attr}"
            if not _exists_attr(plug):
                stats['missing_attrs'] += len(times)
                continue
            if not _free_and_keyable(plug):
                stats['locked'] += len(times)
                continue

            # 读取已存在关键帧时刻
            existing = cmds.keyframe(plug, q=True, tc=True) or []
            for t, v in zip(times, vals):
                stats['total'] += 1
                if _has_time(existing, t):
                    stats['skipped_existing'] += 1
                    continue
                try:
                    cmds.setKeyframe(plug, time=(t,), value=v)
                    stats['written'] += 1
                except Exception:
                    # 写失败也算跳过现有/异常，不额外分类
                    stats['skipped_existing'] += 1

        return stats

    def import_same_name_wav(self,fbx_path, start_frame):
        pass

    def _on_import_clicked(self):
        def scene_time_range(ranges=None):
            """
            用法:
            1) 保存当前范围:
                saved = scene_time_range()
                # saved = {
                #   'anim_start': float,
                #   'anim_end': float,
                #   'playback_start': float,
                #   'playback_end': float
                # }

            2) 恢复范围:
                scene_time_range(saved)

            Args:
                ranges (dict or None):
                    None 时 → 返回当前动画范围/回放范围
                    dict 时 → 恢复这些范围

            Returns:
                dict: 当前/已恢复的范围
            """
            if ranges is None:
                # 读取当前值
                anim_start = cmds.playbackOptions(q=True, animationStartTime=True)
                anim_end = cmds.playbackOptions(q=True, animationEndTime=True)
                pb_start = cmds.playbackOptions(q=True, minTime=True)
                pb_end = cmds.playbackOptions(q=True, maxTime=True)
                return {
                    'anim_start': anim_start,
                    'anim_end': anim_end,
                    'playback_start': pb_start,
                    'playback_end': pb_end
                }
            else:
                # 恢复指定值
                cmds.playbackOptions(animationStartTime=ranges['anim_start'],
                                     animationEndTime=ranges['anim_end'],
                                     minTime=ranges['playback_start'],
                                     maxTime=ranges['playback_end'])
                return dict(ranges)

        def import_same_name_wav(fbx_path, start_frame):

            if not fbx_path or not os.path.isfile(fbx_path):
                return
            base, _ = os.path.splitext(fbx_path)
            wav_path = base + ".wav"
            if not os.path.exists(wav_path):
                wav_path_upper = base + ".WAV"
                if os.path.exists(wav_path_upper):
                    wav_path = wav_path_upper
                else:
                    return (False, None)
            try:
                sound=cmds.sound(file=wav_path, offset=start_frame)
                cmds.select(sound)
                #cmds.select(clear=True)
            except:
                return

        if mh_api is None:
            self._log(f"❌ metahuman_api not available: {_mh_api_import_error}")
            return

        saved_ranges = scene_time_range()
        ns = self._current_namespace()

        oldanimations=self.mh_anim_io(namespace=ns)
        self._clear_existing_on_controls(namespace=ns)

        text = self.start_edit.text().strip()
        if not text or not re.match(r"^-?\d+$", text):
            self._log(f"❌ Invalid start frame: {text}")
            return
        desired_start = int(text)

        # file
        fbx_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Choose FBX", "", "FBX Files (*.fbx);;All Files (*.*)"
        )
        if not fbx_path:
            self._log("Cancelled.")
            return

        timeunit = cmds.currentUnit(q=True, time=True)
        self._log(
            f"Retarget start:\n- File: {fbx_path}\n- Namespace: {ns}\n- Time Unit: {timeunit}\n- Target Start: {desired_start}"
        )

        # retarget
        try:
            elapsed, err = mh_api.retarget_metahuman_animation_sequence(
                fbx_path=fbx_path,
                namespace=ns,       # ':' means no namespace
                timeunit=timeunit
            )
        except Exception as e:
            self._log(f"❌ Exception during import: {e}")
            return

        if err:
            self._log(f"❌ Retarget failed: {err}")
            return

        self._log(f"Retarget finished. Elapsed: {elapsed or 'N/A'}")

        # time shift
        ok, msg = self._shift_animation_to_start(ns, desired_start)
        self._log(("✅ " if ok else "⚠️") + msg)
        scene_time_range(saved_ranges)
        self.mh_anim_io(data=oldanimations ,namespace=ns)
        import_same_name_wav(fbx_path,desired_start)

    def add_dropframe_tab(self):
        """在现有工具中新增“Drop Frame”页签（整合功能 + 布局优化：刷新按钮在下拉右侧，T/R/S 横向排列）"""
        from PySide2 import QtWidgets, QtCore
        import maya.cmds as cmds
        import time

        layer_name_base = "dropFramelayer"

        # —— 内部工具函数 ——
        def _refresh_set_list():
            sets = cmds.ls("*_dropFramelayerSet", type="objectSet", r=True) or []
            ui['set_dropdown'].clear()
            if sets:
                ui['set_dropdown'].addItems(sets)
            else:
                ui['set_dropdown'].addItem("No _dropFramelayerSet found")
            ui['set_dropdown'].addItem("Create New Set")

        def _current_scene_range():
            return (int(cmds.playbackOptions(q=True, min=True)),
                    int(cmds.playbackOptions(q=True, max=True)))

        def _create_new_set_from_selection(parent):
            sel = cmds.ls(sl=True) or []
            if not sel:
                cmds.warning("No objects selected to create a new set.")
                return None
            name, ok = QtWidgets.QInputDialog.getText(parent, "Create New Set",
                                                      "Enter set name (will append '_dropFramelayerSet'):")
            if not ok or not name.strip():
                cmds.warning("Creation cancelled or invalid name.")
                return None
            full = f"{name.strip()}_dropFramelayerSet"
            if not cmds.objExists(full):
                cmds.createNode("objectSet", name=full)
            cmds.sets(sel, add=full)
            return full

        def _get_selected_set_members(parent):
            item = ui['set_dropdown'].currentText()
            if item == "Create New Set":
                newset = _create_new_set_from_selection(parent)
                if newset:
                    _refresh_set_list()
                    idx = ui['set_dropdown'].findText(newset)
                    if idx != -1:
                        ui['set_dropdown'].setCurrentIndex(idx)
                    return cmds.sets(newset, q=True) or []
                return []
            if item == "No _dropFramelayerSet found":
                return []
            return cmds.sets(item, q=True) or []

        def _ensure_anim_layer_exists(parent, base_name):
            name = base_name
            if cmds.objExists(name):
                res = QtWidgets.QMessageBox.question(
                    parent, "Layer Exists",
                    f"Animation layer '{name}' already exists. Create a new one with numeric suffix?",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                )
                if res == QtWidgets.QMessageBox.Yes:
                    i = 1
                    while cmds.objExists(f"{name}_{i}"):
                        i += 1
                    name = f"{name}_{i}"
                    cmds.animLayer(name)
                    return name
                return name
            cmds.animLayer(name)
            return name

        def _mute_lock_other_layers(excluded=None):
            layers = cmds.ls(f"*{layer_name_base}*", type="animLayer") or []
            for L in layers:
                if L != excluded:
                    try:
                        cmds.setAttr(f"{L}.mute", 1)
                        cmds.animLayer(L, e=True, lock=True)
                    except Exception:
                        pass

        def _unmute_unlock(layer_name):
            try:
                cmds.animLayer(layer_name, e=True, lock=False)
                cmds.setAttr(f"{layer_name}.mute", 0)
            except Exception:
                pass

        def _ensure_objects_in_layer(objs, layer_name):
            if not cmds.objExists(layer_name):
                raise RuntimeError(f"Animation layer '{layer_name}' does not exist.")
            for o in objs:
                attrs = cmds.listAttr(o, keyable=True, unlocked=True) or []
                if not attrs:
                    continue
                plugs = [f"{o}.{a}" for a in attrs]
                try:
                    cmds.animLayer(layer_name, e=True, attribute=plugs)
                except Exception:
                    pass

        def _has_keys_in_range(obj, attrs, tmin, tmax):
            for a in attrs:
                plug = f"{obj}.{a}"
                try:
                    if cmds.keyframe(plug, q=True, time=(tmin, tmax)):
                        return True
                except Exception:
                    pass
            return False

        def _filter_objs_with_keys(objs, tmin, tmax, use_t, use_r, use_s):
            keep = []
            t_attrs = ["translateX", "translateY", "translateZ"] if use_t else []
            r_attrs = ["rotateX", "rotateY", "rotateZ"] if use_r else []
            s_attrs = ["scaleX", "scaleY", "scaleZ"] if use_s else []
            attrs = t_attrs + r_attrs + s_attrs
            if not attrs:
                return []
            for o in objs:
                if _has_keys_in_range(o, attrs, tmin, tmax):
                    keep.append(o)
            return keep

        def _record_keyframes(objs, tmin, tmax, n, use_t, use_r, use_s):
            _mute_lock_other_layers()
            data = {o: [] for o in objs}
            cur = tmin
            t_attrs = ["translateX", "translateY", "translateZ"] if use_t else []
            r_attrs = ["rotateX", "rotateY", "rotateZ"] if use_r else []
            s_attrs = ["scaleX", "scaleY", "scaleZ"] if use_s else []
            attrs_all = t_attrs + r_attrs + s_attrs

            while cur <= tmax:
                try:
                    cmds.currentTime(cur, e=True)
                except Exception:
                    pass
                for o in objs:
                    entry = {'frame': int(cur)}
                    has_any = False
                    for a in attrs_all:
                        plug = f"{o}.{a}"
                        try:
                            if cmds.keyframe(plug, q=True, time=(tmin, tmax)):
                                val = cmds.getAttr(plug)
                                entry[a] = val
                                has_any = True
                        except Exception:
                            pass
                    if has_any:
                        data[o].append(entry)
                cur += n

            if (cur - n) < tmax:
                try:
                    cmds.currentTime(tmax, e=True)
                except Exception:
                    pass
                for o in objs:
                    entry = {'frame': int(tmax)}
                    has_any = False
                    for a in attrs_all:
                        plug = f"{o}.{a}"
                        try:
                            if cmds.keyframe(plug, q=True, time=(tmin, tmax)):
                                val = cmds.getAttr(plug)
                                entry[a] = val
                                has_any = True
                        except Exception:
                            pass
                    if has_any:
                        data[o].append(entry)
            return data

        def _apply_keyframes(objs, data, tmin, tmax, n, layer_name):
            _unmute_unlock(layer_name)
            for o in objs:
                kfs = data.get(o, [])
                for k in kfs:
                    f0 = int(k['frame'])
                    f1 = min(f0 + n, tmax + 1)
                    for f in range(f0, f1):
                        for attr, val in k.items():
                            if attr == 'frame':
                                continue
                            plug = f"{o}.{attr}"
                            try:
                                if cmds.getAttr(plug, lock=True):
                                    continue
                            except Exception:
                                pass
                            try:
                                cmds.setKeyframe(o, at=attr, t=f, v=val, animLayer=layer_name)
                            except Exception:
                                pass

        # —— 构建 UI ——
        tab = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout(tab)
        grid.setVerticalSpacing(6)
        grid.setHorizontalSpacing(8)

        start_default, end_default = _current_scene_range()

        ui = {}
        ui['set_dropdown'] = QtWidgets.QComboBox()
        ui['btn_refresh'] = QtWidgets.QPushButton("⟳")  # 刷新按钮放在下拉右侧
        ui['btn_refresh'].setFixedWidth(32)
        ui['btn_refresh'].setToolTip("Refresh Sets")

        ui['start_spin'] = QtWidgets.QSpinBox()
        ui['end_spin'] = QtWidgets.QSpinBox()
        ui['n_spin'] = QtWidgets.QSpinBox()

        # —— T / R / S 横向一行 ——
        ui['chk_t'] = QtWidgets.QCheckBox()
        ui['chk_r'] = QtWidgets.QCheckBox()
        ui['chk_s'] = QtWidgets.QCheckBox()
        # 行容器
        trs_row = QtWidgets.QHBoxLayout()
        trs_row.setSpacing(16)

        # 小组：文本 + 复选框
        def _pair(label_text, chk):
            box = QtWidgets.QHBoxLayout()
            box.setSpacing(6)
            lab = QtWidgets.QLabel(label_text)
            box.addWidget(lab)
            box.addWidget(chk)
            box.addStretch(1)
            return box

        trs_row.addLayout(_pair("Translate (t)", ui['chk_t']))
        trs_row.addLayout(_pair("Rotate (r)", ui['chk_r']))
        trs_row.addLayout(_pair("Scale (s)", ui['chk_s']))
        trs_row.addStretch(1)

        ui['btn_run'] = QtWidgets.QPushButton("Run")

        ui['start_spin'].setRange(-1000000, 1000000)
        ui['end_spin'].setRange(-1000000, 1000000)
        ui['n_spin'].setRange(1, 100)

        ui['start_spin'].setValue(start_default)
        ui['end_spin'].setValue(end_default)
        ui['n_spin'].setValue(5)
        ui['chk_t'].setChecked(True)
        ui['chk_r'].setChecked(True)
        ui['chk_s'].setChecked(False)

        # —— 第一行：Select Set + 下拉 + 刷新按钮（同一行） ——
        top_row = QtWidgets.QHBoxLayout()
        top_row.setSpacing(8)
        top_row.addWidget(QtWidgets.QLabel("Select Set:"))
        top_row.addWidget(ui['set_dropdown'], 1)
        top_row.addWidget(ui['btn_refresh'], 0, QtCore.Qt.AlignRight)

        grid.addLayout(top_row, 0, 0, 1, 2)
        grid.addWidget(QtWidgets.QLabel("Start Frame:"), 1, 0)
        grid.addWidget(ui['start_spin'], 1, 1)
        grid.addWidget(QtWidgets.QLabel("End Frame:"), 2, 0)
        grid.addWidget(ui['end_spin'], 2, 1)
        grid.addWidget(QtWidgets.QLabel("Frame Interval (n):"), 3, 0)
        grid.addWidget(ui['n_spin'], 3, 1)
        grid.addLayout(trs_row, 4, 0, 1, 2)  # T/R/S 一行
        grid.addWidget(ui['btn_run'], 5, 0, 1, 2)

        tab.setLayout(grid)
        self.tabs.addTab(tab, "Drop Frame")

        # —— 行为绑定 ——
        def _on_refresh():
            _refresh_set_list()

        def _on_run():
            t0 = time.time()
            start_f = ui['start_spin'].value()
            end_f = ui['end_spin'].value()
            n = ui['n_spin'].value()
            use_t = ui['chk_t'].isChecked()
            use_r = ui['chk_r'].isChecked()
            use_s = ui['chk_s'].isChecked()

            objs = _get_selected_set_members(tab)
            if not objs:
                cmds.warning("No objects found in the selected set.")
                return

            objs = _filter_objs_with_keys(objs, start_f, end_f, use_t, use_r, use_s)
            if not objs:
                cmds.warning("No objects with keyframes found in the selected set.")
                return

            layer_name = _ensure_anim_layer_exists(tab, f"F{n}_{layer_name_base}")
            _ensure_objects_in_layer(objs, layer_name)

            snap = _record_keyframes(objs, start_f, end_f, n, use_t, use_r, use_s)
            _apply_keyframes(objs, snap, start_f, end_f, n, layer_name)

            elapsed = time.time() - t0
            QtWidgets.QMessageBox.information(tab, "Process Completed",
                                              f"Processed {len(objs)} objects in {elapsed:.2f} seconds.")

        ui['btn_refresh'].clicked.connect(_on_refresh)
        ui['btn_run'].clicked.connect(_on_run)

        _refresh_set_list()


# Close previous window and create a new one
try:
    RomeoToolwindow.close()
except:
    pass
RomeoToolwindow = RomeoTool()
