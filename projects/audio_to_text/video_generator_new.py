import json
import re
import os
import shutil
import numpy as np
import pysrt
import requests
from langdetect import detect
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
from moviepy import *
from moviepy.video.fx import FadeIn, FadeOut
import ffmpeg
import argparse

# --- CONFIGURATION ---
# Base paths that will be formatted with the surah number
BASE_JSON_PATH = "quran/{}.json"
BASE_AUDIO_PATH = "data/{}.mp3"
BASE_INIT_VIDEO_PATH = "data/{}.mp4"
BASE_TEMP_MERGED_PATH = "data/temp_merged_{}.mp4"
BASE_SUBS_PATH = "data/{}_subtitles.srt"
BASE_OUTPUT_VIDEO_PATH = "data/{}-video-temp.mp4"
TEMP_DIR = "data/temp_subtitle_images"

# Font configuration
FONT_ENGLISH_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_ARABIC_PATH = "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf"
FALLBACK_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Style configuration
FONT_SIZE = 30
FONT_SIZE_ARABIC = 50
COLOR_ENGLISH = "#E0E0E0"
COLOR_ARABIC = "#E0E0E0"
BG_COLOR = (0, 0, 0, 200)
LINE_SPACING = 80
SUBTITLE_HEIGHT = 120
CHAR_ANIMATION_DELAY = 0.02
FADE_DURATION = 0.01
ARABIC_ANIMATION_SPEED = 0.02  # Speed of Arabic text reveal (lower is faster)


# --- DOWNLOAD FUNCTION ---
def download_audio(json_file_path, audio_file_path):
    """Parses a JSON file to find the audio URL and downloads the MP3 file."""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        audio_url = data["audio"]["audio_files"][0]["audio_url"]
        print(f"Downloading audio from: {audio_url}")

        response = requests.get(audio_url)
        response.raise_for_status()  # Check for HTTP errors

        os.makedirs(os.path.dirname(audio_file_path), exist_ok=True)
        with open(audio_file_path, 'wb') as f:
            f.write(response.content)

        print(f"Audio downloaded successfully to: {audio_file_path}")
        return True
    except (requests.exceptions.RequestException, KeyError) as e:
        print(f"Error downloading audio: {e}")
        return False


# --- SRT GENERATION FUNCTIONS ---
def ms_to_srt_time(ms):
    """Convert milliseconds to SRT format: HH:MM:SS,mmm"""
    seconds, millis = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"


def clean_html_tags(text):
    """Remove HTML tags like <sup ...> from text"""
    text = re.sub(r'<[^>]*>', '', text)
    text = re.sub(r'[˹˺]', '', text)
    text = re.sub(r'<[^>]*>', '', text)
    return re.sub(r'[˹˺]', '', text).strip()


def generate_srt(data):
    verse_timings = data["audio"]["audio_files"][0]["verse_timings"]
    verses = {v["verse_key"]: v for v in data["surah_verses"]}

    srt_lines = []
    counter = 1

    for timing in verse_timings:
        verse_key = timing["verse_key"]
        if verse_key not in verses:
            continue

        arabic = verses[verse_key]["arabic_text"]
        english = clean_html_tags(verses[verse_key]["en_text"])

        start_time = ms_to_srt_time(timing["timestamp_from"])
        end_time = ms_to_srt_time(timing["timestamp_to"])

        srt_lines.append(f"{counter}")
        srt_lines.append(f"{start_time} --> {end_time}")
        srt_lines.append(arabic)
        srt_lines.append(english)
        srt_lines.append("")

        counter += 1

    return "\n".join(srt_lines)


def json_to_srt(json_file, srt_file):
    with open(json_file, "r+", encoding="utf-8") as f:
        data = json.load(f)
    srt_content = generate_srt(data)
    with open(srt_file, "w+", encoding="utf-8") as f:
        f.write(srt_content)


# --- SUBTITLE GENERATION FUNCTIONS ---
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


def preprocess_subtitle(line, font, is_arabic=False):
    """Process a single line of subtitle text"""
    if is_arabic:
        configuration = {
            'delete_harakat': False,
            'support_ligatures': True,
            'RIAL SIGN': True,
        }
        reshaper = arabic_reshaper.ArabicReshaper(configuration=configuration)
        reshaped_text = reshaper.reshape(line)
        line = get_display(reshaped_text)

    text_bbox = font.getbbox(line)
    total_width = text_bbox[2] - text_bbox[0]
    total_height = text_bbox[3] - text_bbox[1] + 20

    return line, total_width, total_height


