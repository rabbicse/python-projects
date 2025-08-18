import numpy as np
from moviepy import *
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display


def create_rtl_arabic_animation(text, font_path, font_size=40, duration=5, bg_color=(0, 0, 0, 0)):
    # Step 1: Reshape and force RTL
    reshaped_text = arabic_reshaper.reshape(text)
    display_text = get_display(reshaped_text)  # Correct RTL order

    # Step 2: Pre-render the full text to get dimensions
    font = ImageFont.truetype(font_path, font_size)
    text_bbox = font.getbbox(display_text)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    canvas_width = text_width + 100  # Add padding
    canvas_height = text_height + 40

    # Step 3: Create a full pre-rendered image of the RTL text
    full_text_img = Image.new("RGBA", (canvas_width, canvas_height), bg_color)
    draw = ImageDraw.Draw(full_text_img)
    draw.text((canvas_width - text_width - 20, 20), display_text, font=font, fill="white")
    full_text_array = np.array(full_text_img)

    # Step 4: Animate by sliding a window (right-to-left)
    def make_frame(t):
        progress = min(1.0, t / duration)
        visible_width = int(canvas_width * progress)

        # Crop the visible portion (right side)
        cropped = full_text_array[:, -visible_width:] if visible_width > 0 else full_text_array[:, :0]

        # Pad to maintain canvas dimensions
        if visible_width < canvas_width:
            padding = np.zeros((canvas_height, canvas_width - visible_width, 4), dtype=np.uint8)
            frame = np.hstack([padding, cropped])
        else:
            frame = full_text_array

        return frame

    return VideoClip(make_frame, duration=duration)


# Example Usage
arabic_text = "لَكُمْ دِينُكُمْ وَلِىَ دِينِ"
font_path = "fonts/NotoSansArabic-Regular.ttf"  # Replace with your font
animated_clip = create_rtl_arabic_animation(arabic_text, font_path, duration=5)

# Composite onto a background
background = ColorClip(size=(1280, 720), color=(0, 0, 0), duration=5)
final_clip = CompositeVideoClip([background, animated_clip])
final_clip.write_videofile("arabic_animation_fixed.mp4", fps=24)