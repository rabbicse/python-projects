from moviepy import *
from arabic_reshaper import reshape
from bidi.algorithm import get_display
import textwrap
import numpy as np
import os

# Font configuration
FONT_ENGLISH_HEADER_PATH = "fonts/DejaVuSans.ttf"
FONT_ENGLISH_PATH = "fonts/DejaVuSans.ttf"
FONT_ARABIC_HEADER_PATH = "fonts/Amiri-Regular.ttf"
FONT_ARABIC_PATH = "fonts/NotoSansArabic-Regular.ttf"
FALLBACK_FONT_PATH = "fonts/DejaVuSans.ttf"


# Function to get appropriate font with fallback
def get_font(is_arabic=False, is_header=False):
    if is_arabic:
        font_path = FONT_ARABIC_HEADER_PATH if is_header else FONT_ARABIC_PATH
    else:
        font_path = FONT_ENGLISH_HEADER_PATH if is_header else FONT_ENGLISH_PATH

    # Check if font file exists, use fallback if not
    if not os.path.exists(font_path):
        print(f"Warning: Font file {font_path} not found. Using fallback font.")
        return FALLBACK_FONT_PATH
    return font_path


# Function to format text (handles both English and Arabic)
def format_text(text, fontsize, color, is_arabic=False, is_header=False):
    font = get_font(is_arabic, is_header)

    if is_arabic:
        # Reshape and apply bidirectional algorithm for Arabic
        reshaped_text = reshape(text)
        bidi_text = get_display(reshaped_text)
        return TextClip(text=bidi_text, font_size=fontsize, font=font,
                        color=color, text_align='center', method='label')
    else:
        # Wrap English text if needed
        wrapped_text = "\n".join(textwrap.wrap(text, width=40))
        return TextClip(text=wrapped_text, font_size=fontsize, font=font,
                        color=color, text_align='center', method='label')


# Create a sample video if no video is available
def create_sample_video(duration=30, size=(1280, 720)):
    # Create a color clip with a simple gradient
    def make_frame(t):
        # Create a simple gradient background
        gradient = np.zeros((size[1], size[0], 3), dtype=np.uint8)
        for y in range(size[1]):
            gradient[y, :, 0] = int(y / size[1] * 255)  # Red gradient
            gradient[y, :, 1] = int((1 - y / size[1]) * 255)  # Green gradient
            gradient[y, :, 2] = int((y / size[1]) * 128)  # Blue gradient
        return gradient

    return VideoClip(make_frame, duration=duration)


# Main function
def main():
    # Define your subtitles with timing [start_time, end_time, text, is_arabic, is_header]
    subtitles = [
        (1, 5, "Hello, welcome to our video", False, False),
        (5, 10, "مرحبًا بكم في هذا الفيديو", True, False),
        (10, 15, "Today we're learning about subtitle animations", False, False),
        (15, 20, "اليوم نتعلم عن الرسوم المتحركة للترجمة", True, False),
        (20, 25, "Thank you for watching!", False, True),
        (25, 30, "شكرًا للمشاهدة!", True, True)
    ]

    # Create a sample video (replace with your actual video)
    video = create_sample_video(duration=30)

    # Create text clips
    text_clips = []
    for start, end, text, is_arabic, is_header in subtitles:
        # Determine font size based on whether it's a header
        fontsize = 50 if is_header else 40

        # Create text clip
        txt_clip = format_text(text, fontsize, "white", is_arabic, is_header)

        # Position text at the bottom center with some padding
        position = ('center', video.size[1] - 100)
        txt_clip = txt_clip.with_position(position).with_start(start).with_end(end)

        # Add fade in/out animation
        txt_clip = txt_clip.with_effects([vfx.FadeIn(0.5), vfx.FadeOut(0.5)]) #.fadein(0.5).fadeout(0.5)

        text_clips.append(txt_clip)

    # Composite everything together
    final_video = CompositeVideoClip([video] + text_clips)

    # Write to file
    final_video.write_videofile(
        "output_video.mp4",
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=4
    )


if __name__ == "__main__":
    main()