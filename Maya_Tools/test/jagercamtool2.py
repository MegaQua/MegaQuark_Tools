from PySide2 import QtWidgets, QtGui, QtCore



class MyWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MyWindow, self).__init__(None)
        self.setWindowTitle("jager camera tool")

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
            "rotate_threshold": 1,
            "translate_deviation" : 0.1,
            "rotate_deviation" : 20,
            "n_frames" : 4,
            "translateX_correction" : 0,
            "translateY_correction" : 0,
            "translateZ_correction" : 0,
            "rotateX_correction" : 0,
            "rotateY_correction" : 0,
            "rotateZ_correction" : 0,
            "excessive_deviation_threshold" : 1,
            "useless_rate_threshold": 0.1
        }

        # 创建标签和文本框
        self.textEdits = {}
        row = 0
        for param, value in self.params.items():
            label = QtWidgets.QLabel(param, self.groupBox)
            textEdit = QtWidgets.QLineEdit(self.groupBox)
            textEdit.setText(str(value))
            textEdit.textChanged.connect(lambda text, p=param: self.on_text_changed(p, text))

            groupBoxLayout.addWidget(label, row, 0)
            groupBoxLayout.addWidget(textEdit, row, 1)
            self.textEdits[param] = textEdit
            row += 1

        #self.setLayout(groupBoxLayout)

        # 创建布局

        layout = QtWidgets.QGridLayout()
        layout.addWidget(button1, 0, 0)  # 第0行，第0列
        layout.addWidget(self.text1, 0, 1)  # 第0行，第1列
        layout.addWidget(button2, 1, 0)  # 第1行，第0列
        layout.addWidget(self.text2, 1, 1)  # 第1行，第1列
        layout.addWidget(button3, 2, 0)  # 第2行，第0列
        #layout.addWidget(self.checkbox, 2, 1)
        layout.addWidget(self.checkbox3, 3, 0)
        #layout.addWidget(self.checkbox2, 3, 1)
        layout.addWidget(self.groupBox, 4, 0, 1, 2)

        self.setLayout(layout)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        #self.resize(1, 1)
        self.Object=""
        self.Smooth_Object = ""
        self.Shake_Object = ""
        self.Aim_Object = ""

        self.show()
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

        smooth_group = cmds.duplicate(selected_obj, name=selected_obj + '_test_cam')[0]
        cmds.setAttr(f'{smooth_group}.translate', 0, 0, 0)
        cmds.setAttr(f'{smooth_group}.rotate', 0, 0, 0)
        #smooth_group = cmds.group(em=True, name=selected_obj + '_smooth_anim')
        #noise_group=cmds.group(em=True, name=selected_obj + '_shake_anim')

        # 设置层级结构
        #cmds.parent(test_obj, noise_group)
        #cmds.parent(noise_group, smooth_group)

        #offset_values = cmds.getAttr(f"{smooth_group}.rotateAxis")[0]
        #cmds.setAttr(f"{smooth_group}.rotateAxis", *offset_values)

        translate_threshold = self.params.get("translate_threshold")
        rotate_threshold = self.params.get("rotate_threshold")
        translate_deviation = self.params.get("translate_deviation")
        rotate_deviation = self.params.get("rotate_deviation")
        n_frames = self.params.get("n_frames")
        excessive_deviation_threshold = self.params.get("excessive_deviation_threshold")
        useless_rate_threshold = self.params.get("useless_rate_threshold")


        corrections = {
            'translateX': self.params.get("translateX_correction"),
            'translateY': self.params.get("translateY_correction"),
            'translateZ': self.params.get("translateZ_correction"),
            'rotateX': self.params.get("rotateX_correction"),
            'rotateY': self.params.get("rotateY_correction"),
            'rotateZ': self.params.get("rotateZ_correction"),
        }

        # 处理 translate 和 rotate 的每个属性
        for attr in ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']:
            is_translate = 'translate' in attr
            threshold = translate_threshold + corrections[attr] if is_translate else rotate_threshold + corrections[attr]
            deviation_threshold = (translate_deviation + corrections[attr]) if is_translate else (rotate_deviation + corrections[attr])
            # deviation_threshold = translate_deviation if is_translate else rotate_deviation

            keyframes = cmds.keyframe(selected_obj, attribute=attr, query=True)

            if not keyframes:
                continue

            # 对每个关键帧进行处理
            for frame in keyframes:

                current_value = cmds.getAttr(f'{selected_obj}.{attr}', time=frame)

                if frame == keyframes[0]:
                    first_value = current_value
                    cmds.setKeyframe(smooth_group, attribute=attr, time=frame, value=current_value)
                    continue

                start_frame = max(frame - n_frames, min(keyframes))
                end_frame = min(frame + n_frames + 1, max(keyframes) + 1)
                frame_range = range(int(start_frame), int(end_frame))
                frame_values = [cmds.getAttr(f'{selected_obj}.{attr}', time=f) for f in frame_range]

                if len(frame_values) >= 3:
                    frame_values.remove(max(frame_values))
                    frame_values.remove(min(frame_values))

                avg_value = sum(frame_values) / len(frame_values)

                if abs(current_value - avg_value) < threshold:
                    continue
                else:
                    prev_frame = frame - 1
                    cmds.setKeyframe(smooth_group, attribute=attr, time=frame, value=current_value)
                    if cmds.keyframe(smooth_group, attribute=attr, query=True, time=(prev_frame, prev_frame)) and prev_frame != keyframes[0]:
                        cmds.cutKey(smooth_group, time=(prev_frame, prev_frame), attribute=attr)

            # 检查偏离并根据需要调整关键帧
            for frame in keyframes:
                original_value = cmds.getAttr(f'{selected_obj}.{attr}', time=frame)
                smooth_value = cmds.getAttr(f'{smooth_group}.{attr}', time=frame)
                if abs(original_value - smooth_value) > deviation_threshold and abs(original_value - smooth_value) <= excessive_deviation_threshold:
                    prev_frame = frame - 1
                    cmds.setKeyframe(smooth_group, attribute=attr, time=frame, value=original_value)
                    # if cmds.keyframe(smooth_group, attribute=attr, query=True, time=(prev_frame, prev_frame)) and prev_frame!=keyframes[0]:
                    #    cmds.cutKey(smooth_group, time=(prev_frame, prev_frame), attribute=attr)

            keyframes_smooth_group = cmds.keyframe(smooth_group, attribute=attr, query=True)
            # 遍历关键帧
            if keyframes_smooth_group:
                for _ in range(2):
                    for i in range(1, len(keyframes_smooth_group) - 1):  # 跳过第一个和最后一个关键帧
                        try:
                            current_frame = keyframes_smooth_group[i]
                            prev_frame = keyframes_smooth_group[i - 1]
                            next_frame = keyframes_smooth_group[i + 1]

                            # 获取关键帧的值
                            current_value = cmds.getAttr(f'{smooth_group}.{attr}', time=current_frame)
                            prev_value = cmds.getAttr(f'{smooth_group}.{attr}', time=prev_frame)
                            next_value = cmds.getAttr(f'{smooth_group}.{attr}', time=next_frame)

                            # 计算值变化率
                            rate_prev = (current_value - prev_value) / (current_frame - prev_frame)
                            rate_next = (next_value - current_value) / (next_frame - current_frame)

                            # 判断是否为无用帧
                            if abs(rate_next - rate_prev) < useless_rate_threshold:
                                cmds.cutKey(smooth_group, time=(current_frame, current_frame), attribute=attr)
                                del keyframes_smooth_group[i]
                            if len(keyframes_smooth_group) <= 3:
                                break
                        except:
                            pass



        self.Smooth_Object = smooth_group
        #self.Shake_Object = noise_group
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
        """
        # 复制相机并重命名
        aim_camera = cmds.group(em=True, name=self.Object + "_aim_anim")
        aim_camera2 = cmds.group(em=True, name=self.Object + "_aim_anim2")
        # 创建一个新的locator作为瞄准目标
        aim_locator = cmds.spaceLocator(name=self.Object + "_aim_locator")[0]
        aim_locator2 = cmds.spaceLocator(name=self.Object + "_aim_locator2")[0]
        # 将locator放置在原始相机的位置
        cmds.matchTransform(aim_locator, self.Object, position=True)
        cmds.matchTransform(aim_locator, self.Object, rotation=True)
        cmds.matchTransform(aim_locator2, self.Smooth_Object, position=True)
        cmds.matchTransform(aim_locator2, self.Smooth_Object, rotation=True)
        cmds.rotate(-offset_values[0], -offset_values[1], -offset_values[2], aim_locator, relative=True, objectSpace=True)
        cmds.rotate(-offset_values[0], -offset_values[1], -offset_values[2], aim_locator2, relative=True, objectSpace=True)
        cmds.move(0, 0, cmds.getAttr(f"{self.Object}.focusDistance"), aim_locator, relative=True, objectSpace=True, worldSpaceDistance=0)
        cmds.move(0, 0, cmds.getAttr(f"{self.Object}.focusDistance"), aim_locator2, relative=True, objectSpace=True, worldSpaceDistance=0)
        cmds.parentConstraint(camera_name, aim_locator, maintainOffset=True)
        cmds.parentConstraint(camera_name, aim_locator, maintainOffset=True)
        # 创建瞄准约束
        cmds.aimConstraint(aim_locator, aim_camera, aimVector=[0, 0, -1], upVector=[0, 1, 0], worldUpType="vector")
        cmds.aimConstraint(aim_locator2, aim_camera2, aimVector=[0, 0, -1], upVector=[0, 1, 0], worldUpType="vector")
        # 复制原始相机的动画到新相机
        for attr in ["translateX", "translateY", "translateZ"]:
            # 如果原相机上有动画曲线，则复制到新相机
            if cmds.listConnections(camera_name + '.' + attr, type='animCurve'):
                cmds.copyKey(camera_name, attribute=attr)
                cmds.pasteKey(aim_camera, attribute=attr)
            if cmds.listConnections(self.Smooth_Object + '.' + attr, type='animCurve'):
                cmds.copyKey(self.Smooth_Object, attribute=attr)
                cmds.pasteKey(aim_camera2, attribute=attr)
        """
        offset_group = cmds.group(em=True, name=self.Object + '_offset_group')
        offset_group2 = cmds.group(em=True, name=self.Object + '_offset_group2')
        cmds.parent(offset_group, Smooth_camera_name)
        cmds.parent(offset_group2, self.Object)
        cmds.setAttr(f'{offset_group}.translate', 0, 0, 0)
        cmds.setAttr(f'{offset_group}.rotate', 0, 0, 0)
        cmds.setAttr(f'{offset_group2}.translate', 0, 0, 0)
        cmds.setAttr(f'{offset_group2}.rotate', 0, 0, 0)


        # 创建约束

        #cmds.parentConstraint(f"{namespace}:camMainAndRotateY", f"{namespace}:camUp", maintainOffset=True, skipRotate=("x", "y", "z"))
        cmds.pointConstraint(offset_group, f"{namespace}:camMainAndRotateY", maintainOffset=False)
        cmds.orientConstraint(offset_group, f"{namespace}:camRotateZ ", skip=("x", "y"), maintainOffset=False)
        cmds.orientConstraint(offset_group, f"{namespace}:camRotateX ", skip=("y", "z"), maintainOffset=False)
        cmds.orientConstraint(offset_group, f"{namespace}:camMainAndRotateY ", skip=("x", "z"), maintainOffset=False)
        #cmds.aimConstraint(camera_name, f"{namespace}:camRotateX", aimVector=[0, 0, -1], upVector=[0, 1, 0], worldUpType="vector", skip=("y", "z"))
        #cmds.aimConstraint(camera_name, f"{namespace}:camMainAndRotateY",  aimVector=[0, 0, -1], upVector=[1, 0, 0], worldUpType="vector", skip=("x", "z"))
        #cmds.pointConstraint(aim_locator, f"{namespace}:camAim", maintainOffset=False)
        cmds.connectAttr(f"{self.Object}.focalLength", f"{namespace}:camMainOpt.focalLength",)
        cmds.connectAttr(f"{self.Object}.focusDistance", f"{namespace}:focusPoint.translateZ", )
        cmds.parentConstraint(offset_group2, f"{namespace}:camShakeAnim", maintainOffset=True)
        #if self.Smooth_Object :
        #    if self.checkbox2.isChecked():
        #        cmds.parentConstraint(self.Object, f"{namespace}:camShakeAnim", maintainOffset=True, skipRotate="z")
        #    else:
        #        cmds.parentConstraint(self.Object, f"{namespace}:camShakeAnim", maintainOffset=True)


    def bake(self):
        # 在这里实现按钮的功能
        pass


# 创建窗口实例
window = MyWindow()
