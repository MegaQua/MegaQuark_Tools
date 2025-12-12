from pyfbsdk import *

from PySide2 import QtWidgets, QtGui, QtCore
import os
import re



class PlayblastExporter(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.overwriteflag = 0
        self.setWindowTitle("camera key frame Exporter fot MB_v001")

        layout = QtWidgets.QGridLayout(self)

        # 指定输出文件夹
        output_folder_label = QtWidgets.QLabel("Output Folder:")
        self.output_folder_text = QtWidgets.QLineEdit()
        output_folder_btn = QtWidgets.QPushButton("Browse Output Folder")

        filename_label = QtWidgets.QLabel("filename:")
        self.filename_text = QtWidgets.QLineEdit()
        autoname_btn = QtWidgets.QPushButton("autoname")


        self.checkbox1 = QtWidgets.QCheckBox("render frame now", self)
        self.checkbox1.setChecked(True)  # 默认勾选
        self.checkbox2 = QtWidgets.QCheckBox("render from camera keyframe", self)
        self.checkbox2.setChecked(False)  # 默认勾选
        #self.checkbox3 = QtWidgets.QCheckBox("Separate shake Animation", self)
        #self.checkbox3.setChecked(True)  # 默认勾选
        # 添加 "Select Camera" 文本
        #select_camera_label = QtWidgets.QLabel("Select Camera(s) and then ")
        #select_camera_label.setAlignment(QtCore.Qt.AlignRight)
        # 执行输出
        Render_btn = QtWidgets.QPushButton("Render")
        # 连接按钮的信号
        output_folder_btn.clicked.connect(self.browse_output_folder)
        Render_btn.clicked.connect(self.playblast_frame)

        layout.addWidget(output_folder_label, 0, 0)
        layout.addWidget(self.output_folder_text, 0, 1)
        layout.addWidget(output_folder_btn, 0, 2)
        layout.addWidget(filename_label, 1, 0)
        layout.addWidget(self.filename_text, 1, 1)
        layout.addWidget(autoname_btn, 1, 2)
        layout.addWidget(self.checkbox1, 2, 0)
        layout.addWidget(self.checkbox2, 3, 0)
        layout.addWidget(Render_btn, 3, 2)

        #self.resize(500, 80)  # 设置窗口的默认尺寸
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.show()
    def get_camera_keyframes(self):
        renderer = FBSystem().Renderer
        camera_keyframes = []

        # 获取当前活动的相机
        if renderer.GetPaneCount() > 0:
            current_camera = renderer.GetCameraInPane(0)

            if current_camera:
                print("Current Camera: {}".format(current_camera.Name))

                # 获取相机的动画节点
                anim_node = current_camera.Translation.GetAnimationNode()

                # 检查是否存在动画节点
                if anim_node:
                    for node in anim_node.Nodes:
                        curve = node.FCurve

                        # 检查是否存在动画曲线
                        if curve:
                            for key_index in range(len(curve.Keys)):
                                key = curve.Keys[key_index]
                                key_frame = key.Time.GetFrame()
                                camera_keyframes.append(int(key_frame))

                # 去除重复的帧号
                camera_keyframes = sorted(list(set(camera_keyframes)))

            else:
                print("No active camera found.")
        else:
            print("No active rendering pane found.")

        return camera_keyframes

    def playblast_frame(self):
        options=FBVideoGrabber().GetOptions()
        options.TimeSteps = FBTime(0, 0, 0, 1)
        options.CameraResolution = FBCameraResolutionMode.kFBResolutionCustom
        if not os.path.exists(os.path.dirname(self.output_folder_text.text())):
            os.makedirs(os.path.dirname(self.output_folder_text.text()))
        filename=self.filename_text.text()
        file_format="jpg"
        pathname=self.output_folder_text.text()
        folder_name=os.path.basename(pathname)
        file_name = pathname+"/"+str(filename)+"_"+str(folder_name)+"_"+"."+file_format
        options.OutputFileName = file_name
        print(options.OutputFileName)
        options.TimeSpan = FBTimeSpan(FBSystem().LocalTime, FBSystem().LocalTime)

        frames = self.get_camera_keyframes()

        for frame in frames:
            if frame != 0:
                options.TimeSpan = FBTimeSpan(FBTime(0, 0, 0, frame), FBTime(0, 0, 0, frame))
                FBApplication().FileRender(options)
    def browse_output_folder(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Folder", "")
        if folder_path:
            self.output_folder_text.setText(folder_path)

    def export_playblast(self):
        self.overwriteflag = 0
        cameras = cmds.ls(selection=True, shortNames=True)
        if not cameras:
            QtWidgets.QMessageBox.warning(self, "Warning", "please select camera.", QtWidgets.QMessageBox.Ok)
            return

        output_folder = self.output_folder_text.text()

        if not cameras or not output_folder:
            QtWidgets.QMessageBox.warning(self, "Warning", "Camera or Output Folder not set.", QtWidgets.QMessageBox.Ok)
            return

        camera_now = cmds.lookThru(q=True)
        current_frame_now = cmds.currentTime(query=True)

        for camera in cameras:
            try:
                cmds.getAttr(f"{camera}.focalLength")
            except:
                QtWidgets.QMessageBox.warning(self, "Warning", f"{camera} is not camera", QtWidgets.QMessageBox.Ok)
                break
            # 获取有关键帧的帧
            frames = cmds.keyframe(camera, query=True)
            if frames:
                cmds.lookThru(camera)
                unique_frames = sorted(set(frames))
                for frame in unique_frames:

                    cmds.currentTime(frame, edit=True)

                    self.playblast_frame(camera, output_folder, frame)
                    if self.overwriteflag == 2:
                        return

            else:
                QtWidgets.QMessageBox.warning(self, "Warning", f"No keyframes found for \"{camera}\".", QtWidgets.QMessageBox.Ok)
        cmds.lookThru(camera_now)
        cmds.currentTime(current_frame_now, edit=True)
        QtWidgets.QMessageBox.warning(self, "Finished", "Finished!", QtWidgets.QMessageBox.Ok)
        os.startfile(output_folder)



# 创建窗口实例
playblast_exporter = PlayblastExporter()