# -*- coding: utf-8 -*-
# 遍历 Mono_Video_Ingest 子文件夹：若存在 MetaHuman Performance，
# 读取其“Footage Capture Data”槽；为空则把同目录的 CaptureData 填入。

import unreal
import re

SRC_ABS = r"D:\files\ue5flie\romeofacail2\Content\CaptureManager\Imports\Mono_Video_Ingest"

# ---------- 工具 ----------
def abs_to_game_path(abs_path: str) -> str:
    p = abs_path.replace("\\", "/")
    i = p.lower().find("/content/")
    if i == -1:
        raise ValueError("路径必须位于项目 Content 下: {}".format(abs_path))
    rel = p[i + len("/content/") :].strip("/")
    return "/Game/" + rel if rel else "/Game"

def _to_str(n):
    return n.to_string() if hasattr(n, "to_string") else str(n)

def _cls(ad: unreal.AssetData) -> str:
    try:
        return ad.asset_class_path.asset_name
    except Exception:
        return str(ad.asset_class)

def asset_obj_path(ad: unreal.AssetData) -> str:
    """构造对象路径用于日志：/Game/.../Name.Name"""
    return f"{_to_str(ad.package_name)}.{_to_str(ad.asset_name)}"

def is_mhp(ad: unreal.AssetData) -> bool:
    return _cls(ad) in ("MetaHumanPerformance", "MetaHumanPerformanceAsset")

def is_capture_data(ad: unreal.AssetData) -> bool:
    return _cls(ad) in ("FootageCaptureData", "CaptureData", "MeshCaptureData")

def pick_best_capture_data_in_folder(folder: str):
    ed = unreal.EditorAssetLibrary
    paths = ed.list_assets(folder, recursive=False, include_folder=False)
    cands = []
    for p in paths:
        ad = ed.find_asset_data(p)
        if ad.is_valid() and is_capture_data(ad):
            cands.append(ad)
    if not cands:
        return None
    pri = {"FootageCaptureData": 0, "CaptureData": 1, "MeshCaptureData": 2}
    cands.sort(key=lambda ad: pri.get(_cls(ad), 9))
    return cands[0]

_EV_PAT = re.compile(r"(ev\d+_\d+_\d+_\d+)(?=_(?:\d+)?$)", re.IGNORECASE)
def derive_ev_name(name) -> str:
    s = _to_str(name)
    m = _EV_PAT.search(s)
    return m.group(1) if m else s

_PROP_KEYS = ["FootageCaptureData", "footage_capture_data", "CaptureData", "capture_data"]

def get_first_existing_prop(uobj, keys):
    for k in keys:
        try:
            uobj.get_editor_property(k)
            return k
        except Exception:
            pass
    return None

def slot_is_empty(uobj, prop_name: str) -> bool:
    val = uobj.get_editor_property(prop_name)
    if val is None:
        return True
    try:
        return len(val) == 0
    except Exception:
        return False

def set_slot_value(uobj, prop_name: str, obj_to_set) -> bool:
    val = uobj.get_editor_property(prop_name)
    # 数组属性
    try:
        if hasattr(val, "append"):
            if len(val) == 0:
                val.append(obj_to_set)
                uobj.set_editor_property(prop_name, val)
                return True
            else:
                # 已有值则不覆盖
                return False
    except Exception:
        pass
    # 单引用属性
    try:
        uobj.set_editor_property(prop_name, obj_to_set)
        return True
    except Exception as e:
        unreal.log_warning(f"写属性失败 {prop_name}: {e}")
        return False

# ---------- 主逻辑 ----------
def run():
    ed = unreal.EditorAssetLibrary
    SRC_GAME = abs_to_game_path(SRC_ABS)

    all_assets = ed.list_assets(SRC_GAME, recursive=True, include_folder=False)
    if not all_assets:
        unreal.log_warning(f"未找到资产：{SRC_GAME}")
        return

    seen_folders = set()
    checked_mhp = 0
    filled = 0
    skipped = 0
    missing_cd = 0

    with unreal.ScopedSlowTask(len(all_assets), "Scanning MHP folders") as task:
        task.make_dialog(True)

        for obj_path in all_assets:
            if task.should_cancel():
                break
            task.enter_progress_frame(1, obj_path)

            ad = ed.find_asset_data(obj_path)
            if not ad.is_valid() or not is_mhp(ad):
                continue

            folder = _to_str(ad.package_path)  # /Game/.../<take folder>
            if folder in seen_folders:
                continue
            seen_folders.add(folder)
            checked_mhp += 1

            # 加载 MHP 对象（用 get_asset()，避免 object_path_string）
            mhp_obj = ad.get_asset()
            if not mhp_obj:
                unreal.log_warning(f"[MHP] 加载失败: {asset_obj_path(ad)}")
                skipped += 1
                continue

            prop_key = get_first_existing_prop(mhp_obj, _PROP_KEYS)
            if not prop_key:
                unreal.log_warning(f"[MHP] 未发现 Footage Capture Data 槽位属性: {asset_obj_path(ad)}")
                skipped += 1
                continue

            if not slot_is_empty(mhp_obj, prop_key):
                unreal.log(f"[MHP] 已有 CaptureData，跳过: {asset_obj_path(ad)}")
                skipped += 1
                continue

            # 找同目录下的 CaptureData
            cd_ad = pick_best_capture_data_in_folder(folder)
            if not cd_ad:
                unreal.log_warning(f"[MHP] 该目录无 CaptureData：{folder}")
                missing_cd += 1
                continue

            cd_obj = cd_ad.get_asset()
            if not cd_obj:
                unreal.log_warning(f"[MHP] CaptureData 加载失败：{asset_obj_path(cd_ad)}")
                missing_cd += 1
                continue

            if set_slot_value(mhp_obj, prop_key, cd_obj):
                # 保存该资产（传包路径）
                ed.save_asset(_to_str(ad.package_name), only_if_is_dirty=True)
                unreal.log(f"[MHP] 已填充 Footage Capture Data: {asset_obj_path(ad)} <- {asset_obj_path(cd_ad)}")
                filled += 1
            else:
                skipped += 1

    ed.save_directory(SRC_GAME, only_if_is_dirty=True)
    unreal.log(f"完成。检查 MHP：{checked_mhp}，填充：{filled}，跳过：{skipped}，未找到 CaptureData：{missing_cd}。根：{SRC_GAME}")

run()
