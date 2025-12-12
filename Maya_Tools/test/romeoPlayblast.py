# -*- coding: utf-8 -*-
# 批量打开 .mb；可按名称倒序；可跳过事件号；front 相机；带声音 playblast
# 若文件名以 _Acelino 结尾，则把 front 相机的 translateY 设为 163（若锁定先解锁）
import os, re
import maya.cmds as cmds
import maya.mel as mel

# ==== 配置 ====
MB_DIR  = r"D:\files\mayafile\ROMEO\scenes\fin"
OUT_DIR = r"C:/Users/justcause/Desktop/fin"
WIDTH, HEIGHT = 810, 1080
SKIP_EVENTS = ["1030","1050","1051"]   # 只写四位数字
SORT_DESC = False                       # True=名称倒序，False=正序
SPECIAL_SUFFIX = "_Acelino"            # 特殊文件名后缀
ACELINO_FRONT_Y = 163.0                # _Acelino 时 front.ty 设定值

# ==== 小工具 ====
ev_pat = re.compile(r"ev(\d{4})", re.I)

def ev_of(name):
    m = ev_pat.search(name)
    return m.group(1) if m else None

def set_front_camera():
    try:
        for p in (cmds.getPanel(type="modelPanel") or []):
            try:
                cmds.modelPanel(p, e=True, camera="front")
            except:
                pass
        cmds.lookThru("front")
    except:
        pass

def bind_timeslider_first_audio():
    auds = cmds.ls(type='audio') or []
    if not auds: return None
    snd = auds[0]
    try:
        ctrl = mel.eval('$a=$gPlayBackSlider')
        cmds.timeControl(ctrl, e=True, useTraxSounds=False)
        cmds.timeControl(ctrl, e=True, sound=snd, displaySound=True)
    except:
        pass
    try:
        if cmds.objExists(snd + ".mute"):
            cmds.setAttr(snd + ".mute", 0)
    except:
        pass
    return snd

def set_front_ty_if_needed(file_base):
    """
    若文件名以 _Acelino 结尾，则把 front.translateY 设为 ACELINO_FRONT_Y；
    若属性被锁定则先解锁。若为引用导致不能改，跳过并提示。
    """
    if not file_base.endswith(SPECIAL_SUFFIX):
        return
    cam = "front"
    if not cmds.objExists(cam):
        cmds.warning(u"[Romeo] 未找到 front 相机，跳过设置 ty。")
        return
    # 引用节点可能无法改属性
    try:
        if cmds.referenceQuery(cam, isNodeReferenced=True):
            cmds.warning(u"[Romeo] front 是引用节点，无法改 ty。")
            return
    except:
        pass

    attr = cam + ".translateY"
    try:
        # 先解锁
        try:
            if cmds.getAttr(attr, lock=True):
                cmds.setAttr(attr, lock=False)
        except:
            pass
        # 设值（同时设为可关键帧，避免隐藏）
        cmds.setAttr(attr, ACELINO_FRONT_Y)
        try:
            cmds.setAttr(attr, k=True)
        except:
            pass
        print(u"[Romeo] 已设置 front.translateY = {}".format(ACELINO_FRONT_Y))
    except Exception as e:
        cmds.warning(u"[Romeo] 设置 front.translateY 失败: {}".format(e))

# ==== 主流程 ====
def main():
    if not os.path.isdir(OUT_DIR):
        try: os.makedirs(OUT_DIR)
        except: pass

    mb_list = [f for f in os.listdir(MB_DIR) if f.lower().endswith(".mb")]
    if not mb_list:
        print(u"[Romeo] 没有 .mb")
        return
    mb_list.sort(key=lambda s: s.lower(), reverse=SORT_DESC)

    for fname in mb_list:
        ev = ev_of(fname)
        if ev and ev in SKIP_EVENTS:
            print(u"[跳过-事件号] {} (ev{})".format(fname, ev))
            continue

        mb_path = os.path.join(MB_DIR, fname)
        base = os.path.splitext(fname)[0]
        out_mov = os.path.join(OUT_DIR, base + ".mov")

        if os.path.exists(out_mov):
            print(u"[跳过-已存在] {}".format(out_mov))
            continue

        print(u"[打开] {}".format(mb_path))
        try:
            cmds.file(mb_path, o=True, f=True, prompt=False)
        except Exception as e:
            print(u"[失败-打开] {} -> {}".format(fname, e))
            continue

        snd = bind_timeslider_first_audio()
        set_front_camera()

        # 特殊后缀处理：_Acelino -> front.ty = 163
        set_front_ty_if_needed(base)

        t_min = cmds.playbackOptions(q=True, minTime=True)
        t_max = cmds.playbackOptions(q=True, maxTime=True)

        print(u"[playblast] -> {}".format(out_mov))
        try:
            cmds.playblast(
                format='qt',
                filename=out_mov.replace("\\", "/"),
                forceOverwrite=True,
                sequenceTime=False,
                clearCache=True,
                viewer=False,
                showOrnaments=False,
                fp=0,
                percent=100,
                compression='H.264',
                quality=100,
                widthHeight=[WIDTH, HEIGHT],
                startTime=t_min,
                endTime=t_max,
                sound=snd,
                useTraxSounds=False
            )
        except Exception as e:
            print(u"[失败-playblast] {} -> {}".format(fname, e))

if __name__ == "__main__":
    main()
