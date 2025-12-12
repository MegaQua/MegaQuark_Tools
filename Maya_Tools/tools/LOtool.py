from PySide2 import QtWidgets, QtGui, QtCore
import pymel.core as pm
import maya.cmds as cmds
import os
import inspect
from maya import OpenMayaUI as omui
import shiboken2
import getpass
import json
import maya.mel as mel

class LOtool(QtWidgets.QWidget):
    def __init__(self):
        super(LOtool, self).__init__(None)
        self.setWindowTitle("LOtool")

        self.tabs = QtWidgets.QTabWidget()

        # === 第一页 facial test ===
        facial_tab = QtWidgets.QWidget()
        self.tabs.addTab(facial_tab, "facial test")
        facial_tab.layout = QtWidgets.QGridLayout()
        facial_tab.setLayout(facial_tab.layout)

        # 按钮 1 - 选择面部控制器
        btn1 = QtWidgets.QPushButton("Create HUD Mask")
        btn1.clicked.connect(self.CreatMaskNode)

        # 按钮 2 - 应用绑定权重
        btn2 = QtWidgets.QPushButton("Hide or Show HUD Mask")
        btn2.clicked.connect(self.HUDMask_visibility)

        # 按钮 4 - 导出当前表情
        btn4 = QtWidgets.QPushButton("smart playblast")
        btn4.clicked.connect(self.smart_playblast)
        # 添加 Facial Animation Importer 按钮
        btn5 = QtWidgets.QPushButton("Facial Animation Importer")
        btn5.clicked.connect(self.launch_facial_importer)
        facial_tab.layout.addWidget(btn5, 4, 0, 1, 2)
        # 状态反馈区


        # 加入布局
        #facial_tab.layout.addWidget(btn1, 0, 0, 1, 2)
        facial_tab.layout.addWidget(btn2, 1, 0, 1, 2)
        #facial_tab.layout.addWidget(btn3, 2, 0, 1, 2)
        #facial_tab.layout.addWidget(btn4, 3, 0, 1, 2)
        facial_tab.layout.addWidget(btn5, 2, 0, 1, 2)

        # === Facial Camera Creator ===
        self.facial_cam_tab = QtWidgets.QWidget()
        self.tabs.addTab(self.facial_cam_tab, "Facial Camera Creator")
        self._build_facial_camera_tab()


        # 主 Layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.tabs)
        self.setLayout(mainLayout)

        #self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.resize(300, 150)
        self.show()

    # ==== 功能函数定义 ====
    def printself(self):
        sender = self.sender()
        if isinstance(sender, QtWidgets.QPushButton):
            print("Button pressed:", sender.text())

    def launch_facial_importer(self):
        import json
        class MyWindow(QtWidgets.QWidget):
            def __init__(self):
                super(MyWindow, self).__init__()
                self.setWindowTitle("Facial Animation Importer for Maya 2020")

                # Facial Animation JSON Path
                label_facialAnim = QtWidgets.QLabel("Facial Animation JSON:")
                self.text_facialAnimPath = QtWidgets.QLineEdit()
                self.text_facialAnimPath.setReadOnly(True)
                button_browseFacialAnim = QtWidgets.QPushButton("Browse")
                button_browseFacialAnim.clicked.connect(self.a2fjsonpath)

                self.label_frameLength = QtWidgets.QLabel("Frame Length: N/A")
                label_startFrame = QtWidgets.QLabel("Import Start Frame:")
                self.text_startFrame = QtWidgets.QLineEdit("0")
                label_importLength = QtWidgets.QLabel("Import Length:")
                self.text_importLength = QtWidgets.QLineEdit("N/A")
                label_namespace = QtWidgets.QLabel("Namespace:")
                self.namespace_combo = QtWidgets.QComboBox()
                self.update_namespace_list()

                self.checkbox_importWAV = QtWidgets.QCheckBox("Import WAV File")
                self.checkbox_onlyFirstFrame = QtWidgets.QCheckBox("Only First Frame")

                button_import = QtWidgets.QPushButton("Import")
                button_import.clicked.connect(self.browseFacialAnimation)

                layout = QtWidgets.QGridLayout()
                layout.addWidget(label_facialAnim, 0, 0)
                layout.addWidget(self.text_facialAnimPath, 0, 1)
                layout.addWidget(button_browseFacialAnim, 0, 2)
                layout.addWidget(self.label_frameLength, 1, 0, 1, 3)
                layout.addWidget(label_startFrame, 2, 0)
                layout.addWidget(self.text_startFrame, 2, 1, 1, 2)
                layout.addWidget(label_importLength, 3, 0)
                layout.addWidget(self.text_importLength, 3, 1, 1, 2)
                layout.addWidget(label_namespace, 4, 0)

                namespace_layout = QtWidgets.QHBoxLayout()
                namespace_layout.addWidget(self.namespace_combo)

                refresh_button = QtWidgets.QPushButton("⟳")
                refresh_button.setFixedWidth(30)
                refresh_button.setToolTip("刷新命名空间列表")
                refresh_button.clicked.connect(self.update_namespace_list)

                namespace_layout.addWidget(refresh_button)
                layout.addLayout(namespace_layout, 4, 1, 1, 2)

                #layout.addWidget(self.checkbox_importWAV, 5, 0)
                #layout.addWidget(self.checkbox_onlyFirstFrame, 5, 0)
                layout.addWidget(button_import, 5, 1, 1, 2)

                self.setLayout(layout)
                self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
                self.resize(400, 200)
                self.show()

            def update_namespace_list(self):
                self.namespace_combo.clear()
                self.namespace_combo.addItem("")
                all_objs = cmds.ls()
                namespaces = set()
                for obj in all_objs:
                    if ":" in obj:
                        ns = obj.split(":")[0]
                        if ns and not ns.startswith("shared"):
                            namespaces.add(ns)
                for ns in sorted(namespaces):
                    self.namespace_combo.addItem(ns)

            def a2fjsonpath(self):
                default_dir = r"K:\LO\11_Users\Q\100020702_1408room2_animation_A2F"
                filePath, _ = QtWidgets.QFileDialog.getOpenFileName(
                    self,
                    "Select Facial Animation JSON",
                    default_dir,  # 设置默认路径
                    "JSON Files (*.json)"
                )
                if filePath:
                    self.text_facialAnimPath.setText(filePath)

            def browseFacialAnimation(self):
                affected_controllers = set()
                try:
                    startframe = int(self.text_startFrame.text())
                except:
                    QtWidgets.QMessageBox.warning(self, "", "Invalid input for start frame", QtWidgets.QMessageBox.Ok)
                    return

                a2f_json_path = self.text_facialAnimPath.text()
                setting_path = 'S:/Public/qiu_yi/JCQ_Tool/data/LOarkit52.json'
                try:
                    with open(a2f_json_path, 'r') as file:
                        a2f_json_data = json.load(file)
                    with open(setting_path, 'r') as file:
                        setting_data = json.load(file)
                except Exception as e:
                    QtWidgets.QMessageBox.warning(self, "Load Error", str(e), QtWidgets.QMessageBox.Ok)
                    return

                numFrames = a2f_json_data['numFrames']
                facsNames = a2f_json_data['facsNames']
                weightMat = a2f_json_data['weightMat']
                selected_namespace = self.namespace_combo.currentText()

                # === 提取默认值表 ===
                default_value_map = setting_data.get("__defaultValues__", {})

                for frame_index in range(numFrames):
                    controller_values = {}
                    for facsIndex, facsName in enumerate(facsNames):
                        weight = weightMat[frame_index][facsIndex]
                        if weight == 0: continue
                        if facsName in setting_data:
                            facs_values = setting_data[facsName]
                            for controller, attrs in facs_values.items():
                                for attr, base_value in attrs.items():
                                    # === 应用默认值修正逻辑 ===
                                    default_val = default_value_map.get(controller, {}).get(attr, 0.0)
                                    final_value = weight * (base_value - default_val) + default_val

                                    controller_values.setdefault(controller, {}).setdefault(attr, 0)
                                    controller_values[controller][attr] += final_value

                    for controller, attrs in controller_values.items():
                        for attr, value in attrs.items():
                            ctrl = f"{selected_namespace}:{controller}" if selected_namespace else controller
                            try:
                                cmds.setAttr(f"{ctrl}.{attr}", value)
                                cmds.setKeyframe(f"{ctrl}.{attr}", time=startframe + frame_index)
                                affected_controllers.add(ctrl.split('.')[0])
                            except Exception as e:
                                print(f"设置关键帧失败: {ctrl}.{attr} = {value}，错误：{e}")

                set_name = f"{selected_namespace}A2FcontrolerSet" if selected_namespace else "A2FcontrolerSet"
                if not cmds.objExists(set_name):
                    cmds.sets(name=set_name, empty=True)
                    for ctrl in affected_controllers:
                        if cmds.objExists(ctrl):
                            try:
                                cmds.sets(ctrl, add=set_name)
                            except Exception as e:
                                print(f"添加 {ctrl} 到 Set 时出错：{e}")
                else:
                    print(f"Set {set_name} 已存在，未添加任何对象。")

                QtWidgets.QMessageBox.information(self, "", "Import succeeded", QtWidgets.QMessageBox.Ok)


            def browseFacialAnimation2(self):
                affected_controllers = set()
                try:
                    startframe = int(self.text_startFrame.text())
                except:
                    QtWidgets.QMessageBox.warning(self, "", "Invalid input for start frame", QtWidgets.QMessageBox.Ok)
                    return

                a2f_json_path = self.text_facialAnimPath.text()
                setting_path = 'S:/Public/qiu_yi/JCQ_Tool/data/LOarkit52.json'
                #setting_path = 'S:/Public/qiu_yi/JCQ_Tool/data/LOarkit52_v2.json'
                try:
                    with open(a2f_json_path, 'r') as file:
                        a2f_json_data = json.load(file)
                    with open(setting_path, 'r') as file:
                        setting_data = json.load(file)
                except Exception as e:
                    QtWidgets.QMessageBox.warning(self, "Load Error", str(e), QtWidgets.QMessageBox.Ok)
                    return

                numFrames = a2f_json_data['numFrames']
                facsNames = a2f_json_data['facsNames']
                weightMat = a2f_json_data['weightMat']
                selected_namespace = self.namespace_combo.currentText()

                for frame_index in range(numFrames):
                    controller_values = {}
                    for facsIndex, facsName in enumerate(facsNames):
                        weight = weightMat[frame_index][facsIndex]
                        if weight == 0: continue
                        if facsName in setting_data:
                            facs_values = setting_data[facsName]
                            for controller, attrs in facs_values.items():
                                #if "Eye" in controller: continue
                                for attr, value in attrs.items():
                                    weighted_value = weight * value
                                    controller_values.setdefault(controller, {}).setdefault(attr, 0)
                                    controller_values[controller][attr] += weighted_value
                                    #controller_values[controller][attr] = max(-1.0, min(1.0, controller_values[controller][attr]))

                    for controller, attrs in controller_values.items():
                        for attr, value in attrs.items():
                            ctrl = f"{selected_namespace}:{controller}" if selected_namespace else controller
                            try:
                                cmds.setAttr(f"{ctrl}.{attr}", value)
                                cmds.setKeyframe(f"{ctrl}.{attr}", time=startframe + frame_index)
                                affected_controllers.add(ctrl.split('.')[0])
                            except Exception as e:
                                print(f"设置关键帧失败: {ctrl}.{attr} = {value}，错误：{e}")

                set_name = f"{selected_namespace}A2FcontrolerSet" if selected_namespace else "A2FcontrolerSet"
                if not cmds.objExists(set_name):
                    cmds.sets(name=set_name, empty=True)
                    for ctrl in affected_controllers:
                        if cmds.objExists(ctrl):
                            try:
                                cmds.sets(ctrl, add=set_name)
                            except Exception as e:
                                print(f"添加 {ctrl} 到 Set 时出错：{e}")
                else:
                    print(f"Set {set_name} 已存在，未添加任何对象。")

                QtWidgets.QMessageBox.information(self, "", "Import succeeded", QtWidgets.QMessageBox.Ok)

        self.facial_importer_window = MyWindow()

    def CreatMaskNode(self):
            plugin_name = 'mask_node.py'
            current_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
            current_dir = current_dir.replace("tools", "test")
            plugin_path = os.path.join(current_dir, plugin_name)

            if pm.pluginInfo(plugin_name, q=True, loaded=True):
                loaded_plugin_path = pm.pluginInfo(plugin_name, q=True, path=True)
                if os.path.normpath(loaded_plugin_path) != os.path.normpath(plugin_path):
                    pm.unloadPlugin(plugin_name, force=True)
                    pm.loadPlugin(plugin_path)
            else:
                pm.loadPlugin(plugin_path)

            nodename = "camera_mask_node"
            if cmds.objExists(nodename):
                pm.delete(nodename)
            transform_node = pm.createNode("transform", name=nodename)
            mask_node = pm.createNode('mask_node', name=nodename + "Shape", parent=transform_node)

            mask_node.setAttr('topLeftData', 0)
            mask_node.setAttr('topCenterData', 0)
            mask_node.setAttr('topRightData', 0)
            mask_node.setAttr('bottomLeftData', 6)
            mask_node.setAttr('bottomCenterData', 1)
            mask_node.setAttr('bottomRightData', 6)
            mask_node.setAttr('centerData', 0)
            mask_node.setAttr('textPadding', 0)
            mask_node.setAttr('borderAlpha', 0)
            mask_node.setAttr('borderScale', 1)
            mask_node.setAttr('bottomBorder', False)
            mask_node.setAttr('topBorder', False)
            mask_node.setAttr('textPadding', 0)
            mask_node.setAttr('fontColor', (1, 1, 1))
            try:
                cmds.setAttr(f"{mask_node.name()}.camera", "persp", type="string")
                mask_node.setAttr("fontName", "Arial")
            except:
                print("persp does not exist")

    def HUDMask_visibility(self):
        node_name = "LO_camera_mask_node"
        if cmds.objExists(node_name):
            current_state = cmds.getAttr(f"{node_name}.visibility")
            cmds.setAttr(f"{node_name}.visibility", not current_state)
            print(f"Toggled visibility of '{node_name}' to {not current_state}")
        else:
            print(f"⚠ Object '{node_name}' not found in scene.")

    def smart_playblast(self):
        # 获取当前场景名
        scene_path = cmds.file(q=True, sn=True)
        scene_name = os.path.splitext(os.path.basename(scene_path))[0] or "untitled"

        # 获取用户名
        username = getpass.getuser()
        default_filename = f"{scene_name}_{username}.mov"

        # 选择输出文件夹
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            None, "选择输出文件夹", os.path.expanduser("~"))
        if not folder:
            cmds.warning("取消输出")
            return

        # 文件名输入窗口
        dialog = QtWidgets.QDialog()
        dialog.setWindowFlags(dialog.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        dialog.setWindowTitle("确认输出文件名")
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.addWidget(QtWidgets.QLabel("你可以修改文件名（无需扩展名）："))

        filename_edit = QtWidgets.QLineEdit(default_filename.replace(".mov", ""))
        layout.addWidget(filename_edit)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if not dialog.exec_():
            cmds.warning("用户取消了播放输出。")
            return

        final_filename = filename_edit.text().strip()
        if not final_filename:
            cmds.warning("文件名不能为空。")
            return

        # 输出视频路径
        video_path = os.path.join(folder, final_filename + ".mov").replace("\\", "/")

        # ---------- ⚠️ 先处理保存场景 ----------
        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle("保存当前场景？")
        msg_box.setText("是否也将当前场景另存到该目录？")
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msg_box.setWindowFlags(msg_box.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        reply = msg_box.exec_()

        if reply == QtWidgets.QMessageBox.Yes:
            input_dialog = QtWidgets.QInputDialog()
            input_dialog.setWindowTitle("保存场景")
            input_dialog.setLabelText("输入要保存的文件名（可省略扩展名，默认为 .mb）")
            input_dialog.setTextValue(f"{scene_name}_{username}")
            input_dialog.setWindowFlags(input_dialog.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

            if input_dialog.exec_():
                text = input_dialog.textValue().strip()
                ok = True
            else:
                text = ""
                ok = False

            if ok and text.strip():
                filename = text.strip()
                if not filename.lower().endswith((".ma", ".mb")):
                    filename += ".mb"

                scene_save_path = os.path.join(folder, filename).replace("\\", "/")
                cmds.file(rename=scene_save_path)
                cmds.file(save=True, type="mayaBinary")
                print(f"💾 场景已保存为：{scene_save_path}")
            else:
                cmds.warning("取消保存场景。")

        # ---------- ✅ 然后执行 playblast ----------
        start = cmds.playbackOptions(q=True, min=True)
        end = cmds.playbackOptions(q=True, max=True)

        cmds.playblast(
            format="qt",
            filename=video_path,
            forceOverwrite=True,
            sequenceTime=False,
            clearCache=True,
            viewer=True,
            showOrnaments=False,
            offScreen=True,
            combineSound=True,
            framePadding=0,
            percent=100,
            compression="H.264",
            quality=100,
            widthHeight=(1950, 900),
            startTime=start,
            endTime=end
        )

        print(f"✅ Playblast 输出完成：{video_path}")
    # === Facial Camera Creator ===
    def _build_facial_camera_tab(self):
        lay = QtWidgets.QGridLayout(self.facial_cam_tab)

        # 命名空间
        lay.addWidget(QtWidgets.QLabel("Namespace:"), 0, 0)
        self.fc_ns_combo = QtWidgets.QComboBox()
        self._fc_update_namespace_list()
        btn_refresh = QtWidgets.QPushButton("⟳")
        btn_refresh.setFixedWidth(30)
        btn_refresh.setToolTip("refrash")
        btn_refresh.clicked.connect(self._fc_update_namespace_list)

        ns_row = QtWidgets.QHBoxLayout()
        ns_row.addWidget(self.fc_ns_combo)
        ns_row.addWidget(btn_refresh)
        lay.addLayout(ns_row, 0, 1, 1, 2)

        # 偏移默认改为 0 2 37 / 0 0 0
        def spin(init=0.0):
            s = QtWidgets.QDoubleSpinBox()
            s.setRange(-100000.0, 100000.0)
            s.setDecimals(3)
            s.setValue(float(init))
            s.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
            s.setFixedWidth(80)
            return s

        lay.addWidget(QtWidgets.QLabel("Translate X/Y/Z"), 1, 0)
        self.fc_tx, self.fc_ty, self.fc_tz = spin(0), spin(2), spin(37)
        tr_row = QtWidgets.QHBoxLayout()
        tr_row.addWidget(self.fc_tx);
        tr_row.addWidget(self.fc_ty);
        tr_row.addWidget(self.fc_tz)
        lay.addLayout(tr_row, 1, 1, 1, 2)

        lay.addWidget(QtWidgets.QLabel("Rotate X/Y/Z"), 2, 0)
        self.fc_rx, self.fc_ry, self.fc_rz = spin(0), spin(0), spin(0)
        rt_row = QtWidgets.QHBoxLayout()
        rt_row.addWidget(self.fc_rx);
        rt_row.addWidget(self.fc_ry);
        rt_row.addWidget(self.fc_rz)
        lay.addLayout(rt_row, 2, 1, 1, 2)

        btn_create = QtWidgets.QPushButton("Create Facial Camera")
        btn_create.clicked.connect(self._fc_create_camera)
        lay.addWidget(btn_create, 3, 1, 1, 2)

    def _fc_update_namespace_list(self):
        """仅列出以 _face 结尾的命名空间"""
        self.fc_ns_combo.clear()
        self.fc_ns_combo.addItem("")  # 空=无命名空间
        namespaces = set()
        for obj in cmds.ls():
            if ":" in obj:
                ns = obj.split(":", 1)[0]
                if ns and not ns.startswith("shared") and ns.endswith("_face"):
                    namespaces.add(ns)
        for ns in sorted(namespaces):
            self.fc_ns_combo.addItem(ns)

    def _fc_target_name(self, ns, short):
        """拼装带命名空间的名字"""
        return f"{ns}:{short}" if ns else short

    def _fc_create_camera(self):
        # 目标控制器
        ns = self.fc_ns_combo.currentText().strip()
        target = f"{ns}:pointCtrl_Nose" if ns else "pointCtrl_Nose"
        if not cmds.objExists(target):
            QtWidgets.QMessageBox.warning(self, "no target", f"cant find：{target}", QtWidgets.QMessageBox.Ok)
            return

        cam_name = f"{ns}_facialCamera" if ns else "facialCamera"
        grp_name = f"{ns}_facialCamera_grp" if ns else "facialCamera_grp"

        # 偏移（默认 0,2,37 / 0,0,0）
        tx, ty, tz = self.fc_tx.value(), self.fc_ty.value(), self.fc_tz.value()
        rx, ry, rz = self.fc_rx.value(), self.fc_ry.value(), self.fc_rz.value()

        def _delete_constraints(node):
            for c in cmds.listRelatives(node, type="constraint", p=True) or []:
                try:
                    cmds.delete(c)
                except:
                    pass

        # —— AE/刷新 规避：清选择 + 挂起刷新 ——
        prev_sel = cmds.ls(sl=True) or []
        cmds.select(clear=True)
        cmds.refresh(suspend=True)
        try:
            # 相机：复用或新建
            if cmds.objExists(cam_name):
                cam = cam_name
                try:
                    cmds.parent(cam, w=True)
                except:
                    pass
                _delete_constraints(cam)
            else:
                cam, _ = cmds.camera()
                cam = cmds.rename(cam, cam_name)
            try:
                cmds.setAttr(f"{cam}.nearClipPlane", 10)
            except:
                pass
            # 组：复用或新建
            if cmds.objExists(grp_name):
                grp = grp_name
                try:
                    cmds.parent(grp, w=True)
                except:
                    pass
                _delete_constraints(grp)
            else:
                grp = cmds.createNode("transform", name=grp_name)

            # 相机放入组，相机本地归零
            try:
                cmds.parent(cam, grp)
            except:
                pass
            for a in ("tx", "ty", "tz", "rx", "ry", "rz"):
                try:
                    cmds.setAttr(f"{cam}.{a}", 0)
                except:
                    pass

            # ——关键：把组临时挂到目标下，在“局部空间”施加偏移——
            try:
                cmds.parent(grp, target)
            except:
                pass
            # 组在目标下归零
            for a in ("tx", "ty", "tz", "rx", "ry", "rz"):
                try:
                    cmds.setAttr(f"{grp}.{a}", 0)
                except:
                    pass
            # 局部偏移
            cmds.setAttr(f"{grp}.translateX", tx)
            cmds.setAttr(f"{grp}.translateY", ty)
            cmds.setAttr(f"{grp}.translateZ", tz)
            cmds.setAttr(f"{grp}.rotateX", rx)
            cmds.setAttr(f"{grp}.rotateY", ry)
            cmds.setAttr(f"{grp}.rotateZ", rz)

            # 放回世界根
            try:
                cmds.parent(grp, w=True)
            except:
                pass

            # 由目标驱动组（保持偏移）
            _delete_constraints(grp)
            cmds.parentConstraint(target, grp, mo=True)

            print(f"✅ fin：{grp_name} <- parentConstraint(mo=True) <- {target}，camera：{cam_name}")


        finally:
            cmds.refresh(suspend=False)
            # 仅当 refreshAE 存在时才调用，避免 NameError
            try:
                cmds.evalDeferred(lambda: mel.eval('if (`exists refreshAE`) refreshAE;'))
            except:
                pass
            # 恢复选择
            try:
                if prev_sel:
                    cmds.select(prev_sel, r=True)
                else:
                    cmds.select(clear=True)
            except:
                pass
            # —— 最后选择相机 ——
            try:
                cmds.select(cam, r=True)
            except:
                pass

LOtool = LOtool()