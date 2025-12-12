# -*- coding: utf-8 -*-
import re
import maya.cmds as cmds
import maya.mel as mel
from maya.api import OpenMaya as om

# ===== UUID / 命名空间工具 =====
def node_from_uuid(u):
    try:
        sel = om.MSelectionList(); sel.add(om.MUuid(u))
        try:
            dag,_ = sel.getDagPath(0); return dag.fullPathName()
        except:
            obj = sel.getDependNode(0); return om.MFnDependencyNode(obj).name()
    except:
        return None

def uuid_of(n):
    if not cmds.objExists(n): return None
    try: return cmds.ls(n, uuid=True)[0]
    except:
        try:
            sel = om.MSelectionList(); sel.add(n)
            return om.MFnDependencyNode(sel.getDependNode(0)).uuid().asString()
        except: return None

def short_no_ns(n):
    s = n.split('|')[-1]; return s.split(':')[-1]

def get_namespace(n):
    sn = n.split('|')[-1]
    return sn.rsplit(':',1)[0] if ':' in sn else ""

def with_ns(name, ns):
    return "{}:{}".format(ns, name) if ns else name

def strip_trailing_digits(s): return re.sub(r'\d+$', '', s)

def infer_prefix(sel):
    base = short_no_ns(sel[0]); return strip_trailing_digits(base) or base

def ensure_group(name, parent=None):
    if cmds.objExists(name) and cmds.nodeType(name) == 'transform':
        node = name
    else:
        node = cmds.group(em=True, n=name)
    if parent:
        try: cmds.parent(node, parent)
        except RuntimeError: pass
    return node

def uniq(name):
    """返回场景唯一名（支持命名空间）"""
    if not cmds.objExists(name): return name
    ns, short = (name.rsplit(':',1)[0], name.rsplit(':',1)[1]) if ':' in name else ("", name)
    i = 1
    while cmds.objExists(with_ns("{}_{}".format(short, i), ns)):
        i += 1
    return with_ns("{}_{}".format(short, i), ns)

def unique_rename(node, target_name):
    new_name = uniq(target_name)
    if node and isinstance(node, (str,)) and cmds.objExists(node):
        return cmds.rename(node, new_name)
    return new_name

def safe_parent(child, parent):
    if not (cmds.objExists(child) and cmds.objExists(parent)): return
    cur = cmds.listRelatives(child, p=True, pa=True) or []
    if cur and cur[0] == parent: return
    try: cmds.parent(child, parent)
    except RuntimeError: pass

# ===== 关节链 =====
def is_single_chain(j):
    ch = cmds.listRelatives(j, c=True, type='joint') or []
    if not ch: return True
    if len(ch) > 1: return False
    return is_single_chain(ch[0])

def get_joint_chain(j):
    chain = [j]
    ch = cmds.listRelatives(j, c=True, type='joint') or []
    while ch:
        chain.append(ch[0]); ch = cmds.listRelatives(ch[0], c=True, type='joint') or []
    return chain

def rename_joint_descendants_with_suffix(root_joint, suffix="_workJ", ns=""):
    if not cmds.objExists(root_joint): return
    desc = cmds.listRelatives(root_joint, ad=True, type='joint', f=True) or []
    for j in desc:
        base = short_no_ns(j)
        target = with_ns(base + suffix, ns)
        try: cmds.rename(j, uniq(target))
        except RuntimeError:
            try: cmds.rename(j, uniq(with_ns(base + suffix + "_x", ns)))
            except RuntimeError: pass

def duplicate_single_chain(root_joint, suffix="_workJ"):
    if not is_single_chain(root_joint):
        cmds.warning(u"多分支，跳过复制: {}".format(root_joint)); return None
    ns = get_namespace(root_joint)
    dup = cmds.duplicate(root_joint, rr=True)[0]
    dup = unique_rename(dup, with_ns(short_no_ns(root_joint) + suffix, ns))
    rename_joint_descendants_with_suffix(dup, suffix=suffix, ns=ns)
    return dup

