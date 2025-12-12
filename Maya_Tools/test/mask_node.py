# coding: utf-8
###############################################################################
# Name:
#   mask_node.py
#
# Author:
#   Chris Zurbrigg (http://zurbrigg.com)
#
# Usage:
#   Visit http://zurbrigg.com for details
#
# Copyright (C) 2018 Chris Zurbrigg. All rights reserved.
###############################################################################
__version__ = "1.0.2"
import getpass
import time

import maya.api.OpenMaya as om
import maya.api.OpenMayaRender as omr
import maya.api.OpenMayaUI as omui
import maya.cmds as cmds
import pymel.core as pm

LABEL_ATTRS = [("topLeftLabel", "tll"),
               ("topCenterLabel", "tcl"),
               ("topRightLabel", "trl"),
               ("bottomLeftLabel", "bll"),
               ("bottomCenterLabel", "bcl"),
               ("bottomRightLabel", "brl"),
               ("centerLabel", 'cl')]

DATA_ATTRS = [("topLeftData", "tld"),
              ("topCenterData", "tcd"),
              ("topRightData", "trd"),
              ("bottomLeftData", "bld"),
              ("bottomCenterData", "bcd"),
              ("bottomRightData", "brd"),
              ("centerData", "cd")]

DATA_ITEMS = [
    (u'无', 'None'),
    (u'摄像机名称', 'Camera'),
    (u'摄像机名称 int', 'Camera int'),
    (u'日期', 'Date'),
    (u'任务环节', 'TaskType'),
    (u'帧范围', 'FrameRange'),
    (u'文件名', 'FileName'),
    (u'当前帧', 'CurFrame'),
    (u'用户名', 'User'),
    (u'当前帧/结尾帧', 'Cur_EndFrame'),
    (u'引用资产版本', 'AssetVersion'),
    (u'焦距+当前帧', 'focal length + CurFrame'),
    (u'焦距+当前帧', 'focal length + CurFrame (int)'),
]


def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass


