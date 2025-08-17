import numpy as np
from moviepy import *
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

# --- CONFIGURATION ---
FONT_ARABIC_PATH = "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf"
FALLBACK_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

FONT_SIZE_ARABIC = 80
COLOR_ARABIC = "#FFFFFF"
BG_COLOR = (0, 0, 0, 200)

# --- FONT SETUP ---
try:
    font_arabic = ImageFont.truetype(FONT_ARABIC_PATH, FONT_SIZE_ARABIC)
except IOError:
    print("Warning: Arabic font not found. Using fallback font.")
    font_arabic = ImageFont.truetype(FALLBACK_FONT_PATH, FONT_SIZE_ARABIC)


# --- CORE ANIMATION LOGIC ---
def animate_arabic_text(text, duration=10):
    """
    Creates a VideoClip of animated Arabic text.
    """
    # Reshape and get display text once
    reshaped_text = arabic_reshaper.reshape(text)
    display_text = get_display(reshaped_text)
    display_text = display_text[::-1]

    # Calculate full text dimensions
    text_bbox = font_arabic.getbbox(display_text)
    total_width = text_bbox[2] - text_bbox[0] + 30
    total_height = text_bbox[3] - text_bbox[1] + 30

    # Create frame dimensions with padding
    frame_width = total_width + 40
    frame_height = total_height + 40

    def get_frame(t):
        """
        Function to generate a frame at time 't'.
        """
        # Calculate progress (0 to 1)
        progress = min(1.0, max(0.0, t / duration))

        # Calculate how many characters to show
        chars_to_show = int(len(display_text) * progress)
        visible_text = display_text[:chars_to_show]

        # Create a transparent image for the frame
        frame_img = Image.new('RGBA', (frame_width, frame_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(frame_img)

        # Draw semi-transparent background (optional)
        # draw.rounded_rectangle([(0, 0), (frame_width, frame_height)],
        #                      radius=20, fill=BG_COLOR)

        # Calculate text position (right-aligned)
        text_width = font_arabic.getlength(visible_text)
        x_pos = frame_width - text_width - 20  # Right padding
        y_pos = (frame_height - (text_bbox[3] - text_bbox[1])) // 2

        # Draw the visible portion of the text
        draw.text((x_pos, y_pos), visible_text, font=font_arabic, fill=COLOR_ARABIC)

        return np.array(frame_img)

    return VideoClip(get_frame, duration=duration)


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    arabic_text = "لَكُمْ دِينُكُمْ وَلِىَ دِينِ"
    output_filename = "arabic_animation_test.mp4"

    print(f"Generating test video for: {arabic_text}")

    animated_clip = animate_arabic_text(arabic_text, duration=5.0)

    # Create background and composite
    background = ColorClip(size=(1280, 720), color=(0, 0, 0), duration=animated_clip.duration)

    # Center the animated clip on the background
    # animated_clip = animated_clip.set_position(('center', 'center'))
    final_clip = CompositeVideoClip([background, animated_clip])

    final_clip.write_videofile(
        output_filename,
        fps=24,
        codec="libx264",
        audio=False,
        preset="medium"
    )

    print(f"Test video saved as {output_filename}")