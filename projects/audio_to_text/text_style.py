from PIL import Image, ImageDraw, ImageFont

FONT_ENGLISH_HEADER_PATH = "fonts/DejaVuSans.ttf"
# Create blank image
width, height = 800, 300
image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

# Text and font
text = "Surah Al-Kafirun"
font = ImageFont.truetype(FONT_ENGLISH_HEADER_PATH, 80)  # Replace with your Arabic font if needed

# Create gradient
gradient = Image.new("RGBA", (width, height))
grad_draw = ImageDraw.Draw(gradient)

for i, color in enumerate(((255,215,0), (255,140,0))):  # gold → orange gradient
    grad_draw.rectangle([0, i * height // 2, width, (i + 1) * height // 2], fill=color)

# Create text mask
text_mask = Image.new("L", (width, height), 0)
mask_draw = ImageDraw.Draw(text_mask)
bbox = draw.textbbox((0, 0), text, font=font)
w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]

mask_draw.text(((width - w) // 2, (height - h) // 2), text, font=font, fill=255)

# Apply gradient to text
gradient.putalpha(text_mask)
result = Image.alpha_composite(Image.new("RGBA", (width, height), (0, 0, 0, 0)), gradient)

result.show()

# Save result
# result.save("gradient_text.png")
