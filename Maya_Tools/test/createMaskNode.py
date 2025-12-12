# Create MaskNode
import pymel.core as pm
import maya.cmds as cmds

def create_mask_node():
    if not pm.pluginInfo('mask_node.py', q=True, loaded=True):
        pm.loadPlugin('mask_node.py')
        mask_node = pm.ls(type='mask_node')
        if mask_node:
            return mask_node[0]
        else:
            transform_node = pm.createNode("transform", name='mask_node')
            mask_node = pm.createNode('mask_node', name='mask_nodeShape', parent=transform_node)
            return mask_node

def ini_mask_node(node):
    node.setAttr('topLeftData', 1)
    node.setAttr('topCenterData', 2)
    node.setAttr('topRightData', 3)
    node.setAttr('bottomLeftData', 7)
    node.setAttr('bottomCenterData', 5)
    node.setAttr('bottomRightData', 8)
    node.setAttr('centerData', 9)
    node.setAttr('textPadding', 6)
    node.setAttr('borderAlpha', 0)

node = create_mask_node()
ini_mask_node(node)