class ZShotMaskLocator(omui.MPxLocatorNode):
    NAME = "mask_node"
    TYPE_ID = om.MTypeId(0x0011A885)
    DRAW_DB_CLASSIFICATION = "drawdb/geometry/mask_node"
    DRAW_REGISTRANT_ID = "mask_node"

    def __init__(self):
        super(ZShotMaskLocator, self).__init__()

    def excludeAsLocator(self):
        return False

    @classmethod
    def creator(cls):
        return ZShotMaskLocator()

    @classmethod
    def initialize(cls):
        attr = om.MFnTypedAttribute()
        stringData = om.MFnStringData()
        obj = stringData.create("")
        camera_name = attr.create("camera", "cam", om.MFnData.kString, obj)
        attr.writable = True
        attr.storable = True
        attr.keyable = False
        ZShotMaskLocator.addAttribute(camera_name)

        for i, attr in enumerate(LABEL_ATTRS, 1):
            attr_long_name, attr_short_name = attr
            attr = om.MFnTypedAttribute()
            stringData = om.MFnStringData()
            obj = stringData.create('')
            position = attr.create(attr_long_name, attr_short_name,
                                   om.MFnData.kString, obj)
            attr.writable = True
            attr.storable = True
            attr.keyable = True
            ZShotMaskLocator.addAttribute(position)

        for i, attr in enumerate(DATA_ATTRS, 1):
            attr_long_name, attr_short_name = attr
            attr = om.MFnEnumAttribute()
            enum = attr.create(attr_long_name, attr_short_name, 0)
            for m, attr_name in enumerate(DATA_ITEMS):
                attr.addField(attr_name[1], m)

            attr.storable = True
            attr.keyable = True
            ZShotMaskLocator.addAttribute(enum)

        attr = om.MFnNumericAttribute()
        counter_position = attr.create("textPadding", "tp",
                                       om.MFnNumericData.kShort, 10)
        attr.writable = True
        attr.storable = True
        attr.keyable = True
        attr.setMin(0)
        attr.setMax(50)
        ZShotMaskLocator.addAttribute(counter_position)

        attr = om.MFnTypedAttribute()
        stringData = om.MFnStringData()
        obj = stringData.create("Consolas")
        font_name = attr.create("fontName", "fn", om.MFnData.kString, obj)
        attr.writable = True
        attr.storable = True
        attr.keyable = True
        ZShotMaskLocator.addAttribute(font_name)

        attr = om.MFnTypedAttribute()
        stringData = om.MFnStringData()
        obj = stringData.create("Animation")
        task_type = attr.create("taskType", "tt", om.MFnData.kString, obj)
        attr.writable = True
        attr.storable = True
        attr.keyable = True
        ZShotMaskLocator.addAttribute(task_type)

        attr = om.MFnTypedAttribute()
        stringData = om.MFnStringData()
        obj = stringData.create("")
        error_asset_version = attr.create("errorAssetVersion", "eav",
                                          om.MFnData.kString, obj)
        attr.writable = True
        attr.storable = True
        attr.keyable = True
        ZShotMaskLocator.addAttribute(error_asset_version)

        attr = om.MFnNumericAttribute()
        font_color = attr.createColor("fontColor", "fc")
        attr.default = (0, 1, 0)
        attr.writable = True
        attr.storable = True
        attr.keyable = True
        ZShotMaskLocator.addAttribute(font_color)

        attr = om.MFnNumericAttribute()
        font_error_color = attr.createColor("fontErrorColor", "fec")
        attr.default = (1, 0, 0)
        attr.writable = True
        attr.storable = True
        attr.keyable = True
        ZShotMaskLocator.addAttribute(font_error_color)

        attr = om.MFnNumericAttribute()
        font_alpha = attr.create("fontAlpha", "fa", om.MFnNumericData.kFloat,
                                 1)
        attr.writable = True
        attr.storable = True
        attr.keyable = True
        attr.setMin(0)
        attr.setMax(1)
        ZShotMaskLocator.addAttribute(font_alpha)

        attr = om.MFnNumericAttribute()
        font_scale = attr.create("fontScale", "fs", om.MFnNumericData.kFloat,
                                 1)
        attr.writable = True
        attr.storable = True
        attr.keyable = True
        attr.setMin(0.1)
        attr.setMax(2.0)
        ZShotMaskLocator.addAttribute(font_scale)

        attr = om.MFnNumericAttribute()
        top_border = attr.create("topBorder", "tbd",
                                 om.MFnNumericData.kBoolean, True)
        attr.writable = True
        attr.storable = True
        attr.keyable = True
        ZShotMaskLocator.addAttribute(top_border)

        attr = om.MFnNumericAttribute()
        bottom_border = attr.create("bottomBorder", "bbd",
                                    om.MFnNumericData.kBoolean, True)
        attr.writable = True
        attr.storable = True
        attr.keyable = True
        ZShotMaskLocator.addAttribute(bottom_border)

        attr = om.MFnNumericAttribute()
        border_color = attr.createColor("borderColor", "bc")
        attr.default = (0, 0, 0)
        attr.writable = True
        attr.storable = True
        attr.keyable = True
        ZShotMaskLocator.addAttribute(border_color)

        attr = om.MFnNumericAttribute()
        border_alpha = attr.create("borderAlpha", "ba",
                                   om.MFnNumericData.kFloat, 0.5)
        attr.writable = True
        attr.storable = True
        attr.keyable = True
        attr.setMin(0)
        attr.setMax(1)
        ZShotMaskLocator.addAttribute(border_alpha)

        attr = om.MFnNumericAttribute()
        border_scale = attr.create("borderScale", "bs",
                                   om.MFnNumericData.kFloat, 1.0)
        attr.writable = True
        attr.storable = True
        attr.keyable = True
        attr.setMin(0.5)
        attr.setMax(4.0)
        ZShotMaskLocator.addAttribute(border_scale)


class ZShotMaskData(om.MUserData):
    """
    """

    def __init__(self):
        super(ZShotMaskData, self).__init__(False)  # don't delete after draw


