import maya.cmds as cmds

# 选择要操作的物体
selected_objects = cmds.ls(selection=True)

if selected_objects:
    for obj in selected_objects:
        # 获取物体的中心点位置（pivots）
        pivot_x = cmds.getAttr(obj + ".rotatePivotX")
        pivot_y = cmds.getAttr(obj + ".rotatePivotY")
        pivot_z = cmds.getAttr(obj + ".rotatePivotZ")

        # 使用doGroup命令将物体分组
        group_name = cmds.group(obj, name=obj + "_offset")

        # 将组的中心点位置（pivots）设置为与物体相同
        cmds.setAttr(group_name + ".rotatePivotX", pivot_x)
        cmds.setAttr(group_name + ".rotatePivotY", pivot_y)
        cmds.setAttr(group_name + ".rotatePivotZ", pivot_z)
        cmds.setAttr(group_name + ".scalePivotX", pivot_x)
        cmds.setAttr(group_name + ".scalePivotY", pivot_y)
        cmds.setAttr(group_name + ".scalePivotZ", pivot_z)

        # 获取物体的世界坐标原点位置
        world_origin = [0, 0, 0]

        # 计算移动偏移量，将组移动到世界坐标原点
        translation = [world_origin[0] - pivot_x, world_origin[1] - pivot_y, world_origin[2] - pivot_z]
        cmds.setAttr(group_name + ".translateX", translation[0])
        cmds.setAttr(group_name + ".translateY", translation[1])
        cmds.setAttr(group_name + ".translateZ", translation[2])

        # 冻结组的变换数值
        cmds.makeIdentity(group_name, apply=True, t=1, r=1, s=1)

        # 将组移动回初始位置
        cmds.setAttr(group_name + ".translateX", pivot_x)
        cmds.setAttr(group_name + ".translateY", pivot_y)
        cmds.setAttr(group_name + ".translateZ", pivot_z)

        print("已使用doGroup命令为物体 {} 创建组，并将组的中心点与物体的中心点一致，并冻结了组的变换数值，并将组移动回初始位置。".format(obj))
else:
    print("请先选择要操作的物体。")
