"""
ITQAN Enterprise Intelligence Studio — Master YouTube Short 01 Producer
Produces vertical 9:16 viral YouTube Short with embedded cover title card:
"شيك بـ 12 مليون دولار ارتد دون رصيد بسبب هذا الخطأ!"
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

def produce_short01():
    print("=" * 70)
    print("   ITQAN STUDIO — YOUTUBE SHORT 01 VIRAL PRODUCER")
    print("   شيك بـ 12 مليون دولار ارتد دون رصيد بسبب هذا الخطأ!")
    print("=" * 70)

    base_dir = Path(__file__).resolve().parent.parent.parent
    long_prod_dir = base_dir / "03_الفيديوهات_الطويلة_والشروحات" / "الإنتاج_والمقاطع"
    short_prod_dir = base_dir / "02_فيديوهات_الشورتس_والريلز" / "الإنتاج_والمقاطع"
    ffmpeg_exe = find_ffmpeg()

    # Clips sequence
    sequence = [
        ("1.mp4", 7.0),
        ("2.mp4", 7.0),
        ("3.mp4", 8.0),
        ("6.mp4", 6.5),
        ("7.mp4", 5.5),
        ("10.mp4", 5.5),
        ("23.mp4", 10.0),
    ]

    vo_file = short_prod_dir / "short01_voiceover.mp3"
    sub_file = short_prod_dir / "short01_bilingual_subtitles.ass"
    thumb_file = short_prod_dir / "ITQAN_SHORT01_THUMBNAIL.png"

    if not vo_file.exists():
        print(f"[!] Voiceover file not found: {vo_file}")
        sys.exit(1)
    if not sub_file.exists():
        print(f"[!] Subtitle file not found: {sub_file}")
        sys.exit(1)
    if not thumb_file.exists():
        print(f"[!] Thumbnail file not found: {thumb_file}")
        sys.exit(1)

    temp_dir = Path(tempfile.gettempdir()) / "itqan_short01_merge"
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        intro_sec = 2.0
        # 1. Prepare 2.0s intro video from thumbnail
        intro_clip = temp_dir / "intro_thumb.mp4"
        cmd_thumb = [
            ffmpeg_exe, "-y",
            "-loop", "1", "-t", str(intro_sec),
            "-i", str(thumb_file.as_posix()),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "24",
            str(intro_clip.as_posix())
        ]
        subprocess.run(cmd_thumb, cwd=str(temp_dir), check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        list_lines = [f"file 'intro_thumb.mp4'"]
        for idx, (fname, dur) in enumerate(sequence, 1):
            src = long_prod_dir / fname
            dest_name = f"clip_{idx:02d}.mp4"
            dest_path = temp_dir / dest_name
            cmd_trim = [
                ffmpeg_exe, "-y",
                "-ss", "00:00:00", "-t", str(dur),
                "-i", str(src.as_posix()),
                "-c:v", "libx264", "-preset", "fast", "-crf", "20",
                "-r", "24", "-an",
                str(dest_path.as_posix())
            ]
            subprocess.run(cmd_trim, cwd=str(temp_dir), check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            list_lines.append(f"file '{dest_name}'")

        concat_file = temp_dir / "concat_short.txt"
        concat_file.write_text("\n".join(list_lines), encoding="utf-8")

        temp_audio = temp_dir / "audio.mp3"
        shutil.copy2(str(vo_file), str(temp_audio))

        temp_sub = temp_dir / "subtitles.ass"
        shutil.copy2(str(sub_file), str(temp_sub))

        temp_output = temp_dir / "final_short01.mp4"
        final_dest = short_prod_dir / "ITQAN_SHORT01_CARTHET_AL_MOSTAKHLESAAT.mp4"

        print(f"[*] Rendering Short 01 with embedded Cover Card and delayed audio...")

        cmd_merge = [
            ffmpeg_exe, "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_file.as_posix()),
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
            print("\n[!] FFmpeg Error:")
            print(res.stderr.decode("utf-8", errors="replace")[-1500:])
            sys.exit(1)

        shutil.copy2(str(temp_output), str(final_dest))
        print(f"\n[OK] SUCCESS! YouTube Short 01 rendered successfully:")
        print(f"     -> {final_dest}")
        print(f"     -> Size: {final_dest.stat().st_size / 1024 / 1024:.2f} MB")
        print("=" * 70)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    produce_short01()