def create_arabic_animation(line, font, color, duration, total_width, total_height):
    """Create an animated Arabic text clip with proper channel handling"""
    # Reshape and get display text
    configuration = {
        'delete_harakat': False,
        'support_ligatures': True,
        'RIAL SIGN': True,
    }
    reshaper = arabic_reshaper.ArabicReshaper(configuration=configuration)
    reshaped_text = reshaper.reshape(line)
    display_text = get_display(reshaped_text)
    display_text = display_text[::-1]

    # Create background image with consistent dimensions
    bg_img = Image.new('RGBA', (total_width + 20, total_height + 20), (0, 0, 0, 0))
    draw_bg = ImageDraw.Draw(bg_img)
    draw_bg.rounded_rectangle([(0, 0), (total_width + 20, total_height + 20)],
                              radius=15, fill=BG_COLOR)

    def make_frame(t):
        """Generate frame at time t with animated text"""
        # Calculate progress (0 to 1)
        # progress = min(1.0, max(0.0, t / duration))

        # Create a new image with the background
        frame_img = bg_img.copy()
        draw = ImageDraw.Draw(frame_img)

        # Calculate how many characters to show
        # chars_to_show = int(len(display_text) * progress)
        chars_to_show = int(len(line) * min(1, t / (len(line) * ARABIC_ANIMATION_SPEED)))
        visible_text = display_text[:chars_to_show]

        # Calculate text position (right-aligned)
        text_width = font.getlength(visible_text)
        x_pos = (total_width + 20) - text_width - 10  # Right padding
        y_pos = 10

        # Draw the visible portion of the text
        draw.text((x_pos, y_pos), visible_text, font=font, fill=color)

        # Convert to numpy array and ensure RGBA format
        frame_array = np.array(frame_img)
        if frame_array.shape[2] == 3:  # If RGB, add alpha channel
            alpha = np.full(frame_array.shape[:2], 255, dtype=np.uint8)
            frame_array = np.dstack((frame_array, alpha))
        return frame_array

    # Create clip with ismask=False to indicate this is not a mask
    return VideoClip(make_frame, duration=duration, is_mask=False)


def create_english_animation(line, font, color, duration, total_width, total_height):
    """Create left-to-right animation for English text"""
    bg_img = Image.new('RGBA', (total_width + 20, total_height + 20), (0, 0, 0, 0))
    draw_bg = ImageDraw.Draw(bg_img)
    draw_bg.rounded_rectangle([(0, 0), (total_width + 20, total_height + 20)],
                              radius=15, fill=BG_COLOR)

    def make_frame(t):
        # progress = min(1.0, max(0.0, t / duration))
        frame_img = bg_img.copy()
        draw = ImageDraw.Draw(frame_img)

        # chars_to_show = int(len(line) * progress)
        chars_to_show = int(len(line) * min(1, t / (len(line) * CHAR_ANIMATION_DELAY)))
        visible_text = line[:chars_to_show]

        # Left-aligned for English
        draw.text((10, 10), visible_text, font=font, fill=color)

        frame_array = np.array(frame_img)
        if frame_array.shape[2] == 3:
            alpha = np.full(frame_array.shape[:2], 255, dtype=np.uint8)
            frame_array = np.dstack((frame_array, alpha))
        return frame_array

    return VideoClip(make_frame, duration=duration, is_mask=False)


def process_subtitle_line(line, font, color, is_arabic=False, duration=5.0):
    """Process a subtitle line with proper image format handling"""
    processed_line, total_width, total_height = preprocess_subtitle(line, font, is_arabic)

    if is_arabic:
        return create_arabic_animation(line, font, color, duration, total_width, total_height)
    else:
        # English animation (left-to-right)
        return create_english_animation(line, font, color, duration, total_width, total_height)


def apply_fade_effects(clip, fade_duration):
    """Apply fade effects with proper color handling"""
    # Ensure clip has alpha channel
    if clip.mask is None:
        clip = clip.with_mask()

    # Convert initial_color to RGB tuple if needed
    fade_in = vfx.CrossFadeIn(
        duration=fade_duration,
        # initial_color=[0, 0, 0, 0]  # RGB black
    )

    fade_out = vfx.CrossFadeOut(
        duration=fade_duration,
        # final_color=[0, 0, 0, 0]  # RGB black
    )

    return clip.with_effects([fade_in, fade_out])


