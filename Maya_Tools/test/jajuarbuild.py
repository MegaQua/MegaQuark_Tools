from PySide2 import QtWidgets, QtGui, QtCore
import maya.cmds as cmds
import maya.mel as mel

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
            button3.clicked.connect(lambda: self.constraint_cam(anno=True))

            button4 = QtWidgets.QPushButton("bake", self)
            button4.clicked.connect(lambda: self.bake(anno=True))

            button5 = QtWidgets.QPushButton("constrain and bake", self)
            button5.clicked.connect(self.main)

            self.Label1 = QtWidgets.QLabel("smooth vcam: None")
            self.cutoff_frequency_Label = QtWidgets.QLabel("cutoff frequency:")
            self.sampling_rate_Label = QtWidgets.QLabel("sampling rate:")
            self.cutoff_frequency_text = QtWidgets.QLineEdit(self)
            self.sampling_rate_text = QtWidgets.QLineEdit(self)

            self.cutoff_frequency_text.setText("0.65")
            self.sampling_rate_text.setText("30")

            # 创建布局

            #layout = QtWidgets.QGridLayout()
            # 第0行
            vcam_Tab.layout.addWidget(button1, 0, 0)  # 第0行，第0列
            vcam_Tab.layout.addWidget(self.text1, 0, 1, 1, 3)  # 第0行，第1到第3列

            # 第1行
            vcam_Tab.layout.addWidget(button2, 1, 0)  # 第1行，第0列
            vcam_Tab.layout.addWidget(self.text2, 1, 1, 1, 3)  # 第1行，第1到第3列

            # 第2行
            vcam_Tab.layout.addWidget(button3, 2, 0)  # 第2行，第0列
            vcam_Tab.layout.addWidget(self.cutoff_frequency_Label, 2, 1)  # 第2行，第1列
            vcam_Tab.layout.addWidget(self.cutoff_frequency_text, 2, 2, 1, 2)  # 第2行，第2到第3列

            # 第3行
            vcam_Tab.layout.addWidget(button4, 3, 0)  # 第3行，第0列
            vcam_Tab.layout.addWidget(self.sampling_rate_Label, 3, 1)  # 第3行，第1列
            vcam_Tab.layout.addWidget(self.sampling_rate_text, 3, 2, 1, 2)  # 第3行，第2到第3列

            # 第4行
            vcam_Tab.layout.addWidget(button5, 4, 0)  # 第4行，第0列
            vcam_Tab.layout.addWidget(self.Label1, 4, 1, 1, 3)  # 第4行，第1到第3列

            #vcam_Tab.layout.addWidget(self.checkbox, 2, 1)
            #vcam_Tab.layout.addWidget(self.checkbox3, 3, 0)
            #vcam_Tab.layout.addWidget(self.checkbox2, 3, 1)
            #vcam_Tab.layout.addWidget(self.groupBox, 4, 0, 1, 2)
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
        self.namespace = ""
        self.sub_namespace="JCQ"
        self.Object=""
        self.Smooth_Object = ""
        self.Shake_Object = ""
        self.Aim_Object = ""
        self.p1 = False
        self.p2 = False
        self.show()


    def update_smooth_obj(self):
        if self.Smooth_Object:
            self.Label1.setText(f"smooth vcam:{self.Smooth_Object}")
        else:
            self.Label1.setText(f"smooth vcam: None")

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
    """
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


        self.Smooth_Object = smooth_group
        #self.Shake_Object = noise_group
    """
    def create_smooth_and_noise_groups_v2(self,selected_obj):
        if not selected_obj:
            raise ValueError("No object selected.")

        # 复制对象，并重置平移和旋转属性
        smooth_group = cmds.duplicate(selected_obj, name=selected_obj + '_smooth_cam')[0]
        cmds.setAttr(f'{smooth_group}.translate', 0, 0, 0)
        cmds.setAttr(f'{smooth_group}.rotate', 0, 0, 0)

        # 遍历每个属性，并复制动画关键帧
        for attr in ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']:
            # 复制关键帧
            cmds.copyKey(f'{selected_obj}.{attr}')
            # 粘贴到新对象的对应属性上
            cmds.pasteKey(f'{smooth_group}.{attr}')

        # 遍历每个属性，并复制动画关键帧
        for attr in ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']:
            keyframes = cmds.keyframe(smooth_group, attribute=attr, query=True)
            values = cmds.keyframe(smooth_group, attribute=attr, query=True, valueChange=True)

            if keyframes:
                # 初始化起始帧和结束帧
                start_frame = None
                end_frame = None

                # 遍历关键帧，寻找开始和结束变化的帧
                for i in range(len(keyframes) - 1):
                    if values[i] != values[i + 1]:
                        start_frame = keyframes[i]
                        break

                for i in range(len(keyframes) - 1, 0, -1):
                    if values[i] != values[i - 1]:
                        end_frame = keyframes[i]
                        break

                # 如果没有找到变化，则将起始帧设置为第一帧
                if start_frame is None:
                    start_frame = keyframes[0]
                if end_frame is None:
                    end_frame = keyframes[-1]
                #print(f"{smooth_group}_{attr}_{start_frame}_{end_frame}")
                if attr not in ['translateX', 'translateY', 'translateZ']:
                    self.smooth_keyframes(smooth_group, attr, start_frame, end_frame)
        self.Smooth_Object = smooth_group
        self.update_smooth_obj()

    def smooth_keyframes(self,object_name, attribute, start_frame, end_frame):
        sampling_rate = 0.65
        cutoff_frequency = 30
        try:
            sampling_rate = float(self.sampling_rate_text.text())
        except:
            sampling_rate = 0.65  # 当转换失败时使用默认值

        try:
            cutoff_frequency = int(self.cutoff_frequency_text.text())
        except:
            cutoff_frequency = 30  # 当转换失败时使用默认值

        """
        对指定对象和属性的关键帧应用平滑滤波器。

        :param object_name: 对象名称
        :param attribute: 属性名称
        :param start_frame: 平滑开始的帧数
        :param end_frame: 平滑结束的帧数
        :param cutoff_frequency: 截止频率，默认为2
        :param sampling_rate: 采样率，默认为1
        """
        cmds.select(clear=True)
        cmds.select(object_name, replace=True)
        # 构建MEL命令字符串
        clear_selection_cmd = 'selectKey -clear;'
        select_key_cmd = 'selectKey -add -k -t "{0}:{1}" {2}_{3};'.format(start_frame, end_frame, object_name, attribute)
        filter_curve_cmd = 'filterCurve -f butterworth -cof {0} -sr {1} -kof -sk;'.format(cutoff_frequency, sampling_rate)
        #print(f"{object_name}_{attribute}_{start_frame}_{end_frame}")
        #print(select_key_cmd)
        # 执行MEL命令

        mel.eval(clear_selection_cmd)
        mel.eval(select_key_cmd)
        mel.eval(filter_curve_cmd)

    def bake(self,anno=True):
        if  self.p1 == False:
            QtWidgets.QMessageBox.warning(self, "warning", "constraint before bake.", QtWidgets.QMessageBox.Ok)
            return
        if self.Object and self.Smooth_Object:
            keyframes = cmds.keyframe(self.Object, query=True)
        else :
            QtWidgets.QMessageBox.warning(self, "warning", "no vcam or no Smooth camera ", QtWidgets.QMessageBox.Ok)
            return

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
                   'rotateZ', ]
        for frame in keyframes:
            for attra, attrb in zip(attrs_a, attrs_b):
                value = cmds.getAttr(f'{self.sub_namespace}:{attra}.{attrb}', time=frame)
                cmds.setKeyframe(f"{self.namespace}:{attra}", attribute=attrb, time=frame, value=value)
        cmds.file(r"K:/Jaguar/11_Users/Q/camera_rig/JCQcam.ma", removeReference=True)
        if cmds.namespace(exists="JCQ"):
            nodes = cmds.namespaceInfo("JCQ", listOnlyDependencyNodes=True)
            if nodes:
                for node in nodes:
                    cmds.delete(node)
            cmds.namespace(removeNamespace="JCQ", mergeNamespaceWithRoot=True)

        cmds.delete("JCQcamRNfosterParent1")
        cmds.delete(self.offset_group)
        cmds.delete(self.offset_group2)
        cmds.delete(self.Smooth_Object)
        self.Smooth_Object = ""
        self.update_smooth_obj()
        self.p1 = False
        if anno:
            QtWidgets.QMessageBox.warning(self, "finished", "bake finished.", QtWidgets.QMessageBox.Ok)
    def main(self):
        if not self.constraint_cam(anno=False):
            self.bake(anno=False)
            QtWidgets.QMessageBox.warning(self, "finished", "constraint and bake finished.", QtWidgets.QMessageBox.Ok)
    def constraint_cam(self,anno=True):

        # 获取text2中的物体名称
        target_name = self.text2.text()
        if not target_name:
            QtWidgets.QMessageBox.warning(self, "warning", "No target object specified in text2.", QtWidgets.QMessageBox.Ok)
            #cmds.warning("No target object specified in text2.")
            return True

        # 分析命名空间
        self.namespace = target_name.split(':')[0] if ':' in target_name else ''
        if not self.namespace:
            QtWidgets.QMessageBox.warning(self, "warning", "No namespace found in the target object name.", QtWidgets.QMessageBox.Ok)
            #cmds.warning("No namespace found in the target object name.")
            return True

        # 获取text1中的相机名称
        camera_name = self.text1.text()
        if not camera_name:
            QtWidgets.QMessageBox.warning(self, "warning", "No camera object specified in text1..", QtWidgets.QMessageBox.Ok)
            #cmds.warning("No camera object specified in text1.")
            return True
        self.Object=camera_name

        self.create_smooth_and_noise_groups_v2(camera_name)

        offset_values = cmds.getAttr(f"{self.Object}.rotateAxis")[0]
        cmds.setAttr(f"{self.Object}.scaleX", 1)
        cmds.setAttr(f"{self.Object}.scaleY", 1)
        cmds.setAttr(f"{self.Object}.scaleZ", 1)


        self.offset_group = cmds.group(em=True, name=self.Object + 'offset_group')
        self.offset_group2 = cmds.group(em=True, name=self.Object + 'offset_group2')
        cmds.parent(self.offset_group, self.Smooth_Object)
        cmds.parent(self.offset_group2, self.Object)
        cmds.setAttr(f'{self.offset_group}.translate', 0, 0, 0)
        cmds.setAttr(f'{self.offset_group}.rotate', 0, 0, 0)
        cmds.setAttr(f'{self.offset_group2}.translate', 0, 0, 0)
        cmds.setAttr(f'{self.offset_group2}.rotate', 0, 0, 0)

        try:
            cmds.file(r"K:/Jaguar/11_Users/Q/camera_rig/JCQcam.ma", removeReference=True)
        except:
            pass
        if cmds.namespace(exists="JCQ"):
            nodes = cmds.namespaceInfo("JCQ", listOnlyDependencyNodes=True)
            if nodes:
                for node in nodes:
                    cmds.delete(node)
            cmds.namespace(removeNamespace="JCQ", mergeNamespaceWithRoot=True)

        file_path="K:/Jaguar/11_Users/Q/camera_rig/JCQcam.ma"
        cmds.file(file_path, reference=True, namespace=":")


        try:
            for attr in ["TransAmplitude","RotAmplitude"]:
                cmds.setAttr(f"{self.namespace}:camMainOpt.{attr}", 0)
        except:
            pass

        # 创建约束
        keyframes = cmds.keyframe(self.Object, query=True)
        first_keyframe_time = min(keyframes)
        last_keyframe_time = max(keyframes)

        #cmds.pointConstraint(self.offset_group, f"{self.sub_namespace}:camMainAndRotateY", maintainOffset=False)
        #cmds.orientConstraint(self.offset_group, f"{self.sub_namespace}:camMainAndRotateY ", skip=("x", "z"), maintainOffset=False)
        cmds.parentConstraint(self.offset_group, f"{self.sub_namespace}:camMainAndRotateY",skipRotate=("x", "z"), maintainOffset=False)

        cmds.orientConstraint(self.offset_group, f"{self.sub_namespace}:camRotateX ", skip=("y", "z"), maintainOffset=False)
        cmds.orientConstraint(self.offset_group, f"{self.sub_namespace}:camRotateZ ", skip=("x", "y"), maintainOffset=False)
        if cmds.keyframe(f"{self.Object}.focalLength", query=True):
            cmds.copyKey(f"{self.Object}.focalLength")
            cmds.pasteKey(f"{self.sub_namespace}:camMainOpt.focalLength")
        else:
            value = cmds.getAttr(f"{self.Object}.focalLength")
            cmds.setKeyframe(f"{self.sub_namespace}:camMainOpt.focalLength", time=(first_keyframe_time, last_keyframe_time), value=value)
        if cmds.keyframe(f"{self.Object}.focusDistance", query=True):
            cmds.copyKey(f"{self.Object}.focusDistance")
            cmds.pasteKey(f"{self.sub_namespace}:focusPoint.translateZ")
        else:
            value = cmds.getAttr(f"{self.Object}.focusDistance")
            cmds.setKeyframe(f"{self.sub_namespace}:focusPoint.translateZ", time=(first_keyframe_time, last_keyframe_time), value=value)
        cmds.pointConstraint(self.offset_group2, f"{self.sub_namespace}:camShakeAnim", maintainOffset=False)
        cmds.orientConstraint(self.offset_group2, f"{self.sub_namespace}:camShakeAnim ", maintainOffset=False)
        self.p1 = True
        if anno:
            QtWidgets.QMessageBox.warning(self, "finished", "constraint finished.", QtWidgets.QMessageBox.Ok)




# 创建窗口实例
window = MyWindow()
