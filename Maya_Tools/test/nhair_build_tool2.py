# -*- coding: utf-8 -*-
import re
import maya.cmds as cmds
import maya.mel as mel

# ========= 小工具 =========
def short_no_ns(n):
    s = n.split('|')[-1]
    return s.split(':')[-1]

def common_prefix_by_underscore(names):
    if not names: return ""
    parts_list = [short_no_ns(n).split('_') for n in names]
    pref = []
    for z in zip(*parts_list):
        if len(set(z)) == 1: pref.append(z[0])
        else: break
    return "_".join(pref) if pref else ""

def strip_trailing_digits(s):
    return re.sub(r'\d+$', '', s)

def infer_prefix(sel):
    cp = common_prefix_by_underscore(sel)
    if cp: return cp
    base = short_no_ns(sel[0])
    return strip_trailing_digits(base) or base

def ensure_group(name, parent=None):
    if cmds.objExists(name) and cmds.nodeType(name) == 'transform':
        node = name
    else:
        node = cmds.group(em=True, n=name)
    if parent:
        if not (cmds.objExists(parent) and cmds.nodeType(parent) == 'transform'):
            parent = cmds.group(em=True, n=parent)
        try: cmds.parent(node, parent)
        except RuntimeError: pass
    return node

# ========= 关节链 =========
def get_all_child_joints(start_joint):
    all_joints, q = [], [start_joint]
    while q:
        j = q.pop(0)
        all_joints.append(j)
        q.extend(cmds.listRelatives(j, c=True, type='joint') or [])
    return all_joints

def is_single_chain(j):
    ch = cmds.listRelatives(j, c=True, type='joint') or []
    if not ch: return True
    if len(ch) > 1: return False
    return is_single_chain(ch[0])

def get_joint_chain(j):
    chain = [j]
    ch = cmds.listRelatives(j, c=True, type='joint') or []
    while ch:
        chain.append(ch[0])
        ch = cmds.listRelatives(ch[0], c=True, type='joint') or []
    return chain

# ========= 复制并重命名起点关节树 =========
def duplicate_rename_joints(selected_joints, prefix):
    gp = "{}_joint_GP".format(prefix)
    ensure_group(gp)
    for start in selected_joints:
        src_chain = get_all_child_joints(start)
        dup_root = cmds.duplicate(start, rc=True)[0]
        cmds.parent(dup_root, gp)
        dst_chain = get_all_child_joints(dup_root)
        for s, d in zip(src_chain, dst_chain):
            cmds.rename(d, "{}_{}".format(prefix, short_no_ns(s)))
    children = cmds.listRelatives(gp, c=True, type='joint') or []
    if children: cmds.select(children, r=True)
    return children

# ========= splineIK：自动创建曲线（不简化） =========
def create_ik_spline_auto_curve(joint_root):
    """返回 (ikHandle, 由IK自动创建的曲线transform)，ccv=True，simplifyCurve=False"""
    if not is_single_chain(joint_root):
        cmds.warning(u"多分支，跳过: {}".format(joint_root)); return None, None
    chain = get_joint_chain(joint_root)
    if len(chain) < 2:
        cmds.warning(u"少于2关节，跳过: {}".format(joint_root)); return None, None

    sj, ej = chain[0], chain[-1]
    res = cmds.ikHandle(
        n="{}_ikHandle".format(joint_root),
        sj=sj, ee=ej,
        sol="ikSplineSolver",
        ccv=True,            # 自动生成曲线
        pcv=False,
        simplifyCurve=False  # 不简化
    )
    ikh = res[0]
    auto_curve = None
    # ccv=True 时通常返回 (ikh, eff, curve)
    if len(res) >= 3 and cmds.objExists(res[2]):
        auto_curve = res[2]
    else:
        # 兜底：从 inCurve 连接查找
        cons = cmds.listConnections(ikh + ".inCurve", s=True, d=False, sh=True) or []
        for c in cons:
            if cmds.nodeType(c) == 'nurbsCurve':
                auto_curve = cmds.listRelatives(c, p=True, pa=True)[0]
                break
        if not auto_curve:
            any_shapes = cmds.listConnections(ikh, s=True, d=False, type='nurbsCurve') or []
            if any_shapes:
                auto_curve = cmds.listRelatives(any_shapes[0], p=True, pa=True)[0]

    return ikh, auto_curve

# ========= 动力学曲线改名 =========
def _rename_after_make_dynamic(input_curve_transform, base_no_suffix):
    in_shapes = cmds.listRelatives(input_curve_transform, s=True, pa=True) or []
    if not in_shapes: return (None, None)
    in_shape = in_shapes[0]

    fol_shapes = cmds.listConnections(in_shape, s=True, d=True, type='follicle') or []
    if not fol_shapes:
        p = cmds.listRelatives(input_curve_transform, p=True, pa=True) or []
        if p:
            cand = cmds.listRelatives(p[0], s=True, pa=True) or []
            fol_shapes = [x for x in cand if cmds.nodeType(x) == 'follicle']
    if not fol_shapes: return (None, None)

    fol_shape = fol_shapes[0]
    fol_xf = cmds.listRelatives(fol_shape, p=True, pa=True)[0]

    out_shapes = cmds.listConnections(fol_shape + ".outCurve", s=True, d=True, sh=True) or []
    if not out_shapes: return (None, None)
    out_shape = out_shapes[0]
    out_xf = cmds.listRelatives(out_shape, p=True, pa=True)[0]

    if cmds.objExists(fol_shape + ".pointLock"):
        cmds.setAttr(fol_shape + ".pointLock", 1)

    new_fol = base_no_suffix + "_follicle"
    new_out = base_no_suffix + "_curve_dy"
    if cmds.objExists(fol_xf): fol_xf = cmds.rename(fol_xf, new_fol)
    if cmds.objExists(out_xf): out_xf = cmds.rename(out_xf, new_out)
    return fol_xf, out_xf

