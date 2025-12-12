import maya.cmds as cmds

selected_objects_long_names = cmds.ls(selection=True, long=True)

for obj_long_name in selected_objects_long_names:
    #print(obj_long_name)
    attributes = [
            '.rotateX', '.rotateY', '.rotateZ',
            '.scaleX', '.scaleY', '.scaleZ',
            '.translateX', '.translateY', '.translateZ'
        ]

    for attr in attributes:
        print(obj_long_name + attr)
        cmds.setAttr(obj_long_name + attr, keyable=True)
        cmds.setAttr(obj_long_name + attr, lock=False)

