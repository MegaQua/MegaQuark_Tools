# -*- coding: utf-8 -*-
import maya.cmds as cmds
import random, math

# ===== PySide =====
from maya import OpenMayaUI as omui
try:
    from PySide2 import QtWidgets, QtCore
    from shiboken2 import wrapInstance
except Exception:
    from PySide6 import QtWidgets, QtCore
    from shiboken6 import wrapInstance

# ===== OpenMaya API2（面法线） =====

# ===== 小工具 =====
def _maya_main_window():
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QWidget)

def _first_selected_mesh_transform():
    shp = cmds.ls(sl=True, dag=True, ni=True, type='mesh') or []
    if shp:
        return cmds.listRelatives(shp[0], p=True, f=False)[0]
    trs = cmds.ls(sl=True, dag=True, type='transform') or []
    for x in trs:
        if cmds.listRelatives(x, s=True, ni=True, type='mesh'):
            return x
    return None

def _gather_world_points_from_selection():
    pts = []
    sel = cmds.ls(sl=True, fl=True) or []
    if not sel: return pts
    verts = cmds.filterExpand(cmds.polyListComponentConversion(sel, toVertex=True), sm=31) or []
    for v in verts:
        try:
            p = cmds.pointPosition(v, w=True)
            pts.append((p[0], p[1], p[2]))
        except: pass
    for s in sel:
        if "." in s: continue
        if cmds.objExists(s) and cmds.nodeType(s) == "transform":
            p = cmds.xform(s, q=True, ws=True, t=True)
            pts.append((p[0], p[1], p[2]))
    return pts

