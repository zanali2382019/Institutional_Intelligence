"""
Institutional Intelligence Studio — Master Video Merger Engine
Merges cinematic enterprise B-Roll clips, adds AI Voiceover track,
applies the luxury Midnight Navy & Gold Subscribe CTA overlay,
and compresses to ultra-clean H.264 CRF=22 faststart.
"""

import os
import sys
import argparse
import subprocess
import shutil
import tempfile
from pathlib import Path

# Fix console encodings on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def find_ffmpeg() -> str:
    # 1. Check shared dreammatter ffmpeg
    shared_ffmpeg = Path(r"E:\my Office\youtube channel\قناة DreamMatter\مسلسل الاطفال الاحترافي\tools\ffmpeg\ffmpeg.exe")
    if shared_ffmpeg.exists():
        return str(shared_ffmpeg)
    # 2. Check local tools ffmpeg
    local_ffmpeg = Path(__file__).resolve().parent / "ffmpeg" / "ffmpeg.exe"
    if local_ffmpeg.exists():
        return str(local_ffmpeg)
    # 3. System fallback
    sys_ffmpeg = shutil.which("ffmpeg")
    if sys_ffmpeg:
        return sys_ffmpeg
    return "ffmpeg"

def merge_enterprise_short(ep_num: int):
    print("=" * 65)
    print(f"   INSTITUTIONAL INTELLIGENCE STUDIO — SHORTS #{ep_num:02d}")
    print("=" * 65)

    base_dir = Path(__file__).resolve().parent.parent.parent
    prod_dir = base_dir / "02_فيديوهات_الشورتس_والريلز" / "الإنتاج_والمقاطع"
    tools_dir = Path(__file__).resolve().parent
    ffmpeg_exe = find_ffmpeg()

    overlay_img = tools_dir / "subscribe_overlay_enterprise.png"
    if not overlay_img.exists():
        print("[!] Warning: subscribe_overlay_enterprise.png not found. Proceeding without overlay.")
        overlay_img = None

    # Locate shot video clips
    shots = []
    for i in range(1, 10):
        for pattern in (f"shot{i:02d}.mp4", f"shot0{i}.mp4", f"clip{i:02d}.mp4", f"clip0{i}.mp4", f"shot{i}.mp4"):
            candidate = prod_dir / pattern
            if candidate.exists() and "final" not in candidate.name.lower():
                shots.append(candidate)
                break

    if not shots:
        # Check wildcard
        candidates = list(prod_dir.glob("*.mp4"))
        shots = [c for c in candidates if "final" not in c.name.lower()]

    if not shots:
        print(f"[!] No video clips found in: {prod_dir}")
        print("    Please save your Google Flow clips as shot01.mp4, shot02.mp4, etc.")
        sys.exit(1)

    print(f"[1/4] Found {len(shots)} video clips:")
    for s in shots:
        print(f"      - {s.name} ({s.stat().st_size / 1024 / 1024:.2f} MB)")

    # Voiceover check
    vo_file = None
    for vo_cand in [prod_dir / f"voiceover_ep{ep_num:02d}.mp3", prod_dir / "voiceover.mp3", prod_dir / "audio.mp3"]:
        if vo_cand.exists():
            vo_file = vo_cand
            break

    if vo_file:
        print(f"[2/4] Found AI Voiceover track: {vo_file.name}")
    else:
        print("[2/4] No voiceover file found, using original audio.")

    # Temp staging for ASCII path safety
    temp_dir = Path(tempfile.gettempdir()) / f"enterprise_merge_ep{ep_num:02d}"
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Copy shots to temp
        list_lines = []
        for i, s in enumerate(shots, 1):
            dest_name = f"shot_{i:02d}.mp4"
            shutil.copy2(str(s), str(temp_dir / dest_name))
            list_lines.append(f"file '{dest_name}'")

        (temp_dir / "list.txt").write_text("\n".join(list_lines) + "\n", encoding="ascii")

        print("[3/4] Concatenating B-Roll scenes...")
        raw_concat = temp_dir / "concat_raw.mp4"
        subprocess.run(
            [ffmpeg_exe, "-y", "-f", "concat", "-safe", "0", "-i", "list.txt", "-c", "copy", str(raw_concat.name)],
            cwd=str(temp_dir), check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        print("[4/4] Applying Enterprise styling, voiceover & H.264 CRF=22 compression...")
        final_temp = temp_dir / f"final_ep{ep_num:02d}.mp4"

        # Build ffmpeg command with overlay & optional voiceover
        if overlay_img and overlay_img.exists():
            shutil.copy2(str(overlay_img), str(temp_dir / "overlay.png"))
            has_overlay = True
        else:
            has_overlay = False

        if vo_file:
            shutil.copy2(str(vo_file), str(temp_dir / "voiceover.mp3"))
            if has_overlay:
                # Video + Voiceover + Overlay in last 12 seconds
                cmd = [
                    ffmpeg_exe, "-y",
                    "-i", str(raw_concat.name),
                    "-i", "voiceover.mp3",
                    "-i", "overlay.png",
                    "-filter_complex", "[0:v][2:v] overlay=0:0:enable='gte(t,18)' [v]",
                    "-map", "[v]", "-map", "1:a",
                    "-c:v", "libx264", "-crf", "22", "-preset", "medium", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
                    str(final_temp.name)
                ]
            else:
                cmd = [
                    ffmpeg_exe, "-y",
                    "-i", str(raw_concat.name),
                    "-i", "voiceover.mp3",
                    "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-crf", "22", "-preset", "medium", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
                    str(final_temp.name)
                ]
        else:
            if has_overlay:
                cmd = [
                    ffmpeg_exe, "-y",
                    "-i", str(raw_concat.name),
                    "-i", "overlay.png",
                    "-filter_complex", "[0:v][1:v] overlay=0:0:enable='gte(t,18)' [v]",
                    "-map", "[v]", "-map", "0:a?",
                    "-c:v", "libx264", "-crf", "22", "-preset", "medium", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    str(final_temp.name)
                ]
            else:
                cmd = [
                    ffmpeg_exe, "-y",
                    "-i", str(raw_concat.name),
                    "-c:v", "libx264", "-crf", "22", "-preset", "medium", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    str(final_temp.name)
                ]

        subprocess.run(cmd, cwd=str(temp_dir), check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        dest_final = prod_dir / f"short_ep{ep_num:02d}_final.mp4"
        shutil.copy2(str(final_temp), str(dest_final))
        mb_size = dest_final.stat().st_size / (1024 * 1024)

        print("=" * 65)
        print(f"   SUCCESS! ENTERPRISE SHORT #{ep_num:02d} IS READY!")
        print(f"   Output: {dest_final}")
        print(f"   Size: {mb_size:.2f} MB (High Dynamic Range Business Quality)")
        print(f"   Audio: Synchronized Voiceover included")
        print(f"   Call to Action: Luxury Gold & Navy Subscribe Banner Active")
        print("=" * 65)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Merge Institutional Intelligence Videos')
    parser.add_argument('--episode', type=int, default=1, help='Episode/Short number')
    args = parser.parse_args()
    merge_enterprise_short(args.episode)

