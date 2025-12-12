# -*- coding: utf-8 -*-
import maya.cmds as cmds

def _short_no_ns(n):
    s = n.split('|')[-1]
    return s.split(':')[-1]

def _safe_parent(shape):
    p = cmds.listRelatives(shape, p=True, f=False) or []
    return p[0] if p else None

def _first_mesh_shape(node):
    """从任意节点找到连接的 mesh shape（源）。"""
    # 直接找 mesh 连接
    m = cmds.listConnections(node, s=True, d=False, sh=True, type='mesh') or []
    if not m:
        return None
    ms = m[0]
    # 若拿到的是transform，取其shape
    if cmds.nodeType(ms) != 'mesh':
        sh = cmds.listRelatives(ms, s=True, ni=True, type='mesh') or []
        return sh[0] if sh else None
    return ms

def _unique_rename(node, new_name):
    """尽量按目标名重命名，存在重名时交给 Maya 自动加后缀。"""
    if not node or not cmds.objExists(node):
        return None
    short = _short_no_ns(node)
    if short == new_name:
        return node
    try:
        return cmds.rename(node, new_name)
    except:
        # 若因同名失败，交给 Maya 处理（仍然以new_name为基础）
        try:
            return cmds.rename(node, new_name)
        except:
            return node  # 放弃

def rename_nrigid_by_mesh():
    nrigid_shapes = cmds.ls(type='nRigid') or []
    if not nrigid_shapes:
        cmds.warning('No nRigidShape found.')
        return []

    renamed = []
    for nrs in nrigid_shapes:
        # 找到驱动该 nRigid 的 mesh shape
        mesh_shape = _first_mesh_shape(nrs)
        if not mesh_shape:
            # 有些 nRigid 可能未绑定网格，跳过
            continue

        mesh_xform = _safe_parent(mesh_shape)
        if not mesh_xform:
            continue

        base = _short_no_ns(mesh_xform)

        # 先拿到 nRigid 的 transform
        rigid_xform = _safe_parent(nrs)
        if not rigid_xform:
            continue

        target_xform = f'{base}_nRigid'
        target_shape = f'{base}_nRigidShape'

        # 先改 shape，再改 transform（或相反都可，这里选先改transform降低层级名变动影响）
        new_xform = _unique_rename(rigid_xform, target_xform)
        # 重命名后 shape 路径可能变化，重新获取 shape 名称
        # 找到 new_xform 下的 nRigid shape（有时一个transform下可能多个shape，过滤 type）
        shapes = cmds.listRelatives(new_xform, s=True, ni=True) or []
        nrigid_under_x = [s for s in shapes if cmds.nodeType(s) == 'nRigid']

        # 如果原来的 nrs 还在列表里，优先改它；否则改找到的第一个 nRigid shape
        target_shape_node = nrs if nrs in nrigid_under_x else (nrigid_under_x[0] if nrigid_under_x else None)
        if target_shape_node:
            new_shape = _unique_rename(target_shape_node, target_shape)
        else:
            new_shape = None

        renamed.append((new_xform, new_shape, mesh_xform))

    return renamed

# 执行
result = rename_nrigid_by_mesh()
print('Renamed nRigid count:', len(result))
for xform_name, shape_name, src_mesh in result:
    print('  From Mesh:', src_mesh, '=>', xform_name, '/', shape_name)
