from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

# Arabic text
line = "السلام عليكم ورحمة الله وبركاته"

# Reshape and handle RTL
reshaped_text = arabic_reshaper.reshape(line)

rev_text = reshaped_text[::-1]  # slice backwards

bidi_text = get_display(rev_text)

# Image parameters
W, H = 1000, 200
img = Image.new('RGBA', (W, H), (255, 255, 255, 255))
draw = ImageDraw.Draw(img)

# Use a good Arabic font that supports ligatures
font_path = "/usr/share/fonts/truetype/amiri/Amiri-Regular.ttf"
font = ImageFont.truetype(font_path, 64)

# Measure text properly
if hasattr(draw, "textbbox"):
    l, t, r, b = draw.textbbox((0, 0), bidi_text, font=font)
    text_w, text_h = r - l, b - t
else:
    text_w, text_h = draw.textsize(bidi_text, font=font)

# Right-align for Arabic
x = W - text_w - 20
y = (H - text_h) // 2

# Draw text
draw.text((x, y), bidi_text, font=font, fill=(0, 0, 0))

# Save & show
img.save("arabic_fixed.png")
img.show()