# ===== splineIK / 曲线 =====
def create_ik_spline_auto_curve(joint_root):
    if not is_single_chain(joint_root):
        cmds.warning(u"多分支，跳过: {}".format(joint_root)); return None, None
    chain = get_joint_chain(joint_root)
    if len(chain) < 2:
        cmds.warning(u"少于2关节，跳过: {}".format(joint_root)); return None, None

    sj, ej = chain[0], chain[-1]
    ikh_name = uniq(with_ns("{}_ikHandle".format(short_no_ns(joint_root)), get_namespace(joint_root)))
    res = cmds.ikHandle(n=ikh_name, sj=sj, ee=ej, sol="ikSplineSolver", ccv=True, pcv=False, simplifyCurve=False)
    ikh = res[0]

    # 找自动曲线 transform
    auto_curve = None
    if len(res) >= 3 and cmds.objExists(res[2]):
        auto_curve = res[2]
    else:
        cons = cmds.listConnections(ikh + ".inCurve", s=True, d=False, sh=True) or []
        for c in cons:
            if cmds.nodeType(c) == 'nurbsCurve':
                auto_curve = cmds.listRelatives(c, p=True, pa=True)[0]; break
        if not auto_curve:
            any_shapes = cmds.listConnections(ikh, s=True, d=False, type='nurbsCurve') or []
            if any_shapes: auto_curve = cmds.listRelatives(any_shapes[0], p=True, pa=True)[0]

    return ikh, auto_curve  # 不在此处设 advanced twist

def _setup_ikh_upvector_with_two_groups(ikh, ctrl0):
    """
    在 ctrl0 下创建两个空组：upBase 与 upRef，对齐 ctrl0，ref 本地+Y 移动1。
    IK 使用 Object Up(Start)，指向 upRef。
    """
    if not (ikh and ctrl0 and cmds.objExists(ikh) and cmds.objExists(ctrl0)):
        return

    ns   = get_namespace(ctrl0)
    base = unique_rename(cmds.group(em=True), uniq(with_ns(short_no_ns(ctrl0) + "_upBase", ns)))
    ref  = unique_rename(cmds.group(em=True), uniq(with_ns(short_no_ns(ctrl0) + "_upRef",  ns)))

    cmds.matchTransform(base, ctrl0, pos=True, rot=True, scl=True)
    cmds.matchTransform(ref,  ctrl0, pos=True, rot=True, scl=True)

    cmds.parent(base, ctrl0)
    cmds.parent(ref,  base)

    cmds.move(0, 1, 0, ref, r=True, os=True)

    cmds.setAttr(ikh + ".dTwistControlEnable", 1)
    cmds.setAttr(ikh + ".dWorldUpType", 1)  # Object Up (Start)
    if not cmds.isConnected(ref + ".worldMatrix[0]", ikh + ".dWorldUpMatrix"):
        cmds.connectAttr(ref + ".worldMatrix[0]", ikh + ".dWorldUpMatrix", f=True)
    # 如骨骼前向不是 +X，可改 dForwardAxis：
    # cmds.setAttr(ikh + ".dForwardAxis", 0)  # 0:+X

def curve_shape_of(curve_xf):
    shapes = cmds.listRelatives(curve_xf, s=True, ni=True, pa=True) or []
    for s in shapes:
        if cmds.nodeType(s) == 'nurbsCurve': return s
    return None

# ===== nHair 命名 =====
def rename_after_make_dynamic(input_curve_transform, base_no_suffix, ns=""):
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
    fol_shape = fol_shapes[0]; fol_xf = cmds.listRelatives(fol_shape, p=True, pa=True)[0]
    out_shapes = cmds.listConnections(fol_shape + ".outCurve", s=True, d=True, sh=True) or []
    if not out_shapes: return (None, None)
    out_shape = out_shapes[0]; out_xf = cmds.listRelatives(out_shape, p=True, pa=True)[0]
    if cmds.objExists(fol_shape + ".pointLock"): cmds.setAttr(fol_shape + ".pointLock", 1)
    fol_xf = unique_rename(fol_xf, uniq(with_ns(base_no_suffix + "_follicle", ns)))
    out_xf = unique_rename(out_xf, uniq(with_ns(base_no_suffix + "_curve_dy", ns)))
    return fol_xf, out_xf

