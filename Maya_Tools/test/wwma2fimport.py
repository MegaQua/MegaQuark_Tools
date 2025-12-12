import json
from PySide2 import QtWidgets, QtCore

class MyWindow(QtWidgets.QWidget):

    def __init__(self):
        super(MyWindow, self).__init__()
        self.setWindowTitle("Facial Animation Importer for Maya 2020")

        # Facial Animation JSON Path
        label_facialAnim = QtWidgets.QLabel("Facial Animation JSON:")
        self.text_facialAnimPath = QtWidgets.QLineEdit()
        self.text_facialAnimPath.setReadOnly(True)  # 使文本框不可编辑
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

        # Checkboxes
        self.checkbox_importWAV = QtWidgets.QCheckBox("Import WAV File")
        self.checkbox_onlyFirstFrame = QtWidgets.QCheckBox("Only First Frame")

        # Import Button
        button_import = QtWidgets.QPushButton("Import")
        # 注意：这里应该连接到执行导入逻辑的函数，而不是浏览文件的函数
        button_import.clicked.connect(self.browseFacialAnimation)

        button_export_blendshape_data = QtWidgets.QPushButton("Import")
        button_export_blendshape_data.clicked.connect(self.export_blendshape_data)
        # Layout
        layout = QtWidgets.QGridLayout()
        layout.addWidget(label_facialAnim, 0, 0)
        layout.addWidget(self.text_facialAnimPath, 0, 1)
        layout.addWidget(button_browseFacialAnim, 0, 2)

        layout.addWidget(self.label_frameLength, 1, 0, 1, 3)

        layout.addWidget(label_startFrame, 2, 0)
        layout.addWidget(self.text_startFrame, 2, 1, 1, 2)

        layout.addWidget(label_importLength, 3, 0)
        layout.addWidget(self.text_importLength, 3, 1, 1, 2)

        # 将复选框并列
        layout.addWidget(self.checkbox_importWAV, 4, 0)
        layout.addWidget(self.checkbox_onlyFirstFrame, 4, 1)

        # 将导入按钮放在右下角
        layout.addWidget(button_export_blendshape_data, 5, 1)
        layout.addWidget(button_import, 5, 2)

        self.setLayout(layout)
        self.show()
    def a2fjsonpath(self):
        # 浏览和选择 JSON 文件，更新文本框内容为选中的文件路径
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Facial Animation JSON", "", "JSON Files (*.json)")
        if filePath:
            self.text_facialAnimPath.setText(filePath)
            # 可在此处调用更新帧长度的函数，例如 self.updateFrameLength(filePath)
    def browseFacialAnimation(self):
        try:
            startframe =int(self.text_startFrame.text())
        except:
            QtWidgets.QMessageBox.warning(self, "", "Invalid input for start frame", QtWidgets.QMessageBox.Ok)
            return


        #a2f_json_path = 'C:/Users/justcause/Desktop/wwm_a2f_export_test.json'
        a2f_json_path =self.text_facialAnimPath.text()
        wwm_setting_path = 'S:/Public/qiu_yi/JCQ_Tool/data/wwmarkit52.json'

        # 读取JSON文件
        with open(a2f_json_path, 'r') as file:
            a2f_json_data = json.load(file)
        with open(wwm_setting_path, 'r') as file:
            setting_data = json.load(file)

        # 获取动画长度、表情名称和权重矩阵
        numFrames = a2f_json_data['numFrames']
        facsNames = a2f_json_data['facsNames']
        weightMat = a2f_json_data['weightMat']

        # 命名空间
        namespace = "wanjia_male"

        # 遍历每一帧
        for frame_index in range(numFrames):
            controller_values = {}  # 重置为当前帧的控制器属性数值

            # 遍历所有表情名字与权重
            for facsIndex, facsName in enumerate(facsNames):
                weight = weightMat[frame_index][facsIndex]  # 获取当前帧当前表情的权重
                if weight == 0:
                    continue  # 权重为0则跳过

                # 获取b中对应表情名的键的键值
                if facsName in setting_data:
                    facs_values = setting_data[facsName]  # 这是一个字典，键为控制器名字，值为属性数值字典
                    for controller, attrs in facs_values.items():
                        for attr, value in attrs.items():
                            weighted_value = weight * value
                            # 累加到控制器的属性数值上
                            controller_values.setdefault(controller, {}).setdefault(attr, 0)
                            controller_values[controller][attr] += weighted_value

            # 为每个控制器的属性设置关键帧
            for controller, attrs in controller_values.items():
                for attr, value in attrs.items():
                    controller_with_namespace = "{}:{}".format(namespace, controller)
                    cmds.setAttr("{}.{}".format(controller_with_namespace, attr), value)
                    cmds.setKeyframe("{}.{}".format(controller_with_namespace, attr), time=(frame_index,))
        QtWidgets.QMessageBox.warning(self, "", "successed" , QtWidgets.QMessageBox.Ok)
    def test52(self,blendshape_node='blendShape1'):

        arkit52list = [
            'eyeBlinkLeft', 'eyeLookDownLeft', 'eyeLookInLeft', 'eyeLookOutLeft', 'eyeLookUpLeft',
            'eyeSquintLeft', 'eyeWideLeft', 'eyeBlinkRight', 'eyeLookDownRight', 'eyeLookInRight',
            'eyeLookOutRight', 'eyeLookUpRight', 'eyeSquintRight', 'eyeWideRight', 'jawForward',
            'jawLeft', 'jawRight', 'jawOpen', 'mouthClose', 'mouthFunnel', 'mouthPucker',
            'mouthLeft', 'mouthRight', 'mouthSmileLeft', 'mouthSmileRight', 'mouthFrownLeft',
            'mouthFrownRight', 'mouthDimpleLeft', 'mouthDimpleRight', 'mouthStretchLeft',
            'mouthStretchRight', 'mouthRollLower', 'mouthRollUpper', 'mouthShrugLower',
            'mouthShrugUpper', 'mouthPressLeft', 'mouthPressRight', 'mouthLowerDownLeft',
            'mouthLowerDownRight', 'mouthUpperUpLeft', 'mouthUpperUpRight', 'browDownLeft',
            'browDownRight', 'browInnerUp', 'browOuterUpLeft', 'browOuterUpRight', 'cheekPuff',
            'cheekSquintLeft', 'cheekSquintRight', 'noseSneerLeft', 'noseSneerRight', 'tongueOut'
        ]
        num_targets = len(arkit52list)

        for i in range(num_targets):
            # 重置所有子节点的权重为0
            for target in arkit52list:
                cmds.setAttr("{}.{}".format(blendshape_node, target), 0)

            # 设置当前子节点的权重为1
            current_target = arkit52list[i]
            cmds.setAttr("{}.{}".format(blendshape_node, current_target), 1)

            # 在当前帧为所有子节点设置关键帧
            for target in arkit52list:
                cmds.setKeyframe("{}.{}".format(blendshape_node, target), time=(i + 1,))

        # 调用函数
        #set_blendshape_keyframes('blendShape1')


    def export_blendshape_data(self,blendshape_node='shapes', start_frame=1, end_frame=10):
        # 获取场景的帧率
        time_unit = cmds.currentUnit(query=True, time=True)
        if time_unit == 'film':
            fps = 24
        elif time_unit == 'pal':
            fps = 25
        elif time_unit == 'ntsc':
            fps = 30
        else:
            fps = 24  # 默认使用24，或者根据需要修改
        arkit52list_FaceCap =  {
            'eyeBlinkLeft': 'eyeBlink_L',
            'eyeLookDownLeft': 'eyeLookDown_L',
            'eyeLookInLeft': 'eyeLookIn_L',
            'eyeLookOutLeft': 'eyeLookOut_L',
            'eyeLookUpLeft': 'eyeLookUp_L',
            'eyeSquintLeft': 'eyeSquint_L',
            'eyeWideLeft': 'eyeWide_L',
            'eyeBlinkRight': 'eyeBlink_R',
            'eyeLookDownRight': 'eyeLookDown_R',
            'eyeLookInRight': 'eyeLookIn_R',
            'eyeLookOutRight': 'eyeLookOut_R',
            'eyeLookUpRight': 'eyeLookUp_R',
            'eyeSquintRight': 'eyeSquint_R',
            'eyeWideRight': 'eyeWide_R',
            'jawForward': 'jawForward',
            'jawLeft': 'jawLeft',
            'jawRight': 'jawRight',
            'jawOpen': 'jawOpen',
            'mouthClose': 'mouthClose',
            'mouthFunnel': 'mouthFunnel',
            'mouthPucker': 'mouthPucker',
            'mouthLeft': 'mouthLeft',
            'mouthRight': 'mouthRight',
            'mouthSmileLeft': 'mouthSmile_L',
            'mouthSmileRight': 'mouthSmile_R',
            'mouthFrownLeft': 'mouthFrown_L',
            'mouthFrownRight': 'mouthFrown_R',
            'mouthDimpleLeft': 'mouthDimple_L',
            'mouthDimpleRight': 'mouthDimple_R',
            'mouthStretchLeft': 'mouthStretch_L',
            'mouthStretchRight': 'mouthStretch_R',
            'mouthRollLower': 'mouthRollLower',
            'mouthRollUpper': 'mouthRollUpper',
            'mouthShrugLower': 'mouthShrugLower',
            'mouthShrugUpper': 'mouthShrugUpper',
            'mouthPressLeft': 'mouthPress_L',
            'mouthPressRight': 'mouthPress_R',
            'mouthLowerDownLeft': 'mouthLowerDown_L',
            'mouthLowerDownRight': 'mouthLowerDown_R',
            'mouthUpperUpLeft': 'mouthUpperUp_L',
            'mouthUpperUpRight': 'mouthUpperUp_R',
            'browDownLeft': 'browDown_L',
            'browDownRight': 'browDown_R',
            'browInnerUp': 'browInnerUp',
            'browOuterUpLeft': 'browOuterUp_L',
            'browOuterUpRight': 'browOuterUp_R',
            'cheekPuff': 'cheekPuff',
            'cheekSquintLeft': 'cheekSquint_L',
            'cheekSquintRight': 'cheekSquint_R',
            'noseSneerLeft': 'noseSneer_L',
            'noseSneerRight': 'noseSneer_R',
            'tongueOut': 'tongueOut',
            }

        # 初始化结果字典
        result = {
            "exportFps": fps,
            "numPoses": len(arkit52list_FaceCap),
            "numFrames": end_frame - start_frame + 1,
            "weightMat": []
        }

        # 遍历每一帧
        for frame in range(start_frame, end_frame + 1):
            cmds.currentTime(frame)  # 设置当前时间为frame
            frame_weights = []
            # 遍历每个blendShape目标
            for target in arkit52list_FaceCap.keys():
                weight = cmds.getAttr(f"{blendshape_node}.{arkit52list_FaceCap[target]}")
                frame_weights.append(weight)
            result["weightMat"].append(frame_weights)

        print(result)
window = MyWindow()