import maya.cmds as cmds
from PySide2 import QtWidgets, QtGui, QtCore
import os
import re



class PlayblastExporter(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.overwriteflag = 0
        self.setWindowTitle("camera key frame Exporter")

        layout = QtWidgets.QGridLayout(self)

        # 指定输出文件夹
        output_folder_label = QtWidgets.QLabel("Output Folder:")
        self.output_folder_text = QtWidgets.QLineEdit()
        output_folder_btn = QtWidgets.QPushButton("Browse Output Folder")
        layout.addWidget(output_folder_label, 0, 0)
        layout.addWidget(self.output_folder_text, 0, 1)
        layout.addWidget(output_folder_btn, 0, 2)

        # 添加 "Select Camera" 文本
        select_camera_label = QtWidgets.QLabel("Select Camera(s) and then ")
        select_camera_label.setAlignment(QtCore.Qt.AlignRight)
        layout.addWidget(select_camera_label, 1, 1)

        # 执行输出
        export_playblast_btn = QtWidgets.QPushButton("Keyframe Playblast")
        layout.addWidget(export_playblast_btn, 1, 2)

        # 连接按钮的信号

        output_folder_btn.clicked.connect(self.browse_output_folder)
        export_playblast_btn.clicked.connect(self.export_playblast)

        self.resize(500, 80)  # 设置窗口的默认尺寸

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    # 修改选择相机的方法

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

    def playblast_frame(self, camera, output_folder, frame):

        scene_name = cmds.file(query=True, sceneName=True)
        base_name = os.path.basename(scene_name)

        # 如果场景尚未保存，base_name将为空
        if base_name:
            # 移除文件扩展名
            base_name = os.path.splitext(base_name)[0] + "_"

        filetype = "jpg"
        widthHeight = [1920,1080]

        if "_" not in camera:
            filename = f"{output_folder}/{camera}_{int(frame)}F.{filetype}"
        else:
            last_part = camera.split('_')[-1]
            pattern = re.compile(r"^\d+F$")

            if bool(pattern.search(last_part)):
                filename = f"{output_folder}/{camera.split('_')[0]}_{int(frame)}F.{filetype}"
            else:
                filename = f"{output_folder}/{camera.split('_')[0]}_{int(frame)}F_{last_part}.{filetype}"

        if os.path.exists(filename) :
            if self.overwriteflag == 0:

                msgBox = QtWidgets.QMessageBox(self)
                msgBox.setWindowTitle('File Exists')
                msgBox.setText("File already exists. Do you want to overwrite?")
                # 创建自定义按钮
                overwrite_button = msgBox.addButton("Overwrite all", QtWidgets.QMessageBox.YesRole)
                keep_button = msgBox.addButton("Cancel Playblast", QtWidgets.QMessageBox.NoRole)
                msgBox.setDefaultButton(keep_button)
                msgBox.exec_()

                if msgBox.clickedButton() == overwrite_button:
                    self.overwriteflag = 1

                    try:
                        os.remove(filename)
                    except:
                        pass
                else:
                    self.overwriteflag = 2
                    QtWidgets.QMessageBox.warning(self, "canceled", "canceled!", QtWidgets.QMessageBox.Ok)

                    return
                    """
                    # 如果不覆盖，则生成一个新的文件名
                    counter = 1
                    new_filename = f"{output_folder}/{camera.split('_')[0]}_{int(frame)}F_{counter}.{filetype}"
                    while os.path.exists(new_filename):
                        counter += 1
                        new_filename = f"{output_folder}/{camera.split('_')[0]}_{int(frame)}F_{counter}.{filetype}"
                    filename = new_filename
                    """
            elif self.overwriteflag == 1:
                try:
                    os.remove(filename)
                except:
                    pass


        cmds.playblast(filename=filename,
                       format="image",
                       compression=filetype,
                       percent=100,
                       quality=100,
                       viewer=False,
                       forceOverwrite=True,
                       offScreen=True,
                       framePadding=0,
                       showOrnaments=True,
                       frame=[frame],
                       widthHeight=widthHeight)
        os.rename(filename + f".0.{filetype}", filename)


# 创建窗口实例
playblast_exporter = PlayblastExporter()
