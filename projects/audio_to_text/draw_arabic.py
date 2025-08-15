from moviepy import *
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

FONT_ARABIC_PATH = "fonts/Amiri-Regular.ttf"

# Your Arabic text
line = "السلام عليكم ورحمة الله وبركاته"

# Step 1: Reshape Arabic text
reshaped_text = arabic_reshaper.reshape(line)

# Step 2: Get RTL display order
bidi_text = get_display(reshaped_text)

# Create an image with PIL
img = Image.new('RGBA', (800, 200), (255, 255, 255, 0))
draw = ImageDraw.Draw(img)
font = ImageFont.truetype(FONT_ARABIC_PATH, 40)  # Make sure you have this font
color = (0, 0, 0)

draw.text((10, 10), bidi_text, font=font, fill=color)

# Save temp image
img.save("temp.png")

# # Step 3: Add to moviepy
# clip = ImageClip("temp.png").set_duration(5)
#
# clip.write_videofile("output.mp4", fps=24)
