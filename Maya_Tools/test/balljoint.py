import maya.cmds as cmds

# 获取当前选择的关节
selected_joints = cmds.ls(selection=True, type='joint')
if not selected_joints:
    cmds.warning("请先选择一系列关节")
else:
    for joint in selected_joints:
        # 获取关节的名称
        joint_name = joint.split('|')[-1]

        # 创建球体并设置半径为2
        sphere = cmds.polySphere(radius=2)[0]

        # 删除球体的历史记录
        cmds.delete(constructionHistory=True)

        # 重命名球体为关节名称 + "ball" 后缀
        ball_name = joint_name + "ball"
        cmds.rename(sphere, ball_name)

        # 获取关节的世界坐标
        joint_position = cmds.xform(joint, query=True, translation=True, worldSpace=True)

        # 将球体移动到关节的位置
        cmds.move(joint_position[0], joint_position[1], joint_position[2], ball_name, absolute=True)

        # 创建蒙皮集群
        skin_cluster = cmds.skinCluster(joint, ball_name)[0]

    print("完成关节球体的蒙皮绑定")
