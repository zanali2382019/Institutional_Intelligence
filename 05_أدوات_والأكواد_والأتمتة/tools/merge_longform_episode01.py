"""
ITQAN Enterprise Intelligence Studio — Master Long-Form Video Merger
Merges 24 cinematic enterprise 16:9 shots with the Master AI Voiceover (voiceover_ep01_master.mp3),
integrates the official thumbnail as a 2.5s Cold-Open Title Card, burns synchronized bilingual subtitles,
embeds dual-corner permanent watermarks, and attaches cover artwork metadata into the final 720p HD MP4.
"""

import os
import sys
import shutil
import tempfile
import subprocess
from pathlib import Path

# Fix console encodings on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def find_ffmpeg() -> str:
    shared_ffmpeg = Path(r"E:\my Office\youtube channel\قناة DreamMatter\مسلسل الاطفال الاحترافي\tools\ffmpeg\ffmpeg.exe")
    if shared_ffmpeg.exists():
        return str(shared_ffmpeg)
    local_ffmpeg = Path(__file__).resolve().parent / "ffmpeg" / "ffmpeg.exe"
    if local_ffmpeg.exists():
        return str(local_ffmpeg)
    sys_ffmpeg = shutil.which("ffmpeg")
    if sys_ffmpeg:
        return sys_ffmpeg
    return "ffmpeg"

