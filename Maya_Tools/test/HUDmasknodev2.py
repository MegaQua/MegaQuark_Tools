import pymel.core as pm
import maya.cmds as cmds
import os
import inspect
import shutil


def create_mask_node(nodename):
    plugin_name = 'mask_node.py'
    current_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
    current_dir = current_dir.replace("tools", "test")
    plugin_path = os.path.join(current_dir, plugin_name)

    maya_version = "2023"
    user_plugin_dir = os.path.expanduser(f"~/Documents/maya/{maya_version}/plug-ins")
    os.makedirs(user_plugin_dir, exist_ok=True)

    target_path = os.path.join(user_plugin_dir, "mask_node.py")


    print(plugin_path)
    print(target_path)


    if not os.path.exists(target_path):
        try:
            shutil.copy2(plugin_path, target_path)
        except :
            print("copy fail")


    if pm.pluginInfo(plugin_name, q=True, loaded=True):
        loaded_plugin_path = pm.pluginInfo(plugin_name, q=True, path=True)
        if os.path.normpath(loaded_plugin_path) != os.path.normpath(target_path):
            pm.unloadPlugin(plugin_name)
            pm.loadPlugin(target_path)
    else:
        pm.loadPlugin(target_path)

    transform_node = pm.createNode("transform", name=nodename)
    mask_node = pm.createNode('mask_node', name=nodename + "Shape", parent=transform_node)
    return mask_node


def ini_mask_node(node):
    node.setAttr('topLeftData', 0)
    node.setAttr('topCenterData', 0)
    node.setAttr('topRightData', 0)
    node.setAttr('bottomLeftData', 0)
    node.setAttr('bottomCenterData', 0)
    node.setAttr('bottomRightData', 10)
    node.setAttr('centerData', 0)
    node.setAttr('textPadding', 0)
    node.setAttr('borderAlpha', 0)
    node.setAttr('borderScale', 0.9)
    node.setAttr('bottomBorder', False)
    node.setAttr('topBorder', False)
    node.setAttr('textPadding', 0)
    try:
        cmds.setAttr(f"{node.name()}.camera", "persp", type="string")
    except:
        print("persp does not exist")


nodename = "camera_mask_node"
if cmds.objExists(nodename):
    pm.delete(nodename)

mask_node = create_mask_node(nodename)
ini_mask_node(mask_node)