# ===== CV 控制（序号大的放进序号小的层级）=====
def create_clusters_and_ctrls(curve_transform):
    shp = curve_shape_of(curve_transform)
    if not shp:
        cmds.warning(u"[跳过] 非曲线或已丢失: {}".format(curve_transform)); return None, None
    cv_count = cmds.getAttr(shp + ".cp", s=True)
    ns = get_namespace(curve_transform)
    base_no_ns = short_no_ns(curve_transform).replace("_curve_dy_start","")
    root_gp = cmds.group(em=True, n=uniq(with_ns("{}_curve_dy_start_cluster_GP".format(base_no_ns), ns)))

    ctrls = []
    for i in range(cv_count):
        cl, clh = cmds.cluster("{}.cv[{}]".format(shp, i),
                               n=uniq(with_ns("{}_cluster_{}".format(base_no_ns, i), ns)))
        cmds.setAttr(clh + ".v", 0)
        ctrl = cmds.circle(n=uniq(with_ns("{}_start_con_curve_{}".format(base_no_ns, i), ns)),
                           ch=False, o=True)[0]
        cmds.matchTransform(ctrl, clh)
        cmds.makeIdentity(ctrl, a=True, t=True, r=True, s=True)
        cmds.parent(clh, ctrl)
        ctrls.append(ctrl)

    for i in range(1, len(ctrls)):
        try: cmds.parent(ctrls[i], ctrls[i-1])
        except RuntimeError: pass
    if ctrls:
        cmds.matchTransform(root_gp, ctrls[0])
        try: cmds.parent(ctrls[0], root_gp)
        except RuntimeError: pass
    return root_gp, ctrls

# ===== Point + Aim 约束（替代原父/缩放约束）=====
def _remove_constraints(node, types=('pointConstraint','aimConstraint','parentConstraint','orientConstraint','scaleConstraint')):
    """删除 node 上已有的相关约束，避免叠加"""
    seen = set()
    for t in types:
        cons = cmds.listConnections(node, s=True, d=False, type=t) or []
        for c in cons:
            if c in seen:
                continue
            seen.add(c)
            try: cmds.delete(c)
            except RuntimeError: pass

def build_point_aim_map(orig_root, dup_root):
    """
    返回 [(orig_uuid, work_j, work_next_j or None), ...]，按链顺序
    A -> (A, workA, workB), B -> (B, workB, workC) ... 最后 next=None
    """
    oc = get_joint_chain(orig_root)
    dc = get_joint_chain(dup_root)
    n  = min(len(oc), len(dc))
    out = []
    for i in range(n):
        ou = uuid_of(oc[i])
        if not ou:
            continue
        work_j      = dc[i]
        work_next_j = dc[i+1] if i+1 < n else None
        out.append((ou, work_j, work_next_j))
    return out

def constrain_point_aim(mappings, aim_vec=(1,0,0), maintain_offset_point=False):
    """
    原骨骼 point -> 同序工作骨骼（mo 可选）；
    原骨骼 aim -> 下一节工作骨骼（mo=True 维持原本 offset；worldUpType='none' 不使用 up 对象/向量）。
    """
    for ou, work_j, work_next in mappings:
        oj = node_from_uuid(ou)
        if not (oj and cmds.objExists(oj) and cmds.objExists(work_j)):
            continue

        _remove_constraints(oj)

        # 位置（按需是否保持偏移）
        try:
            cmds.pointConstraint(work_j, oj, mo=maintain_offset_point, weight=1.0)
        except RuntimeError:
            pass

        # 朝向（末节不做 aim）
        if work_next and cmds.objExists(work_next):
            try:
                cmds.aimConstraint(
                    work_next, oj,
                    mo=True,                      # ★ 维持原本 offset（不瞬跳）
                    weight=1.0,
                    aimVector=aim_vec,
                    worldUpType="none"            # ★ 不使用 up（无 up 对象/向量）
                )
            except RuntimeError:
                pass

