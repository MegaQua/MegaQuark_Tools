import maya.cmds as cmds
import random

def random_delete_faces(percentage=10.0):
    # 选择一个物体
    selected_object = cmds.ls(selection=True)
    if not selected_object:
        cmds.warning("请在Maya中选择一个物体")
        return
    else:
        selected_object = selected_object[0]

    # 获取物体的面数量
    num_faces = cmds.polyEvaluate(selected_object, face=True)

    # 计算要选择和删除的面的数量（四舍五入），确保至少删除一个面
    num_faces_to_select = max(1, round(num_faces * (percentage / 100)))

    # 获取所有面的索引列表
    all_face_indices = list(range(num_faces))

    # 随机选择面的索引
    selected_faces_indices = random.sample(all_face_indices, min(num_faces_to_select, len(all_face_indices)))

    # 构建要删除的面的列表
    faces_to_delete = [f"{selected_object}.f[{index}]" for index in selected_faces_indices]

    # 一次性删除所有选定的面
    cmds.delete(faces_to_delete)

    print(f"已删除 {len(selected_faces_indices)} 个面")

# 调用函数，可以修改百分比参数
random_delete_faces(percentage=30.0)