class ZShotMaskDrawOverride(omr.MPxDrawOverride):
    """
    """

    NAME = "zshotmask_draw_override"

    def __init__(self, obj):
        super(ZShotMaskDrawOverride, self
              ).__init__(obj, ZShotMaskDrawOverride.draw)

    def supportedDrawAPIs(self):
        return (omr.MRenderer.kAllDevices)

    def isBounded(self, obj_path, camera_path):
        return False

    def boundingBox(self, obj_path, camera_path):
        return om.MBoundingBox()

    def prepareForDraw(self, obj_path, camera_path, frame_context, data):
        if not isinstance(data, ZShotMaskData):
            data = ZShotMaskData()

        fnDagNode = om.MFnDagNode(obj_path)

        data.camera_name = fnDagNode.findPlug("camera", False).asString()

        data.text_fields = []
        # 节点显示文字
        hud_command_map = self.get_data(fnDagNode)

        for i in range(len(LABEL_ATTRS)):
            label_attr = LABEL_ATTRS[i][0]
            data_attr = DATA_ATTRS[i][0]
            # 'topLeftLabel', 'topLeftData'
            label = fnDagNode.findPlug(label_attr, False).asString()
            data_index = fnDagNode.findPlug(data_attr, False).asInt()
            key = DATA_ITEMS[data_index][1]
            value = str(hud_command_map[key]())

            data.text_fields.append('{}{}'.format(label, value))

        data.text_padding = fnDagNode.findPlug("textPadding", False).asInt()
        data.font_name = fnDagNode.findPlug("fontName", False).asString()

        # font color
        r = fnDagNode.findPlug("fontColorR", False).asFloat()
        g = fnDagNode.findPlug("fontColorG", False).asFloat()
        b = fnDagNode.findPlug("fontColorB", False).asFloat()
        a = fnDagNode.findPlug("fontAlpha", False).asFloat()
        data.font_color = om.MColor((r, g, b, a))

        # error font color
        r = fnDagNode.findPlug("fontErrorColorR", False).asFloat()
        g = fnDagNode.findPlug("fontErrorColorG", False).asFloat()
        b = fnDagNode.findPlug("fontErrorColorB", False).asFloat()

        data.fontErrorColor = om.MColor((r, g, b, 0.5))

        data.font_scale = fnDagNode.findPlug("fontScale", False).asFloat()

        # 遮罩颜色设置
        r = fnDagNode.findPlug("borderColorR", False).asFloat()
        g = fnDagNode.findPlug("borderColorG", False).asFloat()
        b = fnDagNode.findPlug("borderColorB", False).asFloat()
        a = fnDagNode.findPlug("borderAlpha", False).asFloat()
        data.border_color = om.MColor((r, g, b, a))

        data.border_scale = fnDagNode.findPlug("borderScale", False).asFloat()

        data.top_border = fnDagNode.findPlug("topBorder", False).asBool()
        data.bottom_border = fnDagNode.findPlug("bottomBorder", False).asBool()

        return data

    def hasUIDrawables(self):
        return True

    def addUIDrawables(self, obj_path, draw_manager, frame_context, data):
        if not isinstance(data, ZShotMaskData):
            return

        camera_path = frame_context.getCurrentCameraPath()
        camera = om.MFnCamera(camera_path)
        if not data.camera_name or not self.camera_exists(data.camera_name):
            return

        camera_aspect_ratio = camera.aspectRatio()
        device_aspect_ratio = pm.getAttr("defaultResolution.deviceAspectRatio")

        vp_x, vp_y, vp_width, vp_height = frame_context.getViewportDimensions()
        vp_half_width = 0.5 * vp_width
        vp_half_height = 0.5 * vp_height
        vp_aspect_ratio = vp_width / float(vp_height)

        scale = 1

        if camera.filmFit == om.MFnCamera.kHorizontalFilmFit:
            mask_width = vp_width / camera.overscan
            mask_height = mask_width / device_aspect_ratio
        elif camera.filmFit == om.MFnCamera.kVerticalFilmFit:
            mask_height = vp_height / camera.overscan
            mask_width = mask_height * device_aspect_ratio
        elif camera.filmFit == om.MFnCamera.kFillFilmFit:
            if vp_aspect_ratio < camera_aspect_ratio:
                if camera_aspect_ratio < device_aspect_ratio:
                    scale = camera_aspect_ratio / vp_aspect_ratio
                else:
                    scale = device_aspect_ratio / vp_aspect_ratio
            elif camera_aspect_ratio > device_aspect_ratio:
                scale = device_aspect_ratio / camera_aspect_ratio

            mask_width = vp_width / camera.overscan * scale
            mask_height = mask_width / device_aspect_ratio

        elif camera.filmFit == om.MFnCamera.kOverscanFilmFit:
            if vp_aspect_ratio < camera_aspect_ratio:
                if camera_aspect_ratio < device_aspect_ratio:
                    scale = camera_aspect_ratio / vp_aspect_ratio
                else:
                    scale = device_aspect_ratio / vp_aspect_ratio
            elif camera_aspect_ratio > device_aspect_ratio:
                scale = device_aspect_ratio / camera_aspect_ratio

            mask_height = vp_height / camera.overscan / scale
            mask_width = mask_height * device_aspect_ratio
        else:
            om.MGlobal.displayError("[ZShotMask] Unknown Film Fit value")
            return

        mask_half_width = 0.5 * mask_width
        mask_x = vp_half_width - mask_half_width

        mask_half_height = 0.5 * mask_height
        mask_bottom_y = vp_half_height - mask_half_height
        mask_top_y = vp_half_height + mask_half_height

        border_height = int(0.05 * mask_height * data.border_scale)
        background_size = (int(mask_width), border_height)

        draw_manager.beginDrawable()
        draw_manager.setFontName(data.font_name)
        draw_manager.setFontSize(
            int((border_height - border_height * 0.15) * data.font_scale))
        draw_manager.setColor(data.font_color)

        if data.top_border:
            self.draw_border(draw_manager,
                             om.MPoint(mask_x, mask_top_y - border_height),
                             background_size, data.border_color)
        if data.bottom_border:
            self.draw_border(draw_manager, om.MPoint(mask_x, mask_bottom_y),
                             background_size, data.border_color)

        self.draw_text(draw_manager, om.MPoint(mask_x + data.text_padding,
                                               mask_top_y - border_height),
                       data.text_fields[0], omr.MUIDrawManager.kLeft,
                       background_size,color=data.border_color)
        self.draw_text(draw_manager,
                       om.MPoint(vp_half_width, mask_top_y - border_height),
                       data.text_fields[1], omr.MUIDrawManager.kCenter,
                       background_size,color=data.border_color)
        self.draw_text(draw_manager,
                       om.MPoint(mask_x + mask_width - data.text_padding,
                                 mask_top_y - border_height),
                       data.text_fields[2], omr.MUIDrawManager.kRight,
                       background_size,color=data.border_color)
        self.draw_text(draw_manager,
                       om.MPoint(mask_x + data.text_padding, mask_bottom_y),
                       data.text_fields[3], omr.MUIDrawManager.kLeft,
                       background_size,color=data.border_color)
        self.draw_text(draw_manager, om.MPoint(vp_half_width, mask_bottom_y),
                       data.text_fields[4], omr.MUIDrawManager.kCenter,
                       background_size,color=data.border_color)
        self.draw_text(draw_manager,
                       om.MPoint(mask_x + mask_width - data.text_padding,
                                 mask_bottom_y), data.text_fields[5],
                       omr.MUIDrawManager.kRight, background_size,color=data.border_color)

        # Draw Error Asset Name
        draw_manager.setColor(data.fontErrorColor)
        draw_manager.setFontSize(
            int((border_height - border_height * 0.15) * data.font_scale *
                0.5))
        error_text_lst = data.text_fields[6].split(';')
        if error_text_lst:
            for index, error_text in enumerate(error_text_lst):
                self.draw_text(draw_manager,
                               om.MPoint(mask_x + data.text_padding,
                                         mask_top_y -
                                         border_height * 2 - index *
                                         border_height * 0.8),
                               error_text,
                               omr.MUIDrawManager.kLeft,
                               background_size)

        draw_manager.endDrawable()

    def draw_border(self, draw_manager, position, background_size, color):
        draw_manager.text2d(position, ' ', alignment=omr.MUIDrawManager.kLeft,
                            backgroundSize=background_size,
                            backgroundColor=color)

    def draw_text(self, draw_manager, position, text, alignment,
                  background_size, color=om.MColor(
                                    (0.0, 0.0, 0.0, 0.0))):
        if text:
            draw_manager.text2d(position, text, alignment=alignment,
                                backgroundSize=background_size,
                                backgroundColor=color)

    def camera_exists(self, name):
        return name in pm.listCameras()

    def get_data(self, mask_node):
        """
        下拉框对应的数据格式

        """
        # 获取属性
        hud_command_map = {
            'FileName': lambda: pm.sceneName().basename().rsplit('.', 1)[0],
            'Camera': lambda: self.get_current_camera(),
            'Camera int': lambda: self.get_current_camera_int(),
            'None': lambda: "",
            'FrameRange': lambda: '{:.0f}/{:.0f}'.format(
                pm.playbackOptions(q=1, ast=1),
                pm.playbackOptions(q=1, aet=1)),
            'Date': lambda: time.strftime("%Y/%m/%d", time.localtime()),
            'TaskType': lambda: mask_node.findPlug(
                'taskType', False).asString(),
            'User': lambda: getpass.getuser(),
            'CurFrame': lambda: int(pm.currentTime()),
            'Cur_EndFrame': lambda: '{:.0f}/{:.0f}'.format(
                pm.currentTime(), pm.playbackOptions(q=1, aet=1)),
            'AssetVersion': lambda: mask_node.findPlug('errorAssetVersion',
                                                       False).asString(),
            'focal length + CurFrame': lambda: '{} {}'.format(self.get_current_camera2(), str(int(pm.currentTime())).zfill(4)),
            'focal length + CurFrame (int)': lambda: '{} {}'.format(self.get_current_camera2_int(), str(int(pm.currentTime())).zfill(4)),
        }
        return hud_command_map

    @staticmethod
    def get_current_camera2():
        camera_name = cmds.lookThru(q=True)
        data_str = '{focal}{unit}'.format(
            camera_name=camera_name,
            focal=round(cmds.getAttr("{}.focalLength".format(camera_name)), 3),
            # unit=pm.currentUnit(query=True, linear=True))
            unit='mm')  # the camera focal length is measured in millimeters
        return data_str

    @staticmethod
    def get_current_camera2_int():
        camera_name = cmds.lookThru(q=True)
        data_str = '{focal}{unit}'.format(
            camera_name=camera_name,
            focal=int(round(cmds.getAttr("{}.focalLength".format(camera_name)), 3)),
            # unit=pm.currentUnit(query=True, linear=True))
            unit='mm')  # the camera focal length is measured in millimeters
        return data_str

    @staticmethod
    def get_current_camera():
        camera_name = cmds.lookThru(q=True)
        data_str = '{camera_name}:{focal}{unit}'.format(
            camera_name=camera_name,
            focal=round(cmds.getAttr("{}.focalLength".format(camera_name)), 3),
            # unit=pm.currentUnit(query=True, linear=True))
            unit='mm')  # the camera focal length is measured in millimeters
        return data_str
    @staticmethod
    def get_current_camera_int():
        camera_name = cmds.lookThru(q=True)
        data_str = '{camera_name}:{focal}{unit}'.format(
            camera_name=camera_name,
            focal=int(round(cmds.getAttr("{}.focalLength".format(camera_name)), 3)),
            # unit=pm.currentUnit(query=True, linear=True))
            unit='mm')  # the camera focal length is measured in millimeters
        return data_str

    @staticmethod
    def creator(obj):
        return ZShotMaskDrawOverride(obj)

    @staticmethod
    def draw(context, data):
        return


