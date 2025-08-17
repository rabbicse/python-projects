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
def animate_arabic_text(text, duration=5.0):
    """
    Creates a VideoClip of animated Arabic text.
    """
    # 1. Reshape the full text to get its final dimensions
    reshaped_full_text = arabic_reshaper.reshape(text)
    display_full_text = get_display(reshaped_full_text)
    display_full_text = display_full_text[::-1]

    text_bbox = font_arabic.getbbox(display_full_text)
    total_width = text_bbox[2] - text_bbox[0] + 20
    total_height = text_bbox[3] - text_bbox[1] + 20

    final_width = total_width + 40
    final_height = total_height + 40

    def get_frame(t):
        """
        Function to generate a frame at time 't'.
        """
        # Calculate how many characters to show based on time 't'
        # The animation is linear over the duration
        chars_to_show = int(len(display_full_text) * (t / duration))

        # 2. Get the original substring in correct RTL order
        original_substring = display_full_text[:chars_to_show]

        # --- The crucial change is here ---
        # Reverse the substring before passing it to the reshaper
        # This ensures that the characters are processed in the correct order for RTL
        # even if the reshaper doesn't do it automatically.
        reversed_substring = original_substring[::-1]

        # 3. Reshape the substring for the current frame
        reshaped_substring = arabic_reshaper.reshape(reversed_substring)
        display_substring = get_display(reshaped_substring)

        # 4. Create a transparent image for the frame
        frame_img = Image.new('RGBA', (final_width, final_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(frame_img)

        # 5. Draw a semi-transparent background box
        draw.rounded_rectangle([(0, 0), (final_width, final_height)], radius=20, fill=BG_COLOR)

        # 6. Draw the correctly positioned text
        text_width = font_arabic.getlength(display_substring)
        x_pos = final_width - text_width - 20
        y_pos = 10

        draw.text((x_pos, y_pos), display_substring, font=font_arabic, fill=COLOR_ARABIC)

        return np.array(frame_img)

    return VideoClip(get_frame, duration=duration)


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    arabic_text = "لَكُمْ دِينُكُمْ وَلِىَ دِينِ"
    output_filename = "arabic_animation_test.mp4"

    print(f"Generating test video for: {arabic_text}")

    # Create the animated clip
    animated_clip = animate_arabic_text(arabic_text, duration=5.0)

    # Create a background of 1280x720
    background = ColorClip(size=(1280, 720), color=(0, 0, 0), duration=animated_clip.duration)

    # Overlay the animated text centered
    final_clip = CompositeVideoClip([background, animated_clip])

    # Write the video file
    final_clip.write_videofile(
        output_filename,
        fps=24,
        codec="libx264",
        audio=False,  # No audio for this simple test
        preset="medium"
    )

    print(f"Test video saved as {output_filename}")