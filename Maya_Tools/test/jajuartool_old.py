from PySide2 import QtWidgets, QtGui, QtCore
import sys
subsyspath = 'S:\Public\qiu_yi\pymaya2022\Lib\site-packages'
sys.path.insert(0, subsyspath)
import numpy as np
#from scipy.signal import savgol_filter
import maya.cmds as cmds

class MyWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MyWindow, self).__init__(None)
        self.setWindowTitle("jager tool")

        # 创建一个选项卡部件
        self.tabs = QtWidgets.QTabWidget()


        TAB1=True
        if TAB1:
            vcam_Tab = QtWidgets.QWidget()
            self.tabs.addTab(vcam_Tab, "vcam to rig cam")
            vcam_Tab.layout = QtWidgets.QGridLayout()
            vcam_Tab.setLayout(vcam_Tab.layout)

            # 创建按钮
            button1 = QtWidgets.QPushButton("get vcam", self)
            button1.clicked.connect(self.get_vcam)
            self.text1 = QtWidgets.QLineEdit(self)
            self.text1.setReadOnly(True)
            button2 = QtWidgets.QPushButton("get cam rig GP", self)
            button2.clicked.connect(self.get_cam_rig_GP)
            self.text2 = QtWidgets.QLineEdit(self)
            self.text2.setReadOnly(True)
            button3 = QtWidgets.QPushButton("constrain", self)
            button3.clicked.connect(self.constraint_cam)
            #self.checkbox = QtWidgets.QCheckBox("Separate shake Animation", self)
            #self.checkbox.setChecked(True)  # 默认勾选
            #self.checkbox2 = QtWidgets.QCheckBox("Ignore rotateZ shake", self)
            #self.checkbox2.setChecked(False)  # 默认勾选
            self.checkbox3 = QtWidgets.QCheckBox("Parameter Settings", self)
            self.checkbox3.setChecked(False)  # 默认勾选
            self.checkbox3.stateChanged.connect(self.on_groupBox_toggled)


            self.groupBox = QtWidgets.QGroupBox("Parameter Settings", self)
            groupBoxLayout = QtWidgets.QGridLayout(self.groupBox)
            self.groupBox.setLayout(groupBoxLayout)
            self.groupBox.setVisible(False)
            self.params = {
                "translate_threshold": 0.1,
                "rotate_threshold": 5,
                "translate_deviation" : 1,
                "rotate_deviation" : 20,
                "n_frames" : 4,
                "translateX_correction" : 0,
                "translateY_correction" : 0,
                "translateZ_correction" : 0,
                "rotateX_correction" : 0,
                "rotateY_correction" : 0,
                "rotateZ_correction" : 0,
                "excessive_deviation_threshold" : 1,
                "useless_rate_threshold": 0.5
            }

            # 创建标签和文本框
            self.textEdits = {}
            row = 0
            for param, value in self.params.items():
                if param=="useless_rate_threshold":
                    label = QtWidgets.QLabel(param, self.groupBox)
                    textEdit = QtWidgets.QLineEdit(self.groupBox)
                    textEdit.setText(str(value))
                    textEdit.textChanged.connect(lambda text, p=param: self.on_text_changed(p, text))

                    groupBoxLayout.addWidget(label, row, 0)
                    groupBoxLayout.addWidget(textEdit, row, 1)
                    self.textEdits[param] = textEdit
                    row += 1
            label = QtWidgets.QLabel("Note: lower value, fewer keyframes.", self.groupBox)
            groupBoxLayout.addWidget(label, row, 0)
            #self.setLayout(groupBoxLayout)

            # 创建布局

            #layout = QtWidgets.QGridLayout()
            vcam_Tab.layout.addWidget(button1, 0, 0)  # 第0行，第0列
            vcam_Tab.layout.addWidget(self.text1, 0, 1)  # 第0行，第1列
            vcam_Tab.layout.addWidget(button2, 1, 0)  # 第1行，第0列
            vcam_Tab.layout.addWidget(self.text2, 1, 1)  # 第1行，第1列
            vcam_Tab.layout.addWidget(button3, 2, 0)  # 第2行，第0列
            #vcam_Tab.layout.addWidget(self.checkbox, 2, 1)
            vcam_Tab.layout.addWidget(self.checkbox3, 3, 0)
            #vcam_Tab.layout.addWidget(self.checkbox2, 3, 1)
            vcam_Tab.layout.addWidget(self.groupBox, 4, 0, 1, 2)
        TAB2 = True
        if TAB2 :

            Keyframe_Tab = QtWidgets.QWidget()
            self.tabs.addTab(Keyframe_Tab, "Keyframe playblast")
            Keyframe_Tab.layout = QtWidgets.QGridLayout()
            Keyframe_Tab.setLayout(Keyframe_Tab.layout)



            # 选择相机
            camera_label = QtWidgets.QLabel("Camera:")
            self.camera_text = QtWidgets.QLineEdit()
            select_camera_btn = QtWidgets.QPushButton("Select Camera")
            Keyframe_Tab.layout.addWidget(camera_label, 0, 0)
            Keyframe_Tab.layout.addWidget(self.camera_text, 0, 1)
            Keyframe_Tab.layout.addWidget(select_camera_btn, 0, 2)

            # 指定输出文件夹
            output_folder_label = QtWidgets.QLabel("Output Folder:")
            self.output_folder_text = QtWidgets.QLineEdit()
            output_folder_btn = QtWidgets.QPushButton("Browse Output Folder")
            Keyframe_Tab.layout.addWidget(output_folder_label, 1, 0)
            Keyframe_Tab.layout.addWidget(self.output_folder_text, 1, 1)
            Keyframe_Tab.layout.addWidget(output_folder_btn, 1, 2)

            # 执行输出
            export_playblast_btn = QtWidgets.QPushButton("Keyframe Playblast")
            Keyframe_Tab.layout.addWidget(export_playblast_btn, 2, 2)

            # 连接按钮的信号
            select_camera_btn.clicked.connect(self.select_camera)
            output_folder_btn.clicked.connect(self.browse_output_folder)
            export_playblast_btn.clicked.connect(self.export_playblast)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.tabs)
        self.setLayout(mainLayout)

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        #self.resize(1, 1)
        self.Object=""
        self.Smooth_Object = ""
        self.Shake_Object = ""
        self.Aim_Object = ""

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

    def on_text_changed(self, param, text):
        try:
            self.params[param] = float(text)  # 将文本转换为浮点数
        except ValueError:
            pass  # 如果转换失败，保持原值不变

    def on_groupBox_toggled(self, checked):
        # 控制GroupBox内容的显示与隐藏
        self.groupBox.setFlat(not checked)
        self.groupBox.setVisible(checked)
        #self.resize(1, 1)

        self.checkbox3.setVisible(not checked)
    def button_clicked(self):
        button_text = self.sender().text()
        print(f"按钮 '{button_text}' 被点击！")


    def get_vcam(self):
        # 获取当前选择的物体名字
        selection = cmds.ls(selection=True)
        if selection:
            self.text1.setText(selection[0])
        else:
            self.text1.setText("")

    def get_cam_rig_GP(self):
        # 获取当前选择的物体名字
        selection = cmds.ls(selection=True)
        if selection:
            self.text2.setText(selection[0])
        else:
            self.text2.setText("")

    def create_smooth_and_noise_groups(self,selected_obj):
        if not selected_obj:
            raise ValueError("No object selected.")
        smooth_group = cmds.duplicate(selected_obj, name=selected_obj + '_smooth_cam')[0]
        cmds.setAttr(f'{smooth_group}.translate', 0, 0, 0)
        cmds.setAttr(f'{smooth_group}.rotate', 0, 0, 0)

        n_frames = 5
        threshold = 0.1
        useless_rate_threshold=0.05
        # 处理 translate 和 rotate 的每个属性
        for attr in ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']:
            keyframes = cmds.keyframe(selected_obj, attribute=attr, query=True)
            if not keyframes:
                continue

            # 对每个关键帧进行处理
            keyframe_values = [cmds.getAttr(f'{selected_obj}.{attr}', time=frame) for frame in keyframes]



            # 获取关键帧值
            keyframe_values = [cmds.getAttr(f'{selected_obj}.{attr}', time=frame) for frame in keyframes]

            # 计算平均值和标准差
            mean = np.mean(keyframe_values)
            std_dev = np.std(keyframe_values)

            # 只考虑在平均值±2个标准差范围内的值
            filtered_values = [value for value in keyframe_values if mean - 2 * std_dev <= value <= mean + 2 * std_dev]

            max_value = max(filtered_values)
            min_value = min(filtered_values)

            difference = max_value - min_value

            threshold = 0.1 * difference
            print(f"{attr}-{threshold}")
            for frame in keyframes:
                current_value = cmds.getAttr(f'{selected_obj}.{attr}', time=frame)

                if frame == keyframes[0]:
                    cmds.setKeyframe(smooth_group, attribute=attr, time=frame, value=current_value)
                    continue

                # 获取当前帧在keyframes中的位置
                frame_index = keyframes.index(frame)

                # 考虑靠近列表开始和结束的情况
                if frame_index < n_frames:
                    start_frame = keyframes[0]
                    end_frame = keyframes[min(frame_index + n_frames, len(keyframes) - 1)] + 1
                elif frame_index > len(keyframes) - n_frames - 1:
                    start_frame = keyframes[max(frame_index - n_frames, 0)]
                    end_frame = keyframes[-1] + 1
                else:
                    start_frame = frame - n_frames
                    end_frame = frame + n_frames + 1

                frame_range = range(int(start_frame), int(end_frame))
                frame_values = [cmds.getAttr(f'{selected_obj}.{attr}', time=f) for f in frame_range]

                if len(frame_values) >= 3:
                    frame_values.remove(max(frame_values))
                    frame_values.remove(min(frame_values))

                avg_value = sum(frame_values) / len(frame_values)

                cmds.setKeyframe(smooth_group, attribute=attr, time=frame, value=avg_value)

            # 无用帧
            keyframes_smooth_group = cmds.keyframe(smooth_group, attribute=attr, query=True)
            if keyframes_smooth_group:
                for _ in range(1):
                    frames_to_delete = []  # 用于记录要删除的帧

                    for i in range(1, len(keyframes_smooth_group) - 1):  # 跳过第一个和最后一个关键帧
                        current_frame = keyframes_smooth_group[i]
                        prev_frame = keyframes_smooth_group[i - 1]
                        next_frame = keyframes_smooth_group[i + 1]

                        # 获取关键帧的值
                        current_value = cmds.getAttr(f'{smooth_group}.{attr}', time=current_frame)
                        prev_value = cmds.getAttr(f'{smooth_group}.{attr}', time=prev_frame)
                        next_value = cmds.getAttr(f'{smooth_group}.{attr}', time=next_frame)

                        # 计算值变化率
                        rate_prev = abs(current_value - prev_value) / (current_frame - prev_frame)
                        rate_next = abs(next_value - current_value) / (next_frame - current_frame)

                        # 判断是否为无用帧
                        if abs(rate_next - rate_prev) < useless_rate_threshold:
                            frames_to_delete.append(current_frame)

                    # 删除记录的所有无用帧
                    for frame in frames_to_delete:
                        cmds.cutKey(smooth_group, time=(frame, frame), attribute=attr)

                    # 更新关键帧组列表
                    keyframes_smooth_group = [frame for frame in keyframes_smooth_group if frame not in frames_to_delete]

            keyframes_smooth_group = cmds.keyframe(smooth_group, attribute=attr, query=True)
            # 检查偏离并根据需要调整关键帧
            def process_keyframes(keyframes, process_function):
                for frame in keyframes:
                    process_function(frame)

            def your_processing_function(frame):
                # 你之前的处理逻辑
                original_value = cmds.getAttr(f'{selected_obj}.{attr}', time=frame)
                smooth_value = cmds.getAttr(f'{smooth_group}.{attr}', time=frame)

                current_index = keyframes.index(frame)

                if current_index > 1:
                    prev_frame = keyframes[current_index - 1]
                    prev_original_value = cmds.getAttr(f'{selected_obj}.{attr}', time=prev_frame)

                    if original_value == prev_original_value:
                        cmds.setKeyframe(smooth_group, attribute=attr, time=frame, value=original_value)

                        if cmds.keyframe(smooth_group, attribute=attr, query=True, time=(prev_frame, prev_frame)):
                            cmds.cutKey(smooth_group, time=(prev_frame, prev_frame), attribute=attr)

                elif abs(original_value - smooth_value) > threshold and abs(original_value - smooth_value) <= 5 * threshold:
                    cmds.setKeyframe(smooth_group, attribute=attr, time=frame, value=original_value)

            # 正向处理关键帧
            process_keyframes(keyframes, your_processing_function)

            # 反向处理关键帧
            process_keyframes(reversed(keyframes), your_processing_function)

            """
                # 获取当前帧在关键帧列表中的索引
                current_index = keyframes.index(frame)

                # 确保有足够的关键帧来进行比较
                if current_index >= 2:
                    prev_frame = keyframes[current_index - 1]
                    prev_prev_frame = keyframes[current_index - 2]

                    # 检查上上个关键帧与当前关键帧的距离是否不超过30帧
                    # 并确保上上个关键帧不是第一个关键帧
                    # 并且当前关键帧与上一个关键帧的距离大于10帧
                    if frame - prev_prev_frame < 30 and prev_prev_frame != keyframes[0] and frame - prev_frame < 10:
                        # 检查并删除上一个关键帧
                        if cmds.keyframe(smooth_group, attribute=attr, query=True, time=(prev_frame, prev_frame)):
                            cmds.cutKey(smooth_group, time=(prev_frame, prev_frame), attribute=attr)
            """
        self.Smooth_Object = smooth_group
        #self.Shake_Object = noise_group

    def create_smooth_and_noise_groups_v2(self,selected_obj):
        meta = 0.5
        if not selected_obj:
            raise ValueError("No object selected.")

        smooth_group = cmds.duplicate(selected_obj, name=selected_obj + '_smooth_cam')[0]
        cmds.setAttr(f'{smooth_group}.translate', 0, 0, 0)
        cmds.setAttr(f'{smooth_group}.rotate', 0, 0, 0)

        attributes = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']

        # 复制动画曲线
        for attr in attributes:
            cmds.copyKey(selected_obj, attribute=attr)
            cmds.pasteKey(smooth_group, attribute=attr)

        # 对smooth_group执行关键帧平滑和删除操作
        for attr in attributes:
            keyframes = cmds.keyframe(smooth_group, attribute=attr, query=True)

            if not keyframes:
                continue

            retain_count = int(len(keyframes) * meta)

            if retain_count >= len(keyframes):
                continue

            frame_values = {frame: cmds.getAttr(f'{smooth_group}.{attr}', time=frame) for frame in keyframes}
            to_delete = []

            for i in range(1, len(keyframes) - 1):
                frame = keyframes[i]
                prev_frame = keyframes[i - 1]
                next_frame = keyframes[i + 1]

                current_value = frame_values[frame]
                prev_value = frame_values[prev_frame]
                next_value = frame_values[next_frame]

                if (current_value > prev_value and current_value > next_value) or (current_value < prev_value and current_value < next_value):
                    to_delete.append((frame, abs(current_value - (prev_value + next_value) / 2)))
                else:
                    change_rate = abs(current_value - prev_value) + abs(current_value - next_value)
                    to_delete.append((frame, change_rate))

            to_delete.sort(key=lambda x: x[1])

            for frame, _ in to_delete[:len(to_delete) - retain_count]:
                cmds.cutKey(smooth_group, time=(frame, frame), attribute=attr)
        self.Smooth_Object = smooth_group
    def smooth_animation_curve(self,obj, attr, window_length, polyorder):
        """
        使用Savitzky-Golay滤波器平滑Maya中对象的动画曲线。
        :param obj: 对象名称
        :param attr: 属性名称
        :param window_length: 滤波器的窗口长度，必须为正奇数
        :param polyorder: 多项式的阶数，必须小于窗口长度
        """
        # 获取关键帧
        keyframes = cmds.keyframe(obj, attribute=attr, query=True)

        if not keyframes or len(keyframes) < window_length:
            print("Not enough keyframes or invalid window length.")
            return

        # 获取关键帧值
        keyframe_values = np.array([cmds.getAttr(f'{obj}.{attr}', time=frame) for frame in keyframes])

        # 保留第一个和最后一个关键帧值
        first_value, last_value = keyframe_values[0], keyframe_values[-1]

        # 应用滤波器
        smoothed_values = savgol_filter(keyframe_values, window_length, polyorder)

        # 保证第一个和最后一个关键帧值不变
        smoothed_values[0], smoothed_values[-1] = first_value, last_value

        # 设置平滑后的关键帧
        for frame, value in zip(keyframes, smoothed_values):
            cmds.setKeyframe(obj, attribute=attr, time=frame, value=value)

    def shake(self,selected_obj):
        # 创建噪点帧
        keyframes = cmds.keyframe(selected_obj, attribute="translateX", query=True)
        #print(keyframes)
        #if keyframes:

        for frame in keyframes:
            cmds.currentTime(frame)
            cmds.matchTransform(noise_group, selected_obj, position=True)
            cmds.matchTransform(noise_group, selected_obj, rotation=True)
            for attr in ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']:
                attr_value = cmds.getAttr(f'{noise_group}.{attr}')
                cmds.setKeyframe(noise_group, attribute=attr, time=frame, value=attr_value)

    def constraint_cam(self):
        self.Object=""
        self.Smooth_Object = ""
        self.Shake_Object = ""
        self.Aim_Object = ""
        # 获取text2中的物体名称
        target_name = self.text2.text()
        if not target_name:
            cmds.warning("No target object specified in text2.")
            return

        # 分析命名空间
        namespace = target_name.split(':')[0] if ':' in target_name else ''
        if not namespace:
            cmds.warning("No namespace found in the target object name.")
            return

        # 获取text1中的相机名称
        camera_name = self.text1.text()
        if not camera_name:
            cmds.warning("No camera object specified in text1.")
            return
        self.Object=camera_name

        #if self.checkbox.isChecked():
        self.create_smooth_and_noise_groups(camera_name)
        Smooth_camera_name=self.Smooth_Object

        offset_values = cmds.getAttr(f"{self.Object}.rotateAxis")[0]
        cmds.setAttr(f"{self.Object}.scaleX", 1)
        cmds.setAttr(f"{self.Object}.scaleY", 1)
        cmds.setAttr(f"{self.Object}.scaleZ", 1)






        offset_group = cmds.group(em=True, name=self.Object + '_offset_group')
        offset_group2 = cmds.group(em=True, name=self.Object + '_offset_group2')
        cmds.parent(offset_group, Smooth_camera_name)
        cmds.parent(offset_group2, self.Object)
        cmds.setAttr(f'{offset_group}.translate', 0, 0, 0)
        cmds.setAttr(f'{offset_group}.rotate', 0, 0, 0)
        cmds.setAttr(f'{offset_group2}.translate', 0, 0, 0)
        cmds.setAttr(f'{offset_group2}.rotate', 0, 0, 0)


        # 创建约束
        namespace_delete = "JCQ"

        # 检查Namespace是否存在
        if cmds.namespace(exists=namespace_delete):
            # 列出Namespace中的所有节点
            nodes = cmds.namespaceInfo(namespace_delete, listOnlyDependencyNodes=True)

            if nodes:
                # 如果Namespace中有节点，则报告无法删除
                print(f"Namespace '{namespace_delete}' contains nodes and cannot be deleted: {nodes}")
            else:
                # 如果Namespace为空，则删除
                cmds.namespace(removeNamespace=namespace_delete, mergeNamespaceWithRoot=True)
                print(f"Namespace '{namespace_delete}' has been deleted.")


        file_path="K:/Jaguar/11_Users/Q/camera_rig/JCQcam.ma"
        cmds.file(file_path, reference=True, namespace=":")
        sub_namespace="JCQ"

        cmds.pointConstraint(offset_group, f"{sub_namespace}:camMainAndRotateY", maintainOffset=False)
        cmds.orientConstraint(offset_group, f"{sub_namespace}:camRotateZ ", skip=("x", "y"), maintainOffset=False)
        cmds.orientConstraint(offset_group, f"{sub_namespace}:camRotateX ", skip=("y", "z"), maintainOffset=False)
        cmds.orientConstraint(offset_group, f"{sub_namespace}:camMainAndRotateY ", skip=("x", "z"), maintainOffset=False)
        cmds.connectAttr(f"{self.Object}.focalLength", f"{sub_namespace}:camMainOpt.focalLength",)
        cmds.connectAttr(f"{self.Object}.focusDistance", f"{sub_namespace}:focusPoint.translateZ", )
        cmds.pointConstraint(offset_group2, f"{sub_namespace}:camShakeAnim", maintainOffset=False)
        cmds.orientConstraint(offset_group2, f"{sub_namespace}:camShakeAnim ", maintainOffset=False)

        keyframes = cmds.keyframe(camera_name, query=True)
        attrs_a = ['camMainAndRotateY',
                 'camMainAndRotateY',
                 'camMainAndRotateY',
                 'camRotateX',
                 'camMainAndRotateY',
                 'camRotateZ',
                 'camMainOpt',
                 'focusPoint',
                 "camShakeAnim",
                "camShakeAnim",
                "camShakeAnim",
                "camShakeAnim",
                "camShakeAnim",
                "camShakeAnim",
                   ]
        attrs_b = ['translateX',
                 'translateY',
                 'translateZ',
                 'rotateX',
                 'rotateY',
                 'rotateZ',
                 'focalLength',
                 'translateZ',
                 'translateX',
                 'translateY',
                 'translateZ',
                 'rotateX',
                 'rotateY',
                 'rotateZ',]
        for frame in keyframes:
            for attra ,attrb in zip(attrs_a, attrs_b):
                value = cmds.getAttr(f'{sub_namespace}:{attra}.{attrb}', time=frame)
                cmds.setKeyframe(f"{namespace}:{attra}", attribute=attrb, time=frame, value=value)
        cmds.file(r"K:/Jaguar/11_Users/Q/camera_rig/JCQcam.ma", removeReference=True)
        namespace_delete = "JCQ"

        # 检查Namespace是否存在
        if cmds.namespace(exists=namespace_delete):
            # 列出Namespace中的所有节点
            nodes = cmds.namespaceInfo(namespace_delete, listOnlyDependencyNodes=True)

            if nodes:
                # 如果Namespace中有节点，则报告无法删除
                print(f"Namespace '{namespace_delete}' contains nodes and cannot be deleted: {nodes}")
            else:
                # 如果Namespace为空，则删除
                cmds.namespace(removeNamespace=namespace_delete, mergeNamespaceWithRoot=True)
                print(f"Namespace '{namespace_delete}' has been deleted.")
        try:
            cmds.delete("JCQcamRNfosterParent1")
            cmds.delete(offset_group)
            cmds.delete(offset_group2)
            cmds.delete(self.Smooth_Object)
        except:
            pass
        QtWidgets.QMessageBox.warning(self, "finished", "finished.", QtWidgets.QMessageBox.Ok)




# 创建窗口实例
window = MyWindow()