# —— 曲线 shape 获取 ——
def curve_shape_of(curve_xf):
    shapes = cmds.listRelatives(curve_xf, s=True, ni=True, pa=True) or []
    for s in shapes:
        if cmds.nodeType(s) == 'nurbsCurve': return s
    return None

# ========= CV 控制 =========
def create_clusters_and_ctrls_for_curve(curve_transform, ctrl_prefix, all_cluster_group):
    shp = curve_shape_of(curve_transform)
    if not shp or not cmds.objExists(shp):
        cmds.warning(u"[跳过] 非曲线或已丢失: {}".format(curve_transform)); return None
    cv_count = cmds.getAttr(shp + ".cp", s=True)
    sub_gp = cmds.group(em=True, n="{}_{}_cluster_GP".format(ctrl_prefix, curve_transform))
    if all_cluster_group and cmds.objExists(all_cluster_group):
        cmds.parent(sub_gp, all_cluster_group)
    for i in range(cv_count):
        cl, clh = cmds.cluster("{}.cv[{}]".format(shp, i), n="{}_cluster_{}".format(curve_transform, i))
        cmds.setAttr(clh + ".v", 0)
        ctrl = cmds.circle(n="{}_con_curve_{}".format(curve_transform, i), ch=False, o=True)[0]
        cmds.matchTransform(ctrl, clh)
        cmds.makeIdentity(ctrl, a=True, t=True, r=True, s=True)
        cmds.parent(clh, ctrl)
        if i == 0: cmds.matchTransform(sub_gp, ctrl)
        cmds.parent(ctrl, sub_gp)
    return sub_gp

# ========= 主流程 =========
def run(prefix=None):
    sel = cmds.ls(sl=True, type='joint') or []
    if not sel:
        cmds.warning(u"请选择一个或多个关节起点"); return
    if prefix is None:
        prefix = infer_prefix(sel)

    cmds.undoInfo(ock=True)
    try:
        curves_gp      = ensure_group("{}_ik_curve_GP".format(prefix))
        follicle_gp    = ensure_group("{}_follicle_GP".format(prefix))
        ik_gp          = ensure_group("{}_ikHandle_GP".format(prefix))
        dy_start_gp    = ensure_group("{}_dy_start_GP".format(prefix))
        all_cluster_gp = ensure_group("{}_cluster_GP".format(prefix))

        dup_roots = duplicate_rename_joints(sel, prefix)
        work_roots = dup_roots if dup_roots else (cmds.ls(sl=True, type='joint') or [])

        backup_curves, pairs = [], []

        for j in work_roots:
            ikh, auto_curve = create_ik_spline_auto_curve(j)
            if not ikh or not auto_curve:
                continue

            base = short_no_ns(j)                      # 基名
            # 重命名自动生成的曲线为 {base}_curve
            orig_curve = cmds.rename(auto_curve, base + "_curve")

            # 分组
            cmds.parent(ikh, ensure_group(ik_gp))
            cmds.parent(orig_curve, ensure_group(curves_gp))

            # 备份曲线用于做动态
            bkp = cmds.duplicate(orig_curve, n=base + "_curve_dy_start")[0]
            cmds.parent(bkp, ensure_group(follicle_gp))

            backup_curves.append(bkp)
            pairs.append((base, orig_curve))

        if backup_curves:
            cmds.select(backup_curves, r=True)
            mel.eval('makeCurvesDynamic 2 { "1", "0", "1", "1", "0"};')  # 创建 nHair 动力
            cmds.select(cl=True)

        for base, orig_curve in pairs:
            in_curve = base + "_curve_dy_start"
            fol, out_dy = _rename_after_make_dynamic(in_curve, base)
            if out_dy and cmds.objExists(orig_curve):
                bs = cmds.blendShape(out_dy, orig_curve, n=base + "_bshape")[0]
                cmds.setAttr("{}.{}".format(bs, out_dy), 1.0)
            if cmds.objExists(in_curve):
                cmds.parent(in_curve, ensure_group(dy_start_gp))
            if fol and cmds.objExists(fol):
                cmds.parent(fol, ensure_group(follicle_gp))

        dy_children = cmds.listRelatives(dy_start_gp, c=True, type='transform') or []
        all_cluster_gp = ensure_group(all_cluster_gp)
        for c in dy_children:
            create_clusters_and_ctrls_for_curve(c, prefix, all_cluster_gp)

        print(u"[OK] 前缀: {} | 处理曲线: {} | 分组: {}, {}, {}, {}, {}".format(
            prefix, len(dy_children), curves_gp, follicle_gp, ik_gp, dy_start_gp, all_cluster_gp))
    finally:
        cmds.undoInfo(cck=True)

# 运行
run()
