# -*- coding: utf-8 -*-
# 批量转码：MOV(MJPEG/gray等) -> MP4(H.264/yuv420p)，保持灰度外观
# 递归 ROOT，目标生成到 DST_ROOT，目录结构镜像
import os, sys, json, subprocess, shlex
from pathlib import Path

FFMPEG  = r"S:\Public\qiu_yi\ffmpeg-2024-04-07-git-2d33d6bfcc-full_build\bin\ffmpeg.exe"
FFPROBE = r"S:\Public\qiu_yi\ffmpeg-2024-04-07-git-2d33d6bfcc-full_build\bin\ffprobe.exe"

ROOT     = Path(r"D:\Project\Awakening\20251025_depth_test\60FPS Technoprops Sample")
DST_ROOT = Path(r"D:\Project\Awakening\data\JC")

# 可选：用 NVENC（True 开启，机器需支持）
USE_NVENC = False

def run(cmd:list, check=True):
    # Windows 路径含空格，建议 list 传参
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check)

def ffprobe_json(src: Path):
    cmd = [
        FFPROBE, "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", str(src)
    ]
    p = run(cmd)
    return json.loads(p.stdout.decode("utf-8", errors="ignore"))

def get_timecode(meta:dict)->str:
    # 优先 format.tags.timecode，其次各 stream.tags.timecode
    fmt = meta.get("format", {})
    tags = fmt.get("tags", {}) or {}
    tc = tags.get("timecode")
    if tc: return tc
    for s in meta.get("streams", []):
        t = (s.get("tags") or {}).get("timecode")
        if t: return t
    return ""

def need_transcode(src: Path, dst: Path)->bool:
    if not dst.exists(): return True
    return src.stat().st_mtime > dst.stat().st_mtime  # 源更新才重转

def build_dst_path(src: Path)->Path:
    rel = src.relative_to(ROOT)
    dst = DST_ROOT / rel
    dst = dst.with_suffix(".mp4")
    dst.parent.mkdir(parents=True, exist_ok=True)
    return dst

def transcode_one(src: Path):
    meta = ffprobe_json(src)
    tc   = get_timecode(meta)  # 可能为空

    dst = build_dst_path(src)
    if not need_transcode(src, dst):
        print(f"[SKIP] {dst} 已最新")
        return

    # 为保证解码/播放兼容与尺寸偶数：scale 到偶数，再转 yuv420p；eq=saturation=0 强制灰度外观
    vf = "scale=ceil(iw/2)*2:ceil(ih/2)*2,format=yuv420p,eq=saturation=0"

    if USE_NVENC:
        vcodec = ["-c:v", "h264_nvenc", "-rc", "vbr", "-cq", "18", "-b:v", "0", "-preset", "p5"]
    else:
        vcodec = ["-c:v", "libx264", "-crf", "18", "-preset", "slow", "-profile:v", "high", "-level", "4.2"]

    # 只取首个视频流；保留基础元数据；写 faststart；固定 GOP 便于编辑回放
    cmd = [
        FFMPEG, "-y",
        "-i", str(src),
        "-map", "0:v:0",
        "-vf", vf,
        *vcodec,
        "-pix_fmt", "yuv420p",
        "-g", "60", "-keyint_min", "60", "-sc_threshold", "0",
        "-movflags", "+faststart",
        "-map_metadata", "0",
        "-an",  # 源若无音频，避免空轨
    ]

    if tc:
        cmd += ["-timecode", tc]

    cmd += [str(dst)]

    print("[CMD]", " ".join(shlex.quote(x) for x in cmd))
    p = run(cmd, check=False)
    if p.returncode != 0:
        sys.stderr.write(p.stderr.decode("utf-8", errors="ignore"))
        raise RuntimeError(f"转码失败: {src}")
    print(f"[OK ] {dst}")

def main():
    # 递归 .mov / .MOV
    movs = list(ROOT.rglob("*.mov")) + list(ROOT.rglob("*.MOV"))
    if not movs:
        print("未找到 mov")
        return
    for i, src in enumerate(sorted(movs), 1):
        try:
            print(f"[{i}/{len(movs)}] {src}")
            transcode_one(src)
        except Exception as e:
            print(f"[ERR] {src} -> {e}")

if __name__ == "__main__":
    main()
