import numpy as np
import pysrt
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, vfx
from langdetect import detect
from PIL import Image, ImageDraw, ImageFont
import os
import shutil
import arabic_reshaper
from bidi.algorithm import get_display
from networkx.algorithms.distance_measures import radius

# --- CONFIGURATION ---
VIDEO_PATH = "data/113-init.mp4"
SUBS_PATH = "data/113_subtitles.srt"
OUTPUT_VIDEO_PATH = "data/113-video.mp4"
TEMP_DIR = "data/temp_subtitle_images"

# Font configuration
FONT_ENGLISH_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_ARABIC_PATH = "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf"
FALLBACK_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Style configuration
FONT_SIZE = 30
FONT_SIZE_ARABIC = 40
COLOR_ENGLISH = "#E0E0E0"  # Soft light gray
COLOR_ARABIC = "#E0E0E0"  # Professional sky blue
BG_COLOR = (0, 0, 0, 200)  # Semi-transparent black background
LINE_SPACING = 80
SUBTITLE_HEIGHT = 120
CHAR_ANIMATION_DELAY = 0.05  # Time between characters appearing
FADE_DURATION = 0.3  # Fade in/out duration


# --- END CONFIGURATION ---

def setup_environment():
    """Initialize directories and fonts"""
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR)

    try:
        font_english = ImageFont.truetype(FONT_ENGLISH_PATH, FONT_SIZE)
        font_arabic = ImageFont.truetype(FONT_ARABIC_PATH, FONT_SIZE_ARABIC)
    except IOError:
        print("Warning: Specified fonts not found. Using fallback font.")
        font_english = font_arabic = ImageFont.truetype(FALLBACK_FONT_PATH, FONT_SIZE)

    return font_english, font_arabic

def preprocess_subtitle(line, font, color, is_arabic=False):
    """Process a single line of subtitle text"""
    if is_arabic:
        # Step 1: Reshape Arabic text
        configuration = {
            'delete_harakat': False,
            'support_ligatures': True,
            'RIAL SIGN': True,  # Replace ر ي ا ل with ﷼
        }
        reshaper = arabic_reshaper.ArabicReshaper(configuration=configuration)
        reshaped_text = reshaper.reshape(line)
        # rev_text = reshaped_text[::-1]
        line = get_display(reshaped_text)

    text_bbox = font.getbbox(line)
    total_width = text_bbox[2] - text_bbox[0]
    total_height = text_bbox[3] - text_bbox[1] + 20

    return total_width, total_height


def process_subtitle_line(line, font, color, is_arabic=False):
    total_width, total_height = preprocess_subtitle(line, font, color, is_arabic)

    # Create image with background
    img = Image.new('RGBA', (total_width + 20, total_height + 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw background rectangle
    draw.rounded_rectangle(
        [(0, 0), (total_width + 20, total_height + 20)],
        radius=15,
        fill=BG_COLOR
    )

    # Draw text
    draw.text(
        (10, 10),
        line,
        font=font,
        fill=color
    )

    return img, total_width, total_height


def create_subtitle_clips(video, subs, font_english, font_arabic):
    """Generate animated subtitle clips"""
    subtitle_clips = []

    for sub in subs:
        lines = sub.text.split('\n')
        start_time = sub.start.ordinal / 1000
        end_time = sub.end.ordinal / 1000

        for line_idx, line in enumerate(lines):
            # print(line)
            if not line.strip():
                continue

            try:
                lang = detect(line)
            except:
                lang = "en"

            is_arabic = lang == "ar"
            font = font_arabic if is_arabic else font_english
            color = COLOR_ARABIC if is_arabic else COLOR_ENGLISH

            # Process the entire line as one unit for Arabic
            if is_arabic:
                line_img, total_width, total_height = process_subtitle_line(line, font, color, True)
                # img_path = os.path.join(TEMP_DIR, f"sub_{sub.index}_{line_idx}.png")
                # line_img.save(img_path)

                line_clip = ImageClip(np.array(line_img), duration=end_time - start_time)
                y_pos = video.h - SUBTITLE_HEIGHT - line_idx * LINE_SPACING
                x_pos = (video.w - total_width) / 2

                line_clip = (
                    line_clip
                    .with_position((x_pos, y_pos))
                    .with_start(start_time)
                    .with_end(end_time)
                    .with_effects([vfx.FadeIn(FADE_DURATION)])
                )
                subtitle_clips.append(line_clip)

            else:
                # English - character by character animation
                total_width, total_height = preprocess_subtitle(line, font, color)

                # Create a single background image for the whole line
                bg_img = Image.new('RGBA', (total_width + 20, total_height + 20), (0, 0, 0, 0))
                draw_bg = ImageDraw.Draw(bg_img)
                draw_bg.rounded_rectangle(
                    [(0, 0), (total_width + 20, total_height + 20)],
                    radius=15,
                    fill=BG_COLOR
                )

                # bg_path = os.path.join(TEMP_DIR, f"sub_bg_{sub.index}_{line_idx}.png")
                # bg_img.save(bg_path)

                # Position of the background bar
                y_pos = video.h - SUBTITLE_HEIGHT - line_idx * LINE_SPACING
                x_pos = (video.w - total_width) / 2

                # Create the background clip that stays for the whole subtitle duration
                bg_clip = (
                    ImageClip(np.array(bg_img), duration=end_time - start_time)
                    .with_position((x_pos, y_pos))
                    .with_start(start_time)
                    .with_end(end_time)
                    .with_effects([vfx.FadeIn(FADE_DURATION), vfx.FadeOut(FADE_DURATION)])
                )
                subtitle_clips.append(bg_clip)

                ## animation
                y_pos = video.h - SUBTITLE_HEIGHT - line_idx * LINE_SPACING
                base_x = (video.w - total_width) / 2

                for char_idx, char in enumerate(line):
                    if char == ' ':
                        continue

                    char_bbox = font.getbbox(char)
                    char_width = char_bbox[2] - char_bbox[0]

                    # Create individual character image
                    char_img = Image.new('RGBA', (char_width + 10, total_height + 20), (0, 0, 0, 0))
                    draw = ImageDraw.Draw(char_img)
                    draw.text(
                        (5, 10),
                        char,
                        font=font,
                        fill=color
                    )

                    # img_path = os.path.join(TEMP_DIR, f"sub_{sub.index}_{line_idx}_{char_idx}.png")
                    # char_img.save(img_path)

                    char_clip = ImageClip(np.array(char_img), duration=end_time - start_time)
                    x_pos = base_x + font.getlength(line[:char_idx])

                    char_clip = (
                        char_clip
                        .with_position((x_pos, y_pos))
                        .with_start(start_time + char_idx * CHAR_ANIMATION_DELAY)
                        .with_end(end_time)
                        .with_effects([vfx.FadeIn(FADE_DURATION)])
                    )
                    subtitle_clips.append(char_clip)

    return subtitle_clips


def main():
    try:
        # Initialize environment
        font_english, font_arabic = setup_environment()

        # Load video and subtitles
        video = VideoFileClip(VIDEO_PATH)
        subs = pysrt.open(SUBS_PATH)

        # Create subtitle clips
        subtitle_clips = create_subtitle_clips(video, subs, font_english, font_arabic)

        # Compose final video
        final = CompositeVideoClip([video] + subtitle_clips)

        # Write output
        final.write_videofile(
            OUTPUT_VIDEO_PATH,
            fps=video.fps,
            codec="libx264",
            audio_codec="aac",
            threads=4,
            preset="medium"
        )
        print("Video created successfully!")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)


if __name__ == "__main__":
    main()
