import pymel.core as pm
import maya.cmds as cmds
import sys

maya_python_version = sys.version_info[:3]
if maya_python_version == (3, 7, 7):
    subsyspath = 'S:\Public\qiu_yi\py3716\Lib\site-packages'
elif maya_python_version == (3, 10, 8):
    subsyspath = 'S:\Public\qiu_yi\JCQ_Tool\Lib\site-packages'
elif maya_python_version == (3, 9, 7):
    subsyspath = 'S:\Public\qiu_yi\py397\Lib\site-packages'
try:
    sys.path.insert(0, subsyspath)
except:
    pass

def create_mask_node(nodename):
    plugin_name = 'mask_node.py'
    plugin_path = r'S:\Public\qiu_yi\JCQ_Tool\codes\test\mask_node.py'

    if not pm.pluginInfo(plugin_name, q=True, loaded=True):
        pm.loadPlugin(plugin_path)

    transform_node = pm.createNode("transform", name=nodename)
    mask_node = pm.createNode('mask_node', name=nodename+"shape", parent=transform_node)
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

nodename = "camera_mask_node"
if not cmds.objExists(nodename):
    mask_nodes = pm.ls(type='mask_node')
    node = create_mask_node(nodename)
    ini_mask_node(node)
    cmds.setAttr("{}.camera".format(nodename), "persp", type="string")
    #cmds.setAttr("{}.fontColor".format(nodename), *(1, 1, 1), type="double3")