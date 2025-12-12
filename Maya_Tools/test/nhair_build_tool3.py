# -*- coding: utf-8 -*-
import re
import maya.cmds as cmds
import maya.mel as mel

# ===== 小工具 =====
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

def strip_trailing_digits(s): return re.sub(r'\d+$', '', s)

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
        try: cmds.parent(node, parent)
        except RuntimeError: pass
    return node

# —— 唯一命名 ——（修复 None 导致的 Too few arguments）
def uniq(base_name):
    if not cmds.objExists(base_name):
        return base_name
    i = 1
    while cmds.objExists("{}_{}".format(base_name, i)):
        i += 1
    return "{}_{}".format(base_name, i)

def unique_rename(node, target_base):
    """若 node 有效则重命名为唯一名；若 node 为 None，仅返回唯一名。"""
    new_name = uniq(target_base)
    if node and isinstance(node, basestring if 'basestring' in globals() else str) and cmds.objExists(node):
        return cmds.rename(node, new_name)
    return new_name

def safe_parent(child, parent):
    """已是子节点则跳过；否则 parent。"""
    if not (cmds.objExists(child) and cmds.objExists(parent)):
        return
    cur = cmds.listRelatives(child, p=True, pa=True) or []
    if cur and cur[0] == parent:
        return
    try:
        cmds.parent(child, parent)
    except RuntimeError:
        pass

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
        chain.append(ch[0])
        ch = cmds.listRelatives(ch[0], c=True, type='joint') or []
    return chain

def duplicate_single_chain(root_joint, suffix="_workJ"):
    """复制单链根关节；返回复制根。"""
    if not is_single_chain(root_joint):
        cmds.warning(u"多分支，跳过复制: {}".format(root_joint)); return None
    dup = cmds.duplicate(root_joint, rr=True)[0]  # 先复制
    # 先给复制根唯一命名
    dup = unique_rename(dup, short_no_ns(root_joint) + suffix)
    # 再把所有子关节统一追加后缀，避免与原链重名
    rename_joint_descendants_with_suffix(dup, suffix=suffix)
    return dup


# ===== splineIK：自动曲线（不简化）=====
def create_ik_spline_auto_curve(joint_root):
    if not is_single_chain(joint_root):
        cmds.warning(u"多分支，跳过: {}".format(joint_root)); return None, None
    chain = get_joint_chain(joint_root)
    if len(chain) < 2:
        cmds.warning(u"少于2关节，跳过: {}".format(joint_root)); return None, None

    sj, ej = chain[0], chain[-1]
    ikh_name = uniq("{}_ikHandle".format(short_no_ns(joint_root)))
    res = cmds.ikHandle(
        n=ikh_name, sj=sj, ee=ej,
        sol="ikSplineSolver",
        ccv=True, pcv=False, simplifyCurve=False
    )
    ikh = res[0]
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
            if any_shapes:
                auto_curve = cmds.listRelatives(any_shapes[0], p=True, pa=True)[0]
    return ikh, auto_curve

def curve_shape_of(curve_xf):
    shapes = cmds.listRelatives(curve_xf, s=True, ni=True, pa=True) or []
    for s in shapes:
        if cmds.nodeType(s) == 'nurbsCurve': return s
    return None

# ===== nHair 产物重命名（不 parent）=====
def rename_after_make_dynamic(input_curve_transform, base_no_suffix):
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

    fol_xf = unique_rename(fol_xf, base_no_suffix + "_follicle")
    out_xf = unique_rename(out_xf, base_no_suffix + "_curve_dy")
    return fol_xf, out_xf

# ===== CV 控制 =====
def create_clusters_and_ctrls(curve_transform, ctrl_prefix):
    shp = curve_shape_of(curve_transform)
    if not shp:
        cmds.warning(u"[跳过] 非曲线或已丢失: {}".format(curve_transform)); return None, None
    cv_count = cmds.getAttr(shp + ".cp", s=True)

    sub_gp_name = unique_rename(None, "{}_{}_cluster_GP".format(ctrl_prefix, short_no_ns(curve_transform)))
    sub_gp = cmds.group(em=True, n=sub_gp_name)

    ctrls = []
    for i in range(cv_count):
        cl, clh = cmds.cluster("{}.cv[{}]".format(shp, i),
                               n=uniq("{}_cluster_{}".format(short_no_ns(curve_transform), i)))
        cmds.setAttr(clh + ".v", 0)
        ctrl = cmds.circle(n=uniq("{}_con_curve_{}".format(short_no_ns(curve_transform), i)),
                           ch=False, o=True)[0]
        cmds.matchTransform(ctrl, clh)
        cmds.makeIdentity(ctrl, a=True, t=True, r=True, s=True)
        cmds.parent(clh, ctrl)
        if i == 0: cmds.matchTransform(sub_gp, ctrl)
        cmds.parent(ctrl, sub_gp)
        ctrls.append(ctrl)
    return sub_gp, ctrls
def rename_joint_descendants_with_suffix(root_joint, suffix="_workJ"):
    """
    将 root_joint 以下所有子关节统一追加后缀，保证与原链不重名。
    叶子到根方向重命名，避免路径变化导致找不到节点。
    """
    if not cmds.objExists(root_joint):
        return
    # 所有关节（不含 root），从深到浅
    desc = cmds.listRelatives(root_joint, ad=True, type='joint', f=True) or []
    desc = [d for d in desc if d != root_joint]
    # 叶子优先
    for j in desc:
        short = j.split('|')[-1]
        base  = short.split(':')[-1]
        target = base + suffix
        # 用我们已有的唯一命名工具，避免场景内冲突
        new_name = uniq(target)
        try:
            cmds.rename(j, new_name)
        except RuntimeError:
            # 极端情况下再给一次唯一名
            cmds.rename(j, uniq(target + "_x"))
