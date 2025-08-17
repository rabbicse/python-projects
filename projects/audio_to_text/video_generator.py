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
import ffmpeg
import argparse # Import the argparse module


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
FONT_SIZE_ARABIC = 40
COLOR_ENGLISH = "#E0E0E0"
COLOR_ARABIC = "#E0E0E0"
BG_COLOR = (0, 0, 0, 200)
LINE_SPACING = 80
SUBTITLE_HEIGHT = 120
CHAR_ANIMATION_DELAY = 0.05
FADE_DURATION = 0.3

# --- DOWNLOAD FUNCTION ---
def download_audio(json_file_path, audio_file_path):
    """
    Parses a JSON file to find the audio URL and downloads the MP3 file.
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        audio_url = data["audio"]["audio_files"][0]["audio_url"]
        print(f"Downloading audio from: {audio_url}")

        response = requests.get(audio_url)
        response.raise_for_status() # Check for HTTP errors

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
    hours, seconds = divmod(seconds, 3600)
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"

def clean_html_tags(text):
    """Remove HTML tags like <sup ...> from text"""
    text = re.sub(r'<[^>]*>', '', text)
    text = re.sub(r'˹|˺', '', text)
    text = re.sub(r'<[^>]*>', '', text)
    return re.sub(r'˹|˺', '', text).strip()

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


# --- SUBTITLE GENERATION FUNCTIONS (from your original script) ---
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

    return total_width, total_height

def process_subtitle_line(line, font, color, is_arabic=False):
    total_width, total_height = preprocess_subtitle(line, font, is_arabic)
    img = Image.new('RGBA', (total_width + 20, total_height + 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([(0, 0), (total_width + 20, total_height + 20)], radius=15, fill=BG_COLOR)
    draw.text((10, 10), line, font=font, fill=color)
    return img, total_width, total_height

def create_subtitle_clips(video, subs, font_english, font_arabic):
    """Generate animated subtitle clips"""
    subtitle_clips = []

    for sub in subs:
        lines = sub.text.split('\n')
        start_time = sub.start.ordinal / 1000
        end_time = sub.end.ordinal / 1000
        duration = end_time - start_time

        for line_idx, line in enumerate(lines):
            if not line.strip():
                continue
            try:
                lang = detect(line)
            except:
                lang = "en"
            is_arabic = lang == "ar"
            font = font_arabic if is_arabic else font_english
            color = COLOR_ARABIC if is_arabic else COLOR_ENGLISH

            if is_arabic:
                # working
                line_img, total_width, _ = process_subtitle_line(line, font, color, True)
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
                #endworking


                # total_width, total_height = preprocess_subtitle(line, font, is_arabic=True)
                # bg_img = Image.new('RGBA', (total_width + 20, total_height + 20), (0, 0, 0, 0))
                # draw_bg = ImageDraw.Draw(bg_img)
                # draw_bg.rounded_rectangle([(0, 0), (total_width + 20, total_height + 20)], radius=15, fill=BG_COLOR)
                # bg_clip = (
                #     ImageClip(np.array(bg_img), duration=end_time - start_time)
                #     .with_position(((video.w - total_width) / 2, video.h - SUBTITLE_HEIGHT - line_idx * LINE_SPACING))
                #     .with_start(start_time)
                #     .with_end(end_time)
                #     .with_effects([vfx.FadeIn(FADE_DURATION), vfx.FadeOut(FADE_DURATION)])
                # )
                # subtitle_clips.append(bg_clip)
                #
                # y_pos = video.h - SUBTITLE_HEIGHT - line_idx * LINE_SPACING
                # base_x = (video.w + total_width) / 2 - 10  # Start from the right edge of the bounding box
                # current_x = base_x
                # print(line)
                # for char_idx, char in enumerate(line):
                #     if char == ' ':
                #         char_bbox = font.getbbox('a')
                #         space_width = font.getlength(' ')
                #         current_x -= space_width
                #         continue
                #
                #     char_bbox = font.getbbox(char)
                #     char_width = char_bbox[2] - char_bbox[0]
                #     char_img = Image.new('RGBA', (char_width + 10, total_height + 20), (0, 0, 0, 0))
                #     draw = ImageDraw.Draw(char_img)
                #     draw.text((5, 10), char, font=font, fill=COLOR_ARABIC)
                #
                #     current_x -= font.getlength(char)
                #
                #     char_clip = (
                #         ImageClip(np.array(char_img), duration=end_time - start_time)
                #         .with_position((current_x, y_pos))
                #         .with_start(start_time + char_idx * CHAR_ANIMATION_DELAY)
                #         .with_end(end_time)
                #         .with_effects([vfx.FadeIn(FADE_DURATION)])
                #     )
                #     subtitle_clips.append(char_clip)
            else:
                total_width, total_height = preprocess_subtitle(line, font, is_arabic=False)
                bg_img = Image.new('RGBA', (total_width + 20, total_height + 20), (0, 0, 0, 0))
                draw_bg = ImageDraw.Draw(bg_img)
                draw_bg.rounded_rectangle([(0, 0), (total_width + 20, total_height + 20)], radius=15, fill=BG_COLOR)
                bg_clip = (
                    ImageClip(np.array(bg_img), duration=end_time - start_time)
                    .with_position(((video.w - total_width) / 2, video.h - SUBTITLE_HEIGHT - line_idx * LINE_SPACING))
                    .with_start(start_time)
                    .with_end(end_time)
                    .with_effects([vfx.FadeIn(FADE_DURATION), vfx.FadeOut(FADE_DURATION)])
                )
                subtitle_clips.append(bg_clip)

                y_pos = video.h - SUBTITLE_HEIGHT - line_idx * LINE_SPACING
                base_x = (video.w - total_width) / 2
                for char_idx, char in enumerate(line):
                    if char == ' ':
                        continue
                    char_bbox = font.getbbox(char)
                    char_width = char_bbox[2] - char_bbox[0]
                    char_img = Image.new('RGBA', (char_width + 10, total_height + 20), (0, 0, 0, 0))
                    draw = ImageDraw.Draw(char_img)
                    draw.text((5, 10), char, font=font, fill=COLOR_ENGLISH)
                    x_pos = base_x + font.getlength(line[:char_idx])
                    char_clip = (
                        ImageClip(np.array(char_img), duration=end_time - start_time)
                        .with_position((x_pos, y_pos))
                        .with_start(start_time + char_idx * CHAR_ANIMATION_DELAY)
                        .with_end(end_time)
                        .with_effects([vfx.FadeIn(FADE_DURATION)])
                    )
                    subtitle_clips.append(char_clip)
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
        # # Step 1: Download MP3 file from JSON
        # print("Step 1: Downloading MP3 file...")
        # if not download_audio(JSON_PATH, AUDIO_PATH):
        #     return
        #
        # Step 2: Merge Canva video and audio using ffmpeg-python
        print("Step 1: Merging video and audio...")

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
        print("Step 2: Generating SRT subtitles...")
        json_to_srt(JSON_PATH, SUBS_PATH)
        print("SRT subtitles generated successfully.")

        # Step 4: Add subtitles to the merged video
        print("Step 3: Adding subtitles to the video...")
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
    finally:
        # Clean up temporary files
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
        if os.path.exists(TEMP_MERGED_PATH):
            os.remove(TEMP_MERGED_PATH)
        if os.path.exists(SUBS_PATH):
            os.remove(SUBS_PATH)


if __name__ == "__main__":
    main()