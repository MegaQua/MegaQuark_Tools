from PySide2 import QtWidgets, QtCore
import maya.cmds as cmds
import time  # 导入时间模块

class DropFrameTool(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drop Frame Tool")

        # 获取当前场景时间范围
        self.start_frame_default = int(cmds.playbackOptions(q=True, min=True))
        self.end_frame_default = int(cmds.playbackOptions(q=True, max=True))

        # 动画层通用名称变量
        self.layer_name_base = "dropFramelayer"

        # 创建主布局
        layout = QtWidgets.QGridLayout(self)

        # 下拉列表：列出 _dropFramelayerSet
        set_label = QtWidgets.QLabel("Select Set:")
        self.set_dropdown = QtWidgets.QComboBox()
        self.refresh_set_list()  # 初始化下拉列表
        layout.addWidget(set_label, 0, 0)
        layout.addWidget(self.set_dropdown, 0, 1)

        # 起始帧输入
        start_frame_label = QtWidgets.QLabel("Start Frame:")
        self.start_frame_input = QtWidgets.QSpinBox()
        self.start_frame_input.setRange(1, 10000)  # 设置帧范围
        self.start_frame_input.setValue(self.start_frame_default)  # 默认起始帧为当前场景起始帧
        layout.addWidget(start_frame_label, 1, 0)
        layout.addWidget(self.start_frame_input, 1, 1)

        # 结束帧输入
        end_frame_label = QtWidgets.QLabel("End Frame:")
        self.end_frame_input = QtWidgets.QSpinBox()
        self.end_frame_input.setRange(1, 10000)  # 设置帧范围
        self.end_frame_input.setValue(self.end_frame_default)  # 默认结束帧为当前场景结束帧
        layout.addWidget(end_frame_label, 2, 0)
        layout.addWidget(self.end_frame_input, 2, 1)

        # N 值调节输入
        n_label = QtWidgets.QLabel("Frame Interval (n):")
        self.n_input = QtWidgets.QSpinBox()
        self.n_input.setRange(1, 100)  # 设置 N 值范围
        self.n_input.setValue(5)  # 默认值为 5
        layout.addWidget(n_label, 3, 0)
        layout.addWidget(self.n_input, 3, 1)

        # 属性选择复选框
        self.translate_check = QtWidgets.QCheckBox("Translate (t)")
        self.translate_check.setChecked(True)
        layout.addWidget(self.translate_check, 4, 0, 1, 2)

        self.rotate_check = QtWidgets.QCheckBox("Rotate (r)")
        self.rotate_check.setChecked(True)
        layout.addWidget(self.rotate_check, 5, 0, 1, 2)

        self.scale_check = QtWidgets.QCheckBox("Scale (s)")
        self.scale_check.setChecked(False)
        layout.addWidget(self.scale_check, 6, 0, 1, 2)

        # 执行按钮
        run_btn = QtWidgets.QPushButton("Run")
        layout.addWidget(run_btn, 7, 0, 1, 2)

        # 刷新按钮
        refresh_btn = QtWidgets.QPushButton("Refresh Sets")
        layout.addWidget(refresh_btn, 8, 0, 1, 2)

        # 信号与槽
        run_btn.clicked.connect(self.main)
        refresh_btn.clicked.connect(self.refresh_set_list)

        # 保持窗口置顶
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    def refresh_set_list(self):
        """刷新下拉列表中的 _dropFramelayerSet 集合"""
        self.set_dropdown.clear()
        sets = cmds.ls("*_dropFramelayerSet", type="objectSet") or []
        self.set_dropdown.addItems(sets)
        self.set_dropdown.addItem("Create New Set")  # 添加新选项
        if not sets:
            self.set_dropdown.insertItem(0, "No _dropFramelayerSet found")
            self.set_dropdown.setCurrentIndex(0)

    def get_selected_set_members(self):
        """获取下拉列表中选中集合的成员"""
        selected_set = self.set_dropdown.currentText()
        if selected_set == "Create New Set":
            return self.create_new_set()
        elif cmds.objExists(selected_set):
            return cmds.sets(selected_set, q=True) or []
        else:
            return []

    def create_new_set(self):
        """创建一个新集合并将选定对象添加到集合中"""
        selected_objects = cmds.ls(selection=True)
        if not selected_objects:
            cmds.warning("No objects selected to create a new set.")
            return []

        # 弹出窗口输入集合名称
        new_set_name, ok = QtWidgets.QInputDialog.getText(self, "Create New Set", "Enter set name (will append '_dropFramelayerSet'):")
        if not ok or not new_set_name.strip():
            cmds.warning("Creation cancelled or invalid name.")
            return []

        full_set_name = f"{new_set_name.strip()}_dropFramelayerSet"
        new_set = cmds.createNode("objectSet", name=full_set_name)
        cmds.sets(selected_objects, add=new_set)
        print(f"Created new set: {full_set_name} with objects: {selected_objects}")

        # 刷新下拉列表并选中新创建的集合
        self.refresh_set_list()
        index = self.set_dropdown.findText(full_set_name)
        if index != -1:
            self.set_dropdown.setCurrentIndex(index)

        return selected_objects

    def mute_and_lock_layer(self, excluded_layer=None):
        """静音并锁定所有包含 layer_name_base 的动画层，除了指定的层"""
        layers = cmds.ls(f"*{self.layer_name_base}*", type="animLayer") or []
        for layer in layers:
            if layer != excluded_layer:
                cmds.setAttr(f"{layer}.mute", 1)
                cmds.animLayer(layer, edit=True, lock=True)

    def unmute_and_unlock_layer(self, layer_name):
        """取消静音并解锁动画层"""
        cmds.animLayer(layer_name, edit=True, lock=False)
        cmds.setAttr(f"{layer_name}.mute", 0)

    def ensure_object_in_layer(self, obj_name, anim_layer):
        """确保对象在指定的动画层中"""
        attributes = cmds.listAttr(obj_name, keyable=True, unlocked=True)
        if attributes:
            node_attrs = [f"{obj_name}.{attr}" for attr in attributes]
            cmds.animLayer(anim_layer, e=True, attribute=node_attrs)
        else:
            cmds.warning(f'Object "{obj_name}" has no keyable attributes to add to animation layer.')

    def ensure_animation_layer_exists(self, layer_name):
        """检查并确保指定的动画层存在，如果存在则提示是否创建新图层"""
        if cmds.objExists(layer_name):
            result = QtWidgets.QMessageBox.question(
                self,
                "Layer Exists",
                f"Animation layer '{layer_name}' already exists. Do you want to create a new layer with a numeric suffix?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if result == QtWidgets.QMessageBox.Yes:
                suffix = 1
                new_layer_name = f"{layer_name}_{suffix}"
                while cmds.objExists(new_layer_name):
                    suffix += 1
                    new_layer_name = f"{layer_name}_{suffix}"
                cmds.animLayer(new_layer_name)
                print(f"Animation layer '{new_layer_name}' created.")
                return new_layer_name
            else:
                print(f"Using existing animation layer '{layer_name}'.")
                return layer_name
        else:
            cmds.animLayer(layer_name)
            print(f"Animation layer '{layer_name}' created.")
            return layer_name

    def ensure_objects_in_layer(self, obj_list, layer_name):
        """确保动画层中包含指定对象列表中的所有对象"""
        if not cmds.objExists(layer_name):
            raise RuntimeError(f"Animation layer '{layer_name}' does not exist.")
        for obj_name in obj_list:
            attributes = cmds.listAttr(obj_name, keyable=True, unlocked=True)
            if attributes:
                node_attrs = [f"{obj_name}.{attr}" for attr in attributes]
                cmds.animLayer(layer_name, e=True, attribute=node_attrs)
                print(f"Added {obj_name} to animation layer '{layer_name}'.")
            else:
                cmds.warning(f'Object "{obj_name}" has no keyable attributes to add to animation layer.')

    def record_keyframes(self, obj_list, start_frame, end_frame, n):
        """记录对象列表的 n 倍数关键帧数据"""
        self.mute_and_lock_layer()  # 静音并锁定所有相关动画层

        key_frames_dict = {obj_name: [] for obj_name in obj_list}
        current_frame = start_frame
        while current_frame <= end_frame:
            cmds.currentTime(current_frame)
            for obj_name in obj_list:
                if self.translate_check.isChecked():
                    for attr in ["translateX", "translateY", "translateZ"]:
                        if cmds.keyframe(f"{obj_name}.{attr}", q=True, time=(start_frame, end_frame)):
                            key_frames_dict[obj_name].append({
                                'frame': current_frame,
                                attr: cmds.getAttr(f"{obj_name}.{attr}")
                            })
                if self.rotate_check.isChecked():
                    for attr in ["rotateX", "rotateY", "rotateZ"]:
                        if cmds.keyframe(f"{obj_name}.{attr}", q=True, time=(start_frame, end_frame)):
                            key_frames_dict[obj_name].append({
                                'frame': current_frame,
                                attr: cmds.getAttr(f"{obj_name}.{attr}")
                            })
                if self.scale_check.isChecked():
                    for attr in ["scaleX", "scaleY", "scaleZ"]:
                        if cmds.keyframe(f"{obj_name}.{attr}", q=True, time=(start_frame, end_frame)):
                            key_frames_dict[obj_name].append({
                                'frame': current_frame,
                                attr: cmds.getAttr(f"{obj_name}.{attr}")
                            })
            current_frame += n

        # 确保记录最后一帧
        if current_frame - n < end_frame:
            cmds.currentTime(end_frame)
            for obj_name in obj_list:
                if self.translate_check.isChecked():
                    for attr in ["translateX", "translateY", "translateZ"]:
                        if cmds.keyframe(f"{obj_name}.{attr}", q=True, time=(start_frame, end_frame)):
                            key_frames_dict[obj_name].append({
                                'frame': end_frame,
                                attr: cmds.getAttr(f"{obj_name}.{attr}")
                            })
                if self.rotate_check.isChecked():
                    for attr in ["rotateX", "rotateY", "rotateZ"]:
                        if cmds.keyframe(f"{obj_name}.{attr}", q=True, time=(start_frame, end_frame)):
                            key_frames_dict[obj_name].append({
                                'frame': end_frame,
                                attr: cmds.getAttr(f"{obj_name}.{attr}")
                            })
                if self.scale_check.isChecked():
                    for attr in ["scaleX", "scaleY", "scaleZ"]:
                        if cmds.keyframe(f"{obj_name}.{attr}", q=True, time=(start_frame, end_frame)):
                            key_frames_dict[obj_name].append({
                                'frame': end_frame,
                                attr: cmds.getAttr(f"{obj_name}.{attr}")
                            })

        return key_frames_dict

    def apply_keyframes(self, obj_list, key_frames_dict, start_frame, end_frame, n, layer_name):
        """将记录的关键帧数据应用到对象列表上"""
        self.unmute_and_unlock_layer(layer_name)
        for obj_name in obj_list:
            key_frames = key_frames_dict.get(obj_name, [])
            for kf in key_frames:
                frame_start = kf['frame']
                frame_end = frame_start + n
                if frame_start >= start_frame and frame_start < end_frame:
                    for frame in range(frame_start, min(frame_end, end_frame + 1)):
                        for attr, value in kf.items():
                            if attr == 'frame':
                                continue
                            if cmds.getAttr(f"{obj_name}.{attr}", lock=True):
                                cmds.warning(f"Skipping locked attribute: {obj_name}.{attr}")
                                continue
                            cmds.setKeyframe(obj_name, at=attr, t=frame, v=value, animLayer=layer_name)

    def remove_nokeyframe_obj(self,selected_set,start_frame,end_frame):
        # 遍历对象列表，移除在勾选属性范围内没有关键帧的对象
        filtered_set = []
        for obj in selected_set:
            has_keyframes = False
            if self.translate_check.isChecked():
                for attr in ["translateX", "translateY", "translateZ"]:
                    if cmds.keyframe(f"{obj}.{attr}", q=True, time=(start_frame, end_frame)):
                        has_keyframes = True
                        break
            if not has_keyframes and self.rotate_check.isChecked():
                for attr in ["rotateX", "rotateY", "rotateZ"]:
                    if cmds.keyframe(f"{obj}.{attr}", q=True, time=(start_frame, end_frame)):
                        has_keyframes = True
                        break
            if not has_keyframes and self.scale_check.isChecked():
                for attr in ["scaleX", "scaleY", "scaleZ"]:
                    if cmds.keyframe(f"{obj}.{attr}", q=True, time=(start_frame, end_frame)):
                        has_keyframes = True
                        break
            if has_keyframes:
                filtered_set.append(obj)
        return filtered_set
    def show_completion_message(self, object_count, elapsed_time):
        """弹出完成提示窗口"""
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle("Process Completed")
        msg_box.setText(f"Processed {object_count} objects in {elapsed_time:.2f} seconds.")
        msg_box.setIcon(QtWidgets.QMessageBox.Information)
        msg_box.exec_()


    def main(self):
        """主流程"""


        # 记录开始时间
        start_time = time.time()

        # 获取参数
        selected_set = self.get_selected_set_members()
        start_frame = self.start_frame_input.value()
        end_frame = self.end_frame_input.value()
        n = self.n_input.value()

        # 检查是否有选中对象
        if not selected_set:
            cmds.warning("No objects found in the selected set.")
            return

        selected_set = self.remove_nokeyframe_obj(selected_set,start_frame,end_frame)

        # 检查是否有剩余的对象
        if not selected_set:
            cmds.warning("No objects with keyframes found in the selected set.")
            return

        # 确保动画层存在
        layer_name = f"F{n}_{self.layer_name_base}"
        layer_name = self.ensure_animation_layer_exists(layer_name)

        # 更新动画层名称
        if layer_name:
            print(f"Updated layer_name to: {layer_name}")

        # 确保动画层包含所有选中的对象
        self.ensure_objects_in_layer(selected_set, layer_name)

        # 记录关键帧
        key_frames_dict = self.record_keyframes(selected_set, start_frame, end_frame, n)

        # 应用关键帧
        self.apply_keyframes(selected_set, key_frames_dict, start_frame, end_frame, n, layer_name)

        # 记录结束时间
        end_time = time.time()

        # 打印消耗时间和对象数量
        elapsed_time = end_time - start_time
        print(f"Processed {len(selected_set)} objects in {elapsed_time:.2f} seconds.")

        print(f"已完成集合中所有对象的降帧动画处理。")

        # 弹出完成提示窗口
        self.show_completion_message(len(selected_set), elapsed_time)
# 在 Maya 中显示窗口
if __name__ == "__main__":
    try:
        drop_frame_tool.close()  # 如果工具已经打开，先关闭
        drop_frame_tool.deleteLater()
    except:
        pass

    drop_frame_tool = DropFrameTool()