def shift_ass_time(time_str: str, shift_sec: float) -> str:
    parts = time_str.split(':')
    h = int(parts[0])
    m = int(parts[1])
    s, cs = parts[2].split('.')
    total_sec = h * 3600 + m * 60 + int(s) + int(cs) / 100.0
    total_sec += shift_sec
    if total_sec < 0:
        total_sec = 0.0
    new_h = int(total_sec // 3600)
    total_sec %= 3600
    new_m = int(total_sec // 60)
    total_sec %= 60
    new_s = int(total_sec)
    new_cs = int(round((total_sec - new_s) * 100))
    return f"{new_h}:{new_m:02d}:{new_s:02d}.{new_cs:02d}"

def merge_longform_episode01():
    print("=" * 70)
    print("   ITQAN STUDIO — LONG-FORM EPISODE 01 MASTER VIDEO MERGER")
    print("   إتقان — الذكاء المؤسسي")
    print("   كارثة المستخلصات: كيف ابتلع بند خرسانة واحد 12 مليون دولار؟")
    print("=" * 70)

    base_dir = Path(__file__).resolve().parent.parent.parent
    prod_dir = base_dir / "03_الفيديوهات_الطويلة_والشروحات" / "الإنتاج_والمقاطع"
    ffmpeg_exe = find_ffmpeg()

    print(f"\n[*] Using FFmpeg binary: {ffmpeg_exe}")
    print(f"[*] Production directory: {prod_dir}")

    # Look for shots
    import re
    shots = []
    for i in range(1, 25):
        found = False
        patterns = (
            f"{i}.mp4", f"{i:02d}.mp4", f"shot{i:02d}.mp4", f"shot0{i}.mp4",
            f"shot{i}.mp4", f"shot_{i:02d}.mp4", f"shot_{i}.mp4"
        )
        for pattern in patterns:
            candidate = prod_dir / pattern
            if candidate.exists() and "final" not in candidate.name.lower():
                shots.append(candidate)
                found = True
                break

    if not shots:
        all_mp4s = [f for f in prod_dir.glob("*.mp4") if "final" not in f.name.lower()]
        def extract_num(p):
            m = re.search(r'(\d+)', p.stem)
            return int(m.group(1)) if m else 999
        candidates = sorted(all_mp4s, key=extract_num)
        shots = [c for c in candidates if extract_num(c) <= 24]

    if not shots:
        print(f"\n[!] No video clips found in: {prod_dir}")
        sys.exit(1)

    print(f"\n[1/6] Found {len(shots)} video clips.")

    # Voiceover check
    vo_file = prod_dir / "voiceover_ep01_master.mp3"
    if not vo_file.exists():
        vo_cand = list(prod_dir.glob("*.mp3"))
        if vo_cand:
            vo_file = vo_cand[0]

    if not vo_file or not vo_file.exists():
        print(f"\n[!] Voiceover file not found in: {prod_dir}")
        sys.exit(1)

    print(f"[2/6] Master AI Voiceover: {vo_file.name} ({vo_file.stat().st_size / 1024 / 1024:.2f} MB)")

    # Thumbnail check
    thumb_file = prod_dir / "ITQAN_EP01_THUMBNAIL_FINAL.png"
    if not thumb_file.exists():
        print(f"\n[!] Thumbnail file not found: {thumb_file}")
        sys.exit(1)

    print(f"[3/6] Official Cover Thumbnail: {thumb_file.name} ({thumb_file.stat().st_size / 1024:.1f} KB)")

    # Subtitles check
    sub_file = prod_dir / "ep01_bilingual_subtitles.ass"
    if not sub_file.exists():
        print(f"\n[!] Subtitle file not found: {sub_file}")
        sys.exit(1)

    print(f"[4/6] Bilingual Subtitles & Dual Watermarks: {sub_file.name}")

    # Temp staging
    temp_dir = Path(tempfile.gettempdir()) / "itqan_longform_ep01_merge"
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 1. Generate concat list with relative names
        list_lines = []
        for i, s in enumerate(shots, 1):
            dest_name = f"shot_{i:02d}.mp4"
            dest_path = temp_dir / dest_name
            shutil.copy2(str(s), str(dest_path))
            list_lines.append(f"file '{dest_name}'")

        concat_list_file = temp_dir / "concat_list.txt"
        concat_list_file.write_text("\n".join(list_lines), encoding="utf-8")

        temp_audio = temp_dir / "master_audio.mp3"
        shutil.copy2(str(vo_file), str(temp_audio))

        temp_thumb = temp_dir / "cover_thumb.png"
        shutil.copy2(str(thumb_file), str(temp_thumb))

        # 2. Shift subtitles by 2.50s for the cold-open title card
        intro_sec = 2.50
        raw_sub = sub_file.read_text(encoding="utf-8")
        shifted_lines = []
        for line in raw_sub.splitlines():
            if line.startswith("Dialogue:"):
                parts = line.split(",", 9)
                style = parts[3].strip()
                start = parts[1].strip()
                end = parts[2].strip()
                if "Watermark" in style:
                    # Watermarks start when main video starts (after thumbnail title card)
                    parts[1] = shift_ass_time(start, intro_sec)
                    parts[2] = shift_ass_time(end, intro_sec)
                else:
                    parts[1] = shift_ass_time(start, intro_sec)
                    parts[2] = shift_ass_time(end, intro_sec)
                shifted_lines.append(",".join(parts))
            else:
                shifted_lines.append(line)

        temp_sub = temp_dir / "subtitles.ass"
        temp_sub.write_text("\n".join(shifted_lines), encoding="utf-8-sig")

        temp_output = temp_dir / "final_output.mp4"
        final_dest = prod_dir / "ITQAN_EP01_CARTHET_AL_MOSTAKHLESAAT_FINAL.mp4"

        print(f"\n[5/6] Rendering Master Video with FFmpeg...")
        print(f"      - Cold-Open Title Card: {intro_sec}s full-screen Cover Thumbnail")
        print("      - Resolution: 720p HD (1280x720) 16:9 Cinematic Ambient Fill")
        print("      - Watermarks: Dual-corner 'الذكاء المؤسسي' (Right) & 'Institutional Intelligence' (Left)")
        print("      - Subtitles: Synchronized bilingual Arabic (gold) & English (white)")
        print(f"      - Audio: Delayed by {int(intro_sec * 1000)}ms to align perfectly with narration")
        print("      - Compression: Ultra-compact H.264 CRF=25, AAC 128k audio")

        cmd = [
            ffmpeg_exe, "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_list_file.as_posix()),
            "-loop", "1", "-t", str(intro_sec), "-i", str(temp_thumb.as_posix()),
            "-i", str(temp_audio.as_posix()),
            "-filter_complex",
            # 1. Title card intro stream
            "[1:v]scale=1280:720,fps=24[intro];"
            # 2. Main video ambient broadcast fill
            "[0:v]scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,boxblur=20:5,eq=brightness=-0.2[bg];"
            "[0:v]scale=-1:720[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2,fps=24[main_v];"
            # 3. Concatenate Intro Title Card + Main Video
            "[intro][main_v]concat=n=2:v=1:a=0[v_joined];"
            # 4. Burn ASS subtitles (bilingual text + watermarks)
            "[v_joined]ass=subtitles.ass,format=yuv420p[v];"
            # 5. Delay audio by intro_sec
            f"[2:a]adelay={int(intro_sec * 1000)}|{int(intro_sec * 1000)}[a]",
            "-map", "[v]",
            "-map", "[a]",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "25",
            "-c:a", "aac",
            "-strict", "-2",
            "-b:a", "128k",
            "-shortest",
            "-movflags", "+faststart",
            str(temp_output.as_posix())
        ]

        result = subprocess.run(cmd, cwd=str(temp_dir), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print("\n[!] FFmpeg Render Error:")
            print(result.stderr.decode("utf-8", errors="replace")[-1500:])
            sys.exit(1)

        # Move to production folder
        shutil.copy2(str(temp_output), str(final_dest))
        print(f"\n[6/6] SUCCESS! Master Episode 01 with embedded Title Card rendered:")
        print(f"      -> {final_dest}")
        print(f"      -> Size: {final_dest.stat().st_size / 1024 / 1024:.2f} MB")
        print("=" * 70)
        print("   الحلقة الأولى مدمجة الآن مع الغلاف السينمائي ككادر افتتاحي رسمي!")
        print("=" * 70)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    merge_longform_episode01()
