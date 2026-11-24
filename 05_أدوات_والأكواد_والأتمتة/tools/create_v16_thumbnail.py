"""
ITQAN Studio — High-CTR 16:9 Thumbnail Generator for ERPNext v16.60 Release
Generates ITQAN_V16_THUMBNAIL_FINAL.png (1280x720) with 3D Gold Typography and Official Channel Branding.
"""

import os
import sys
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import arabic_reshaper
from bidi.algorithm import get_display

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def shape_ar(text: str) -> str:
    return get_display(arabic_reshaper.reshape(text))

def load_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\tahomabd.ttf" if bold else r"C:\Windows\Fonts\tahoma.ttf",
        r"C:\Windows\Fonts\seguisb.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()

def draw_rounded_pill(draw: ImageDraw.ImageDraw, box, radius: int, fill, outline=None, width: int = 2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def generate_v16_thumbnail():
    target_dir = Path("03_الفيديوهات_الطويلة_والشروحات/حلقات_الموسم_الأول/حلقة_تحديثات_ERPNext_v16_60")
    target_dir.mkdir(parents=True, exist_ok=True)
    out_file = target_dir / "ITQAN_V16_THUMBNAIL_FINAL.png"

    brain_dir = Path(r"C:\Users\96777\.gemini\antigravity\brain\931c83d0-96b3-4f73-9e96-1dd50e975079")
    bg_exec = Image.open(brain_dir / "bg_exec.png").convert("RGBA")
    bg_shield = Image.open(brain_dir / "bg_shield.png").convert("RGBA")
    logo_src = brain_dir / ".user_uploaded" / "media_1794402596823_7f5077c4.png"

    W, H = 1280, 720
    bg_exec = bg_exec.resize((W, H), Image.Resampling.LANCZOS)
    bg_shield = bg_shield.resize((W, H), Image.Resampling.LANCZOS)

    # Blend: left side features glowing shield/network, right side features command center
    mask = Image.new("L", (W, H), 0)
    for x in range(W):
        # gradient from x=300 to x=800
        val = int(255 * max(0.0, min(1.0, float(x - 300) / 500.0)))
        for y in range(H):
            mask.putpixel((x, y), val)
    
    # Composite shield on left, exec on right
    blended = Image.composite(bg_exec, bg_shield, mask)

    # Darken and enhance contrast
    enhancer = ImageEnhance.Color(blended)
    blended = enhancer.enhance(1.2)
    enh_bri = ImageEnhance.Brightness(blended)
    blended = enh_bri.enhance(0.85)

    # Readability overlays
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    
    # Top bar shadow
    ov_draw.rectangle([0, 0, W, 120], fill=(5, 12, 25, 160))
    # Bottom vignette for headline
    for y in range(230, H):
        prog = max(0.0, min(1.0, float(y - 230) / float(H - 230)))
        alpha = int(160 * (prog ** 1.3))
        ov_draw.line([(0, y), (W, y)], fill=(4, 9, 20, alpha))

    canvas = Image.alpha_composite(blended, overlay)
    draw = ImageDraw.Draw(canvas)

    # 1. Top-Left Channel Logo (Circular Badge)
    if logo_src.exists():
        raw_logo = Image.open(logo_src).convert("RGBA")
        crop_box = (6, 72, 214, 280)
        cropped = raw_logo.crop(crop_box).resize((110, 110), Image.Resampling.LANCZOS)
        c_mask = Image.new("L", (110, 110), 0)
        ImageDraw.Draw(c_mask).ellipse((2, 2, 108, 108), fill=255)
        circle_logo = Image.new("RGBA", (110, 110), (0, 0, 0, 0))
        circle_logo.paste(cropped, (0, 0), c_mask)

        # Cyan glow rim
        draw.ellipse((36, 22, 152, 138), fill=(0, 212, 255, 255))
        canvas.paste(circle_logo, (39, 25), circle_logo)
        draw = ImageDraw.Draw(canvas)

    # 2. Top-Right Channel Badge: "إتقان — الذكاء المؤسسي"
    badge_font = load_font(25, bold=True)
    badge_text = shape_ar("إتقان — الذكاء المؤسسي")
    bb = draw.textbbox((0, 0), badge_text, font=badge_font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    bx2 = W - 38
    bx1 = bx2 - tw - 44
    by1 = 30
    by2 = by1 + th + 28
    draw_rounded_pill(draw, [bx1, by1, bx2, by2], radius=12, fill=(10, 22, 40, 235), outline=(0, 212, 255, 255), width=2)
    draw.text((bx1 + 22, by1 + 12), badge_text, font=badge_font, fill=(255, 255, 255, 255))

    # 3. Category Tag Pill (Red High-Alert Tag)
    tag_font = load_font(32, bold=True)
    tag_text = shape_ar("تحديث القرن: ERPNext v16.60")
    tb = draw.textbbox((0, 0), tag_text, font=tag_font)
    ttw, tth = tb[2] - tb[0], tb[3] - tb[1]
    tx1 = (W - ttw) // 2 - 30
    tx2 = (W + ttw) // 2 + 30
    ty1 = 280
    ty2 = ty1 + tth + 24
    draw_rounded_pill(draw, [tx1, ty1, tx2, ty2], radius=12, fill=(220, 20, 50, 255), outline=(255, 255, 255, 255), width=2)
    draw.text(((W - ttw) // 2, ty1 + 10), tag_text, font=tag_font, fill=(255, 255, 255, 255))

    # 4. Giant 3D Gold Headline: "الجيل الجديد!"
    main_font = load_font(120, bold=True)
    main_text = shape_ar("الجيل الجديد!")
    mb = draw.textbbox((0, 0), main_text, font=main_font)
    mtw, mth = mb[2] - mb[0], mb[3] - mb[1]
    mx = (W - mtw) // 2
    my = 360

    # 3D Depth Shadows
    for offset in range(12, 0, -1):
        draw.text((mx + offset, my + offset), main_text, font=main_font, fill=(0, 0, 0, 255))
    for dx in (-4, 0, 4):
        for dy in (-4, 0, 4):
            draw.text((mx + dx, my + dy), main_text, font=main_font, fill=(10, 15, 25, 255))
    # Radiant Gold
    draw.text((mx, my), main_text, font=main_font, fill=(255, 215, 0, 255))

    # 5. Sub-headline Pill: "(ذكاء اصطناعي + بناء أنظمة بلا كود)"
    sub_font = load_font(38, bold=True)
    sub_text = shape_ar("(ذكاء اصطناعي + بناء أنظمة بلا كود)")
    sb = draw.textbbox((0, 0), sub_text, font=sub_font)
    stw, sth = sb[2] - sb[0], sb[3] - sb[1]
    sx1 = (W - stw) // 2 - 35
    sx2 = (W + stw) // 2 + 35
    sy1 = 535
    sy2 = sy1 + sth + 26
    draw_rounded_pill(draw, [sx1, sy1, sx2, sy2], radius=16, fill=(10, 20, 35, 240), outline=(0, 212, 255, 255), width=3)
    draw.text(((W - stw) // 2, sy1 + 12), sub_text, font=sub_font, fill=(255, 255, 255, 255))

    canvas.convert("RGB").save(str(out_file), "PNG", quality=98)
    artifact_copy = brain_dir / "ITQAN_V16_THUMBNAIL_FINAL.png"
    shutil.copy2(str(out_file), str(artifact_copy))
    print(f"[OK] Saved v16.60 Thumbnail to: {out_file}")

if __name__ == "__main__":
    generate_v16_thumbnail()

