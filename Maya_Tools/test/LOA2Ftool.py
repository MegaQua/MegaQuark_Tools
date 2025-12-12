import json
import maya.cmds as cmds
from PySide2 import QtWidgets, QtCore


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

        # Frame Length from JSON
        self.label_frameLength = QtWidgets.QLabel("Frame Length: N/A")

        # Import Start Frame
        label_startFrame = QtWidgets.QLabel("Import Start Frame:")
        self.text_startFrame = QtWidgets.QLineEdit("0")

        # Import Length
        label_importLength = QtWidgets.QLabel("Import Length:")
        self.text_importLength = QtWidgets.QLineEdit("N/A")

        # Namespace Dropdown
        label_namespace = QtWidgets.QLabel("Namespace:")
        self.namespace_combo = QtWidgets.QComboBox()
        self.update_namespace_list()

        # Checkboxes
        self.checkbox_importWAV = QtWidgets.QCheckBox("Import WAV File")
        self.checkbox_onlyFirstFrame = QtWidgets.QCheckBox("Only First Frame")

        # Import Button
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
        layout.addWidget(self.namespace_combo, 4, 1)

        layout.addWidget(self.checkbox_importWAV, 5, 0)
        layout.addWidget(self.checkbox_onlyFirstFrame, 5, 1)

        layout.addWidget(button_import, 6, 2)

        self.setLayout(layout)
        self.show()

    def update_namespace_list(self):
        self.namespace_combo.clear()
        self.namespace_combo.addItem("")  # 第一项为空，表示不使用 namespace
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
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Facial Animation JSON", "", "JSON Files (*.json)")
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

        for frame_index in range(numFrames):  # 顶层循环：每一帧
            controller_values = {}

            for facsIndex, facsName in enumerate(facsNames):  # 表情项
                weight = weightMat[frame_index][facsIndex]
                if weight == 0:
                    continue

                if facsName in setting_data:
                    facs_values = setting_data[facsName]
                    for controller, attrs in facs_values.items():
                        if "Eye" in controller:
                            continue  # 跳过包含 Eye 的控制器名

                        for attr, value in attrs.items():
                            weighted_value = weight * value
                            controller_values.setdefault(controller, {}).setdefault(attr, 0)
                            controller_values[controller][attr] += weighted_value

                            # 限制值在 [-1.0, 1.0]
                            if controller_values[controller][attr] > 1.0:
                                controller_values[controller][attr] = 1.0
                            elif controller_values[controller][attr] < -1.0:
                                controller_values[controller][attr] = -1.0

            # ✅ 此处 frame_index 是当前帧，设置关键帧必须放在这里
            for controller, attrs in controller_values.items():
                for attr, value in attrs.items():
                    if selected_namespace:
                        controller_with_namespace = "{}:{}".format(selected_namespace, controller)
                    else:
                        controller_with_namespace = controller
                    try:
                        cmds.setAttr("{}.{}".format(controller_with_namespace, attr), value)
                        cmds.setKeyframe("{}.{}".format(controller_with_namespace, attr), time=startframe + frame_index)
                        affected_controllers.add(controller_with_namespace.split('.')[0])  # 加入控制器 transform 名

                    except Exception as e:
                        print(f"设置关键帧失败: {controller_with_namespace}.{attr} = {value}，错误：{e}")
            # 设置完成后创建控制器Set
        if selected_namespace:
            set_name = f"{selected_namespace}A2FcontrolerSet"
        else:
            set_name = "A2FcontrolerSet"

        # 设置完成后创建控制器Set（如果不存在才创建并添加）
        if selected_namespace:
            set_name = f"{selected_namespace}A2FcontrolerSet"
        else:
            set_name = "A2FcontrolerSet"

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


window = MyWindow()
