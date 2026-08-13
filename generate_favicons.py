#!/usr/bin/env python3
"""Generate crisp, high-resolution favicons for Bible Reading Plan (SVG, ICO, PNG 32x32, 180x180, 512x512).
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def generate_icons(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. SVG Favicon
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect width="512" height="512" rx="110" fill="#0f172a"/>
  <rect x="24" y="24" width="464" height="464" rx="90" fill="none" stroke="#38bdf8" stroke-width="12" opacity="0.3"/>
  
  <!-- Left Page -->
  <path d="M 80,140 Q 240,110 248,150 L 248,400 Q 240,360 80,380 Z" fill="#ffffff"/>
  <!-- Right Page -->
  <path d="M 432,140 Q 272,110 264,150 L 264,400 Q 272,360 432,380 Z" fill="#f8fafc"/>

  <!-- Book Cover / Base -->
  <path d="M 70,135 Q 240,105 256,145 Q 272,105 442,135 L 442,390 Q 272,365 256,410 Q 240,365 70,390 Z" fill="none" stroke="#fbbf24" stroke-width="16" stroke-linejoin="round"/>
  
  <!-- Spine / Center line -->
  <line x1="256" y1="145" x2="256" y2="410" stroke="#d97706" stroke-width="10"/>

  <!-- Bookmark Ribbon -->
  <path d="M 256,145 L 256,330 L 275,310 L 294,330 L 294,145 Z" fill="#0284c7"/>

  <!-- Text lines on left page -->
  <line x1="120" y1="200" x2="215" y2="190" stroke="#cbd5e1" stroke-width="10" stroke-linecap="round"/>
  <line x1="120" y1="240" x2="215" y2="230" stroke="#cbd5e1" stroke-width="10" stroke-linecap="round"/>
  <line x1="120" y1="280" x2="215" y2="270" stroke="#cbd5e1" stroke-width="10" stroke-linecap="round"/>
  <line x1="120" y1="320" x2="190" y2="312" stroke="#cbd5e1" stroke-width="10" stroke-linecap="round"/>

  <!-- Text lines on right page -->
  <line x1="297" y1="190" x2="392" y2="200" stroke="#cbd5e1" stroke-width="10" stroke-linecap="round"/>
  <line x1="297" y1="230" x2="392" y2="240" stroke="#cbd5e1" stroke-width="10" stroke-linecap="round"/>
  <line x1="297" y1="270" x2="392" y2="280" stroke="#cbd5e1" stroke-width="10" stroke-linecap="round"/>
  <line x1="297" y1="312" x2="367" y2="320" stroke="#cbd5e1" stroke-width="10" stroke-linecap="round"/>
</svg>"""

    (out_dir / "favicon.svg").write_text(svg_content, encoding="utf-8")

    # 2. Render PNG 512x512 using PIL
    size = 512
    img = Image.new("RGBA", (size, size), (15, 23, 42, 255))
    draw = ImageDraw.Draw(img)

    # Draw rounded border highlight
    draw.rounded_rectangle([20, 20, 492, 492], radius=90, outline=(56, 189, 248, 80), width=10)

    # Left & Right Pages
    draw.polygon([(80, 140), (248, 120), (248, 400), (80, 380)], fill=(255, 255, 255, 255))
    draw.polygon([(432, 140), (264, 120), (264, 400), (432, 380)], fill=(248, 250, 252, 255))

    # Gold Borders
    draw.line([(70, 135), (256, 115), (442, 135)], fill=(251, 191, 36, 255), width=14)
    draw.line([(70, 390), (256, 410), (442, 390)], fill=(251, 191, 36, 255), width=14)
    draw.line([(70, 135), (70, 390)], fill=(251, 191, 36, 255), width=14)
    draw.line([(442, 135), (442, 390)], fill=(251, 191, 36, 255), width=14)
    draw.line([(256, 115), (256, 410)], fill=(217, 119, 6, 255), width=10)

    # Bookmark Ribbon
    draw.polygon([(256, 115), (256, 330), (275, 310), (294, 330), (294, 115)], fill=(2, 132, 199, 255))

    # Text lines
    for y in [190, 230, 270, 310]:
        draw.line([(120, y), (215, y - 5)], fill=(203, 213, 225, 255), width=10)
        draw.line([(297, y - 5), (392, y)], fill=(203, 213, 225, 255), width=10)

    # Save PNG formats
    img.save(out_dir / "icon-512.png", "PNG")

    img_180 = img.resize((180, 180), Image.Resampling.LANCZOS)
    img_180.save(out_dir / "apple-touch-icon.png", "PNG")

    img_64 = img.resize((64, 64), Image.Resampling.LANCZOS)
    img_64.save(out_dir / "favicon.png", "PNG")

    img_32 = img.resize((32, 32), Image.Resampling.LANCZOS)
    img_16 = img.resize((16, 16), Image.Resampling.LANCZOS)

    img_32.save(out_dir / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (64, 64)])
    print(f"Pomyślnie wygenerowano favikony w: {out_dir}")

if __name__ == "__main__":
    generate_icons(Path("."))
