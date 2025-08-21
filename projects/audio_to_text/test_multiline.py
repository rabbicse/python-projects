import numpy as np
from PIL import Image, ImageDraw, ImageFont


# Test rounded corner background creation
def test_background_creation():
    # Test text
    test_text = "This is a multi-line\ntext example for testing" + "This is a multi-line\ntext example for testing" + "This is a multi-line\ntext example for testing" + "This is a multi-line\ntext example for testing"
    lines = test_text.split('\n')

    # Create font
    try:
        font = ImageFont.truetype("fonts/DejaVuSans.ttf", 30)
    except:
        font = ImageFont.load_default()

    # Calculate dimensions
    line_heights = []
    max_width = 0

    for line in lines:
        bbox = font.getbbox(line)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1] + 10
        line_heights.append(height)
        max_width = max(max_width, width)

    total_height = sum(line_heights) + 40  # padding
    total_width = max_width + 60  # padding

    # Create image with transparent background
    img = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw rounded rectangle with semi-transparent black
    draw.rounded_rectangle([(0, 0), (total_width, total_height)],
                           radius=15, fill=(0, 0, 0, 200))

    # Draw text
    y_offset = 20
    for i, line in enumerate(lines):
        draw.text((30, y_offset), line, font=font, fill="white")
        y_offset += line_heights[i]

    # Save and show
    img.save("test_background.png")
    img.show()
    print(f"Image saved: test_background.png")
    print(f"Dimensions: {total_width}x{total_height}")
    print(f"BG_COLOR used: (0, 0, 0, 200)")


if __name__ == "__main__":
    test_background_creation()