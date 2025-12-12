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
    auto_curve = None
    if len(res) >= 3 and cmds.objExists(res[2]): auto_curve = res[2]
    else:
        cons = cmds.listConnections(ikh + ".inCurve", s=True, d=False, sh=True) or []
        for c in cons:
            if cmds.nodeType(c) == 'nurbsCurve':
                auto_curve = cmds.listRelatives(c, p=True, pa=True)[0]; break
        if not auto_curve:
            any_shapes = cmds.listConnections(ikh, s=True, d=False, type='nurbsCurve') or []
            if any_shapes: auto_curve = cmds.listRelatives(any_shapes[0], p=True, pa=True)[0]

    cmds.setAttr(ikh + ".dTwistControlEnable", 1)
    cmds.setAttr(ikh + ".dWorldUpType", 0)
    return ikh, auto_curve

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

# ===== 基于 UUID 的约束 =====
def pair_by_order(orig_root, dup_root):
    oc = get_joint_chain(orig_root); dc = get_joint_chain(dup_root)
    n = min(len(oc), len(dc)); pairs = []
    for i in range(n):
        ou = uuid_of(oc[i])
        if ou: pairs.append((ou, dc[i]))
    return pairs

def constrain_one_to_one_by_uuid(pairs_uuid_to_dup):
    for ou, dj in pairs_uuid_to_dup:
        oj = node_from_uuid(ou)
        if not (oj and cmds.objExists(oj) and cmds.objExists(dj)): continue
        try: cmds.parentConstraint(dj, oj, mo=True)
        except RuntimeError: pass
        try: cmds.scaleConstraint(dj, oj, mo=True)
        except RuntimeError: pass

# ===== 隐藏 GP 组 =====
def hide_gp_groups(sim_root):
    """隐藏所有 *_GP，除了 sim_GP 本身"""
    all_tr = cmds.listRelatives(sim_root, ad=True, type='transform', f=False) or []
    all_tr += [sim_root]
    for n in set(all_tr):
        if n.endswith("_GP") and n != "sim_GP":
            try: cmds.setAttr(n + ".v", 0)
            except: pass

