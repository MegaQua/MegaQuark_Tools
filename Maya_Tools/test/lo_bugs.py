# -*- coding: utf-8 -*-
from pyfbsdk import *

# ===== 参数 =====
BASE_NAME       = "TBUG"        # 已存在的基础对象
COUNT           = 10            # 复制数量
CURVE_NAME      = "3D Curve"    # 路径曲线名（FBModelPath3D）
AIM_NAME        = "aim point"   # 目标 Null 名
DIST_THRESH     = 1.0           # 相邻 offset 距离阈值
WARP_OFFSET     = -10.0         # 触发时叠加到“后一个”的偏移
CONSTRAINT_ACTIVE = True

# ===== 工具 =====
def _mat(mdl):
    M = FBMatrix(); mdl.GetMatrix(M); return M

def _clone(mdl, idx):
    dup = mdl.Clone()
    dup.Name = f"{mdl.Name}_{idx:02d}"
    return dup

def _ensure_model(name, cls=FBModelNull):
    m = FBFindModelByLabelName(name)
    return m if m else cls(name)

def _add_offset(mdl):
    off = FBModelNull(mdl.Name + "_offset")
    off.SetMatrix(_mat(mdl))
    mdl.Parent = off
    return off

def _path_constraint(obj, curve, active=True):
    cm = FBConstraintManager()
    c = cm.TypeCreateConstraint("Path")
    c.ReferenceAdd(0, obj)    # 源
    c.ReferenceAdd(1, curve)  # 目标
    c.Name = obj.Name + "_Path"
    c.Active = active
    return c

def _aim_constraint(child, target, active=True):
    cm = FBConstraintManager()
    c = cm.TypeCreateConstraint("Aim")
    c.ReferenceAdd(0, child)
    c.ReferenceAdd(1, target)
    c.Name = child.Name + "_" + target.Name + "_Aim"
    c.Active = active
    return c

def _anim_node(obj, prop_label):
    """拿到任意对象属性的 AnimationNode（找不到就抛错，方便定位）"""
    if obj is None:
        raise RuntimeError("传入对象是 None，无法获取属性节点。")
    p = obj.PropertyList.Find(prop_label)
    if not p:
        names = [obj.PropertyList.GetPropertyName(i) for i in range(obj.PropertyList.GetCount())]
        raise RuntimeError(f"对象[{getattr(obj,'Name','<no-name>')}]缺少属性[{prop_label}]，可用属性：{names}")
    return p.GetAnimationNode()

def _path_progress_node(path_constraint):
    """不同版本进度属性名可能不一致，这里自动兼容并返回 AnimationNode。"""
    for label in ("Warp", "Path %", "Path", "Percent"):
        p = path_constraint.PropertyList.Find(label)
        if p:
            return p.GetAnimationNode()
    names = [path_constraint.PropertyList.GetPropertyName(i) for i in range(path_constraint.PropertyList.GetCount())]
    raise RuntimeError(f"Path约束[{path_constraint.Name}]未找到进度属性(Warp/Path %/Path/Percent)。现有属性：{names}")

def _box(rel, cat, name):
    return rel.CreateFunctionBox(cat, name)

# ===== 主流程 =====
def build():
    base  = FBFindModelByLabelName(BASE_NAME)
    if not base:
        FBMessageBox("Error", f"未找到基础对象: {BASE_NAME}", "OK"); return

    curve = FBFindModelByLabelName(CURVE_NAME)
    if not curve or not isinstance(curve, FBModelPath3D):
        FBMessageBox("Error", f"未找到路径曲线: {CURVE_NAME}", "OK"); return

    aimpt = _ensure_model(AIM_NAME, FBModelNull)

    # 复制 -> offset -> Path/Aim 约束
    offs, paths = [], []
    for i in range(1, COUNT + 1):
        dup = _clone(base, i)
        off = _add_offset(dup)
        pc  = _path_constraint(off, curve, CONSTRAINT_ACTIVE)  # 直接保存“返回的约束对象”
        _aim_constraint(off, aimpt, CONSTRAINT_ACTIVE)

        offs.append(off)
        paths.append(pc)

    # Relation：串联 Path 进度（第一个不驱动）
    rel = FBConstraintRelation("TBUG_PathWarp_Relation")

    for i in range(1, len(paths)):
        prev_path = paths[i-1]
        this_path = paths[i]

        prev_prog = _path_progress_node(prev_path)     # 上一个进度（AnimationNode）
        this_prog = _path_progress_node(this_path)     # 当前进度（AnimationNode）
        a_trans   = _anim_node(offs[i-1], "Lcl Translation")
        b_trans   = _anim_node(offs[i],   "Lcl Translation")

        # 距离
        dist = _box(rel, "Vector", "Distance")
        dist_v1 = dist.AnimationNodeInGet().Nodes[0]    # v1 (Position)
        dist_v2 = dist.AnimationNodeInGet().Nodes[1]    # v2 (Position)
        dist_o  = dist.AnimationNodeOutGet().Nodes[0]   # Result
        FBConnect(a_trans, dist_v1)
        FBConnect(b_trans, dist_v2)

        # 比较：dist > 阈值
        gt   = _box(rel, "Number", "Is Greater or Equal (a >= b)")
        gt_a = gt.AnimationNodeInGet().Nodes[0]
        gt_b = gt.AnimationNodeInGet().Nodes[1]
        gt_o = gt.AnimationNodeOutGet().Nodes[0]
        FBConnect(dist_o, gt_a)
        gt_b.WriteData([float(DIST_THRESH)])

        # (gt?1:0) * WARP_OFFSET
        mul   = _box(rel, "Number", "Multiply (a x b)")
        mul_a = mul.AnimationNodeInGet().Nodes[0]
        mul_b = mul.AnimationNodeInGet().Nodes[1]
        mul_o = mul.AnimationNodeOutGet().Nodes[0]
        FBConnect(gt_o, mul_a)
        mul_b.WriteData([float(WARP_OFFSET)])

        # this = prev + delta
        add   = _box(rel, "Number", "Add (a + b)")
        add_a = add.AnimationNodeInGet().Nodes[0]
        add_b = add.AnimationNodeInGet().Nodes[1]
        add_o = add.AnimationNodeOutGet().Nodes[0]
        FBConnect(prev_prog, add_a)
        FBConnect(mul_o,    add_b)
        FBConnect(add_o,    this_prog)

        # 摆放（可选）
        rel.SetBoxPosition(dist, -200, i*160 + 40)
        rel.SetBoxPosition(gt,    120, i*160 + 40)
        rel.SetBoxPosition(mul,   360, i*160 + 40)
        rel.SetBoxPosition(add,   600, i*160)

    rel.Active = True
    FBSystem().Scene.Evaluate()
    print("[OK] 完成：复制/offset/Path/Aim/Relation 串联。")

build()