def create_subtitle_clips(video, subs, font_english, font_arabic):
    """Generate subtitle clips with proper compositing"""
    subtitle_clips = []
    video_size = video.size

    for sub in subs:
        lines = sub.text.split('\n')
        start_time = sub.start.ordinal / 1000
        end_time = sub.end.ordinal / 1000
        duration = end_time - start_time

        # Separate Arabic and English lines
        arabic_lines = []
        english_lines = []

        for line in lines:
            if not line.strip():
                continue
            try:
                lang = detect(line)
            except:
                lang = "en"
            if lang == "ar":
                arabic_lines.append(line)
            else:
                english_lines.append(line)

        for line_idx, line in enumerate(arabic_lines):
            font = font_arabic
            color = COLOR_ARABIC
            line_clip = process_subtitle_line(line, font, color, True, duration)

            # Position the clip
            _, total_width, total_height = preprocess_subtitle(line, font, True)
            # y_pos = video_size[1] - SUBTITLE_HEIGHT - line_idx * LINE_SPACING
            y_pos = video_size[1] - SUBTITLE_HEIGHT - (len(english_lines) * LINE_SPACING) - line_idx * LINE_SPACING - 80
            x_pos = (video_size[0] - total_width) / 2

            try:
                # Set clip properties
                # Configure clip using current MoviePy API
                positioned_clip = line_clip.with_position((x_pos, y_pos)) \
                    .with_start(start_time) \
                    .with_duration(duration)

                positioned_clip = positioned_clip.with_effects([vfx.FadeIn(FADE_DURATION, initial_color=[0, 0, 0, 0])])

                subtitle_clips.append(positioned_clip)
            except Exception as ex:
                print(ex)

        for line_idx, line in enumerate(english_lines):
            font = font_english
            color = COLOR_ENGLISH
            line_clip = process_subtitle_line(line, font, color, False, duration)

            # Position the clip
            _, total_width, total_height = preprocess_subtitle(line, font, False)
            # y_pos = video_size[1] - SUBTITLE_HEIGHT - line_idx * LINE_SPACING
            y_pos = video_size[1] - SUBTITLE_HEIGHT - line_idx * LINE_SPACING
            x_pos = (video_size[0] - total_width) / 2

            try:
                # Set clip properties
                # Configure clip using current MoviePy API
                positioned_clip = line_clip.with_position((x_pos, y_pos)) \
                    .with_start(start_time) \
                    .with_duration(duration)

                positioned_clip = positioned_clip.with_effects([vfx.FadeIn(FADE_DURATION, initial_color=[0, 0, 0, 0])])

                # positioned_clip = apply_fade_effects(positioned_clip, FADE_DURATION)

                subtitle_clips.append(positioned_clip)
            except Exception as ex:
                print(ex)

    return subtitle_clips


# --- MAIN EXECUTION ---
def main():
    # Setup argparse
    parser = argparse.ArgumentParser(description="Generate a subtitled video from a JSON file and audio.")
    parser.add_argument("surah_number", type=int, help="The number of the surah (e.g., 113)")
    args = parser.parse_args()
    surah_number = args.surah_number

    # Update file paths with the dynamic surah number
    JSON_PATH = BASE_JSON_PATH.format(surah_number)
    AUDIO_PATH = BASE_AUDIO_PATH.format(surah_number)
    INIT_VIDEO_PATH = BASE_INIT_VIDEO_PATH.format(surah_number)
    TEMP_MERGED_PATH = BASE_TEMP_MERGED_PATH.format(surah_number)
    SUBS_PATH = BASE_SUBS_PATH.format(surah_number)
    OUTPUT_VIDEO_PATH = BASE_OUTPUT_VIDEO_PATH.format(surah_number)

    try:
        # Step 1: Download MP3 file from JSON
        print("Step 1: Downloading MP3 file...")
        if not os.path.exists(AUDIO_PATH) and not download_audio(JSON_PATH, AUDIO_PATH):
            return

        # Step 2: Merge Canva video and audio using ffmpeg-python
        print("Step 1: Merging video and audio...")
        if not os.path.exists(TEMP_MERGED_PATH):
            (
                ffmpeg
                .input(INIT_VIDEO_PATH, stream_loop=-1)
                .video
                .output(
                    ffmpeg.input(AUDIO_PATH).audio,
                    TEMP_MERGED_PATH,
                    vcodec="libx264",
                    acodec="aac",
                    pix_fmt="yuv420p",
                    shortest=None,
                    map_metadata="-1"
                )
                .run(overwrite_output=True)
            )

            print("Video and audio merged successfully.")

        # Step 3: Generate SRT subtitles
        if not os.path.exists(SUBS_PATH):
            print("Step 2: Generating SRT subtitles...")
            json_to_srt(JSON_PATH, SUBS_PATH)
            print("SRT subtitles generated successfully.")

        # Step 4: Add subtitles to the merged video
        print("Step 4: Adding subtitles to the video...")
        font_english, font_arabic = setup_environment()
        video = VideoFileClip(TEMP_MERGED_PATH)
        subs = pysrt.open(SUBS_PATH)
        subtitle_clips = create_subtitle_clips(video, subs, font_english, font_arabic)
        final = CompositeVideoClip([video] + subtitle_clips)
        final.write_videofile(
            OUTPUT_VIDEO_PATH,
            fps=video.fps,
            codec="libx264",
            audio_codec="aac",
            threads=4,
            preset="medium"
        )
        print(f"Final video created at {OUTPUT_VIDEO_PATH}")

    except Exception as e:
        print(f"Error: {e}")
    # finally:
    #     # Clean up temporary files
    #     if os.path.exists(TEMP_DIR):
    #         shutil.rmtree(TEMP_DIR)
    #     if os.path.exists(TEMP_MERGED_PATH):
    #         os.remove(TEMP_MERGED_PATH)
    #     if os.path.exists(SUBS_PATH):
    #         os.remove(SUBS_PATH)


if __name__ == "__main__":
    main()
