selected_objects = cmds.ls(selection=True)
for obj in selected_objects:
    history_list = cmds.listHistory(obj)
    blendshape_nodes = cmds.ls(history_list, type="blendShape")
    if blendshape_nodes:
        print(f"BlendShape nodes found on {obj}: {blendshape_nodes}")
    else:
        print(f"No BlendShape nodes found on {obj}")