# ===== 主流程 =====
def run(prefix=None):
    sel = cmds.ls(sl=True, type='joint') or []
    if not sel:
        cmds.warning(u"请选择一个或多个关节起点"); return
    if prefix is None: prefix = infer_prefix(sel)

    # 每个选择的父对象（与顺序一一对应；无父为 None）
    parents_of_sel = []
    for j in sel:
        p = cmds.listRelatives(j, p=True, pa=True) or []
        parents_of_sel.append(p[0] if p else None)

    # 复制链 & UUID配对（继承命名空间）；收集处理成功的 root
    dup_roots, bases_for_processed, pair_maps = [], [], []
    processed_roots = []
    for j in sel:
        if not is_single_chain(j):
            cmds.warning(u"多分支，跳过: {}".format(j)); continue
        dup = duplicate_single_chain(j, suffix="_workJ")
        if dup:
            dup_roots.append(dup)
            bases_for_processed.append(short_no_ns(j))
            pair_maps.append(pair_by_order(j, dup))
            processed_roots.append(j)
    if not dup_roots:
        cmds.warning(u"无可用复制链，退出"); return

    cmds.undoInfo(ock=True)
    try:
        # sim 总组（复用）
        sim_root = ensure_group("sim_GP")

        # 功能组（放入 sim_GP）
        work_joints_gp = ensure_group("{}_workJoints_GP".format(prefix), sim_root)
        curves_gp      = ensure_group("{}_ik_curve_GP".format(prefix),     sim_root)
        follicle_gp    = ensure_group("{}_follicle_GP".format(prefix),     sim_root)
        ik_gp          = ensure_group("{}_ikHandle_GP".format(prefix),     sim_root)
        dy_start_gp    = ensure_group("{}_dy_start_GP".format(prefix),     sim_root)
        cluster_root   = ensure_group("{}_cluster_GP".format(prefix),      sim_root)

        to_parent = []
        backup_curves = []    # bkp transforms
        orig_curves   = []    # 对应 orig_curve
        base_names    = []    # base_name（无 _curve）

        # 复制链入组 & 创建 splineIK 曲线与 bkp
        for dup_root, base_name, orig_root in zip(dup_roots, bases_for_processed, processed_roots):
            ns = get_namespace(dup_root)
            to_parent.append((dup_root, work_joints_gp))
            ikh, auto_curve = create_ik_spline_auto_curve(dup_root)
            if not ikh or not auto_curve: continue

            orig_curve = unique_rename(auto_curve, uniq(with_ns(base_name + "_curve", ns)))
            to_parent.append((ikh, ik_gp))
            to_parent.append((orig_curve, curves_gp))

            bkp = cmds.duplicate(orig_curve, n=uniq(with_ns(base_name + "_curve_dy_start", ns)))[0]
            to_parent.append((bkp, dy_start_gp))

            backup_curves.append(bkp)
            orig_curves.append(orig_curve)
            base_names.append(base_name)

        # —— 创建 nHair（共用）并重命名 hairSystem；OutputCurves 组放入 sim_GP ——
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

        # —— 精确：用 bkp 改名 & 回驱；创建控制并记录 cluster 根（与 processed_roots 对齐）——
        cluster_roots_in_order = []
        for orig_root, bkp_curve, orig_curve, base_name in zip(processed_roots, backup_curves, orig_curves, base_names):
            ns = get_namespace(bkp_curve)
            base_unique = short_no_ns(orig_curve)
            if base_unique.endswith("_curve"): base_unique = base_unique[:-len("_curve")]

            fol, out_dy = rename_after_make_dynamic(bkp_curve, base_unique, ns=ns)

            if out_dy and cmds.objExists(orig_curve):
                # 创建并直接设置权重，不再 -t 追加 target
                bs = cmds.blendShape(out_dy, orig_curve, n=uniq(with_ns(base_unique + "_bshape", ns)))[0]

                # 取已存在的权重槽位索引（通常只有一个，为 0）
                idxs = cmds.getAttr(bs + ".weight", multiIndices=True) or [0]
                cmds.setAttr(f"{bs}.weight[{idxs[-1]}]", 1.0)

            sub_gp, _ = create_clusters_and_ctrls(bkp_curve)
            cluster_roots_in_order.append(sub_gp)
            if sub_gp:
                to_parent.append((sub_gp, cluster_root))
            if fol and cmds.objExists(fol):
                to_parent.append((fol, follicle_gp))

        # 统一 parent（两次）
        for child, parent in to_parent: safe_parent(child, parent)
        for child, parent in to_parent: safe_parent(child, parent)

        # 原链 <- 复制链（UUID 约束）
        for pairs_uuid_to_dup in pair_maps:
            constrain_one_to_one_by_uuid(pairs_uuid_to_dup)

        # 每个已处理 root 的父对象 -> 约束对应 cluster 根（按索引对齐）
        # 先从 sel 过滤出 processed_roots 的索引，拿到对应父节点
        processed_indices = [sel.index(r) for r in processed_roots]
        for idx, cluster_gp in zip(processed_indices, cluster_roots_in_order):
            parent_node = parents_of_sel[idx]
            if cluster_gp and parent_node and cmds.objExists(parent_node) and cmds.objExists(cluster_gp):
                try: cmds.parentConstraint(parent_node, cluster_gp, mo=True)
                except RuntimeError: pass

        # 隐藏所有 *_GP（除了 sim_GP）
        hide_gp_groups(sim_root)

        print(u"[OK] 完成 | UUID配对 | 继承命名空间 | hairSystem/OutputCurves 就位 | 源链:{} | 复制链:{} | sim: sim_GP"
              .format(len(processed_roots), len(dup_roots)))
    finally:
        cmds.undoInfo(cck=True)

# 运行
run()
