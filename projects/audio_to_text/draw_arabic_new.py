from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

FONT_ARABIC_PATH = "/usr/share/fonts/truetype/amiri/Amiri-Regular.ttf"  # adjust to your path
line = "السلام عليكم ورحمة الله وبركاته"

# Arabic shaping
reshaped_text = arabic_reshaper.reshape(line)
bidi_text = get_display(reshaped_text)

# Create image
W, H = 1000, 200
img = Image.new('RGBA', (W, H), (255, 255, 255, 255))
draw = ImageDraw.Draw(img)
font = ImageFont.truetype(FONT_ARABIC_PATH, 48)

# Draw text (Right aligned for Arabic)
# --- robust measurement ---
if hasattr(draw, "textbbox"):
    l, t, r, b = draw.textbbox((0, 0), bidi_text, font=font)
    text_w, text_h = r - l, b - t
elif hasattr(draw, "textlength"):  # older fallback
    text_w = int(draw.textlength(bidi_text, font=font))
    # height fallback
    if hasattr(font, "getbbox"):
        fl, ft, fr, fb = font.getbbox(bidi_text)
        text_h = fb - ft
    else:
        text_h = font.getsize(bidi_text)[1]
else:
    # very old Pillow fallback
    text_w, text_h = font.getsize(bidi_text)

# Right-align for RTL
x = W - text_w - 20
y = (H - text_h) // 2

# text_width, text_height = draw.textsize(bidi_text, font=font)
draw.text((x, y), bidi_text, font=font, fill=(0, 0, 0))

img.show()
img.save("arabic_correct.png")
