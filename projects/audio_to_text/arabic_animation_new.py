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
    # Reshape the full text once to get the final dimensions and display string
    reshaped_full_text = arabic_reshaper.reshape(text)
    display_full_text = get_display(reshaped_full_text)

    text_bbox = font_arabic.getbbox(display_full_text)
    total_width = text_bbox[2] - text_bbox[0] + 30
    total_height = text_bbox[3] - text_bbox[1] + 30

    final_width = total_width + 40
    final_height = total_height + 40

    def get_frame(t):
        """
        Function to generate a frame at time 't'.
        """
        # Calculate how many characters to show based on time 't'
        # Animation is linear over the duration
        chars_to_show = int(len(display_full_text) * (t / duration))

        # --- THIS LINE IS THE FIX ---
        # Use the already correctly ordered string.
        animated_text = display_full_text

        # Calculate the width of the portion of text that should be visible
        visible_text_width = font_arabic.getlength(animated_text[:chars_to_show])

        # Create a transparent image for the frame
        frame_img = Image.new('RGBA', (final_width, final_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(frame_img)

        # Draw a semi-transparent background box
        # draw.rounded_rectangle([(0, 0), (final_width, final_height)], radius=20, fill=BG_COLOR)

        # Draw the full, correctly-shaped text
        # But we'll crop it using the background box as a mask
        x_pos = final_width - visible_text_width - 20
        y_pos = 10

        print(f"{x_pos}, {y_pos}")

        # Draw the full string, but only the part that is within the visible area will be seen
        draw.text((x_pos, y_pos), animated_text, font=font_arabic, fill=COLOR_ARABIC)

        return np.array(frame_img)

    return VideoClip(get_frame, duration=duration)


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    arabic_text = "لَكُمْ دِينُكُمْ وَلِىَ دِينِ"
    output_filename = "arabic_animation_test.mp4"

    print(f"Generating test video for: {arabic_text}")

    animated_clip = animate_arabic_text(arabic_text, duration=5.0)

    # Use the correct resize method
    # Create a background of 1280x720
    background = ColorClip(size=(1280, 720), color=(0, 0, 0), duration=animated_clip.duration)

    # Overlay the animated text centered
    final_clip = CompositeVideoClip([background, animated_clip])

    final_clip.write_videofile(
        output_filename,
        fps=24,
        codec="libx264",
        audio=False,
        preset="medium"
    )

    print(f"Test video saved as {output_filename}")