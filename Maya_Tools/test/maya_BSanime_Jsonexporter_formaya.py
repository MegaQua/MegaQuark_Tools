import maya.cmds as cmds
from PySide2 import QtWidgets, QtGui, QtCore
import json
import os


class MR_Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BS animation json export")

        layout = QtWidgets.QGridLayout(self)

        # 第一行
        start_frame_label = QtWidgets.QLabel("start frame")
        self.start_frame_text = QtWidgets.QLineEdit()
        end_frame_label = QtWidgets.QLabel("end frame")
        self.end_frame_text = QtWidgets.QLineEdit()
        set_from_scene_btn = QtWidgets.QPushButton("set from scene")
        layout.addWidget(start_frame_label, 0, 0)
        layout.addWidget(self.start_frame_text, 0, 1)
        layout.addWidget(end_frame_label, 0, 2)
        layout.addWidget(self.end_frame_text, 0, 3)
        layout.addWidget(set_from_scene_btn, 0, 4)

        # 第二行
        target_name_label = QtWidgets.QLabel("target name")
        self.sceneBS_list = QtWidgets.QComboBox()
        blendshapes = cmds.ls(type="blendShape")
        for i in blendshapes:
            self.sceneBS_list.addItem(i)
        layout.addWidget(target_name_label, 1, 0)
        layout.addWidget(self.sceneBS_list, 1, 1)
        set_start_frame_now_btn = QtWidgets.QPushButton("set start frame now")
        self.one_frame_checkbox = QtWidgets.QCheckBox("only start frame")
        self.one_frame_checkbox.setChecked(False)
        layout.addWidget(set_start_frame_now_btn, 1, 3)
        layout.addWidget(self.one_frame_checkbox, 1, 2)

        # 第三行
        export_path_label = QtWidgets.QLabel("export path")
        self.export_path_text = QtWidgets.QLineEdit(cmds.workspace(q=True, rd=True))
        browse_btn = QtWidgets.QPushButton("Browse")
        layout.addWidget(export_path_label, 2, 0)
        layout.addWidget(self.export_path_text, 2, 1, 1, 3)
        layout.addWidget(browse_btn, 2, 4)

        # 第四行
        filename_label = QtWidgets.QLabel("file name")
        self.filename_text = QtWidgets.QLineEdit()
        auto_name_btn = QtWidgets.QPushButton("Auto Name")
        layout.addWidget(filename_label, 3, 0)
        layout.addWidget(self.filename_text, 3, 1, 1, 2)
        layout.addWidget(auto_name_btn, 3, 3)

        # 第五行
        self.checkbox_with_image = QtWidgets.QCheckBox("with image")
        self.checkbox_with_image.setChecked(True)
        export_btn = QtWidgets.QPushButton("Export")
        layout.addWidget(self.checkbox_with_image, 4, 3)
        layout.addWidget(export_btn, 4, 4)

        # 为所有按钮连接临时函数
        set_from_scene_btn.clicked.connect(self.update_start_end_frame)
        set_start_frame_now_btn.clicked.connect(self.set_start_frame_now)
        browse_btn.clicked.connect(self.browse_path)
        auto_name_btn.clicked.connect(self.auto_nameing)
        export_btn.clicked.connect(self.exportBSbyJson)

        # 设置窗口置顶
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        self.show()

    def set_start_frame_now(self):
        current_frame = cmds.currentTime(query=True)
        self.start_frame_text.setText(str(int(current_frame)))
        self.one_frame_checkbox.setChecked(True)
        self.end_frame_text.setText("")

    def update_start_end_frame(self):
        start_frame = cmds.playbackOptions(query=True, minTime=True)
        end_frame = cmds.playbackOptions(query=True, maxTime=True)
        self.start_frame_text.setText(str(int(start_frame)))
        self.end_frame_text.setText(str(int(end_frame)))
        self.one_frame_checkbox.setChecked(False)

    def browse_path(self):
        path = cmds.workspace(q=True, rd=True)
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder", path)
        if not folder_path.endswith("/"):
            folder_path += "/"
        if folder_path:
            self.export_path_text.setText(folder_path)

    def auto_nameing(self):
        scene_path = cmds.file(query=True, sceneName=True)
        scene_name = os.path.basename(scene_path)
        scene_name = os.path.splitext(scene_name)[0]
        one_frame = self.one_frame_checkbox.isChecked()
        start_frame = self.start_frame_text.text()
        end_frame = self.end_frame_text.text()
        BSname = self.sceneBS_list.currentText()
        # print(scene_name,start_frame,end_frame)
        if not one_frame:
            autoname = scene_name + "_" + BSname + "_" + start_frame + "_" + end_frame
            self.filename_text.setText(autoname.replace(":", "_"))
        else:
            autoname = scene_name + "_" + BSname + "_" + start_frame
            self.filename_text.setText(autoname.replace(":", "_"))

    def temp_function(self):
        sender = self.sender()
        print(f"{sender.text()} clicked")

    def save_image(self):
        folder_path = self.export_path_text.text()
        filename = self.filename_text.text()

        save_path = folder_path + filename
        current_frame = cmds.currentTime(query=True)
        camera_panel = cmds.getPanel(withFocus=True)
        widthheight = [200, 200]

        file_path = save_path + ".png"
        if os.path.exists(file_path):
            os.remove(file_path)

        cmds.playblast(filename=save_path,
                       format="image",
                       compression="png",
                       viewer=False,
                       percent=100,
                       quality=100,
                       widthHeight=widthheight,
                       forceOverwrite=True,
                       offScreen=True,
                       showOrnaments=False,
                       framePadding=0,
                       frame=current_frame)
        os.rename(save_path + ".0.png", save_path + ".png")
        print("Viewport image saved as:", save_path)

    def exportBSbyJson(self):
        # get data from scene
        BSname = self.sceneBS_list.currentText()
        startFrames = int(self.start_frame_text.text())
        endFrames = int(self.end_frame_text.text())
        folder_path = self.export_path_text.text()
        filename = self.filename_text.text()
        savepath = folder_path + filename + ".json"
        print(savepath)
        one_frame = self.one_frame_checkbox.isChecked()
        with_image = self.checkbox_with_image.isChecked()

        if os.path.exists(savepath):
            message_box = QtWidgets.QMessageBox()
            message_box.setIcon(QtWidgets.QMessageBox.Warning)
            message_box.setWindowTitle("File Exists")
            message_box.setText("The file already exists. Do you want to overwrite it?")
            message_box.addButton(QtWidgets.QMessageBox.Yes)
            message_box.addButton(QtWidgets.QMessageBox.No)
            message_box.setDefaultButton(QtWidgets.QMessageBox.No)
            # 设置窗口置顶
            message_box.setWindowFlags(message_box.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

            result = message_box.exec_()

            if result == QtWidgets.QMessageBox.Yes:
                print("User chose to overwrite the file.")
                # Continue with your code here
            else:
                print("User chose not to overwrite the file.")
                # Stop the code or perform any other action
                return

        else:
            print("File does not exist.")

        if with_image:
            self.save_image()

        bslist = cmds.listAttr(BSname + '.w', m=True)
        weightMat = []
        """
        if one_frame:
            numFrames=1
        else:
            numFrames = int(endFrames)  - int(startFrames) +1

        key_times = cmds.keyframe(f"{BSname}.{attr_name}", query=True, time=(startFrames, endFrames))

        # 获取关键帧的值
        key_values = cmds.keyframe(f"{BSname}.{attr_name}", query=True, valueChange=True, time=(startFrames, endFrames))


        if not one_frame:
            for i in range(int(startFrames), int(endFrames)+1):
                cmds.currentTime(i, update=True, edit=True)
                j = []
                for k in bslist:
                    bsweight = cmds.getAttr(BSname + "." + k)
                    if bsweight <= 0.0001:
                        bsweight = 0.0
                    j.append(bsweight)
                weightMat.append(j)
        else:
            cmds.currentTime(int(startFrames), update=True, edit=True)
            j = []
            for k in bslist:
                bsweight = cmds.getAttr(BSname + "." + k)
                j.append(bsweight)
            weightMat.append(j)
        """
        blendshapeNames = []
        key_times_list = []
        key_values_list = []
        in_tangents_list = []
        out_tangents_list = []
        in_weights_list = []
        out_weights_list = []
        in_angles_list = []
        out_angles_list = []
        in_tangents_locked_list = []
        out_tangents_locked_list = []

        for k in bslist:
            anim_curves = cmds.listConnections(f"{BSname}.{k}", type="animCurve")

            if anim_curves:
                anim_curve = anim_curves[0]
                key_time = cmds.keyframe(anim_curve, query=True, time=(startFrames, endFrames))
                key_value = cmds.keyframe(anim_curve, query=True, time=(startFrames, endFrames), valueChange=True)

                in_tangents = []
                out_tangents = []
                in_weights = []
                out_weights = []
                in_angles = []
                out_angles = []
                in_tangents_locked = []
                out_tangents_locked = []

                for index, time in enumerate(key_time):
                    in_tangent = cmds.keyTangent(anim_curve, time=(time, time), query=True, inTangentType=True)[0]
                    out_tangent = cmds.keyTangent(anim_curve, time=(time, time), query=True, outTangentType=True)[0]

                    in_weight = cmds.keyTangent(anim_curve, time=(time, time), query=True, inWeight=True)[0]
                    out_weight = cmds.keyTangent(anim_curve, time=(time, time), query=True, outWeight=True)[0]

                    in_angle = cmds.keyTangent(anim_curve, time=(time, time), query=True, inAngle=True)[0]
                    out_angle = cmds.keyTangent(anim_curve, time=(time, time), query=True, outAngle=True)[0]

                    in_tangents.append(in_tangent)
                    out_tangents.append(out_tangent)
                    in_weights.append(in_weight)
                    out_weights.append(out_weight)
                    in_angles.append(in_angle)
                    out_angles.append(out_angle)

                blendshapeNames.append(k)
                key_times_list.append(key_time)
                key_values_list.append(key_value)
                in_tangents_list.append(in_tangents)
                out_tangents_list.append(out_tangents)
                in_weights_list.append(in_weights)
                out_weights_list.append(out_weights)
                in_angles_list.append(in_angles)
                out_angles_list.append(out_angles)

        print("blendshapeNames")
        print(blendshapeNames)

        print("key_times_list")
        print(key_times_list)
        print("key_values_list")
        print(key_values_list)

        print("in_tangents_list")
        print(in_tangents_list)
        print("out_tangents_list")
        print(out_tangents_list)

        print("in_weights_list")
        print(in_weights_list)
        print("out_weights_list")
        print(out_weights_list)

        print("in_angles_list")
        print(in_angles_list)
        print("out_angles_list")
        print(out_angles_list)

        # create json

        pyjson = {}

        pyjson['blendshapeNames'] = blendshapeNames
        pyjson['key_times_list'] = key_times_list
        pyjson['key_values_list'] = key_values_list
        pyjson['in_tangents_list'] = in_tangents_list
        pyjson['out_tangents_list'] = out_tangents_list
        pyjson['in_weights_list'] = in_weights_list
        pyjson['out_weights_list'] = out_weights_list
        pyjson['in_angles_list'] = in_angles_list
        pyjson['out_angles_list'] = out_angles_list

        print(pyjson)

        # save json
        jsonfile = json.dumps(pyjson, indent=4, separators=(',', ':'))

        # Check if the folder exists, create it if necessary
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        filenew = open(savepath, 'w')
        filenew.write(jsonfile)
        filenew.close()


bsaj_exporter = MR_Window()