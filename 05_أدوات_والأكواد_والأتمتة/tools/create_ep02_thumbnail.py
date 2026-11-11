"""
ITQAN Studio — High-CTR 16:9 Thumbnail Generator for Episode 02
Generates ITQAN_EP02_THUMBNAIL_FINAL.png (1280x720) using ep02_thumb_bg.jpg + official branding & bold 3D gold typography.
"""

import os
import sys
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import arabic_reshaper
from bidi.algorithm import get_display

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def shape_ar(text: str) -> str:
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

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

def create_ep02_thumbnail():
    base_dir = Path(__file__).resolve().parent.parent.parent
    prod_dir = base_dir / "03_الفيديوهات_الطويلة_والشروحات" / "الإنتاج_والمقاطع"
    out_file = prod_dir / "ITQAN_EP02_THUMBNAIL_FINAL.png"

    bg_path = Path(r"C:\Users\96777\.gemini\antigravity\brain\931c83d0-96b3-4f73-9e96-1dd50e975079\ep02_thumb_bg_1794413340549.jpg")
    logo_src = Path(r"C:\Users\96777\.gemini\antigravity\brain\931c83d0-96b3-4f73-9e96-1dd50e975079\.user_uploaded\media_1794402596823_7f5077c4.png")

    W, H = 1280, 720
    bg = Image.open(bg_path).convert("RGBA").resize((W, H), Image.Resampling.LANCZOS)

    # Dark vignette and center readability boost
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    # Soft gradient darkening in center-bottom for typography contrast
    for y in range(250, H):
        prog = max(0.0, min(1.0, float(y - 250) / float(H - 250)))
        alpha = int(145 * (prog ** 1.3))
        ov_draw.line([(0, y), (W, y)], fill=(5, 10, 20, alpha))

    # Subtle side dark vignette
    ov_draw.rectangle([0, 0, W, 110], fill=(4, 8, 16, 110))
    canvas = Image.alpha_composite(bg, overlay)

    draw = ImageDraw.Draw(canvas)

    # 1. Top-Left Circular ITQAN Logo
    if logo_src.exists():
        raw_logo = Image.open(logo_src).convert("RGBA")
        # Crop the circular badge region from bottom of media_1794402596823_7f5077c4.png (size 227x282)
        lw, lh = raw_logo.size
        # The circle sits roughly from y=72 to y=275, x=5 to x=215
        crop_box = (6, 72, 214, 280)
        cropped = raw_logo.crop(crop_box).resize((112, 112), Image.Resampling.LANCZOS)
        mask = Image.new("L", (112, 112), 0)
        ImageDraw.Draw(mask).ellipse((2, 2, 110, 110), fill=255)
        logo_circle = Image.new("RGBA", (112, 112), (0, 0, 0, 0))
        logo_circle.paste(cropped, (0, 0), mask)
        # Cyan glow rim
        draw.ellipse((34, 24, 154, 144), fill=(0, 212, 255, 255))
        canvas.paste(logo_circle, (38, 28), logo_circle)
        draw = ImageDraw.Draw(canvas)

    # 2. Top-Right Channel Badge: "إتقان — الذكاء المؤسسي"
    badge_font = load_font(25, bold=True)
    badge_text = shape_ar("إتقان — الذكاء المؤسسي")
    bb = draw.textbbox((0, 0), badge_text, font=badge_font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    pad_x, pad_y = 22, 12
    bx2 = W - 38
    bx1 = bx2 - tw - pad_x * 2
    by1 = 30
    by2 = by1 + th + pad_y * 2 + 4
    draw_rounded_pill(draw, [bx1, by1, bx2, by2], radius=12, fill=(10, 22, 40, 235), outline=(0, 212, 255, 255), width=2)
    draw.text((bx1 + pad_x, by1 + pad_y - 2), badge_text, font=badge_font, fill=(255, 255, 255, 255))

    # 3. Red Category Pill Tag (Center Above Title)
    tag_font = load_font(30, bold=True)
    tag_text = shape_ar("ماستر كلاس ERPNext: كشف وهم الأرباح")
    tb = draw.textbbox((0, 0), tag_text, font=tag_font)
    ttw, tth = tb[2] - tb[0], tb[3] - tb[1]
    tx1 = (W - ttw) // 2 - 28
    tx2 = (W + ttw) // 2 + 28
    ty1 = 295
    ty2 = ty1 + tth + 24
    draw_rounded_pill(draw, [tx1, ty1, tx2, ty2], radius=10, fill=(220, 20, 50, 255), outline=(255, 255, 255, 255), width=2)
    draw.text(((W - ttw) // 2, ty1 + 9), tag_text, font=tag_font, fill=(255, 255, 255, 255))

    # 4. Giant 3D Gold Headline: "جحيم الإكسل"
    main_font = load_font(112, bold=True)
    main_text = shape_ar("جحيم الإكسل!")
    mb = draw.textbbox((0, 0), main_text, font=main_font)
    mtw, mth = mb[2] - mb[0], mb[3] - mb[1]
    mx = (W - mtw) // 2
    my = 365

    # Heavy black drop shadow & 3D extrusion
    for offset in range(10, 0, -1):
        draw.text((mx + offset, my + offset), main_text, font=main_font, fill=(0, 0, 0, 255))
    # Black outline
    for dx in (-4, 0, 4):
        for dy in (-4, 0, 4):
            draw.text((mx + dx, my + dy), main_text, font=main_font, fill=(10, 10, 10, 255))
    # Bright Gold Fill
    draw.text((mx, my), main_text, font=main_font, fill=(255, 215, 0, 255))

    # 5. Sub-headline Pill: "(أرباح على الورق.. وإفلاس في البنك!)"
    sub_font = load_font(44, bold=True)
    sub_text = shape_ar("أرباح على الورق.. وإفلاس في البنك!")
    sb = draw.textbbox((0, 0), sub_text, font=sub_font)
    stw, sth = sb[2] - sb[0], sb[3] - sb[1]
    sx1 = (W - stw) // 2 - 35
    sx2 = (W + stw) // 2 + 35
    sy1 = 528
    sy2 = sy1 + sth + 30
    draw_rounded_pill(draw, [sx1, sy1, sx2, sy2], radius=16, fill=(12, 18, 30, 240), outline=(255, 215, 0, 255), width=3)
    draw.text(((W - stw) // 2, sy1 + 12), sub_text, font=sub_font, fill=(255, 255, 255, 255))

    # Save final RGB PNG
    canvas.convert("RGB").save(str(out_file), "PNG", quality=98)
    artifact_copy = Path(r"C:\Users\96777\.gemini\antigravity\brain\931c83d0-96b3-4f73-9e96-1dd50e975079\ITQAN_EP02_THUMBNAIL_FINAL.png")
    shutil.copy2(str(out_file), str(artifact_copy))
    print(f"[OK] Saved Episode 02 Thumbnail to: {out_file}")

if __name__ == "__main__":
    create_ep02_thumbnail()

