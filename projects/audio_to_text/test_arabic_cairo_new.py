from PIL import Image
import cairocffi as cairo
import arabic_reshaper
from bidi.algorithm import get_display
import os
import gi
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Pango, PangoCairo

# Arabic text
line = "السلام عليكم ورحمة الله وبركاته"

# Reshape and handle RTL
reshaped_text = arabic_reshaper.reshape(line)
bidi_text = get_display(reshaped_text)

# Image parameters
W, H = 1000, 200
font_path = "/usr/share/fonts/truetype/amiri/Amiri-Regular.ttf"
font_size = 64
padding = 20

# Create a Cairo surface and context
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
ctx = cairo.Context(surface)

# Set a white background
ctx.set_source_rgb(1, 1, 1)
ctx.paint()

# Create a Pango layout
layout = PangoCairo.create_layout(ctx)

# Create a font description and set it
font_desc = Pango.FontDescription()
font_desc.set_size(font_size * Pango.SCALE)
font_desc.set_family("Amiri Regular")

# A more robust way to set font from file path
# If 'Amiri Regular' doesn't work, you can use the font path directly
# Note: This often requires Pango to be configured to find the font
font_desc_from_path = Pango.FontDescription.from_string(f"{os.path.basename(font_path).split('.')[0]} {font_size}")
layout.set_font_description(font_desc_from_path)
layout.set_font_description(font_desc) # Using the generic name first, as it's cleaner.

# Set the text
layout.set_text(bidi_text)

# Set text alignment to right-to-left
layout.set_direction(Pango.Direction.RTL)

# Measure the layout for alignment
ink_rect, logical_rect = layout.get_pixel_extents()

text_width = logical_rect.width
text_height = logical_rect.height

# Calculate position for right-alignment and vertical centering
x = W - text_width - padding
y = (H - text_height) // 2

# Set the layout position
ctx.move_to(x, y)

# Draw the layout onto the Cairo context
PangoCairo.show_layout(ctx, layout)

# Convert the Cairo surface to a Pillow image
buf = surface.get_data()
img = Image.frombuffer("RGBA", (W, H), buf, "raw", "BGRA", 0, 1)

# Save & show
img.save("arabic_fixed_pango.png")
img.show()