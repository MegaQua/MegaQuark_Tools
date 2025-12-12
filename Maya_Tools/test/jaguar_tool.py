# coding: utf-8
import maya.cmds as cmds
from PySide2 import QtWidgets, QtGui, QtCore
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox
import json


class MyWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MyWindow, self).__init__(None)
        self.setWindowTitle("WWM tool for maya 2020")

        # 创建一个选项卡部件
        self.tabs = QtWidgets.QTabWidget()
        Export_Tab = QtWidgets.QWidget()
        Import_Tab = QtWidgets.QWidget()

        # 将选项卡添加到选项卡部件中
        self.tabs.addTab(Export_Tab, "vcam to rig cam")
        self.tabs.addTab(Import_Tab, "camera keyframe playblast")

        # Tab1
        Export_Tab.layout = QtWidgets.QGridLayout()

        # 创建按钮
        label_path = QtWidgets.QLabel("exportpath:")
        self.text_path = QtWidgets.QLineEdit(self)
        self.text_path.setReadOnly(True)
        button_path = QtWidgets.QPushButton("Browse export Folder", self)
        button_path.clicked.connect(lambda: self.browse(self.text_path))

        label_file = QtWidgets.QLabel("final file name:")
        self.label_file_finalname = QtWidgets.QLabel("")
        #button_autonameflie = QtWidgets.QPushButton("auto name", self)

        tab1_comboBox_target = QComboBox()
        tab1_comboBox_target.addItem("wanjia_male")
        tab1_comboBox_target.addItem("yidao")
        tab1_comboBox_target.setCurrentIndex(0)  # 设置默认选中的项
        tab1_comboBox_target.setEditable(True)  # 让下拉菜单可编辑

        label_costom = QtWidgets.QLabel("file name:")
        self.tab1_text_input = QtWidgets.QLineEdit(self)
        self.tab1_text_input.setReadOnly(False)
        self.tab1_text_input.textChanged.connect(self.updatefilename)
        #button2 = QtWidgets.QPushButton("get cam rig GP", self)
        #button2.clicked.connect(self.get_cam_rig_GP)
        #self.text2 = QtWidgets.QLineEdit(self)
        #self.text2.setReadOnly(True)

        button_export = QtWidgets.QPushButton("export", self)
        button_export.clicked.connect(self.exportfacial)

        # 创建布局
        layout = QtWidgets.QGridLayout()

        Export_Tab.layout.addWidget(label_path, 0, 0)
        Export_Tab.layout.addWidget(self.text_path, 0, 1,1,3)
        Export_Tab.layout.addWidget(button_path, 0, 4)

        Export_Tab.layout.addWidget(label_file, 1, 0)
        Export_Tab.layout.addWidget(self.label_file_finalname, 1, 1,1,4)
        #Export_Tab.layout.addWidget(button_autonameflie, 1, 4)

        #Export_Tab.layout.addWidget(tab1_comboBox_target, 2, 0)
        Export_Tab.layout.addWidget(label_costom, 2, 0)
        Export_Tab.layout.addWidget(self.tab1_text_input, 2, 1,1,2)
        Export_Tab.layout.addWidget(button_export, 2, 4)

        # Tab2

        Tab2_label_path = QtWidgets.QLabel("import flie:")
        self.Tab2_text_path = QtWidgets.QLineEdit(self)
        self.Tab2_text_path.setReadOnly(True)
        Tab2_button_path = QtWidgets.QPushButton("Browse json flie", self)
        Tab2_button_path.clicked.connect(lambda: self.browsejson(self.Tab2_text_path))
        #Export_Tab.clicked.connect(lambda: self.browse(self.Tab2_text_path))

        Tab2_label_namespace = QtWidgets.QLabel("namespace:")
        self.tab2_comboBox_namespace = QComboBox()

        self.tab2_comboBox_namespace.addItem("wanjia_male:")
        self.tab2_comboBox_namespace.addItem("yidao:")
        self.tab2_comboBox_namespace.addItem("")
        self.tab2_comboBox_namespace.setCurrentIndex(0)  # 设置默认选中的项
        self.tab2_comboBox_namespace.setEditable(True)  # 让下拉菜单可编辑

        self.Tab2_label_start_frame = QtWidgets.QLabel("start frame")
        self.Tab2_text_start_frame = QtWidgets.QLineEdit(self)
        self.Tab2_text_start_frame.setText("0")
        self.Tab2_text_start_frame.setReadOnly(False)
        self.Tab2_text_start_frame.textChanged.connect(self.text_start_frame_change)

        self.Tab2_json_frame_length = QtWidgets.QLabel("animetion length:None")

        tab2_button_import = QtWidgets.QPushButton("import", self)
        tab2_button_import.clicked.connect(self.importfacial)

        Export_Tab.setLayout(Export_Tab.layout)

        # 第二个标签先留空
        Import_Tab.layout = QtWidgets.QGridLayout()
        # 在这里可以添加tab2的内容...
        Import_Tab.layout.addWidget(Tab2_label_path, 0, 0)
        Import_Tab.layout.addWidget(self.Tab2_text_path, 0, 1,1,3)
        Import_Tab.layout.addWidget(Tab2_button_path, 0, 4)

        Import_Tab.layout.addWidget(Tab2_label_namespace, 1, 0)
        Import_Tab.layout.addWidget(self.tab2_comboBox_namespace, 1, 1)
        Import_Tab.layout.addWidget(self.Tab2_label_start_frame, 1, 2)
        Import_Tab.layout.addWidget(self.Tab2_text_start_frame, 1, 3)

        Import_Tab.layout.addWidget(self.Tab2_json_frame_length, 2, 0,1,3)
        Import_Tab.layout.addWidget(tab2_button_import, 2, 4)

        Import_Tab.setLayout(Import_Tab.layout)

        # 设置主布局
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.tabs)
        self.setLayout(mainLayout)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)  # 设置窗口置顶
        self.resize(600, 100)
        self.show()
        self.updatefilename()
    def text_start_frame_change(self):
        text=self.Tab2_text_start_frame.text()
        try :
            int(text)
        except:
            if not text:
                pass
            else:
                self.Tab2_text_start_frame.setText("0")
    def getframelength(self,path):
        with open(path, "r") as f:
            json_data = json.loads(f.read())
        max_diff=0
        for key, value in json_data.items():
            for key1, value1 in value.items():
                if isinstance(value1, dict):
                    # 如果找到 'frame' 键
                    if 'frame' in value1 and isinstance(value1['frame'], list):
                        # 获取 frame 列表中的最大值和最小值
                        max_value = max(value1['frame'])
                        min_value = min(value1['frame'])
                        # 计算差值
                        diff = max_value - min_value
                        # 更新最大差值
                        max_diff = int(max(max_diff, diff))
        self.Tab2_json_frame_length.setText("animetion length:"+str(max_diff))
    def browse(self,targetText):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Folder", "")
        if folder_path:
            targetText.setText(folder_path)
        self.updatefilename()
    def browsejson(self,targetText):

        file_filter = "JSON Files (*.json)"
        folder_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select JSON File", "", file_filter)
        if folder_path:
            targetText.setText(folder_path)
        self.updatefilename()
        self.getframelength(folder_path)
    def exportfacial(self):
        objs = ['cn_mouthAll_ctrl',
                  'lf_EyeSqz_ctrl',
                  'rt_UprLid_ctrl',
                  'rt_eyeBall_ctrl',
                  'rt_cheek_ctrl',
                  'lf_mouthLip_up_ctrl',
                  'lf_mouthLip_dn_ctrl',
                  'rt_uppersocket1_ctrl',
                  'eye_aim_ctrl',
                  'lf_mouthLip_conner_ctrl',
                  'rt_BrowOut_ctrl',
                  'cn_mouthLip_dn_ctrl',
                  'lf_uppersocket1_ctrl',
                  'lf_BrowIn_ctrl',
                  'lf_uppersocket3_ctrl',
                  'lf_Muzzle_ctrl',
                  'lf_LwrLid_ctrl',
                  'cn_lwrLip_ctrl',
                  'rt_EyeSqz_ctrl',
                  'rt_mouthLip_dn_ctrl',
                  'rt_BrowIn_ctrl',
                  'cn_chin_ctrl',
                  'cn_eyeBrown_ctrl',
                  'lf_cheek_ctrl',
                  'rt_mouthLip_conner_ctrl',
                  'rt_mouth_conner_ctrl',
                  'rt_MouthCorner02_ctrl',
                  'lf_MouthCorner02_ctrl',
                  'lf_UprLid_ctrl',
                  'lf_uppersocket2_ctrl',
                  'rt_uppersocket2_ctrl',
                  'lf_MouthCorner_ctrl',
                  'cn_jaw_ctrl',
                  'cn_trans_nose_ctrl',
                  'rt_LwrLid_ctrl',
                  'cn_forehead_ctrl',
                  'lf_BrowOut_ctrl',
                  'lf_Nose_ctrl',
                  'cn_nose_ctrl',
                  'lf_eyeBall_ctrl',
                  'lf_mouth_conner_ctrl',
                  'rt_mouthLip_up_ctrl',
                  'rt_uppersocket3_ctrl',
                  'cn_lip_ctrl',
                  'rt_Muzzle_ctrl',
                  'cn_mouthLip_up_ctrl',
                  'cn_uprLip_ctrl',
                  'rt_Nose_ctrl',
                  'rt_MouthCorner_ctrl',]
        startFrames = cmds.playbackOptions(query=True, minTime=True)
        endFrames = cmds.playbackOptions(query=True, maxTime=True)
        savepath = self.text_path.text() + "/" + self.tab1_text_input.text()+".json"

        json_file = {}
        for obj in objs:
            attributes = cmds.listAttr(obj, keyable=True)
            attr_data = {}

            if attributes:  # 确保 attributes 不是 None
                for attr in attributes:
                    item = obj + '.' + attr
                    # 检查属性
                    if cmds.keyframe(item, query=True, keyframeCount=True) > 0 and attr != "visibility":
                        key_frame = cmds.keyframe(item, query=True, time=(startFrames, endFrames))
                        if key_frame:
                            data = {
                                "frame": [],
                                "value": [],
                                "in_tangent_type": [],
                                "out_tangent_type": [],
                                "in_weight": [],
                                "out_weight": [],
                                "in_angle": [],
                                "out_angle": [],
                            }

                            for frame in key_frame:
                                value = cmds.keyframe(item, query=True, time=(frame, frame), valueChange=True)[0]
                                in_tangent_type = cmds.keyTangent(item, time=(frame, frame), query=True, inTangentType=True)[0]
                                out_tangent_type = cmds.keyTangent(item, time=(frame, frame), query=True, outTangentType=True)[0]
                                in_weight = cmds.keyTangent(item, time=(frame, frame), query=True, inWeight=True)[0]
                                out_weight = cmds.keyTangent(item, time=(frame, frame), query=True, outWeight=True)[0]
                                in_angle = cmds.keyTangent(item, time=(frame, frame), query=True, inAngle=True)[0]
                                out_angle = cmds.keyTangent(item, time=(frame, frame), query=True, outAngle=True)[0]

                                data["frame"].append(frame)
                                data["value"].append(value)
                                data["in_tangent_type"].append(in_tangent_type.encode('utf-8'))
                                data["out_tangent_type"].append(out_tangent_type.encode('utf-8'))
                                data["in_weight"].append(in_weight)
                                data["out_weight"].append(out_weight)
                                data["in_angle"].append(in_angle)
                                data["out_angle"].append(out_angle)

                            if attr in ["TransksteX","translateY","translateZ","rotateX","rotateY","rotateZ"]:
                                if  any(data["value"]):
                                    attr_data[attr.encode('utf-8')] = data
                            elif attr in ["scaleX","scaleY","scaleZ"]:
                                if not all(value == 1 for value in data["value"]):
                                    attr_data[attr.encode('utf-8')] = data
                            else:
                                attr_data[attr.encode('utf-8')] = data

            if attr_data:
                json_file[obj] = attr_data

            # save json

        jsonfile = json.dumps(json_file, indent=4, separators=(',', ':'))

        filenew = open(savepath, 'w')
        filenew.write(jsonfile)
        filenew.close()
        QtWidgets.QMessageBox.warning(self, "", "export successed.", QtWidgets.QMessageBox.Ok)

        pass
    def importfacial(self):
        filepath = self.Tab2_text_path.text()
        text = self.Tab2_text_start_frame.text()
        if text:
            start_frame = int(self.Tab2_text_start_frame.text())
        else:
            start_frame = 0
        #end_frame=500


        namespace = self.tab2_comboBox_namespace.currentText()
        if not cmds.objExists(namespace+"model"):
            QtWidgets.QMessageBox.warning(self, "", namespace+"does not exist.", QtWidgets.QMessageBox.Ok)
            return
        if not os.path.exists(filepath):
            QtWidgets.QMessageBox.warning(self, "", filepath+"does not exist.", QtWidgets.QMessageBox.Ok)
            return

        with open(filepath, "r") as f:
            json_data = json.loads(f.read())
            #objs = list(json_data.keys())
            #char=self.tab2_comboBox_target.currentText()
            fullname=namespace


        for obj, value1 in json_data.items():
            for attr, value2 in value1.items():

                frame_list = value2["frame"]
                value_list = value2["value"]
                in_tangent_type_list = value2["in_tangent_type"]
                out_tangent_type_list = value2["out_tangent_type"]
                in_weight_list = value2["in_weight"]
                out_weight_list = value2["out_weight"]
                in_angle_list = value2["in_angle"]
                out_angle_list = value2["out_angle"]

                anim_curve_attr = namespace+obj+"."+attr
                #print anim_curve_attr




                for j, k in enumerate(frame_list):
                    value = value_list[j]
                    time = start_frame + k
                    cmds.setKeyframe(anim_curve_attr, time=time, value=value, inTangentType="auto", outTangentType="auto")
                    cmds.keyTangent(anim_curve_attr, edit=True, time=(time, time), inWeight=in_weight_list[j], outWeight=out_weight_list[j])
                    cmds.keyTangent(anim_curve_attr, edit=True, time=(time, time), inAngle=in_angle_list[j], outAngle=out_angle_list[j])
                    cmds.keyTangent(anim_curve_attr, edit=True, time=(time, time), inTangentType=in_tangent_type_list[j],
                                    outTangentType=out_tangent_type_list[j])
        QtWidgets.QMessageBox.warning(self, "", "import successed.", QtWidgets.QMessageBox.Ok)
    def updatefilename(self):
        finaltext = self.text_path.text() + "/" + self.tab1_text_input.text()+".json"
        #finaltext = self.text_path.text()
        self.label_file_finalname.setText(finaltext)
    def updatescencename(self):
        pass

# 创建窗口实例
window = MyWindow()
