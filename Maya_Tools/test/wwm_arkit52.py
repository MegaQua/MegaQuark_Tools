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

# 定义要跳过的属性列表，增加scaleX, scaleY, scaleZ
skip_attributes = ["visibility", "scaleX", "scaleY", "scaleZ"]

# 定义极小的属性值阈值
min_value_threshold = 1e-5

# 存储每个表情名称及其对应的属性值
expressions_attributes_dict = {}

# 获取当前选择的所有对象，此时保留命名空间
selected_objects = cmds.ls(selection=True)

# 遍历从1到52帧，对应于每个表情
for i, expression in enumerate(arkit52list, start=1):
    cmds.currentTime(i)  # 设置当前时间到对应帧
    objects_attributes_dict = {}  # 重置为当前帧的对象属性字典

    for obj in selected_objects:
        # 获取对象的所有可键属性
        keyable_attributes = cmds.listAttr(obj, keyable=True)
        if keyable_attributes:  # 确保对象有可键属性
            attributes_dict = {}
            for attr in keyable_attributes:
                if attr not in skip_attributes:
                    attr_value = cmds.getAttr("{}.{}".format(obj, attr))
                    # 不再跳过为0的值
                    attributes_dict[attr] = attr_value
            if attributes_dict:
                # 在此阶段保留命名空间以确保唯一性
                objects_attributes_dict[obj] = attributes_dict

    if objects_attributes_dict:
        expressions_attributes_dict[expression] = objects_attributes_dict

# 准备将数据写入 JSON，此时移除命名空间
for expression in expressions_attributes_dict:
    for obj in list(expressions_attributes_dict[expression]):
        # 删除命名空间，只保留对象的实际名称
        clean_name = obj.split(':')[-1]
        expressions_attributes_dict[expression][clean_name] = expressions_attributes_dict[expression].pop(obj)

# 将字典转换为 JSON 字符串并打印，确保使用ensure_ascii=False以支持非ASCII字符
json_str = json.dumps(expressions_attributes_dict, ensure_ascii=False, indent=4)

# 指定保存 JSON 文件的路径
json_file_path = "S:/Public/qiu_yi/JCQ_Tool/data/LOarkit52.json"

# 打开指定的文件并写入 JSON 字符串
# 打开指定的文件并写入 JSON 字符串
with open(json_file_path, "w", encoding="utf-8") as json_file:
    json_file.write(json_str)

