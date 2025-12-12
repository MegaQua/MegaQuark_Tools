import maya.cmds as cmds


def unlock_all_nodes_and_attrs():
    all_nodes = cmds.ls(long=True)
    for node in all_nodes:
        try:

            if cmds.lockNode(node, q=True, lock=True)[0]:
                cmds.lockNode(node, lock=False, lockUnpublished=False)


            all_attrs = cmds.listAttr(node, locked=True) or []
            for attr in all_attrs:
                try:
                    cmds.setAttr(f"{node}.{attr}", lock=False)
                except:
                    pass
        except Exception as e:
            print(f"skip {node}: {e}")


unlock_all_nodes_and_attrs()