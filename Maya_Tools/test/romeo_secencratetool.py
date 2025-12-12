# -*- coding: utf-8 -*-
# 在 Maya Script Editor 运行
import os
import re
import maya.cmds as cmds

# ===== 配置 =====
BASE = r"K:\romeo\10_Facial\facial_capture"       # 纯数字 cut 目录
SCENES_DIR = r"D:\files\mayafile\ROMEO\scenes"    # 角色_setup.mb 所在目录
FIN_DIR = r"D:\files\mayafile\ROMEO\scenes\fin"   # 成品保存目录
SKIP_CUTS = ["1030", "1050", "1051"]              # 默认跳过的 cut

# ===== 依赖 =====
try:
    import metahuman_api as mh_api
except Exception as e:
    raise RuntimeError(u"未找到 metahuman_api，请确认插件可用: {}".format(e))

# ===== 工具函数 =====
def is_digits(name):
    """是否纯数字"""
    return bool(re.fullmatch(r"\d+", name))

def import_same_name_wav(fbx_path, start_frame=0):
    """按 FBX 同名导入 wav"""
    if not fbx_path or not os.path.isfile(fbx_path):
        return (False, None)
    base, _ = os.path.splitext(fbx_path)
    wav_path = base + ".wav"
    if not os.path.exists(wav_path):
        wav_up = base + ".WAV"
        if os.path.exists(wav_up):
            wav_path = wav_up
        else:
            return (False, None)
    try:
        snd = cmds.sound(file=wav_path, offset=start_frame)
        return (True, snd)
    except Exception:
        return (False, None)

def save_mb(save_path):
    """保存为 .mb"""
    cmds.file(rename=save_path)
    cmds.file(save=True, type="mayaBinary")

# ===== 主流程 =====
def batch_process():
    if not os.path.isdir(FIN_DIR):
        os.makedirs(FIN_DIR)

    processed = 0
    skipped_exist = 0
    skipped_missing_scene = 0
    skipped_no_fbx = 0
    skipped_cut = 0
    failed = 0

    for cut_name in sorted(os.listdir(BASE)):
        cut_path = os.path.join(BASE, cut_name)
        if not (os.path.isdir(cut_path) and is_digits(cut_name)):
            continue
        if cut_name in SKIP_CUTS:
            print(u"[跳过CUT] {}".format(cut_name))
            skipped_cut += 1
            continue

        for role_name in sorted(os.listdir(cut_path)):
            role_dir = os.path.join(cut_path, role_name)
            if not os.path.isdir(role_dir):
                continue

            setup_mb = os.path.join(SCENES_DIR, f"{role_name}_setup.mb")
            if not os.path.isfile(setup_mb):
                print(u"[无场景] {}".format(setup_mb))
                skipped_missing_scene += 1
                continue

            fbx_list = sorted([f for f in os.listdir(role_dir) if f.lower().endswith(".fbx")])
            if not fbx_list:
                skipped_no_fbx += 1
                continue

            for fbx_file in fbx_list:
                base_name, _ = os.path.splitext(fbx_file)
                save_name = f"{base_name}_{role_name}.mb"
                save_path = os.path.join(FIN_DIR, save_name)

                # —— 在打开 setup.mb 之前先检查是否已存在 ——
                if os.path.exists(save_path):
                    print(u"[已存在，跳过] {}".format(save_path))
                    skipped_exist += 1
                    continue

                fbx_path = os.path.join(role_dir, fbx_file)

                try:
                    # 打开 setup
                    cmds.file(new=True, force=True)
                    cmds.file(setup_mb, o=True, f=True)

                    # Retarget
                    timeunit = cmds.currentUnit(q=True, time=True)
                    mh_api.retarget_metahuman_animation_sequence(
                        fbx_path=fbx_path,
                        namespace=':',
                        timeunit=timeunit
                    )

                    # WAV
                    import_same_name_wav(fbx_path, start_frame=0)

                    # 保存
                    save_mb(save_path)
                    processed += 1
                    print(u"[OK] {} -> {}".format(fbx_path, save_path))

                except Exception as e:
                    failed += 1
                    print(u"[失败] {} : {}".format(fbx_path, e))

    print(u"—— 批量完成 ——")
    print(u"成功: {}".format(processed))
    print(u"已有跳过: {}".format(skipped_exist))
    print(u"无场景跳过: {}".format(skipped_missing_scene))
    print(u"无FBX跳过: {}".format(skipped_no_fbx))
    print(u"CUT跳过: {}".format(skipped_cut))
    print(u"失败: {}".format(failed))

# ===== 执行 =====
batch_process()