# ===== 运动核心 =====
def bug_crawl_on_surface(
    mesh,
    frames=800,
    radius=0.1,
    speed=0.1,             # ✅ 速度：单位/秒
    turn_sigma=0.4,
    rng=None,
    # 起终点
    start_pos=None,
    start_jitter=0.05,
    end_pos=None,
    delay_frames=100,
    approach_frames=400,
    end_wander_radius=0.2,
    twist=0.6,
    # 活跃度与停顿
    activity=0.6, stop_min=8, stop_max=40,
    # 旋转/法线稳定
    orient=True, nrm_lerp=0.35
):
    import maya.api.OpenMaya as om2
    if not cmds.objExists(mesh): cmds.error('找不到网格: %s' % mesh)
    mshape = (cmds.listRelatives(mesh, s=True, ni=True, type='mesh') or [None])[0]
    if not mshape: cmds.error('不是多边形网格: %s' % mesh)
    if rng is None: rng = random.SystemRandom()

    # —— FPS ——
    def _scene_fps():
        tu = cmds.currentUnit(q=True, time=True)
        map_fps = {
            'game':15.0, 'film':24.0, 'pal':25.0, 'ntsc':30.0,
            'show':48.0, 'palf':50.0, 'ntscf':60.0
        }
        if tu in map_fps: return map_fps[tu]
        # 形如 "23.976fps"
        if tu.endswith('fps'):
            try: return float(tu[:-3])
            except: pass
        return 24.0
    FPS = _scene_fps()
    step_target = float(speed) / max(FPS, 1e-6)   # ✅ 每帧应走的世界弧长

    # —— MFnMesh（面法线）——
    sel = om2.MSelectionList(); sel.add(mshape)
    dag = sel.getDagPath(0)
    fnm = om2.MFnMesh(dag)

    # —— 最近点节点（投影）——
    cpom = cmds.createNode('closestPointOnMesh', n='bugCPOM#')
    cmds.connectAttr(mshape + '.outMesh',        cpom + '.inMesh',      f=True)
    cmds.connectAttr(mesh   + '.worldMatrix[0]', cpom + '.inputMatrix', f=True)

    def _set_inpos(p):
        cmds.setAttr(cpom + '.inPositionX', p[0])
        cmds.setAttr(cpom + '.inPositionY', p[1])
        cmds.setAttr(cpom + '.inPositionZ', p[2])

    def _out_pos():
        return cmds.getAttr(cpom + '.position')[0]

    def _face_normal_at(pos):
        p = om2.MPoint(pos[0], pos[1], pos[2])
        _, poly_id = fnm.getClosestPoint(p, om2.MSpace.kWorld)
        n = fnm.getPolygonNormal(poly_id, om2.MSpace.kWorld)
        v = (n.x, n.y, n.z); l = max((v[0]*v[0]+v[1]*v[1]+v[2]*v[2])**0.5, 1e-8)
        return (v[0]/l, v[1]/l, v[2]/l)

    # vec utils
    def _v_add(a,b): return (a[0]+b[0], a[1]+b[1], a[2]+b[2])
    def _v_sub(a,b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
    def _v_mul(a,s): return (a[0]*s, a[1]*s, a[2]*s)
    def _dot(a,b):   return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
    def _len(a):     return max((_dot(a,a))**0.5, 1e-12)
    def _norm(a):    return _v_mul(a, 1.0/_len(a))
    def _cross(a,b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
    def _proj_plane(v, n): return _v_sub(v, _v_mul(n, _dot(v, n)))
    def _lerp(a,b,t): return (a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t, a[2]+(b[2]-a[2])*t)

    def _mat_cols_to_euler_xyz(xc, yc, zc):
        m00,m01,m02 = xc[0],yc[0],zc[0]; m10,m11,m12 = xc[1],yc[1],zc[1]; m20,m21,m22 = xc[2],yc[2],zc[2]
        sy = math.sqrt(max(m00 * m00 + m10 * m10, 1e-16))
        if sy>1e-8:
            rx = math.atan2(m21, m22); ry = math.atan2(-m20, sy); rz = math.atan2(m10, m00)
        else:
            rx = math.atan2(-m12, m11); ry = math.atan2(-m20, sy); rz = 0.0
        r2d = 57.29577951308232; return (rx*r2d, ry*r2d, rz*r2d)
    def _unwrap(prev, cur):
        d = cur-prev
        while d>180.0: cur -= 360.0; d -= 360.0
        while d<-180.0: cur += 360.0; d += 360.0
        return cur

    # —— 起点 ——
    if start_pos is None:
        bb = cmds.exactWorldBoundingBox(mesh)
        guess = (rng.uniform(bb[0], bb[3]), rng.uniform(bb[1], bb[4]), rng.uniform(bb[2], bb[5]))
        _set_inpos(guess); pos = _out_pos()
    else:
        _set_inpos(start_pos); pos = _out_pos()
        n0 = _face_normal_at(pos)
        for _ in range(5):
            rv = (rng.uniform(-1,1), rng.uniform(-1,1), rng.uniform(-1,1))
            t  = _proj_plane(rv, n0)
            if _len(t)>1e-6:
                _set_inpos(_v_add(pos, _v_mul(_norm(t), start_jitter*rng.random())))
                pos = _out_pos(); break

    nrm = _face_normal_at(pos)
    rv  = (rng.uniform(-1,1), rng.uniform(-1,1), rng.uniform(-1,1))
    fwd = _norm(_proj_plane(rv, nrm))

    # 终点
    tgt = None
    if end_pos is not None: _set_inpos(end_pos); tgt = _out_pos()

    # 创建虫子
    bug = cmds.polySphere(r=radius, n='bugBall#')[0]
    for a in ('tx','ty','tz','rx','ry','rz'):
        try: cmds.setAttr(bug + '.' + a, 0)
        except: pass

    # 时间
    f0 = int(cmds.playbackOptions(q=True, minTime=True))
    f1 = f0 + int(frames) - 1
    if f1 > cmds.playbackOptions(q=True, maxTime=True): cmds.playbackOptions(e=True, maxTime=f1)

    # 活跃度影响
    appF = int(max(1, round(approach_frames * (1.5 - max(0.0, min(1.0, activity))))))
    wander_r   = end_wander_radius * (0.5 + 1.5*activity)
    stop_prob  = 0.08*(1.0-activity) + 0.01*activity
    stop_scale = 1.2 - 0.8*activity

    # 旋转状态
    prev_eul = None
    def _bake_rot(fwd_vec, nrm_vec, frame):
        nonlocal prev_eul
        up = _norm(nrm_vec)
        right = _cross(up, fwd_vec)
        if _len(right)<1e-6:
            tmp = (1,0,0) if abs(up[0])<0.9 else (0,1,0)
            right = _norm(_cross(up, tmp))
            fwd_c = _norm(_cross(right, up))
        else:
            right = _norm(right); fwd_c = _norm(_cross(right, up))
        rx, ry, rz = _mat_cols_to_euler_xyz(right, up, fwd_c)
        if prev_eul is not None:
            rx = _unwrap(prev_eul[0], rx); ry = _unwrap(prev_eul[1], ry); rz = _unwrap(prev_eul[2], rz)
        prev_eul = (rx, ry, rz)
        cmds.setKeyframe(bug + '.rotateX', t=frame, v=rx)
        cmds.setKeyframe(bug + '.rotateY', t=frame, v=ry)
        cmds.setKeyframe(bug + '.rotateZ', t=frame, v=rz)

    # 首帧
    cmds.setKeyframe(bug + '.translateX', t=f0, v=pos[0])
    cmds.setKeyframe(bug + '.translateY', t=f0, v=pos[1])
    cmds.setKeyframe(bug + '.translateZ', t=f0, v=pos[2])
    if orient: _bake_rot(fwd, nrm, f0)

    # 停顿
    stall_left = 0

    # —— 主循环（弧长步进 + 子步）——
    for f in range(f0+1, f1+1):
        # 停顿触发
        if stall_left<=0 and rng.random()<float(stop_prob):
            dur = int(round(rng.uniform(stop_min, stop_max)*stop_scale))
            stall_left = max(1, dur)

        if stall_left>0:
            stall_left -= 1
            cmds.setKeyframe(bug + '.translateX', t=f, v=pos[0])
            cmds.setKeyframe(bug + '.translateY', t=f, v=pos[1])
            cmds.setKeyframe(bug + '.translateZ', t=f, v=pos[2])
            if orient: _bake_rot(fwd, nrm, f)
            continue

        # 随机转向（绕法线）
        ang = rng.gauss(0.0, float(turn_sigma))
        ca, sa = math.cos(ang), math.sin(ang); ax = nrm
        cross = (ax[1]*fwd[2]-ax[2]*fwd[1], ax[2]*fwd[0]-ax[0]*fwd[2], ax[0]*fwd[1]-ax[1]*fwd[0])
        fwd = _norm((
            fwd[0]*ca + cross[0]*sa + ax[0]*_dot(ax, fwd)*(1.0-ca),
            fwd[1]*ca + cross[1]*sa + ax[1]*_dot(ax, fwd)*(1.0-ca),
            fwd[2]*ca + cross[2]*sa + ax[2]*_dot(ax, fwd)*(1.0-ca)
        ))
        fwd = _norm(_proj_plane(fwd, nrm))

        # 目标吸引/徘徊
        if tgt is not None:
            elapsed = f - f0
            if delay_frames <= elapsed < (delay_frames + appF):
                k = (elapsed - delay_frames) / max(1.0, float(appF))
                dir_to = _proj_plane(_v_sub(tgt, pos), nrm)
                if _len(dir_to)>1e-6:
                    dir_to = _norm(dir_to)
                    alpha = max(0.0, min(1.0, 1.0 - float(twist)))
                    mix_w = alpha * k
                    fwd = _norm(_v_add(_v_mul(fwd, 1.0-mix_w), _v_mul(dir_to, mix_w)))
            elif elapsed >= (delay_frames + appF):
                to_tgt = _v_sub(tgt, pos); d = _len(to_tgt)
                if d>1e-6:
                    dir_t = _norm(_proj_plane(to_tgt, nrm))
                    if d > end_wander_radius:
                        fwd = _norm(_v_add(_v_mul(fwd, 0.4), _v_mul(dir_t, 0.6)))
                    else:
                        jitter = rng.uniform(-0.4, 0.4)
                        ca, sa = math.cos(jitter), math.sin(jitter); ax = nrm
                        cross = (ax[1]*fwd[2]-ax[2]*fwd[1], ax[2]*fwd[0]-ax[0]*fwd[2], ax[0]*fwd[1]-ax[1]*fwd[0])
                        fwd = _norm((
                            fwd[0]*ca + cross[0]*sa + ax[0]*_dot(ax, fwd)*(1.0-ca),
                            fwd[1]*ca + cross[1]*sa + ax[1]*_dot(ax, fwd)*(1.0-ca),
                            fwd[2]*ca + cross[2]*sa + ax[2]*_dot(ax, fwd)*(1.0-ca)
                        ))
                        fwd = _norm(_proj_plane(fwd, nrm))

        # —— 子步推进，逼近目标弧长 ——
        remaining = step_target
        max_sub = 5
        while remaining > 1e-6 and max_sub>0:
            max_sub -= 1
            expect = _v_add(pos, _v_mul(fwd, remaining))
            _set_inpos(expect)
            new_pos = _out_pos()
            new_nrm = _face_normal_at(new_pos)
            # 平滑法线
            nrm = _norm(_lerp(nrm, new_nrm, float(nrm_lerp)))

            move_vec = _v_sub(new_pos, pos)
            d = _len(move_vec)
            if d < 1e-6:
                # 卡住，随机刷新切向并缩小剩余步长
                rv = (rng.uniform(-1,1), rng.uniform(-1,1), rng.uniform(-1,1))
                fwd = _norm(_proj_plane(rv, nrm))
                remaining *= 0.5
                continue

            pos = new_pos
            fwd = _norm(_proj_plane(move_vec, nrm))
            remaining = max(0.0, remaining - d)

        # 位移/旋转关键帧
        cmds.setKeyframe(bug + '.translateX', t=f, v=pos[0])
        cmds.setKeyframe(bug + '.translateY', t=f, v=pos[1])
        cmds.setKeyframe(bug + '.translateZ', t=f, v=pos[2])
        if orient: _bake_rot(fwd, nrm, f)

    try: cmds.delete(cpom)
    except: pass
    return bug


    def _set_inpos(p):
        cmds.setAttr(cpom + '.inPositionX', p[0])
        cmds.setAttr(cpom + '.inPositionY', p[1])
        cmds.setAttr(cpom + '.inPositionZ', p[2])

    def _out_pos():
        return cmds.getAttr(cpom + '.position')[0]

    def _face_normal_at(pos):
        # 用最近多边形的几何面法线（不依赖 kFace 常量）
        p = om2.MPoint(pos[0], pos[1], pos[2])
        closest_pt, poly_id = fnm.getClosestPoint(p, om2.MSpace.kWorld)  # 返回(point, polygonId)
        n = fnm.getPolygonNormal(poly_id, om2.MSpace.kWorld)  # 几何面法线
        v = (n.x, n.y, n.z)
        l = max((v[0] * v[0] + v[1] * v[1] + v[2] * v[2]) ** 0.5, 1e-8)
        return (v[0] / l, v[1] / l, v[2] / l)

    # 向量
    def _v_add(a,b): return (a[0]+b[0], a[1]+b[1], a[2]+b[2])
    def _v_sub(a,b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
    def _v_mul(a,s): return (a[0]*s, a[1]*s, a[2]*s)
    def _dot(a,b):   return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
    def _len(a):     return max((_dot(a,a))**0.5, 1e-12)
    def _norm(a):    return _v_mul(a, 1.0/_len(a))
    def _cross(a,b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
    def _proj_plane(v, n): return _v_sub(v, _v_mul(n, _dot(v, n)))
    def _lerp(a,b,t): return (a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t, a[2]+(b[2]-a[2])*t)

    # 欧拉展开，避免±180跳
    def _unwrap(prev, cur):
        d = cur - prev
        while d > 180.0: cur -= 360.0; d -= 360.0
        while d < -180.0: cur += 360.0; d += 360.0
        return cur

    # 从坐标轴列向量取 XYZ 欧拉
    def _mat_cols_to_euler_xyz(xc, yc, zc):
        m00, m01, m02 = xc[0], yc[0], zc[0]
        m10, m11, m12 = xc[1], yc[1], zc[1]
        m20, m21, m22 = xc[2], yc[2], zc[2]
        sy = math.sqrt(max(m00 * m00 + m10 * m10, 1e-16))
        if sy > 1e-8:
            rx = math.atan2(m21, m22)
            ry = math.atan2(-m20, sy)
            rz = math.atan2(m10, m00)
        else:
            rx = math.atan2(-m12, m11)
            ry = math.atan2(-m20, sy)
            rz = 0.0
        r2d = 57.29577951308232
        return (rx*r2d, ry*r2d, rz*r2d)

    # —— 起点 ——
    if start_pos is None:
        bb = cmds.exactWorldBoundingBox(mesh)
        guess = (rng.uniform(bb[0], bb[3]),
                 rng.uniform(bb[1], bb[4]),
                 rng.uniform(bb[2], bb[5]))
        _set_inpos(guess)
        pos = _out_pos()
    else:
        _set_inpos(start_pos)
        pos = _out_pos()
        n0 = _face_normal_at(pos)
        # 切向抖动
        for _ in range(5):
            rv = (rng.uniform(-1,1), rng.uniform(-1,1), rng.uniform(-1,1))
            t  = _proj_plane(rv, n0)
            if _len(t) > 1e-6:
                offset = _v_mul(_norm(t), start_jitter*rng.random())
                _set_inpos(_v_add(pos, offset))
                pos = _out_pos()
                break

    # 初始法线/前向
    nrm = _face_normal_at(pos)
    rv  = (rng.uniform(-1,1), rng.uniform(-1,1), rng.uniform(-1,1))
    fwd = _norm(_proj_plane(rv, nrm))

    # 终点
    tgt = None
    if end_pos is not None:
        _set_inpos(end_pos); tgt = _out_pos()

    # 创建虫子
    bug = cmds.polySphere(r=radius, n='bugBall#')[0]
    for a in ('tx','ty','tz','rx','ry','rz'):
        try: cmds.setAttr(bug + '.' + a, 0)
        except: pass

    # 时间
    f0 = int(cmds.playbackOptions(q=True, minTime=True))
    f1 = f0 + int(frames) - 1
    if f1 > cmds.playbackOptions(q=True, maxTime=True):
        cmds.playbackOptions(e=True, maxTime=f1)

    # 活跃度影响
    appF = int(max(1, round(approach_frames * (1.5 - max(0.0, min(1.0, activity))))))
    wander_r = end_wander_radius * (0.5 + 1.5*activity)
    stop_prob  = 0.08*(1.0-activity) + 0.01*activity
    stop_scale = 1.2 - 0.8*activity

    # 旋转状态
    prev_eul = None  # (rx, ry, rz) 连续角度
    RAD2DEG = 57.29577951308232

    def _bake_rot(fwd_vec, nrm_vec, frame):
        # 构造正交基：X=right, Y=up(法线), Z=forward
        up = _norm(nrm_vec)
        right = _cross(up, fwd_vec)
        if _len(right) < 1e-6:
            # 兜底
            tmp = (1,0,0) if abs(up[0]) < 0.9 else (0,1,0)
            right = _norm(_cross(up, tmp))
            fwd_c = _norm(_cross(right, up))
        else:
            right = _norm(right)
            fwd_c = _norm(_cross(right, up))
        rx, ry, rz = _mat_cols_to_euler_xyz(right, up, fwd_c)

        # 展开到连续角度
        nonlocal prev_eul
        if prev_eul is not None:
            rx = _unwrap(prev_eul[0], rx)
            ry = _unwrap(prev_eul[1], ry)
            rz = _unwrap(prev_eul[2], rz)
        prev_eul = (rx, ry, rz)

        cmds.setKeyframe(bug + '.rotateX', t=frame, v=rx)
        cmds.setKeyframe(bug + '.rotateY', t=frame, v=ry)
        cmds.setKeyframe(bug + '.rotateZ', t=frame, v=rz)

    # 首帧
    cmds.setKeyframe(bug + '.translateX', t=f0, v=pos[0])
    cmds.setKeyframe(bug + '.translateY', t=f0, v=pos[1])
    cmds.setKeyframe(bug + '.translateZ', t=f0, v=pos[2])
    if orient: _bake_rot(fwd, nrm, f0)

    # 停顿
    stall_left = 0

    # 主循环
    for f in range(f0+1, f1+1):
        # 停顿
        if stall_left <= 0 and rng.random() < float(stop_prob):
            dur = int(round(rng.uniform(stop_min, stop_max) * stop_scale))
            stall_left = max(1, dur)

        if stall_left > 0:
            stall_left -= 1
            # 原地烘焙
            cmds.setKeyframe(bug + '.translateX', t=f, v=pos[0])
            cmds.setKeyframe(bug + '.translateY', t=f, v=pos[1])
            cmds.setKeyframe(bug + '.translateZ', t=f, v=pos[2])
            if orient: _bake_rot(fwd, nrm, f)
            continue

        # 随机转向（绕法线）
        ang = rng.gauss(0.0, float(turn_sigma))
        ca, sa = math.cos(ang), math.sin(ang)
        ax = nrm
        cross = (ax[1]*fwd[2]-ax[2]*fwd[1],
                 ax[2]*fwd[0]-ax[0]*fwd[2],
                 ax[0]*fwd[1]-ax[1]*fwd[0])
        fwd = _norm((
            fwd[0]*ca + cross[0]*sa + ax[0]*_dot(ax, fwd)*(1.0-ca),
            fwd[1]*ca + cross[1]*sa + ax[1]*_dot(ax, fwd)*(1.0-ca),
            fwd[2]*ca + cross[2]*sa + ax[2]*_dot(ax, fwd)*(1.0-ca)
        ))
        fwd = _norm(_proj_plane(fwd, nrm))

        # 目标吸引/徘徊
        if tgt is not None:
            elapsed = f - f0
            if elapsed >= delay_frames and elapsed < (delay_frames + appF):
                k = (elapsed - delay_frames) / max(1.0, float(appF))
                dir_to = _proj_plane(_v_sub(tgt, pos), nrm)
                if _len(dir_to) > 1e-6:
                    dir_to = _norm(dir_to)
                    alpha = max(0.0, min(1.0, 1.0 - float(twist)))
                    mix_w = alpha * k
                    fwd = _norm(_v_add(_v_mul(fwd, 1.0 - mix_w), _v_mul(dir_to, mix_w)))
            elif elapsed >= (delay_frames + appF):
                to_tgt = _v_sub(tgt, pos); d = _len(to_tgt)
                if d > 1e-6:
                    dir_t = _norm(_proj_plane(to_tgt, nrm))
                    if d > wander_r:
                        fwd = _norm(_v_add(_v_mul(fwd, 0.4), _v_mul(dir_t, 0.6)))
                    else:
                        jitter = rng.uniform(-0.4, 0.4)
                        ca, sa = math.cos(jitter), math.sin(jitter)
                        ax = nrm
                        cross = (ax[1]*fwd[2]-ax[2]*fwd[1],
                                 ax[2]*fwd[0]-ax[0]*fwd[2],
                                 ax[0]*fwd[1]-ax[1]*fwd[0])
                        fwd = _norm((
                            fwd[0]*ca + cross[0]*sa + ax[0]*_dot(ax, fwd)*(1.0-ca),
                            fwd[1]*ca + cross[1]*sa + ax[1]*_dot(ax, fwd)*(1.0-ca),
                            fwd[2]*ca + cross[2]*sa + ax[2]*_dot(ax, fwd)*(1.0-ca)
                        ))
                        fwd = _norm(_proj_plane(fwd, nrm))

        # 试走一步 → 投影
        expect = _v_add(pos, _v_mul(fwd, float(step)))
        _set_inpos(expect)
        new_pos = _out_pos()
        # 面法线 + 平滑
        new_nrm = _face_normal_at(new_pos)
        nrm = _norm(_lerp(nrm, new_nrm, float(nrm_lerp)))

        move_vec = _v_sub(new_pos, pos)
        if _len(move_vec) < 1e-6:
            # 卡住兜底
            rv = (rng.uniform(-1,1), rng.uniform(-1,1), rng.uniform(-1,1))
            fwd = _norm(_proj_plane(rv, nrm))
            expect = _v_add(pos, _v_mul(fwd, float(step)))
            _set_inpos(expect)
            new_pos = _out_pos()
            new_nrm = _face_normal_at(new_pos)
            nrm = _norm(_lerp(nrm, new_nrm, float(nrm_lerp)))
            move_vec = _v_sub(new_pos, pos)

        pos = new_pos
        if _len(move_vec) > 1e-8:
            fwd = _norm(_proj_plane(move_vec, nrm))

        # 位移
        cmds.setKeyframe(bug + '.translateX', t=f, v=pos[0])
        cmds.setKeyframe(bug + '.translateY', t=f, v=pos[1])
        cmds.setKeyframe(bug + '.translateZ', t=f, v=pos[2])

        # 旋转
        if orient: _bake_rot(fwd, nrm, f)

    try: cmds.delete(cpom)
    except: pass
    return bug

# ===== UI =====
class BugCrawlUI(QtWidgets.QDialog):
    WINDOW_TITLE = u"虫子爬行（稳定旋转/起终点/活跃度）"

    def __init__(self, parent=None):
        super(BugCrawlUI, self).__init__(parent or _maya_main_window())
        self.setObjectName("BugCrawlUI")
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setMinimumWidth(540)
        self.start_points = []
        self.end_points   = []
        self._build()

    def _build(self):
        layout = QtWidgets.QVBoxLayout(self)

        # 目标网格
        row_mesh = QtWidgets.QHBoxLayout()
        self.mesh_edit = QtWidgets.QLineEdit()
        btn_pick = QtWidgets.QPushButton(u"⇦ 取选择")
        btn_pick.clicked.connect(self._on_pick)
        row_mesh.addWidget(QtWidgets.QLabel(u"目标网格:"))
        row_mesh.addWidget(self.mesh_edit, 1)
        row_mesh.addWidget(btn_pick)
        layout.addLayout(row_mesh)

        def spin_dbl(minv, maxv, step, val, dec=4):
            s = QtWidgets.QDoubleSpinBox()
            s.setRange(minv, maxv); s.setSingleStep(step); s.setDecimals(dec); s.setValue(val)
            return s
        def spin_int(minv, maxv, step, val):
            s = QtWidgets.QSpinBox()
            s.setRange(minv, maxv); s.setSingleStep(step); s.setValue(val)
            return s

        # 数量/基本参数
        self.sp_count  = spin_int(1, 9999, 1, 10)
        self.sp_frames = spin_int(1, 200000, 50, 800)
        self.sp_radius = spin_dbl(0.001, 100.0, 0.01, 0.1, 3)
        self.sp_step   = spin_dbl(0.0001, 10.0, 0.005, 0.05, 4)
        self.sp_sigma  = spin_dbl(0.0, 6.2832, 0.05, 0.4, 4)
        self.sp_nrmS   = spin_dbl(0.0, 1.0, 0.05, 0.35, 2)  # 法线平滑

        grid = QtWidgets.QGridLayout()
        grid.addWidget(QtWidgets.QLabel(u"数量"),     0,0); grid.addWidget(self.sp_count,  0,1)
        grid.addWidget(QtWidgets.QLabel(u"帧数"),     0,2); grid.addWidget(self.sp_frames, 0,3)
        grid.addWidget(QtWidgets.QLabel(u"半径"),     1,0); grid.addWidget(self.sp_radius, 1,1)
        grid.addWidget(QtWidgets.QLabel(u"步长"),     1,2); grid.addWidget(self.sp_step,   1,3)
        grid.addWidget(QtWidgets.QLabel(u"转向σ"),   2,0); grid.addWidget(self.sp_sigma,  2,1)
        grid.addWidget(QtWidgets.QLabel(u"法线平滑"), 2,2); grid.addWidget(self.sp_nrmS,   2,3)
        layout.addLayout(grid)

        # 起点
        grp_start = QtWidgets.QGroupBox(u"起点")
        v1 = QtWidgets.QVBoxLayout(grp_start)
        r1 = QtWidgets.QHBoxLayout()
        self.cb_use_start = QtWidgets.QCheckBox(u"使用起点列表")
        self.lbl_start = QtWidgets.QLabel(u"(0)")
        btn_rec_start = QtWidgets.QPushButton(u"记录起点(从选择)")
        btn_clr_start = QtWidgets.QPushButton(u"清空")
        btn_rec_start.clicked.connect(self._on_record_start)
        btn_clr_start.clicked.connect(self._on_clear_start)
        r1.addWidget(self.cb_use_start); r1.addWidget(self.lbl_start); r1.addStretch(1)
        r1.addWidget(btn_rec_start); r1.addWidget(btn_clr_start)
        v1.addLayout(r1)
        r1b = QtWidgets.QHBoxLayout()
        self.sp_start_jitter = spin_dbl(0.0, 10.0, 0.01, 0.05, 3)
        r1b.addWidget(QtWidgets.QLabel(u"起点偏移(半径)")); r1b.addWidget(self.sp_start_jitter)
        v1.addLayout(r1b)
        layout.addWidget(grp_start)

        # 终点
        grp_end = QtWidgets.QGroupBox(u"终点")
        v2 = QtWidgets.QVBoxLayout(grp_end)
        r2 = QtWidgets.QHBoxLayout()
        self.cb_use_end = QtWidgets.QCheckBox(u"使用终点列表")
        self.lbl_end = QtWidgets.QLabel(u"(0)")
        btn_rec_end = QtWidgets.QPushButton(u"记录终点(从选择)")
        btn_clr_end = QtWidgets.QPushButton(u"清空")
        btn_rec_end.clicked.connect(self._on_record_end)
        btn_clr_end.clicked.connect(self._on_clear_end)
        r2.addWidget(self.cb_use_end); r2.addWidget(self.lbl_end); r2.addStretch(1)
        r2.addWidget(btn_rec_end); r2.addWidget(btn_clr_end)
        v2.addLayout(r2)

        r2b = QtWidgets.QGridLayout()
        self.sp_delay    = spin_int(0, 200000, 10, 100)
        self.sp_approach = spin_int(1, 200000, 10, 400)
        self.sp_end_rad  = spin_dbl(0.0, 10.0, 0.01, 0.2, 3)
        self.sp_twist    = spin_dbl(0.0, 1.0, 0.05, 0.6, 2)
        r2b.addWidget(QtWidgets.QLabel(u"到达延迟(帧)"),     0,0); r2b.addWidget(self.sp_delay,    0,1)
        r2b.addWidget(QtWidgets.QLabel(u"到达用时(帧)"),     0,2); r2b.addWidget(self.sp_approach, 0,3)
        r2b.addWidget(QtWidgets.QLabel(u"徘徊半径(基础)"),   1,0); r2b.addWidget(self.sp_end_rad,  1,1)
        r2b.addWidget(QtWidgets.QLabel(u"扭曲度(0直-1绕)"), 1,2); r2b.addWidget(self.sp_twist,    1,3)
        v2.addLayout(r2b)
        layout.addWidget(grp_end)

        # 行为（活跃度与停顿）
        grp_beh = QtWidgets.QGroupBox(u"行为")
        v3 = QtWidgets.QGridLayout(grp_beh)
        self.sp_act_base   = spin_dbl(0.0, 1.0, 0.05, 0.6, 2)
        self.sp_act_jitter = spin_dbl(0.0, 1.0, 0.05, 0.2, 2)
        self.sp_stop_min   = spin_int(1, 1000, 1, 8)
        self.sp_stop_max   = spin_int(1, 2000, 1, 40)
        v3.addWidget(QtWidgets.QLabel(u"活跃度(基准 0~1)"), 0,0); v3.addWidget(self.sp_act_base,   0,1)
        v3.addWidget(QtWidgets.QLabel(u"活跃度浮动(±)"),   0,2); v3.addWidget(self.sp_act_jitter, 0,3)
        v3.addWidget(QtWidgets.QLabel(u"停顿最少帧"),       1,0); v3.addWidget(self.sp_stop_min,   1,1)
        v3.addWidget(QtWidgets.QLabel(u"停顿最多帧"),       1,2); v3.addWidget(self.sp_stop_max,   1,3)
        layout.addWidget(grp_beh)

        # 选项/操作
        self.cb_orient = QtWidgets.QCheckBox(u"烘焙旋转（稳定）")
        self.cb_orient.setChecked(True)
        layout.addWidget(self.cb_orient)

        row_ops = QtWidgets.QHBoxLayout()
        btn_run = QtWidgets.QPushButton(u"生成")
        btn_run.clicked.connect(self._on_run)
        row_ops.addStretch(1); row_ops.addWidget(btn_run)
        layout.addLayout(row_ops)

    # —— 起终点管理 ——
    def _on_record_start(self):
        pts = _gather_world_points_from_selection()
        if not pts:
            QtWidgets.QMessageBox.warning(self, u"提示", u"选 vtx/edge/face 或物体来记录为起点")
            return
        self.start_points.extend(pts)
        self.lbl_start.setText(u"(%d)" % len(self.start_points))

    def _on_clear_start(self):
        self.start_points = []; self.lbl_start.setText(u"(0)")

    def _on_record_end(self):
        pts = _gather_world_points_from_selection()
        if not pts:
            QtWidgets.QMessageBox.warning(self, u"提示", u"选 vtx/edge/face 或物体来记录为终点")
            return
        self.end_points.extend(pts)
        self.lbl_end.setText(u"(%d)" % len(self.end_points))

    def _on_clear_end(self):
        self.end_points = []; self.lbl_end.setText(u"(0)")

    def _on_pick(self):
        m = _first_selected_mesh_transform()
        if not m:
            QtWidgets.QMessageBox.warning(self, u"提示", u"请先选择一个包含 mesh 的对象")
            return
        self.mesh_edit.setText(m)

    def _on_run(self):
        mesh = self.mesh_edit.text().strip()
        if not mesh:
            QtWidgets.QMessageBox.warning(self, u"提示", u"请指定目标网格（可用“取选择”）")
            return

        use_start = self.cb_use_start.isChecked()
        use_end   = self.cb_use_end.isChecked()
        if use_start and not self.start_points:
            QtWidgets.QMessageBox.warning(self, u"提示", u"已勾选“使用起点”，但列表为空")
            return
        if use_end and not self.end_points:
            QtWidgets.QMessageBox.warning(self, u"提示", u"已勾选“使用终点”，但列表为空")
            return

        count   = int(self.sp_count.value())
        frames  = int(self.sp_frames.value())
        radius  = float(self.sp_radius.value())
        step    = float(self.sp_step.value())
        sigma   = float(self.sp_sigma.value())
        nrmS    = float(self.sp_nrmS.value())

        s_jit   = float(self.sp_start_jitter.value())
        delayF  = int(self.sp_delay.value())
        appF    = int(self.sp_approach.value())
        endRad  = float(self.sp_end_rad.value())
        twist   = float(self.sp_twist.value())
        orient  = self.cb_orient.isChecked()

        act_base   = float(self.sp_act_base.value())
        act_jitter = float(self.sp_act_jitter.value())
        stop_min   = int(self.sp_stop_min.value())
        stop_max   = int(self.sp_stop_max.value())

        try:
            cmds.undoInfo(openChunk=True, chunkName="BugCrawl")

            # 本次生成统一组
            grp = cmds.createNode('transform', n='BugCrawl_GRP#')

            bugs = []
            for _ in range(count):
                rng = random.SystemRandom()
                sp = rng.choice(self.start_points) if (use_start and self.start_points) else None
                ep = rng.choice(self.end_points)   if (use_end   and self.end_points)   else None
                a = act_base + rng.uniform(-act_jitter, act_jitter)
                a = max(0.0, min(1.0, a))
                b = bug_crawl_on_surface(
                    mesh=mesh, frames=frames, radius=radius,
                    step=step, turn_sigma=sigma, rng=rng,
                    start_pos=sp, start_jitter=s_jit,
                    end_pos=ep, delay_frames=delayF, approach_frames=appF,
                    end_wander_radius=endRad, twist=twist,
                    activity=a, stop_min=stop_min, stop_max=stop_max,
                    orient=orient, nrm_lerp=nrmS
                )
                # 入组
                try: cmds.parent(b, grp)
                except: pass
                bugs.append(b)
            if bugs: cmds.select(bugs)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, u"出错", str(e))
        finally:
            cmds.undoInfo(closeChunk=True)

# ===== 运行窗口（单例） =====
def show_bug_crawl_ui():
    for w in QtWidgets.QApplication.topLevelWidgets():
        if isinstance(w, BugCrawlUI):
            w.close(); w.deleteLater()
    ui = BugCrawlUI(_maya_main_window()); ui.show(); return ui

# 打开 UI
show_bug_crawl_ui()
