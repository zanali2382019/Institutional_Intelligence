"""
ITQAN Enterprise Intelligence Studio — Master Long-Form Video Merger (Episode 02)
Builds a narrative-synced 16:9 HD 720p documentary timeline from the 12 native widescreen shots,
prepends the high-CTR thumbnail (ITQAN_EP02_THUMBNAIL_FINAL.png) as a 2.5s Cold-Open Title Card,
burns synchronized bilingual subtitles + dual-corner permanent watermarks,
and outputs ITQAN_EP02_JEHEEM_AL_EXCEL_FINAL.mp4.
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

def merge_longform_episode02():
    print("=" * 70)
    print("   ITQAN STUDIO — LONG-FORM EPISODE 02 MASTER VIDEO MERGER")
    print("   إتقان — الذكاء المؤسسي")
    print("   جحيم الإكسل: لماذا يخدعك تقرير الأرباح الشهري وأنت تخسر ملايين؟")
    print("=" * 70)

    base_dir = Path(__file__).resolve().parent.parent.parent
    prod_dir = base_dir / "03_الفيديوهات_الطويلة_والشروحات" / "الإنتاج_والمقاطع"
    shots_dir = prod_dir / "ep02_shots"
    ffmpeg_exe = find_ffmpeg()

    vo_file = prod_dir / "voiceover_ep02_master.mp3"
    thumb_file = prod_dir / "ITQAN_EP02_THUMBNAIL_FINAL.png"
    sub_file = prod_dir / "ep02_bilingual_subtitles.ass"

    for req in (vo_file, thumb_file, sub_file):
        if not req.exists():
            print(f"[!] Missing required asset: {req}")
            sys.exit(1)

    # Narrative-matched editorial timeline: (filename, speed_factor_pts, trim_duration_after_pts)
    # 1.25 PTS means 8s -> 10s smooth cinematic slow-motion
    editorial_timeline = [
        ("1.mp4",  1.25, 10.0),   # 00:00 - 00:10 CFO walking down hallway
        ("2.mp4",  1.25, 10.0),   # 00:10 - 00:20 +$500,000 report & board celebration
        ("3.mp4",  1.45, 11.6),   # 00:20 - 00:31.6 Unpaid invoices vs idle site
        ("4.mp4",  1.45, 11.6),   # 00:31.6 - 00:43.2 $0.00 Bank balance & Excel error
        ("9.mp4",  1.00, 3.5),    # 00:43.2 - 00:46.7 "Excel was lying to you!"
        ("5.mp4",  1.15, 9.2),    # 00:46.7 - 00:55.9 ITQAN Shield Hologram Brand Intro
        ("6.mp4",  1.35, 10.8),   # 00:55.9 - 01:06.7 Book Profit vs Actual Cash Flow
        ("7.mp4",  1.45, 11.6),   # 01:06.7 - 01:18.3 Payment certificate & 10% retention trap
        ("2.mp4",  1.00, 7.8),    # 01:18.3 - 01:26.1 Paper profit contrast
        ("8.mp4",  1.45, 11.6),   # 01:26.1 - 01:37.7 Rusting rebar & hardened cement
        ("3.mp4",  1.00, 4.2),    # 01:37.7 - 01:41.9 Annual audit day crisis
        ("9.mp4",  1.45, 11.6),   # 01:41.9 - 01:53.5 Harvard 88% spreadsheet errors
        ("4.mp4",  1.00, 5.8),    # 01:53.5 - 01:59.3 Silent millions lost
        ("10.mp4", 1.45, 11.6),   # 01:59.3 - 02:10.9 Padlock dissolving into ERPNext GL
        ("5.mp4",  1.00, 5.0),    # 02:10.9 - 02:15.9 ITQAN Institutional pulse
        ("11.mp4", 1.45, 11.6),   # 02:15.9 - 02:27.5 Site QR scan -> Automated Ledger
        ("10.mp4", 1.00, 6.5),    # 02:27.5 - 02:34.0 Live Cost Centers view
        ("12.mp4", 1.45, 11.6),   # 02:34.0 - 02:45.6 90-day Cash Flow Forecast radar
        ("6.mp4",  1.00, 4.0),    # 02:45.6 - 02:49.6 Predictive liquidity warning
        ("12.mp4", 1.00, 8.0),    # 02:49.6 - 02:57.6 "Don't run future empires on old tools"
        ("11.mp4", 1.00, 7.0),    # 02:57.6 - 03:04.6 Free ERPNext Chart of Accounts link
        ("5.mp4",  1.15, 9.2),    # 03:04.6 - 03:13.8 Subscribe to ITQAN!
    ]

    temp_dir = Path(tempfile.gettempdir()) / "itqan_longform_ep02_merge"
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        intro_sec = 2.50
        # 1. Prepare 2.5s intro clip from thumbnail
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

        # 2. Shift ASS timestamps by 2.50s
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

        temp_output = temp_dir / "final_ep02.mp4"
        final_dest = prod_dir / "ITQAN_EP02_JEHEEM_AL_EXCEL_FINAL.mp4"

        print(f"[4/5] Rendering Master Episode 02 MP4 with FFmpeg...")
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
        print(f"\n[5/5] SUCCESS! Master Episode 02 rendered completely:")
        print(f"      -> {final_dest}")
        print(f"      -> Size: {final_dest.stat().st_size / 1024 / 1024:.2f} MB")
        print("=" * 70)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    merge_longform_episode02()
