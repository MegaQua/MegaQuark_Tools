# -*- coding: utf-8 -*-
# 需求变更：不再用工厂创建 MHP，改为把“基准资产”复制到每个拍摄文件夹并重命名

import unreal
import re

# ===== 路径设置 =====
# 根目录（必须位于项目 Content 下）
SRC_ABS = r"D:\files\ue5flie\romeofacail2\Content\CaptureManager\Imports\Mono_Video_Ingest"
# 基准资产（一个已存在的 MetaHuman Performance 资产包路径，不是文件系统复制）
BASE_ASSET_ABS = r"D:\files\ue5flie\romeofacail2\Content\CaptureManager\Imports\Mono_Video_Ingest\SLV_ev1030_000_000_000_1\base"

def abs_to_game_path(abs_path):
    p = abs_path.replace("\\", "/")
    i = p.lower().find("/content/")
    if i == -1:
        raise ValueError("路径必须位于项目 Content 下: {}".format(abs_path))
    rel = p[i + len("/content/") :].strip("/")
    return "/Game/" + rel if rel else "/Game"

SRC_GAME       = abs_to_game_path(SRC_ABS)        # /Game/...
BASE_ASSET_GAME= abs_to_game_path(BASE_ASSET_ABS) # /Game/.../base

ed = unreal.EditorAssetLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

# ===== 工具 =====
def _to_str(n):  # Name/Path 安全转字符串
    return n.to_string() if hasattr(n, "to_string") else str(n)

def _cls(ad: unreal.AssetData):
    try:
        return ad.asset_class_path.asset_name
    except Exception:
        return str(ad.asset_class)

def is_capture_data(ad: unreal.AssetData) -> bool:
    return _cls(ad) in ("CaptureData", "FootageCaptureData", "MeshCaptureData")

def is_soundwave(ad: unreal.AssetData) -> bool:
    return _cls(ad) == "SoundWave"

# 从名称中提取 ev 段：CD_SLV_ev1030_000_000_000_1 → ev1030_000_000_000
_EV_PAT = re.compile(r"(ev\d+_\d+_\d+_\d+)(?=_(?:\d+)?$)", re.IGNORECASE)
def derive_ev_name(name) -> str:
    s = _to_str(name)
    m = _EV_PAT.search(s)
    return m.group(1) if m else s

def make_unique_name_in_folder(folder: str, base_name: str) -> str:
    if not ed.does_asset_exist(f"{folder}/{base_name}"):
        return base_name
    idx = 1
    while True:
        cand = f"{base_name}_{idx:02d}"
        if not ed.does_asset_exist(f"{folder}/{cand}"):
            return cand
        idx += 1

# ===== 复制基准 MHP 到目标文件夹并重命名 =====
def duplicate_mhp_from_base(folder: str, desired_name: str):
    """
    从 BASE_ASSET_GAME 复制到 folder 下，命名为 desired_name（如重名自动加后缀）。
    已存在同名则直接返回该路径。
    """
    if not ed.does_asset_exist(BASE_ASSET_GAME):
        unreal.log_error(f"[MHP] 基准资产不存在：{BASE_ASSET_GAME}")
        return None

    dest_name = make_unique_name_in_folder(folder, desired_name)
    dest_pkg  = f"{folder}/{dest_name}"

    if ed.does_asset_exist(dest_pkg):
        return dest_pkg

    ok = ed.duplicate_asset(BASE_ASSET_GAME, dest_pkg)
    if ok:
        unreal.log(f"[MHP] 复制完成: {BASE_ASSET_GAME} -> {dest_pkg}")
        return dest_pkg
    else:
        unreal.log_warning(f"[MHP] 复制失败: {BASE_ASSET_GAME} -> {dest_pkg}")
        return None

# ===== 重命名同文件夹内 SoundWave 资产 =====
def rename_soundwaves_in_folder(folder: str, base_name: str):
    paths = ed.list_assets(folder, recursive=False, include_folder=False)
    sound_ads = []
    for p in paths:
        ad = ed.find_asset_data(p)
        if ad.is_valid() and is_soundwave(ad):
            sound_ads.append(ad)
    if not sound_ads:
        return (0, 0)

    renamed, skipped = 0, 0
    for i, ad in enumerate(sound_ads):
        old_pkg = _to_str(ad.package_name)  # /Game/.../OldName
        base = base_name if i == 0 else f"{base_name}_{i:02d}"
        new_name = make_unique_name_in_folder(folder, base)

        curr = _to_str(ad.asset_name)
        if curr == new_name:
            skipped += 1
            continue

        new_pkg = f"{folder}/{new_name}"
        ok = ed.rename_asset(old_pkg, new_pkg)
        if ok:
            renamed += 1
            unreal.log(f"[WAV] 重命名: {old_pkg} -> {new_pkg}")
        else:
            skipped += 1
            unreal.log_warning(f"[WAV] 重命名失败: {old_pkg} -> {new_pkg}")

    return (renamed, skipped)

# ===== 主流程 =====
def run():
    if not ed.does_asset_exist(BASE_ASSET_GAME):
        unreal.log_error(f"基准资产未找到：{BASE_ASSET_GAME}")
        return

    all_assets = ed.list_assets(SRC_GAME, recursive=True, include_folder=False)
    if not all_assets:
        unreal.log_warning(f"未找到资产：{SRC_GAME}")
        return

    processed = 0
    total_wav_renamed = 0
    seen_folders = set()

    with unreal.ScopedSlowTask(len(all_assets), "Scanning capture folders") as task:
        task.make_dialog(True)

        for obj_path in all_assets:
            if task.should_cancel():
                break
            task.enter_progress_frame(1, obj_path)

            ad = ed.find_asset_data(obj_path)
            if not ad.is_valid() or not is_capture_data(ad):
                continue

            folder = _to_str(ad.package_path)  # /Game/.../<take folder>
            if folder in seen_folders:
                continue
            seen_folders.add(folder)

            base_name = derive_ev_name(ad.asset_name)

            # 1) 复制 MHP 基准资产到该文件夹并按 ev 名称命名
            duplicate_mhp_from_base(folder, base_name)

            # 2) 重命名同文件夹的 SoundWave
            renamed, _ = rename_soundwaves_in_folder(folder, base_name)
            total_wav_renamed += renamed
            processed += 1

    ed.save_directory(SRC_GAME, only_if_is_dirty=True)
    unreal.log(f"完成。处理拍摄条目：{processed}，重命名 SoundWave：{total_wav_renamed}。根：{SRC_GAME}")

run()