def initializePlugin(obj):
    """
    """
    pluginFn = om.MFnPlugin(obj, "Chris Zurbrigg", "1.0.2", "Any")

    try:
        pluginFn.registerNode(ZShotMaskLocator.NAME,
                              ZShotMaskLocator.TYPE_ID,
                              ZShotMaskLocator.creator,
                              ZShotMaskLocator.initialize,
                              om.MPxNode.kLocatorNode,
                              ZShotMaskLocator.DRAW_DB_CLASSIFICATION)
    except:
        om.MGlobal.displayError(
            "Failed to register node: {0}".format(ZShotMaskLocator.NAME))

    try:
        omr.MDrawRegistry.registerDrawOverrideCreator(
            ZShotMaskLocator.DRAW_DB_CLASSIFICATION,
            ZShotMaskLocator.DRAW_REGISTRANT_ID,
            ZShotMaskDrawOverride.creator)
    except:
        om.MGlobal.displayError("Failed to register draw override: {0}".format(
            ZShotMaskDrawOverride.NAME))


def uninitializePlugin(obj):
    """
    """
    pluginFn = om.MFnPlugin(obj)

    try:
        omr.MDrawRegistry.deregisterDrawOverrideCreator(
            ZShotMaskLocator.DRAW_DB_CLASSIFICATION,
            ZShotMaskLocator.DRAW_REGISTRANT_ID)
    except:
        om.MGlobal.displayError(
            "Failed to deregister draw override: {0}".format(
                ZShotMaskDrawOverride.NAME))

    try:
        pluginFn.deregisterNode(ZShotMaskLocator.TYPE_ID)
    except:
        om.MGlobal.displayError(
            "Failed to unregister node: {0}".format(ZShotMaskLocator.NAME))


if __name__ == "__main__":
    pm.file(f=True, new=True)

    plugin_name = "mask_node.py"
    pm.evalDeferred(
        ('if pm.pluginInfo("{0}", q=True, loaded=True): '
         'pm.unloadPlugin("{0}")').format(plugin_name))
    pm.evalDeferred(
        ('if not pm.pluginInfo("{0}", q=True, loaded=True): '
         'pm.loadPlugin("{0}")').format(plugin_name))

    pm.evalDeferred('pm.createNode("zshotmask")')
