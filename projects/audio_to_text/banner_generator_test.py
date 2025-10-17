from PIL import Image, ImageDraw, ImageFont, ImageColor
import numpy as np


def draw_gradient_text(img, position, text, font, gradient_colors, shadow_offset=(3, 3), shadow_color="#000000"):
    draw = ImageDraw.Draw(img)

    # Draw shadow first
    shadow_pos = (position[0] + shadow_offset[0], position[1] + shadow_offset[1])
    draw.text(shadow_pos, text, font=font, fill=shadow_color)

    # Create text mask
    mask = Image.new("L", img.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.text(position, text, font=font, fill=255)

    # Create gradient image
    gradient = Image.new("RGB", img.size, 0)
    top_color = np.array(ImageColor.getrgb(gradient_colors[0]))
    bottom_color = np.array(ImageColor.getrgb(gradient_colors[1]))

    for y in range(img.size[1]):
        ratio = y / img.size[1]
        r, g, b = (top_color * (1 - ratio) + bottom_color * ratio).astype(int)
        ImageDraw.Draw(gradient).line([(0, y), (img.size[0], y)], fill=(r, g, b))

    # Paste gradient only where text mask is
    img.paste(gradient, (0, 0), mask)

    return img


# Example usage
if __name__ == "__main__":
    # Create canvas
    img = Image.new("RGB", (1200, 400), "#101820")  # Dark background
    font = ImageFont.truetype("fonts/DejaVuSans.ttf", 80)  # Replace with your Quranic/Arabic font

    # Draw Arabic Surah Name
    img = draw_gradient_text(
        img, (100, 100), "سورة التكاثر", font,
        gradient_colors=("#E63946", "#FFB300"),  # crimson → golden
        shadow_offset=(4, 4),
        shadow_color="#7F1D1D"
    )

    # Draw English Surah Name
    img = draw_gradient_text(
        img, (100, 220), "Surah At-Takathur", font,
        gradient_colors=("#1D3557", "#2A9D8F"),  # navy → teal
        shadow_offset=(3, 3),
        shadow_color="#0A192F"
    )

    img.show()

    # img.save("surah_banner.png")
