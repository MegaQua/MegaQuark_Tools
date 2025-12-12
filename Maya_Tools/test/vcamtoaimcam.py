import maya.cmds as cmds


def create_aim_camera_from_selection():
    # 获取当前选择的相机
    selection = cmds.ls(selection=True, long=True)
    if not selection:
        raise RuntimeError("No camera selected.")


    original_camera = selection[0]

    # 确保选择的是相机

    # 复制相机并重命名
    duplicated_camera = cmds.duplicate(original_camera, name=original_camera + "_aim_camera")[0]

    # 创建一个新的locator作为瞄准目标
    aim_locator = cmds.spaceLocator(name=original_camera + "_aim_locator")[0]

    # 将locator放置在原始相机的位置
    cmds.matchTransform(aim_locator, original_camera, position=True)
    cmds.matchTransform(aim_locator, original_camera, rotation=True)
    cmds.move(1, 0, 0, aim_locator, relative=True, objectSpace=True, worldSpaceDistance=0)
    cmds.parentConstraint(original_camera, aim_locator, maintainOffset=True)

    # 设置rotateAxis属性
    new_rotate_axis = (0, 0, 0)
    cmds.setAttr(f"{duplicated_camera}.rotateAxis", *new_rotate_axis, type="double3")
    # 创建瞄准约束
    cmds.aimConstraint(aim_locator, duplicated_camera, aimVector=[0, 0, -1], upVector=[0, 1, 0], worldUpType="vector", skip=('z',))

    # 复制原始相机的动画到新相机
    for attr in ["translateX", "translateY", "translateZ"]:
        # 如果原相机上有动画曲线，则复制到新相机
        if cmds.listConnections(original_camera + '.' + attr, type='animCurve'):
            cmds.copyKey(original_camera, attribute=attr)
            cmds.pasteKey(duplicated_camera, attribute=attr)

    print("Aim camera created: " + duplicated_camera)


# 执行函数
create_aim_camera_from_selection()
