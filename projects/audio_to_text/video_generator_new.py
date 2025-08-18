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
BASE_INIT_VIDEO_PATH = "data/quran.mp4"
BASE_TEMP_MERGED_PATH = "data/{}-init.mp4"
BASE_SUBS_PATH = "data/{}_subtitles.srt"
BASE_OUTPUT_VIDEO_PATH = "data/{}-video.mp4"
TEMP_DIR = "data/temp_subtitle_images"
CHAPTERS_PATH = "quran/chapters.json"

# Font configuration
FONT_ENGLISH_HEADER_PATH = "fonts/DejaVuSans.ttf"
FONT_ENGLISH_PATH = "fonts/DejaVuSans.ttf"
FONT_ARABIC_HEADER_PATH = "fonts/Amiri-Regular.ttf"
FONT_ARABIC_PATH = "fonts/NotoSansArabic-Regular.ttf"
FALLBACK_FONT_PATH = "fonts/DejaVuSans.ttf"

# Style configuration
FONT_SIZE = 30
FONT_SIZE_ARABIC = 50
FONT_HEADER_SIZE = 100
FONT_HEADER_SIZE_ARABIC = 100
COLOR_ENGLISH = "#E0E0E0"
COLOR_ARABIC = "#E0E0E0"
BG_COLOR = (0, 0, 0, 200)
LINE_SPACING = 80
SUBTITLE_HEIGHT = 120
CHAR_ANIMATION_DELAY = 0.05
HEADER_CHAR_ANIMATION_DELAY = 0.5
FADE_DURATION = 0.01
ARABIC_ANIMATION_SPEED = 0.05  # Speed of Arabic text reveal (lower is faster)


# arabic text
# x = w/2 y = 136, font size 101

# english text
# x = w/2, y = 331


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


def clean_html_tags(text: str) -> str:
    """Remove HTML tags like <sup ...> from text"""
    # Remove tags like <sup foot_note=77642>1</sup>
    text = re.sub(r'<sup[^>]*>.*?</sup>', '', text, flags=re.DOTALL)
    # Remove any remaining generic tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove special bracket-like characters
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
        font_english_header = ImageFont.truetype(FONT_ENGLISH_HEADER_PATH, FONT_HEADER_SIZE)
        font_arabic_header = ImageFont.truetype(FONT_ARABIC_HEADER_PATH, FONT_HEADER_SIZE_ARABIC)
    except IOError:
        print("Warning: Specified fonts not found. Using fallback font.")
        font_english = font_arabic = font_arabic_header = font_english_header = ImageFont.truetype(FALLBACK_FONT_PATH,
                                                                                                   FONT_SIZE)

    return font_english, font_arabic, font_english_header, font_arabic_header


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
    # configuration = {
    #     'delete_harakat': False,
    #     'support_ligatures': True,
    #     'RIAL SIGN': True,
    # }
    # reshaper = arabic_reshaper.ArabicReshaper(configuration=configuration)
    # reshaped_text = reshaper.reshape(line)
    # display_text = get_display(reshaped_text)
    # display_text = display_text[::-1] # for linux we need to add it

    display_text = line[::-1]

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

        # print(f"x: {x_pos} y: {y_pos} => {visible_text}")

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
        return create_arabic_animation(processed_line, font, color, duration, total_width, total_height)
    else:
        # English animation (left-to-right)
        return create_english_animation(processed_line, font, color, duration, total_width, total_height)


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


