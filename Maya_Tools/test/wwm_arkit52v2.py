# -*- coding: utf-8 -*-
import maya.cmds as cmds
import json

# ARKit 表情名称列表
arkit52list = [
    'eyeBlinkLeft', 'eyeLookDownLeft', 'eyeLookInLeft', 'eyeLookOutLeft', 'eyeLookUpLeft',
    'eyeSquintLeft', 'eyeWideLeft', 'eyeBlinkRight', 'eyeLookDownRight', 'eyeLookInRight',
    'eyeLookOutRight', 'eyeLookUpRight', 'eyeSquintRight', 'eyeWideRight', 'jawForward',
    'jawLeft', 'jawRight', 'jawOpen', 'mouthClose', 'mouthFunnel', 'mouthPucker',
    'mouthLeft', 'mouthRight', 'mouthSmileLeft', 'mouthSmileRight', 'mouthFrownLeft',
    'mouthFrownRight', 'mouthDimpleLeft', 'mouthDimpleRight', 'mouthStretchLeft',
    'mouthStretchRight', 'mouthRollLower', 'mouthRollUpper', 'mouthShrugLower',
    'mouthShrugUpper', 'mouthPressLeft', 'mouthPressRight', 'mouthLowerDownLeft',
    'mouthLowerDownRight', 'mouthUpperUpLeft', 'mouthUpperUpRight', 'browDownLeft',
    'browDownRight', 'browInnerUp', 'browOuterUpLeft', 'browOuterUpRight', 'cheekPuff',
    'cheekSquintLeft', 'cheekSquintRight', 'noseSneerLeft', 'noseSneerRight', 'tongueOut'
]

# 跳过这些属性的采集
skip_attributes = ["visibility"]
min_value_threshold = 1e-5  # 非零判断的阈值

# 获取当前选择的所有对象
selected_objects = cmds.ls(selection=True)
if not selected_objects:
    cmds.warning("请先选择控制器对象")
    raise RuntimeError("没有选择对象")

# === Step 1: 记录第0帧的默认值（非0） ===
cmds.currentTime(0)
default_values_dict = {}

for obj in selected_objects:
    clean_name = obj.split(":")[-1]
    keyable_attributes = cmds.listAttr(obj, keyable=True)
    if not keyable_attributes:
        continue

    default_attr_dict = {}
    for attr in keyable_attributes:
        if attr in skip_attributes:
            continue
        try:
            val = cmds.getAttr(f"{obj}.{attr}")
            if abs(val) > min_value_threshold:
                default_attr_dict[attr] = val
        except Exception as e:
            print(f"[警告] 获取 {obj}.{attr} 失败: {e}")

    if default_attr_dict:
        default_values_dict[clean_name] = default_attr_dict

# === Step 2: 记录每帧表情对应的属性动画 ===
expressions_attributes_dict = {}

for i, expression in enumerate(arkit52list, start=1):
    cmds.currentTime(i)
    frame_data = {}

    for obj in selected_objects:
        clean_name = obj.split(":")[-1]
        keyable_attributes = cmds.listAttr(obj, keyable=True)
        if not keyable_attributes:
            continue

        attr_values = {}
        for attr in keyable_attributes:
            if attr in skip_attributes:
                continue
            try:
                val = cmds.getAttr(f"{obj}.{attr}")
                attr_values[attr] = val
            except Exception as e:
                print(f"[警告] 获取 {obj}.{attr} 失败: {e}")

        if attr_values:
            frame_data[clean_name] = attr_values

    if frame_data:
        expressions_attributes_dict[expression] = frame_data

# === Step 3: 加入默认值字段，并写入JSON ===
expressions_attributes_dict["__defaultValues__"] = default_values_dict
json_file_path = "S:/Public/qiu_yi/JCQ_Tool/data/LOarkit52_newrig.json"

with open(json_file_path, "w", encoding="utf-8") as json_file:
    json.dump(expressions_attributes_dict, json_file, ensure_ascii=False, indent=4)

print(f"[成功] 表情动画与默认值已保存至：{json_file_path}")
