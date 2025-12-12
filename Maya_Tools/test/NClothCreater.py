# -*- coding: utf-8 -*-
# 选择：网格组件（点/边/面任一） + 一个joint，执行即可。
import maya.cmds as cmds

def _short(n): return (n.split('|')[-1]).split(':')[-1]

def _get_mesh_tr_shape(comp_or_tr):
    if '.' in comp_or_tr:
        tr = comp_or_tr.split('.')[0]
    else:
        tr = comp_or_tr
    shapes = cmds.listRelatives(tr, s=True, ni=True, f=True) or []
    shp = next((s for s in shapes if cmds.nodeType(s) == 'mesh'), None)
    if not shp: cmds.error(u"未找到mesh形节点")
    return tr, shp

def _avg_world_pos_of_component(comp):
    verts = cmds.polyListComponentConversion(comp, tv=True) or []
    verts = cmds.ls(verts, fl=True) or []
    if not verts: cmds.error(u"选中的不是有效网格组件")
    ps = [cmds.pointPosition(v, w=True) for v in verts]
    n = float(len(ps))
    return [sum(p[i] for p in ps)/n for i in range(3)]

def _closest_uv(mesh_tr, mesh_shp, world_pos):
    cpm = cmds.createNode('closestPointOnMesh', n=_short(mesh_tr)+'_CPOM')
    cmds.connectAttr(mesh_shp+'.outMesh', cpm+'.inMesh', f=True)
    # 关键：把mesh的worldMatrix连到CPOM的inputMatrix，保证坐标系一致
    if cmds.attributeQuery('inputMatrix', n=cpm, exists=True):
        cmds.connectAttr(mesh_tr+'.worldMatrix[0]', cpm+'.inputMatrix', f=True)
    cmds.setAttr(cpm+'.inPosition', *world_pos, type='double3')
    u = cmds.getAttr(cpm+'.parameterU')
    v = cmds.getAttr(cpm+'.parameterV')
    cmds.delete(cpm)
    return u, v

def attach_joint_to_selected_point(maintain_offset=False):
    sel = cmds.ls(sl=True, fl=True) or []
    if len(sel) < 2: cmds.error(u"请选：网格组件 + 一个joint")
    joint = next((s for s in sel if cmds.nodeType(s)=='joint'), None)
    comp  = next((s for s in sel if s != joint), None)
    if not joint or not comp: cmds.error(u"未同时选到组件与joint")

    mesh_tr, mesh_shp = _get_mesh_tr_shape(comp)
    wp = _avg_world_pos_of_component(comp)
    u, v = _closest_uv(mesh_tr, mesh_shp, wp)

    fol_shape = cmds.createNode('follicle', n=_short(mesh_tr)+'_surfFolShape')
    fol_tr = cmds.listRelatives(fol_shape, p=True, f=True)[0]
    fol_tr = cmds.rename(fol_tr, _short(mesh_tr)+'_surfFol')

    cmds.connectAttr(mesh_shp+'.outMesh', fol_shape+'.inputMesh', f=True)
    cmds.connectAttr(mesh_tr+'.worldMatrix[0]', fol_shape+'.inputWorldMatrix', f=True)
    cmds.setAttr(fol_shape+'.parameterU', u)
    cmds.setAttr(fol_shape+'.parameterV', v)
    cmds.connectAttr(fol_shape+'.outTranslate', fol_tr+'.translate', f=True)
    cmds.connectAttr(fol_shape+'.outRotate',    fol_tr+'.rotate',    f=True)

    # 位置+朝向一起跟随
    cmds.parentConstraint(fol_tr, joint, mo=maintain_offset)
    print(u"[OK] follicle定位完成: U=%.6f V=%.6f -> %s" % (u, v, joint))

attach_joint_to_selected_point(maintain_offset=True)