def strip_suffix(name, suffix):
    return name[:-len(suffix)] if name.endswith(suffix) else name

def build_dup_map(dup_roots, suffix="_workJ"):
    """
    从复制出来的根开始，收集所有复制关节，按“去后缀后的短名”建立映射：
    { 原关节短名 : 复制关节完整路径 }
    无视复制关节与分组之间是否有中间 transform###。
    """
    m = {}
    for r in dup_roots:
        joints = [r] + (cmds.listRelatives(r, ad=True, type='joint', f=True) or [])
        for j in joints:
            base = short_no_ns(j)
            key = strip_suffix(base, suffix)  # 去掉 _workJ
            m[key] = j
    return m

def constrain_one_to_one(dup_map, orig_roots):
    for r in orig_roots:
        chain = get_joint_chain(r)
        for oj in chain:
            key = short_no_ns(oj)
            dj = dup_map.get(key)
            if not dj:
                continue
            try:
                # 维持偏移
                cmds.parentConstraint(dj, oj, mo=True)   # 平移+旋转
            except RuntimeError:
                pass
            try:
                cmds.scaleConstraint(dj, oj, mo=True)    # 缩放
            except RuntimeError:
                pass

# ===== 主流程（复制关节后操作）=====
def run(prefix=None):
    sel = cmds.ls(sl=True, type='joint') or []
    if not sel:
        cmds.warning(u"请选择一个或多个关节起点"); return
    if prefix is None:
        prefix = infer_prefix(sel)

    # 复制选择的关节链
    dup_roots, bases = [], []
    for j in sel:
        if not is_single_chain(j):
            cmds.warning(u"多分支，跳过: {}".format(j)); continue
        dup = duplicate_single_chain(j, suffix="_workJ")
        if dup:
            dup_roots.append(dup)
            bases.append(short_no_ns(j))
    if not dup_roots:
        cmds.warning(u"无可用复制链，退出"); return

    cmds.undoInfo(ock=True)
    try:
        # 顶层分组
        work_joints_gp = ensure_group("{}_workJoints_GP".format(prefix))
        curves_gp      = ensure_group("{}_ik_curve_GP".format(prefix))
        follicle_gp    = ensure_group("{}_follicle_GP".format(prefix))
        ik_gp          = ensure_group("{}_ikHandle_GP".format(prefix))
        dy_start_gp    = ensure_group("{}_dy_start_GP".format(prefix))
        cluster_root   = ensure_group("{}_cluster_GP".format(prefix))

        to_parent = []   # (child, parent)
        backup_curves, pairs = [], []

        # 复制的关节链先入分组队列
        for dup in dup_roots:
            to_parent.append((dup, work_joints_gp))

        # 逐链创建 splineIK & 原曲线（基于复制链）
        for dup_root, base_name in zip(dup_roots, bases):
            ikh, auto_curve = create_ik_spline_auto_curve(dup_root)
            if not ikh or not auto_curve:
                continue

            orig_curve = unique_rename(auto_curve, base_name + "_curve")
            to_parent.append((ikh, ik_gp))
            to_parent.append((orig_curve, curves_gp))

            # 备份作为动力输入
            bkp = cmds.duplicate(orig_curve, n=uniq(base_name + "_curve_dy_start"))[0]
            to_parent.append((bkp, follicle_gp))
            backup_curves.append(bkp)
            pairs.append((base_name, orig_curve))

        # 批量创建 nHair（共用一个 hairSystem）
        if backup_curves:
            cmds.select(backup_curves, r=True)
            mel.eval('makeCurvesDynamic 2 { "1", "0", "1", "1", "0"};')
            cmds.select(cl=True)

        # 重命名 nHair 产物 & blendShape 回驱
        created_dy_inputs = []
        for base, orig_curve in pairs:
            base_unique = short_no_ns(orig_curve)
            if base_unique.endswith("_curve"):
                base_unique = base_unique[:-len("_curve")]

            in_curve = base_unique + "_curve_dy_start"
            fol, out_dy = rename_after_make_dynamic(in_curve, base_unique)

            if out_dy and cmds.objExists(orig_curve):
                bs = cmds.blendShape(out_dy, orig_curve, n=uniq(base_unique + "_bshape"))[0]
                cmds.setAttr("{}.{}".format(bs, out_dy), 1.0)

            cand = cmds.ls(base_unique + "_curve_dy_start*", type='transform') or []
            if cand:
                in_curve = cand[-1]
                to_parent.append((in_curve, dy_start_gp))
                created_dy_inputs.append(in_curve)

            if fol and cmds.objExists(fol):
                to_parent.append((fol, follicle_gp))

        # 为每条 *_curve_dy_start 创建 CV 控制，并挂到 cluster_root
        for c in created_dy_inputs:
            sub_gp, _ = create_clusters_and_ctrls(c, prefix)
            if sub_gp:
                to_parent.append((sub_gp, cluster_root))

        # 统一 parent
        for child, parent in to_parent:
            safe_parent(child, parent)
        # —— 统一执行 parent（去重检查）——
        for child, parent in to_parent:
            safe_parent(child, parent)

        # —— 一对一约束：复制链驱动原链 ——
        dup_map = build_dup_map(dup_roots, suffix="_workJ")
        constrain_one_to_one(dup_map, sel)

        print(u"[OK] 复制后处理完成 | 前缀: {} | 源链:{} | 复制链:{} | 分组: {}, {}, {}, {}, {}, {}".format(
            prefix, len(sel), len(dup_roots),
            work_joints_gp, curves_gp, follicle_gp, ik_gp, dy_start_gp, cluster_root))
    finally:
        cmds.undoInfo(cck=True)

# 运行
run()