def create_header_clips(video, surah_no, font_english, font_arabic):
    """Generate subtitle clips with proper compositing"""
    header_clips = []

    with open(CHAPTERS_PATH, 'r+', encoding='utf-8') as f:
        data = json.load(f)

    data_en = data["en"][f"{surah_no}"]
    data_ar = data["ar"][f"{surah_no}"]

    surah_name_en = data_en["transliteratedName"]
    surah_name_ar = data_ar["transliteratedName"]

    # draw arabic surah name
    line, total_width, total_height = preprocess_subtitle(surah_name_ar, font_arabic, is_arabic=True)
    img = Image.new('RGBA', (total_width + 30, total_height + 30), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), line, font=font_arabic, fill=COLOR_ARABIC)
    line_clip = ImageClip(np.array(img))
    y_pos = 136
    x_pos = (video.w - total_width) / 2
    duration = video.duration
    line_clip = (
        line_clip
        .with_duration(duration=duration)
        .with_position((x_pos, y_pos))
        .with_start(0)
        .with_end(duration)
        .with_effects([vfx.FadeIn(FADE_DURATION)])
    )
    header_clips.append(line_clip)

    # english header
    # draw arabic surah name
    line, total_width, total_height = preprocess_subtitle(surah_name_en, font_english, is_arabic=False)
    img = Image.new('RGBA', (total_width + 30, total_height + 30), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), line, font=font_english, fill=COLOR_ENGLISH)
    line_clip = ImageClip(np.array(img))
    y_pos = 331
    x_pos = (video.w - total_width) / 2
    duration = video.duration
    line_clip = (
        line_clip
        .with_duration(duration=duration)
        .with_position((x_pos, y_pos))
        .with_start(0)
        .with_end(duration)
        .with_effects([vfx.FadeIn(FADE_DURATION)])
    )
    header_clips.append(line_clip)

    return header_clips


# def create_header_clips_updated(video, surah_no, font_english, font_arabic):
#     """Generate letter-by-letter animated header clips with fade + slide effect"""
#     header_clips = []
#
#     with open(CHAPTERS_PATH, 'r', encoding='utf-8') as f:
#         data = json.load(f)
#
#     data_en = data["en"][f"{surah_no}"]
#     data_ar = data["ar"][f"{surah_no}"]
#
#     surah_name_en = data_en["transliteratedName"]
#     surah_name_ar = data_ar["transliteratedName"]
#
#     total_duration = video.duration
#
#     def make_letter_animation(text, font, color, y_final, is_arabic=False):
#         """Create left-to-right animation for English text"""
#         line, total_width, total_height = preprocess_subtitle(text, font, is_arabic)
#         bg_img = Image.new('RGBA', (total_width + 20, total_height + 20), (0, 0, 0, 0))
#
#         display_text = line
#         if is_arabic:
#             # # Reshape and get display text
#             # configuration = {
#             #     'delete_harakat': False,
#             #     'support_ligatures': True,
#             #     'RIAL SIGN': True,
#             # }
#             # reshaper = arabic_reshaper.ArabicReshaper(configuration=configuration)
#             # reshaped_text = reshaper.reshape(line)
#             # display_text = get_display(reshaped_text)
#             display_text = line[::-1] # for linux we need to add it
#
#         # Step 3: Create a full pre-rendered image of the RTL text
#         draw = ImageDraw.Draw(bg_img)
#         draw.text((10, 10), display_text, font=font, fill=color)
#         full_text_array = np.array(bg_img)
#
#         def make_frame(t):
#             # progress = min(1.0, max(0.0, t / duration))
#             frame_img = bg_img.copy()
#             draw = ImageDraw.Draw(frame_img)
#
#             # chars_to_show = int(len(line) * progress)
#             chars_to_show = int(len(line) * min(1, t / (len(line) * HEADER_CHAR_ANIMATION_DELAY)))
#             visible_text = display_text[:chars_to_show]
#
#             # Left-aligned for English
#             draw.text((10, 0), visible_text, font=font, fill=color)
#
#             frame_array = np.array(frame_img)
#             if frame_array.shape[2] == 3:
#                 alpha = np.full(frame_array.shape[:2], 255, dtype=np.uint8)
#                 frame_array = np.dstack((frame_array, alpha))
#             return frame_array
#
#         def make_frame_arabic(t):
#             """Generate frame at time t with animated text"""
#             # Calculate progress (0 to 1)
#             # progress = min(1.0, max(0.0, t / duration))
#
#             # Create a new image with the background
#             frame_img = bg_img.copy()
#             draw = ImageDraw.Draw(frame_img)
#
#             # Calculate how many characters to show
#             # chars_to_show = int(len(display_text) * progress)
#             chars_to_show = int(len(display_text) * min(1, t / (len(display_text) * HEADER_CHAR_ANIMATION_DELAY)))
#             visible_text = display_text[:chars_to_show]
#
#             # Calculate text position (right-aligned)
#             text_width = font.getlength(visible_text)
#             x_pos = (total_width + 20) - text_width - 10  # Right padding
#             y_pos = 10
#
#             print(f"x: {x_pos} y: {y_pos} => {visible_text}")
#
#             # Draw the visible portion of the text
#             draw.text((x_pos, y_pos), visible_text, font=font, fill=color)
#
#             # Convert to numpy array and ensure RGBA format
#             frame_array = np.array(frame_img)
#             if frame_array.shape[2] == 3:  # If RGB, add alpha channel
#                 alpha = np.full(frame_array.shape[:2], 255, dtype=np.uint8)
#                 frame_array = np.dstack((frame_array, alpha))
#             return frame_array
#
#         def make_frame_arabic_updated(t):
#             """Generate frame at time t with animated text"""
#             # Calculate progress (0 to 1)
#             progress = min(1.0, max(0.0, t / total_duration))
#             visible_width = int(total_width * progress)
#
#             # Crop the visible portion (right side)
#             cropped = full_text_array[:, -visible_width:] if visible_width > 0 else full_text_array[:, :0]
#
#             # Pad to maintain canvas dimensions
#             if visible_width < total_width:
#                 padding = np.zeros((total_height, total_width - visible_width, 4), dtype=np.uint8)
#                 frame = np.hstack([padding, cropped])
#             else:
#                 frame = full_text_array
#
#             return frame
#
#         return VideoClip(make_frame_arabic_updated if is_arabic else make_frame, duration=total_duration, is_mask=False), total_width, total_height
#
#
#     # Arabic header
#     arabic_animation, total_width, total_height = make_letter_animation(surah_name_ar, font_arabic, COLOR_ARABIC, y_final=136, is_arabic=True)
#     x_pos = (video.w - total_width) / 2
#     y_pos = 136
#     positioned_clip = arabic_animation.with_position((x_pos, y_pos)) \
#         .with_start(0) \
#         .with_duration(video.duration)
#     header_clips.append(positioned_clip)
#
#     # English header
#     # header_clips.append(make_letter_animation(surah_name_en, font_english, COLOR_ENGLISH, y_final=331, is_arabic=False))
#     english_animation, total_width, total_height = make_letter_animation(surah_name_en, font_english, COLOR_ENGLISH, y_final=331, is_arabic=False)
#     x_pos = (video.w - total_width) / 2
#     y_pos = 331
#     positioned_clip = english_animation.with_position((x_pos, y_pos)) \
#         .with_start(0) \
#         .with_duration(video.duration)
#     header_clips.append(positioned_clip)
#
#     return header_clips


