import maya.cmds as cmds
from PySide2 import QtWidgets, QtGui, QtCore
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox
import json

startFrames = 0
endFrames = 2

objs =['cn_mouthAll_ctrl',
                      'lf_EyeSqz_ctrl',
                      'rt_UprLid_ctrl',
                      'rt_eyeBall_ctrl',
                      'rt_cheek_ctrl',
                      'lf_mouthLip_up_ctrl',
                      'lf_mouthLip_dn_ctrl',
                      'rt_uppersocket1_ctrl',
                      'eye_aim_ctrl',
                      'lf_mouthLip_conner_ctrl',
                      'rt_BrowOut_ctrl',
                      'cn_mouthLip_dn_ctrl',
                      'lf_uppersocket1_ctrl',
                      'lf_BrowIn_ctrl',
                      'lf_uppersocket3_ctrl',
                      'lf_Muzzle_ctrl',
                      'lf_LwrLid_ctrl',
                      'cn_lwrLip_ctrl',
                      'rt_EyeSqz_ctrl',
                      'rt_mouthLip_dn_ctrl',
                      'rt_BrowIn_ctrl',
                      'cn_chin_ctrl',
                      'cn_eyeBrown_ctrl',
                      'lf_cheek_ctrl',
                      'rt_mouthLip_conner_ctrl',
                      'rt_mouth_conner_ctrl',
                      'rt_MouthCorner02_ctrl',
                      'lf_MouthCorner02_ctrl',
                      'lf_UprLid_ctrl',
                      'lf_uppersocket2_ctrl',
                      'rt_uppersocket2_ctrl',
                      'lf_MouthCorner_ctrl',
                      'cn_jaw_ctrl',
                      'cn_trans_nose_ctrl',
                      'rt_LwrLid_ctrl',
                      'cn_forehead_ctrl',
                      'lf_BrowOut_ctrl',
                      'lf_Nose_ctrl',
                      'cn_nose_ctrl',
                      'lf_eyeBall_ctrl',
                      'lf_mouth_conner_ctrl',
                      'rt_mouthLip_up_ctrl',
                      'rt_uppersocket3_ctrl',
                      'cn_lip_ctrl',
                      'rt_Muzzle_ctrl',
                      'cn_mouthLip_up_ctrl',
                      'cn_uprLip_ctrl',
                      'rt_Nose_ctrl',
                      'rt_MouthCorner_ctrl']
json_file={}
for obj in objs:
    obj_file={}
    attributes = cmds.listAttr(obj, keyable=True)
    if attributes:  # 确保 attributes 不是 None
        for attr in attributes:
            attr_data={}
            # 检查属性
            if cmds.keyframe(obj + '.' + attr, query=True, keyframeCount=True) > 0:
                anim_curves = cmds.listConnections("%s.%s" % (obj, attr), type="animCurve")
                if cmds.listConnections("%s.%s" % (obj, attr), type="animCurve"):
                    anim_curve = anim_curves[0]
                    key_frame = cmds.keyframe(anim_curve, query=True, time=(startFrames, endFrames))
                    if key_frame:
                        data = {
                            "frame":[],
                            "velue":[],
                            "in_tangent_type":[],
                            "out_tangent_type":[],
                            "in_weight":[],
                            "out_weight":[],
                            "in_angle":[],
                            "out_angle":[],
                        }
                        for frame in key_frame:

                            value = cmds.keyframe(anim_curve, query=True, time=(startFrames, endFrames), valueChange=True)[0]

                            in_tangent_type = cmds.keyTangent(anim_curve, time=(frame, frame), query=True, inTangentType=True)[0]
                            out_tangent_type = cmds.keyTangent(anim_curve, time=(frame, frame), query=True, outTangentType=True)[0]

                            in_weight = cmds.keyTangent(anim_curve, time=(frame, frame), query=True, inWeight=True)[0]
                            out_weight = cmds.keyTangent(anim_curve, time=(frame, frame), query=True, outWeight=True)[0]

                            in_angle = cmds.keyTangent(anim_curve, time=(frame, frame), query=True, inAngle=True)[0]
                            out_angle = cmds.keyTangent(anim_curve, time=(frame, frame), query=True, outAngle=True)[0]
                            data["frame"].append(frame)
                            data["velue"].append(value)
                            data["in_tangent_type"].append(in_tangent_type.encode('utf-8'))
                            data["out_tangent_type"].append(out_tangent_type.encode('utf-8'))
                            data["in_weight"].append(in_weight)
                            data["out_weight"].append(out_weight)
                            data["in_angle"].append(in_angle)
                            data["out_angle"].append(out_angle)

            obj_file[attr.encode('utf-8')]=data
    json_file[obj]=obj_file
    # save json

jsonfile = json.dumps(json_file, indent=4, separators=(',', ':'))

# Check if the folder exists, create it if necessary
#if not os.path.exists(folder_path):
    #os.makedirs(folder_path)

filenew = open("C:/Users/justcause/Desktop/test.json", 'w')
filenew.write(jsonfile)
filenew.close()