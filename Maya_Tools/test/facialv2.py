def browseFacialAnimation(self):
    affected_controllers = set()
    try:
        startframe = int(self.text_startFrame.text())
    except:
        QtWidgets.QMessageBox.warning(self, "", "Invalid input for start frame", QtWidgets.QMessageBox.Ok)
        return

    a2f_json_path = self.text_facialAnimPath.text()
    setting_path = 'S:/Public/qiu_yi/JCQ_Tool/data/LOarkit52.json'
    try:
        with open(a2f_json_path, 'r') as file:
            a2f_json_data = json.load(file)
        with open(setting_path, 'r') as file:
            setting_data = json.load(file)
    except Exception as e:
        QtWidgets.QMessageBox.warning(self, "Load Error", str(e), QtWidgets.QMessageBox.Ok)
        return

    numFrames = a2f_json_data['numFrames']
    facsNames = a2f_json_data['facsNames']
    weightMat = a2f_json_data['weightMat']
    selected_namespace = self.namespace_combo.currentText()

    # === 提取默认值表 ===
    default_value_map = setting_data.get("__defaultValues__", {})

    for frame_index in range(numFrames):
        controller_values = {}
        for facsIndex, facsName in enumerate(facsNames):
            weight = weightMat[frame_index][facsIndex]
            if weight == 0: continue
            if facsName in setting_data:
                facs_values = setting_data[facsName]
                for controller, attrs in facs_values.items():
                    for attr, base_value in attrs.items():
                        # === 应用默认值修正逻辑 ===
                        default_val = default_value_map.get(controller, {}).get(attr, 0.0)
                        final_value = weight * (base_value - default_val) + default_val

                        controller_values.setdefault(controller, {}).setdefault(attr, 0)
                        controller_values[controller][attr] += final_value

        for controller, attrs in controller_values.items():
            for attr, value in attrs.items():
                ctrl = f"{selected_namespace}:{controller}" if selected_namespace else controller
                try:
                    cmds.setAttr(f"{ctrl}.{attr}", value)
                    cmds.setKeyframe(f"{ctrl}.{attr}", time=startframe + frame_index)
                    affected_controllers.add(ctrl.split('.')[0])
                except Exception as e:
                    print(f"设置关键帧失败: {ctrl}.{attr} = {value}，错误：{e}")

    set_name = f"{selected_namespace}A2FcontrolerSet" if selected_namespace else "A2FcontrolerSet"
    if not cmds.objExists(set_name):
        cmds.sets(name=set_name, empty=True)
        for ctrl in affected_controllers:
            if cmds.objExists(ctrl):
                try:
                    cmds.sets(ctrl, add=set_name)
                except Exception as e:
                    print(f"添加 {ctrl} 到 Set 时出错：{e}")
    else:
        print(f"Set {set_name} 已存在，未添加任何对象。")

    QtWidgets.QMessageBox.information(self, "", "Import succeeded", QtWidgets.QMessageBox.Ok)



self.facial_importer_window = MyWindow()