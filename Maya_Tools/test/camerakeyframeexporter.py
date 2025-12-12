import maya.cmds as cmds
from PySide2 import QtWidgets, QtGui, QtCore
import os

class PlayblastExporter(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("camera key frame Exporter")

        layout = QtWidgets.QGridLayout(self)

        # 选择相机
        camera_label = QtWidgets.QLabel("Camera:")
        self.camera_text = QtWidgets.QLineEdit()
        select_camera_btn = QtWidgets.QPushButton("Select Camera")
        layout.addWidget(camera_label, 0, 0)
        layout.addWidget(self.camera_text, 0, 1)
        layout.addWidget(select_camera_btn, 0, 2)

        # 指定输出文件夹
        output_folder_label = QtWidgets.QLabel("Output Folder:")
        self.output_folder_text = QtWidgets.QLineEdit()
        output_folder_btn = QtWidgets.QPushButton("Browse Output Folder")
        layout.addWidget(output_folder_label, 1, 0)
        layout.addWidget(self.output_folder_text, 1, 1)
        layout.addWidget(output_folder_btn, 1, 2)

        # 执行输出
        export_playblast_btn = QtWidgets.QPushButton("Keyframe Playblast")
        layout.addWidget(export_playblast_btn, 2, 2)

        # 连接按钮的信号
        select_camera_btn.clicked.connect(self.select_camera)
        output_folder_btn.clicked.connect(self.browse_output_folder)
        export_playblast_btn.clicked.connect(self.export_playblast)

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.show()



    def select_camera(self):
        selected = cmds.ls(selection=True)
        if selected:
            self.camera_text.setText(selected[0])
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "No camera selected.", QtWidgets.QMessageBox.Ok)

    def browse_output_folder(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Folder", "")
        if folder_path:
            self.output_folder_text.setText(folder_path)

    def export_playblast(self):
        camera = self.camera_text.text()
        output_folder = self.output_folder_text.text()

        if not camera or not output_folder:
            QtWidgets.QMessageBox.warning(self, "Warning", "Camera or Output Folder not set.", QtWidgets.QMessageBox.Ok)
            return

        # 获取有关键帧的帧
        frames = cmds.keyframe(camera, query=True)
        if frames:
            unique_frames = sorted(set(frames))
            for frame in unique_frames:
                cmds.currentTime(frame, edit=True)
                self.playblast_frame(camera, output_folder, frame)
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "No keyframes found for the selected camera.", QtWidgets.QMessageBox.Ok)

    def playblast_frame(self, camera, output_folder, frame):
        # 设置当前视图为所选相机
        panel = cmds.getPanel(withFocus=True)
        if panel.startswith('modelPanel'):
            cmds.modelPanel(panel, edit=True, camera=camera)

        scene_name = cmds.file(query=True, sceneName=True)
        base_name = os.path.basename(scene_name)

        # 如果场景尚未保存，base_name将为空
        if base_name:
            # 移除文件扩展名
            base_name = os.path.splitext(base_name)[0]+"_"

        filetype = "jpg"
        widthHeight = [1920, 1080]

        text = ""
        filename = f"{output_folder}/{base_name}{camera}_frame_{int(frame)}.{filetype}"
        cmds.playblast(filename=filename,
                       format="image",
                       compression=filetype,
                       viewer=False,
                       forceOverwrite=True,
                       offScreen=True,
                       showOrnaments=False,
                       frame=[frame],
                       widthHeight= widthHeight)
        os.rename(filename+f".0000.{filetype}", filename)

# 创建窗口实例
playblast_exporter = PlayblastExporter()