def create_rtl_arabic_animation(text, font_path, font_size=40, duration=5, bg_color=(0, 0, 0, 0)):
    # Step 1: Reshape and force RTL
    reshaped_text = arabic_reshaper.reshape(text)
    display_text = get_display(reshaped_text)  # Correct RTL order
    display_text = display_text[::-1]

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


def create_slide_animation(text, font_path, font_size, duration, bg_color, is_rtl=True):
    """Create sliding animation that completes within 5 seconds max and stays visible"""
    # Calculate animation duration (min of 5 seconds or total_duration)
    anim_duration = min(5.0, duration)

    # Prepare text (RTL for Arabic)
    if is_rtl:
        reshaped_text = arabic_reshaper.reshape(text)
        display_text = get_display(reshaped_text)
        display_text = display_text[::-1]
    else:
        display_text = text

    # Load font
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.truetype(FALLBACK_FONT_PATH, font_size)

    # Calculate dimensions
    text_bbox = font.getbbox(display_text)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Create canvas
    canvas_width = text_width + 40
    canvas_height = text_height + 40
    bg_img = Image.new("RGBA", (canvas_width, canvas_height), bg_color)
    draw = ImageDraw.Draw(bg_img)

    # # Draw background
    # draw.rounded_rectangle([(0, 0), (canvas_width, canvas_height)],
    #                        radius=15, fill=BG_COLOR)

    # Position text
    x_pos = canvas_width - text_width - 10 if is_rtl else 10
    draw.text((x_pos, 10), display_text, font=font, fill="white")
    full_text_array = np.array(bg_img)

    def make_frame(t):
        if t < anim_duration:  # Animation phase
            progress = min(1.0, t / anim_duration)
            visible_width = int(canvas_width * progress)

            if is_rtl:  # RTL: crop from right
                cropped = full_text_array[:, -visible_width:] if visible_width > 0 else full_text_array[:, :0]
                padding = np.zeros((canvas_height, canvas_width - visible_width, 4), dtype=np.uint8)
                frame = np.hstack([padding, cropped])
            else:  # LTR: crop from left
                cropped = full_text_array[:, :visible_width] if visible_width > 0 else full_text_array[:, :0]
                padding = np.zeros((canvas_height, canvas_width - visible_width, 4), dtype=np.uint8)
                frame = np.hstack([cropped, padding])
        else:  # After animation - show full text
            frame = full_text_array

        return frame

    return VideoClip(make_frame, duration=duration)


