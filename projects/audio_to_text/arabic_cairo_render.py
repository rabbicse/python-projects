# pip install cairocffi pangocairocffi

import cairocffi as cairo
import pangocffi as pango
import pangocairocffi as pangocairo
from moviepy import ImageClip
import numpy as np

TEXT = "السلام عليكم ورحمة الله وبركاته"
FONT = "Amiri 40"  # font name + size

WIDTH, HEIGHT = 1280, 200

# Create Cairo surface
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

# Pango layout
layout = pangocairo.create_layout(ctx)
layout.set_text(TEXT)
desc = pango.FontDescription(FONT)
layout.set_font_description(desc)

# Right-to-left base direction
layout.set_auto_dir(True)

# Position text (right aligned)
text_width, text_height = layout.get_pixel_size()
ctx.move_to(WIDTH - text_width - 20, (HEIGHT - text_height) // 2)

# Draw text
pangocairo.update_layout(ctx, layout)
pangocairo.show_layout(ctx, layout)

# Convert to numpy for MoviePy
buf = surface.get_data()
img = np.ndarray(shape=(HEIGHT, WIDTH, 4), dtype=np.uint8, buffer=buf)

clip = ImageClip(img).set_duration(4)
clip.write_videofile("pango_arabic.mp4", fps=24)
