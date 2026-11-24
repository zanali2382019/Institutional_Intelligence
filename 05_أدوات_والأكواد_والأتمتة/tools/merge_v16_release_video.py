"""
ITQAN Enterprise Intelligence Studio — Master Video Merger for ERPNext v16.60
Merges cinematic 16:9 widescreen footage with the Master Voiceover (voiceover_v16_master.mp3),
prepends the high-CTR thumbnail (ITQAN_V16_THUMBNAIL_FINAL.png) as a 2.5s Cold-Open Title Card,
burns synchronized bilingual subtitles and dual-corner permanent watermarks,
and produces ITQAN_V16_RELEASE_MASTERCLASS_FINAL.mp4.
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

def merge_v16_video():
    print("=" * 70)
    print("   ITQAN STUDIO — ERPNEXT v16.60 MASTERCLASS VIDEO MERGER")
    print("   إتقان — الذكاء المؤسسي")
    print("   الجيل الجديد من ERPNext (تحديث v16.60): ثورة الذكاء الاصطناعي المؤسسي")
    print("=" * 70)

    base_dir = Path(__file__).resolve().parent.parent.parent
    prod_dir = base_dir / "03_الفيديوهات_الطويلة_والشروحات" / "حلقات_الموسم_الأول" / "حلقة_تحديثات_ERPNext_v16_60"
    shots_dir = base_dir / "03_الفيديوهات_الطويلة_والشروحات" / "الإنتاج_والمقاطع" / "ep02_shots"
    ffmpeg_exe = find_ffmpeg()

    vo_file = prod_dir / "voiceover_v16_chirp3_charon_master.mp3"
    thumb_file = prod_dir / "ITQAN_V16_THUMBNAIL_FINAL.png"
    sub_file = prod_dir / "ep_v16_bilingual_subtitles.ass"

    for req in (vo_file, thumb_file, sub_file):
        if not req.exists():
            print(f"[!] Missing required asset: {req}")
            sys.exit(1)

    # Narrative-matched 16:9 widescreen timeline calibrated to 194.04s Charon master voiceover
    editorial_timeline = [
        ("12.mp4", 1.25, 9.50),   # 00:00 - 00:09.5 Modern Executive Boardroom
        ("1.mp4",  1.25, 9.50),   # 00:09.5 - 00:19.0 CTO walking down hallway
        ("5.mp4",  1.15, 9.00),   # 00:19.0 - 00:28.0 ITQAN Brand & Shield Reveal
        ("10.mp4", 1.35, 10.00),  # 00:28.0 - 00:38.0 Software evolution & Frappe Flow
        ("6.mp4",  1.35, 10.00),  # 00:38.0 - 00:48.0 AI Query & Analytics curves
        ("4.mp4",  1.35, 10.00),  # 00:48.0 - 00:58.0 Role-based Security Architecture
        ("10.mp4", 1.25, 9.50),   # 00:58.0 - 01:07.5 Frappe Studio No-Code Builder
        ("9.mp4",  1.25, 9.50),   # 01:07.5 - 01:17.0 Interactive App Building
        ("12.mp4", 1.35, 10.00),  # 01:17.0 - 01:27.0 Insights Command Center
        ("2.mp4",  1.25, 9.50),   # 01:27.0 - 01:36.5 Multi-dimensional Metrics & Drill-down
        ("11.mp4", 1.35, 10.00),  # 01:36.5 - 01:46.5 Projects & Construction Cockpit
        ("3.mp4",  1.25, 9.50),   # 01:46.5 - 01:56.0 Cost vs. Billing Real-time Audit
        ("7.mp4",  1.35, 9.50),   # 01:56.0 - 02:05.5 Document OCR & Smart Invoice Ingestion
        ("9.mp4",  1.25, 9.50),   # 02:05.5 - 02:15.0 Auto-form Side-by-side Fill
        ("4.mp4",  1.25, 9.50),   # 02:15.0 - 02:24.5 Cheque Management & Day Book
        ("6.mp4",  1.25, 9.50),   # 02:24.5 - 02:34.0 Running Cash Flow Governance
        ("1.mp4",  1.25, 10.00),  # 02:34.0 - 02:44.0 End of Legacy Monopolies
        ("10.mp4", 1.25, 10.00),  # 02:44.0 - 02:54.0 Open-source Digital Sovereignty
        ("12.mp4", 1.25, 10.00),  # 02:54.0 - 03:04.0 ITQAN Enterprise Advisory
        ("5.mp4",  1.15, 10.04),  # 03:04.0 - 03:14.04 Subscribe to ITQAN! Total = 194.04s
    ]

    temp_dir = Path(tempfile.gettempdir()) / "itqan_v16_merge"
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        intro_sec = 2.50
        intro_clip = temp_dir / "intro_thumb.mp4"
        cmd_thumb = [
            ffmpeg_exe, "-y",
            "-loop", "1", "-t", str(intro_sec),
            "-i", str(thumb_file.as_posix()),
            "-vf", "scale=1280:720,fps=24,format=yuv420p",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-an",
            str(intro_clip.as_posix())
        ]
        subprocess.run(cmd_thumb, cwd=str(temp_dir), check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[1/5] Prepared Cold-Open Cover Card: {intro_sec}s")

        list_lines = ["file 'intro_thumb.mp4'"]
        for idx, (fname, pts_mult, out_dur) in enumerate(editorial_timeline, 1):
            src = shots_dir / fname
            if not src.exists():
                print(f"[!] Missing shot file: {src}")
                sys.exit(1)
            seg_name = f"seg_{idx:02d}.mp4"
            seg_path = temp_dir / seg_name
            vf_str = f"setpts={pts_mult}*PTS,scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,fps=24,format=yuv420p"
            cmd_seg = [
                ffmpeg_exe, "-y",
                "-i", str(src.as_posix()),
                "-vf", vf_str,
                "-t", str(out_dur),
                "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-an",
                str(seg_path.as_posix())
            ]
            subprocess.run(cmd_seg, cwd=str(temp_dir), check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            list_lines.append(f"file '{seg_name}'")

        print(f"[2/5] Prepared {len(editorial_timeline)} narrative-synced video segments (1280x720 HD).")

        concat_list_file = temp_dir / "concat_list.txt"
        concat_list_file.write_text("\n".join(list_lines), encoding="utf-8")

        temp_audio = temp_dir / "master_audio.mp3"
        shutil.copy2(str(vo_file), str(temp_audio))

        # Shift ASS subtitles by 2.50s
        raw_sub = sub_file.read_text(encoding="utf-8")
        shifted_lines = []
        for line in raw_sub.splitlines():
            if line.startswith("Dialogue:"):
                parts = line.split(",", 9)
                parts[1] = shift_ass_time(parts[1].strip(), intro_sec)
                parts[2] = shift_ass_time(parts[2].strip(), intro_sec)
                shifted_lines.append(",".join(parts))
            else:
                shifted_lines.append(line)

        temp_sub = temp_dir / "subtitles.ass"
        temp_sub.write_text("\n".join(shifted_lines), encoding="utf-8-sig")
        print(f"[3/5] Shifted bilingual subtitles & watermarks by +{intro_sec}s.")

        temp_output = temp_dir / "final_v16.mp4"
        final_dest = prod_dir / "ITQAN_V16_RELEASE_MASTERCLASS_FINAL.mp4"

        print(f"[4/5] Rendering ERPNext v16.60 Masterclass MP4 with FFmpeg...")
        cmd_merge = [
            ffmpeg_exe, "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_list_file.as_posix()),
            "-i", str(temp_audio.as_posix()),
            "-filter_complex",
            "[0:v]ass=subtitles.ass,format=yuv420p[v];"
            f"[1:a]adelay={int(intro_sec * 1000)}|{int(intro_sec * 1000)}[a]",
            "-map", "[v]",
            "-map", "[a]",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "24",
            "-c:a", "aac",
            "-strict", "-2",
            "-b:a", "128k",
            "-shortest",
            "-movflags", "+faststart",
            str(temp_output.as_posix())
        ]

        res = subprocess.run(cmd_merge, cwd=str(temp_dir), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            print("\n[!] FFmpeg Merge Error:")
            print(res.stderr.decode("utf-8", errors="replace")[-1500:])
            sys.exit(1)

        shutil.copy2(str(temp_output), str(final_dest))
        print(f"\n[5/5] SUCCESS! Master v16.60 Video rendered completely:")
        print(f"      -> {final_dest}")
        print(f"      -> Size: {final_dest.stat().st_size / 1024 / 1024:.2f} MB")
        print("=" * 70)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    merge_v16_video()