def create_header_clips_updated(video, surah_no, font_english, font_arabic):
    """Generate header clips using the new RTL animation approach"""
    header_clips = []

    with open(CHAPTERS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    data_en = data["en"][f"{surah_no}"]
    data_ar = data["ar"][f"{surah_no}"]

    surah_name_en = data_en["transliteratedName"]
    surah_name_ar = data_ar["transliteratedName"]

    # Arabic header
    arabic_clip = create_slide_animation(
        text=surah_name_ar,
        font_path=FONT_ARABIC_HEADER_PATH,
        font_size=FONT_HEADER_SIZE_ARABIC,
        duration=video.duration,
        bg_color=(0, 0, 0, 0),
        is_rtl=True)

    # Get dimensions for positioning
    _, width_ar, height_ar = preprocess_subtitle(surah_name_ar, font_arabic, is_arabic=True)
    header_clips.append(arabic_clip.with_position(((video.w - width_ar) / 2, 136)))

    # English header (using same approach but left-to-right)
    english_clip = create_slide_animation(
        text=surah_name_en,
        font_path=FONT_ENGLISH_HEADER_PATH,
        font_size=FONT_HEADER_SIZE,
        duration=video.duration,
        bg_color=(0, 0, 0, 0),
        is_rtl=False)

    _, width_en, height_en = preprocess_subtitle(surah_name_en, font_english, is_arabic=False)
    header_clips.append(english_clip.with_position(((video.w - width_en) / 2, 331)))

    return header_clips


def create_arabic_animation_new(line, font, color, duration, total_width, total_height):
    """Create Arabic animation using the new RTL approach"""
    return create_rtl_arabic_animation(
        text=line,
        font_path=FONT_ARABIC_PATH,
        font_size=FONT_SIZE_ARABIC,
        duration=duration,
        bg_color=BG_COLOR)


def create_english_animation_new(line, font, color, duration, total_width, total_height):
    """Create LTR animation using slide effect"""
    # Create static text image
    bg_img = Image.new('RGBA', (total_width + 40, total_height + 40), BG_COLOR)
    draw = ImageDraw.Draw(bg_img)
    draw.rounded_rectangle([(0, 0), (total_width + 40, total_height + 40)],
                           radius=15, fill=BG_COLOR)
    draw.text((20, 20), line, font=font, fill=color)

    static_clip = ImageClip(np.array(bg_img)).with_duration(duration)

    # Slide in from left
    return static_clip.with_effects([
        vfx.SlideIn(duration / 2, 'left'),
        vfx.FadeIn(FADE_DURATION)
    ])


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
        font_english, font_arabic, font_english_header, font_arabic_header = setup_environment()
        video = VideoFileClip(TEMP_MERGED_PATH)
        subs = pysrt.open(SUBS_PATH)

        header_clips = create_header_clips_updated(video, surah_number, font_english_header, font_arabic_header)

        subtitle_clips = create_subtitle_clips(video, subs, font_english, font_arabic)
        final = CompositeVideoClip([video] + header_clips + subtitle_clips)
        # final = CompositeVideoClip([video] + header_clips)
        final.write_videofile(
            OUTPUT_VIDEO_PATH,
            fps=video.fps,
            codec="libx264",
            audio_codec="aac",
            threads=8,
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