# ===== 隐藏 GP 组 =====
def hide_gp_groups(sim_root):
    """隐藏部分 *_GP，保留 cluster 和 dy_start"""
    all_tr = cmds.listRelatives(sim_root, ad=True, type='transform', f=False) or []
    all_tr += [sim_root]
    for n in set(all_tr):
        if not n.endswith("_GP"):
            continue
        if n == "sim_GP":
            continue
        if n.endswith("_cluster_GP") or n.endswith("_dy_start_GP"):
            continue
        try:
            cmds.setAttr(n + ".v", 0)
        except:
            pass

# ===== 主流程（IK.inCurve 直接接 dynamic 输出曲线）=====
def run(prefix=None):
    sel = cmds.ls(sl=True, type='joint') or []
    if not sel:
        cmds.warning(u"请选择一个或多个关节起点"); return
    if prefix is None: prefix = infer_prefix(sel)

    parents_of_sel = []
    for j in sel:
        p = cmds.listRelatives(j, p=True, pa=True) or []
        parents_of_sel.append(p[0] if p else None)

    dup_roots, bases_for_processed, pair_maps = [], [], []
    processed_roots = []
    for j in sel:
        if not is_single_chain(j):
            cmds.warning(u"多分支，跳过: {}".format(j)); continue
        dup = duplicate_single_chain(j, suffix="_workJ")
        if dup:
            dup_roots.append(dup)
            bases_for_processed.append(short_no_ns(j))
            # 这里不生成旧的父/缩放映射，改为 point+aim 映射
            pair_maps.append(build_point_aim_map(j, dup))
            processed_roots.append(j)
    if not dup_roots:
        cmds.warning(u"无可用复制链，退出"); return

    cmds.undoInfo(ock=True)
    try:
        sim_root      = ensure_group("sim_GP")
        work_joints_gp= ensure_group("{}_workJoints_GP".format(prefix), sim_root)
        curves_gp     = ensure_group("{}_ik_curve_GP".format(prefix),     sim_root)
        follicle_gp   = ensure_group("{}_follicle_GP".format(prefix),     sim_root)
        ik_gp         = ensure_group("{}_ikHandle_GP".format(prefix),     sim_root)
        dy_start_gp   = ensure_group("{}_dy_start_GP".format(prefix),     sim_root)
        cluster_root  = ensure_group("{}_cluster_GP".format(prefix),      sim_root)

        to_parent, backup_curves, orig_curves, base_names = [], [], [], []
        ikhs = []  # 每条复制链的 ikHandle

        # 1) 复制链入组 & 创建 splineIK（仅创建，不设 upVector）& 备份曲线
        for dup_root, base_name, orig_root in zip(dup_roots, bases_for_processed, processed_roots):
            ns = get_namespace(dup_root)
            to_parent.append((dup_root, work_joints_gp))

            ikh, auto_curve = create_ik_spline_auto_curve(dup_root)
            if not ikh or not auto_curve: continue
            ikhs.append(ikh)

            orig_curve = unique_rename(auto_curve, uniq(with_ns(base_name + "_curve", ns)))
            to_parent.append((ikh, ik_gp))
            to_parent.append((orig_curve, curves_gp))

            bkp = cmds.duplicate(orig_curve, n=uniq(with_ns(base_name + "_curve_dy_start", ns)))[0]
            to_parent.append((bkp, dy_start_gp))

            backup_curves.append(bkp)
            orig_curves.append(orig_curve)
            base_names.append(base_name)

        # 2) nHair 动态
        before_hs = set(cmds.ls(type="hairSystem") or [])
        before_out_groups = set(cmds.ls("*hairSystemOutputCurves*", type="transform") or [])
        if backup_curves:
            cmds.select(backup_curves, r=True)
            mel.eval('makeCurvesDynamic 2 { "1", "0", "1", "1", "0"};')
            cmds.select(cl=True)
        after_hs = set(cmds.ls(type="hairSystem") or [])
        new_hs_shapes = list(after_hs - before_hs)
        if new_hs_shapes:
            hs_shape = new_hs_shapes[0]
            hs_xf = cmds.listRelatives(hs_shape, p=True, pa=True)[0]
            ns0 = get_namespace(sel[0])
            unique_rename(hs_xf, uniq(with_ns("{}_hairSystem".format(prefix), ns0)))
        after_out_groups = set(cmds.ls("*hairSystemOutputCurves*", type="transform") or [])
        for g in (after_out_groups - before_out_groups):
            safe_parent(g, sim_root)

        # 3) 改名 & IK.inCurve 直连动态输出曲线
        cluster_roots_in_order = []
        first_ctrls_in_order = []  # 每条曲线的首个控制器
        for ikh, bkp_curve, orig_curve, base_name in zip(ikhs, backup_curves, orig_curves, base_names):
            ns = get_namespace(bkp_curve)
            base_unique = short_no_ns(orig_curve)
            if base_unique.endswith("_curve"): base_unique = base_unique[:-len("_curve")]

            fol, out_dy = rename_after_make_dynamic(bkp_curve, base_unique, ns=ns)

            # out_dyShape.worldSpace -> ikh.inCurve
            if out_dy and cmds.objExists(ikh):
                out_shape = curve_shape_of(out_dy)
                if out_shape:
                    old_in = cmds.listConnections(ikh + ".inCurve", s=True, d=False, p=True) or []
                    for src in old_in:
                        try: cmds.disconnectAttr(src, ikh + ".inCurve")
                        except RuntimeError: pass
                    try:
                        cmds.connectAttr(out_shape + ".worldSpace[0]", ikh + ".inCurve", f=True)
                    except RuntimeError:
                        cmds.warning(u"连接 inCurve 失败: {} -> {}".format(out_shape, ikh))

            # 控制器/Cluster 建在 start 曲线上
            sub_gp, ctrls = create_clusters_and_ctrls(bkp_curve)
            cluster_roots_in_order.append(sub_gp)
            first_ctrls_in_order.append(ctrls[0] if (ctrls and len(ctrls)>0) else None)

            if sub_gp: to_parent.append((sub_gp, cluster_root))
            if fol and cmds.objExists(fol): to_parent.append((fol, follicle_gp))

        # 4) 统一 parent
        for child, parent in to_parent: safe_parent(child, parent)
        for child, parent in to_parent: safe_parent(child, parent)

        # 5) 为每条 IK 设置 upVector（首控下的 upBase/upRef）
        for ikh, ctrl0 in zip(ikhs, first_ctrls_in_order):
            if ikh and ctrl0:
                _setup_ikh_upvector_with_two_groups(ikh, ctrl0)

        # 6) 原链 <- 复制链（Point + Aim，Aim 维持 offset，无 up）
        for mappings in pair_maps:
            constrain_point_aim(
                mappings,
                aim_vec=(1,0,0),            # 若骨骼前向不是 +X，这里改
                maintain_offset_point=False # 如需保持位置偏移，改 True
            )


        # 7) 已处理 root 的父对象 -> 约束对应 cluster 根
        processed_indices = [sel.index(r) for r in processed_roots]
        for idx, cluster_gp in zip(processed_indices, cluster_roots_in_order):
            parent_node = parents_of_sel[idx]
            if cluster_gp and parent_node and cmds.objExists(parent_node) and cmds.objExists(cluster_gp):
                try: cmds.parentConstraint(parent_node, cluster_gp, mo=True)
                except RuntimeError: pass

        hide_gp_groups(sim_root)
        print(u"[OK] 完成 | IK.inCurve=动态输出曲线 | upVector=首控Y | Point+Aim驱动 | 源链:{} | 复制链:{} | sim: sim_GP"
              .format(len(processed_roots), len(dup_roots)))
    finally:
        cmds.undoInfo(cck=True)

# 运行
run()
