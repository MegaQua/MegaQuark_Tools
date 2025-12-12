import maya.cmds as cmds
from PySide2 import QtWidgets, QtGui, QtCore
import json
import os

class MR_Window(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("BS animation Json Importer For maya")

        layout = QtWidgets.QGridLayout(self)

        # 第一行
        target_name_label = QtWidgets.QLabel("target name")
        self.sceneBS_list = QtWidgets.QComboBox()
        blendshapes = cmds.ls(type="blendShape")
        for i in blendshapes:
            self.sceneBS_list.addItem(i)
        layout.addWidget(target_name_label, 0, 0)
        layout.addWidget(self.sceneBS_list, 0, 1)

        # 第二行
        json_path_label = QtWidgets.QLabel("json file path")
        self.json_file_text = QtWidgets.QLineEdit(cmds.workspace(q=True, rd=True))
        browse_btn = QtWidgets.QPushButton("Browse")
        layout.addWidget(json_path_label, 1, 0)
        layout.addWidget(self.json_file_text, 1, 1, 1, 3)
        layout.addWidget(browse_btn, 1, 4)

        # 第三行
        self.check_label = QtWidgets.QLabel("")
        self.check_image_label = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(r"/noimage.png")
        self.check_image_label.setPixmap(pixmap)
        check_btn = QtWidgets.QPushButton("check data")
        layout.addWidget(self.check_label, 2, 1)
        layout.addWidget(self.check_image_label, 2, 0)
        layout.addWidget(check_btn, 2, 4)

        # 第四行
        start_frame_label = QtWidgets.QLabel("import start frame")
        self.start_frame_text = QtWidgets.QLineEdit()
        end_frame_label = QtWidgets.QLabel("import end frame")
        self.end_frame_text = QtWidgets.QLineEdit()
        layout.addWidget(start_frame_label, 3, 0)
        layout.addWidget(self.start_frame_text, 3, 1)
        layout.addWidget(end_frame_label, 3, 2)
        layout.addWidget(self.end_frame_text, 3, 3)

        # 第五行

        set_frame_btn = QtWidgets.QPushButton("set frame now")
        Auto_frame_btn = QtWidgets.QPushButton("Auto end frame")
        self.checkbox_Skip_df = QtWidgets.QCheckBox("Skip duplicate frames")
        import_btn = QtWidgets.QPushButton("Import")
        layout.addWidget(set_frame_btn, 4, 0)
        layout.addWidget(Auto_frame_btn, 4, 1)
        layout.addWidget(self.checkbox_Skip_df, 4, 2)
        layout.addWidget(import_btn, 4, 4)

        # 为所有按钮连接临时函数
        browse_btn.clicked.connect(self.browse_path)
        check_btn.clicked.connect(self.check_json)
        set_frame_btn.clicked.connect(self.set_start_frame_now)
        Auto_frame_btn.clicked.connect(self.auto_end_frame)
        import_btn.clicked.connect(self.import_json)
        # 设置窗口置顶
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    def auto_end_frame(self):
        filepath = self.json_file_text.text()

        with open(filepath, "r") as f:
            facs_data = json.loads(f.read())
            numFrames = facs_data["numFrames"]

        start_frame = self.start_frame_text.text()
        self.end_frame_text.setText(str(int(start_frame)+numFrames-1))

    def set_start_frame_now(self):
        current_frame = cmds.currentTime(query=True)
        self.start_frame_text.setText(str(int(current_frame)))
        self.end_frame_text.setText("")

    def temp_function(self):
        sender = self.sender()
        print(f"{sender.text()} clicked")

    def browse_path(self):
        path = cmds.workspace(q=True, rd=True)
        file_filter = "JSON Files (*.json)"
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select JSON File", path, file_filter)
        if file_path:
            self.json_file_text.setText(file_path)
        try:
            image_path = file_path.replace(".json", ".png")
            pixmap = QtGui.QPixmap(image_path)
            self.check_image_label.setPixmap(pixmap)
        except:
            pass
    def check_json(self):
        filepath = self.json_file_text.text()
        #start_frame = int(self.start_frame_text.text())
        bsname = self.sceneBS_list.currentText()
        if os.path.exists(filepath) and filepath.endswith(".json"):
            with open(filepath, "r") as f:
                facs_data = json.loads(f.read())
                facsNames = facs_data["facsNames"]
                numPoses = facs_data["numPoses"]
                numFrames = facs_data["numFrames"]
                #weightMat = facs_data["weightMat"]
        else:
            self.check_label.setText("no file selected")
            return
        bslist = cmds.listAttr(bsname + '.w', m=True)
        #print(facsNames,bslist)
        if facsNames  == bslist:
            self.check_label.setText("ok,data importable,numFrames = %s " % numFrames)
        else:
            self.check_label.setText("data check faild,BS system dont match")

    def import_json(self):
        filepath = self.json_file_text.text()
        start_frame = int(self.start_frame_text.text())
        if self.end_frame_text.text():
            end_frame = int(self.end_frame_text.text())
        else:
            end_frame=None
        bsname = self.sceneBS_list.currentText()
        #weight = 0.0

        with open(filepath, "r") as f:
            facs_data = json.loads(f.read())
            facsNames = facs_data["facsNames"]
            numPoses = facs_data["numPoses"]
            numFrames = facs_data["numFrames"]
            weightMat = facs_data["weightMat"]

        for fr in range(numFrames):

            for i in range(numPoses):
                frame = fr + start_frame
                if end_frame:
                    if frame > end_frame:
                        print("break it!!")
                        break

                weight = weightMat[fr][i]

                if fr == 0 or fr+1 == int(numFrames) or frame == end_frame:
                    cmds.setKeyframe(bsname + "." + facsNames[i], v=weight, t=frame)
                else:
                    if weight!=weightMat[fr-1][i] or  weight!=weightMat[fr+1][i] :
                        cmds.setKeyframe(bsname + "." + facsNames[i], v=weight, t=frame)


bsaj_importer= MR_Window()