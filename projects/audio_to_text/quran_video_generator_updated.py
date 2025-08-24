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

os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"
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
FONT_ARABIC_PATH = "fonts/Amiri-Regular.ttf"
FALLBACK_FONT_PATH = "fonts/DejaVuSans.ttf"

# Style configuration
FONT_SIZE = 30
FONT_SIZE_MULTILINE = 20
FONT_SIZE_ARABIC = 50
FONT_SIZE_ARABIC_MULTILINE = 25
FONT_HEADER_SIZE = 100
FONT_HEADER_MEANING_SIZE = 40
FONT_HEADER_SIZE_ARABIC = 120
COLOR_ENGLISH = "#E0E0E0"
COLOR_ARABIC = "#E0E0E0"
BG_COLOR = (0, 0, 0, 200)
LINE_SPACING = 130
SUBTITLE_HEIGHT = 230
CHAR_ANIMATION_DELAY = 0.02
HEADER_CHAR_ANIMATION_DELAY = 0.3
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


def wrap_text(text, font, max_width, is_arabic=False):
    """Wrap text into multiple lines based on maximum width"""
    if is_arabic:
        # For Arabic, we need to process the text first
        configuration = {
            'delete_harakat': False,
            'support_ligatures': True,
            'RIAL SIGN': True,
        }
        reshaper = arabic_reshaper.ArabicReshaper(configuration=configuration)
        reshaped_text = reshaper.reshape(text)
        text = get_display(reshaped_text)
        text = text[::-1]  # Reverse for proper RTL display

    words = text.split()
    lines = []
    current_line = []

    for word in words:
        # Test if adding this word exceeds max width
        test_line = ' '.join(current_line + [word])
        test_width = font.getlength(test_line)

        if test_width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return lines


def process_subtitle_line(line, font, color, is_arabic=False, duration=5.0, max_width=800, is_draw_bg=True):
    """Process a subtitle line with text wrapping"""
    # Wrap the text into multiple lines
    wrapped_lines = wrap_text(line, font, max_width, is_arabic)

    if len(wrapped_lines) == 1:
        # Single line - use existing animation
        if is_arabic:
            return create_slide_animation(
                text=wrapped_lines[0],
                font_path=FONT_ARABIC_PATH,
                font_size=FONT_SIZE_ARABIC,
                duration=duration,
                bg_color=(0, 0, 0, 0),
                is_rtl=True,
                is_draw_bg=is_draw_bg,
                h_pad=40)
        else:
            return create_slide_animation(
                text=wrapped_lines[0],
                font_path=FONT_ENGLISH_PATH,
                font_size=FONT_SIZE,
                duration=duration,
                bg_color=(0, 0, 0, 0),
                is_rtl=False,
                is_draw_bg=is_draw_bg,
                h_pad=40)
    else:
        # Multiple lines - Create a single image with background and text
        # Load appropriate font
        # if is_arabic:
        #     try:
        #         font_obj = ImageFont.truetype(FONT_ARABIC_PATH, FONT_SIZE_ARABIC)
        #     except:
        #         font_obj = ImageFont.truetype(FALLBACK_FONT_PATH, FONT_SIZE_ARABIC)
        # else:
        #     try:
        #         font_obj = ImageFont.truetype(FONT_ENGLISH_PATH, FONT_SIZE)
        #     except:
        #         font_obj = ImageFont.truetype(FALLBACK_FONT_PATH, FONT_SIZE)
        #
        # # Calculate dimensions
        # line_heights = []
        # max_line_width = 0
        #
        # for wrapped_line in wrapped_lines:
        #     if is_arabic:
        #         # Process Arabic text for dimension calculation
        #         configuration = {
        #             'delete_harakat': False,
        #             'support_ligatures': True,
        #             'RIAL SIGN': True,
        #         }
        #         reshaper = arabic_reshaper.ArabicReshaper(configuration=configuration)
        #         reshaped_text = reshaper.reshape(wrapped_line)
        #         display_text = get_display(reshaped_text)
        #         display_text = display_text[::-1]
        #     else:
        #         display_text = wrapped_line
        #
        #     text_bbox = font_obj.getbbox(display_text)
        #     line_width = text_bbox[2] - text_bbox[0]
        #     line_height = text_bbox[3] - text_bbox[1] + 10
        #     line_heights.append(line_height)
        #     max_line_width = max(max_line_width, line_width)
        #
        # # Calculate total dimensions with padding
        # total_height = sum(line_heights) + 40
        # total_width = max_line_width + 60
        #
        # # Create the image with background and text
        # bg_img = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))
        # draw = ImageDraw.Draw(bg_img)
        #
        # # Draw rounded rectangle background
        # draw.rounded_rectangle([(0, 0), (total_width, total_height)],
        #                        radius=15, fill=BG_COLOR)
        #
        # # Draw each line of text
        # y_offset = 20
        # for i, wrapped_line in enumerate(wrapped_lines):
        #     if is_arabic:
        #         # Process Arabic text for display
        #         configuration = {
        #             'delete_harakat': False,
        #             'support_ligatures': True,
        #             'RIAL SIGN': True,
        #         }
        #         reshaper = arabic_reshaper.ArabicReshaper(configuration=configuration)
        #         reshaped_text = reshaper.reshape(wrapped_line)
        #         display_text = get_display(reshaped_text)
        #         display_text = display_text[::-1]
        #
        #         # Right-align Arabic text
        #         text_bbox = font_obj.getbbox(display_text)
        #         text_width = text_bbox[2] - text_bbox[0]
        #         x_pos = total_width - text_width - 30
        #     else:
        #         display_text = wrapped_line
        #         x_pos = 30  # Left-align English text
        #
        #     draw.text((x_pos, y_offset), display_text, font=font_obj, fill=color)
        #     y_offset += line_heights[i]
        #
        # # Convert to numpy array
        # bg_array = np.array(bg_img)
        #
        # # Create simple animation (just show the complete image)
        # def make_frame(t):
        #     if t < anim_duration:  # Animation phase
        #         progress = min(1.0, t / anim_duration)
        #         visible_width = int(total_width * progress)
        #
        #         if is_arabic:  # RTL: crop from right
        #             cropped = full_text_array[:, -visible_width:] if visible_width > 0 else full_text_array[:, :0]
        #             padding = np.zeros((canvas_height, canvas_width - visible_width, 4), dtype=np.uint8)
        #             frame = np.hstack([padding, cropped])
        #         else:  # LTR: crop from left
        #             cropped = full_text_array[:, :visible_width] if visible_width > 0 else full_text_array[:, :0]
        #             padding = np.zeros((total_height, total_width - visible_width, 4), dtype=np.uint8)
        #             frame = np.hstack([cropped, padding])
        #     else:  # After animation - show full text
        #         frame = full_text_array
        #
        #     return frame
        #
        # # Create the clip
        # clip = VideoClip(make_frame, duration=duration)
        # return clip, total_width, total_height

        # else:
        # Multiple lines - Create single animated image with background AND text
        # Load appropriate font
        # working
        if is_arabic:
            try:
                font_obj = ImageFont.truetype(FONT_ARABIC_PATH, FONT_SIZE_ARABIC_MULTILINE)
            except:
                font_obj = ImageFont.truetype(FALLBACK_FONT_PATH, FONT_SIZE_ARABIC_MULTILINE)
        else:
            try:
                font_obj = ImageFont.truetype(FONT_ENGLISH_PATH, FONT_SIZE_MULTILINE)
            except:
                font_obj = ImageFont.truetype(FALLBACK_FONT_PATH, FONT_SIZE_MULTILINE)

        wrapped_lines = wrap_text(line, font_obj, max_width, is_arabic)

        # Calculate dimensions
        line_heights = []
        max_line_width = 0

        for wrapped_line in wrapped_lines:
            if is_arabic:
                # Process Arabic text for dimension calculation
                configuration = {
                    'delete_harakat': False,
                    'support_ligatures': True,
                    'RIAL SIGN': True,
                }
                reshaper = arabic_reshaper.ArabicReshaper(configuration=configuration)
                reshaped_text = reshaper.reshape(wrapped_line)
                display_text = get_display(reshaped_text)
                display_text = display_text[::-1]
            else:
                display_text = wrapped_line

            text_bbox = font_obj.getbbox(display_text)
            line_width = text_bbox[2] - text_bbox[0]
            line_height = text_bbox[3] - text_bbox[1] + 10
            line_heights.append(line_height)
            max_line_width = max(max_line_width, line_width)

        # Calculate total dimensions with padding
        total_height = sum(line_heights) + 40
        total_width = max_line_width + 60

        # Create animation function that draws everything
        # Create simple function that shows full text immediately (no animation)
        def make_frame(t):
            # Create image with transparent background
            img = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Draw rounded rectangle background
            draw.rounded_rectangle([(0, 0), (total_width, total_height)],
                                   radius=15, fill=BG_COLOR)

            # Draw each line of text (full text, no animation)
            y_offset = 25
            for i, wrapped_line in enumerate(wrapped_lines):
                if is_arabic:
                    # Process Arabic text
                    configuration = {
                        'delete_harakat': False,
                        'support_ligatures': True,
                        'RIAL SIGN': True,
                    }
                    reshaper = arabic_reshaper.ArabicReshaper(configuration=configuration)
                    reshaped_text = reshaper.reshape(wrapped_line)
                    display_text = get_display(reshaped_text)
                    display_text = display_text[::-1]

                    # Right-align Arabic text
                    text_bbox = font_obj.getbbox(display_text)
                    text_width = text_bbox[2] - text_bbox[0]
                    x_pos = total_width - text_width - 30
                else:
                    display_text = wrapped_line
                    # Left-align English text
                    x_pos = 30

                draw.text((x_pos, y_offset), display_text, font=font_obj, fill=color)
                y_offset += line_heights[i]

            return np.array(img)

        # Create the clip
        clip = VideoClip(make_frame, duration=duration)

        clip.with_effects([vfx.FadeIn(FADE_DURATION, initial_color=[0, 0, 0, 0])])

        return clip, total_width, total_height
    #endworking







# def process_subtitle_line(line, font, color, is_arabic=False, duration=5.0, max_width=800, is_draw_bg=True):
#     """Process a subtitle line with text wrapping"""
#     # Wrap the text into multiple lines
#     wrapped_lines = wrap_text(line, font, max_width, is_arabic)
#
#     if len(wrapped_lines) == 1:
#         # Single line - use existing animation
#         if is_arabic:
#             return create_slide_animation(
#                 text=wrapped_lines[0],
#                 font_path=FONT_ARABIC_PATH,
#                 font_size=FONT_SIZE_ARABIC,
#                 duration=duration,
#                 bg_color=(0, 0, 0, 0),
#                 is_rtl=True,
#                 is_draw_bg=is_draw_bg,
#                 h_pad=40)
#         else:
#             return create_slide_animation(
#                 text=wrapped_lines[0],
#                 font_path=FONT_ENGLISH_PATH,
#                 font_size=FONT_SIZE,
#                 duration=duration,
#                 bg_color=(0, 0, 0, 0),
#                 is_rtl=False,
#                 is_draw_bg=is_draw_bg,
#                 h_pad=40)
#     else:
#         # Multiple lines - create unified background and animated text
#         line_clips = []
#         line_heights = []
#         line_widths = []
#
#         # Load appropriate font
#         if is_arabic:
#             try:
#                 font_obj = ImageFont.truetype(FONT_ARABIC_PATH, FONT_SIZE_ARABIC)
#             except:
#                 font_obj = ImageFont.truetype(FALLBACK_FONT_PATH, FONT_SIZE_ARABIC)
#         else:
#             try:
#                 font_obj = ImageFont.truetype(FONT_ENGLISH_PATH, FONT_SIZE)
#             except:
#                 font_obj = ImageFont.truetype(FALLBACK_FONT_PATH, FONT_SIZE)
#
#         # Calculate dimensions first
#         for wrapped_line in wrapped_lines:
#             if is_arabic:
#                 # Process Arabic text for dimension calculation
#                 configuration = {
#                     'delete_harakat': False,
#                     'support_ligatures': True,
#                     'RIAL SIGN': True,
#                 }
#                 reshaper = arabic_reshaper.ArabicReshaper(configuration=configuration)
#                 reshaped_text = reshaper.reshape(wrapped_line)
#                 display_text = get_display(reshaped_text)
#                 display_text = display_text[::-1]
#             else:
#                 display_text = wrapped_line
#
#             text_bbox = font_obj.getbbox(display_text)
#             line_width = text_bbox[2] - text_bbox[0]
#             line_height = text_bbox[3] - text_bbox[1] + 10
#             line_heights.append(line_height)
#             line_widths.append(line_width)
#
#         max_line_width = max(line_widths)
#         total_height = sum(line_heights) + 40
#         total_width = max_line_width + 60
#
#         # Create animated text clips (without background)
#         for i, wrapped_line in enumerate(wrapped_lines):
#             if is_arabic:
#                 line_clip, line_width, line_height = create_slide_animation(
#                     text=wrapped_line,
#                     font_path=FONT_ARABIC_PATH,
#                     font_size=FONT_SIZE_ARABIC,
#                     duration=duration,
#                     bg_color=(0, 0, 0, 0),
#                     is_rtl=True,
#                     is_draw_bg=False,  # No individual background
#                     h_pad=40)
#             else:
#                 line_clip, line_width, line_height = create_slide_animation(
#                     text=wrapped_line,
#                     font_path=FONT_ENGLISH_PATH,
#                     font_size=FONT_SIZE,
#                     duration=duration,
#                     bg_color=(0, 0, 0, 0),
#                     is_rtl=False,
#                     is_draw_bg=False,  # No individual background
#                     h_pad=40)
#
#             line_clips.append(line_clip)
#
#         # Create static background
#         bg_img = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))
#         draw = ImageDraw.Draw(bg_img)
#         draw.rounded_rectangle([(0, 0), (total_width, total_height)],
#                                radius=15, fill=BG_COLOR)
#
#         def make_bg_frame(t):
#             return np.array(bg_img)
#
#         bg_clip = VideoClip(make_bg_frame, duration=duration)
#
#         # Position text clips
#         positioned_clips = []
#         y_offset = 20
#
#         for i, (line_clip, line_width, line_height) in enumerate(zip(line_clips, line_widths, line_heights)):
#             if is_arabic:
#                 x_pos = total_width - line_width - 30  # Right-align Arabic
#             else:
#                 x_pos = 30  # Left-align English
#
#             positioned_clip = line_clip.with_position((x_pos, y_offset))
#             positioned_clips.append(positioned_clip)
#             y_offset += line_height
#
#         # Create final composite
#         final_clip = CompositeVideoClip([bg_clip] + positioned_clips)
#         return final_clip, total_width, total_height




# def process_subtitle_line(line, font, color, is_arabic=False, duration=5.0, max_width=800, is_draw_bg=True):
#     """Process a subtitle line with text wrapping"""
#     # Wrap the text into multiple lines
#     wrapped_lines = wrap_text(line, font, max_width, is_arabic)
#
#     if len(wrapped_lines) == 1:
#         # Single line - use existing animation
#         if is_arabic:
#             return create_slide_animation(
#                 text=wrapped_lines[0],
#                 font_path=FONT_ARABIC_PATH,
#                 font_size=FONT_SIZE_ARABIC,
#                 duration=duration,
#                 bg_color=(0, 0, 0, 0),
#                 is_rtl=True,
#                 is_draw_bg=is_draw_bg,
#                 h_pad=40)
#         else:
#             return create_slide_animation(
#                 text=wrapped_lines[0],
#                 font_path=FONT_ENGLISH_PATH,
#                 font_size=FONT_SIZE,
#                 duration=duration,
#                 bg_color=(0, 0, 0, 0),
#                 is_rtl=False,
#                 is_draw_bg=is_draw_bg,
#                 h_pad=40)
#     else:
#         # Multiple lines - create a composite clip
#         # line_clips = []
#         # total_height = 0
#         # line_heights = []
#         # max_line_width = 0
#
#         # Multiple lines - create a unified background for all lines
#         line_clips = []
#         line_heights = []
#         line_widths = []
#         total_height = 0
#
#         for i, wrapped_line in enumerate(wrapped_lines):
#             if is_arabic:
#                 line_clip, line_width, line_height = create_slide_animation(
#                     text=wrapped_line,
#                     font_path=FONT_ARABIC_PATH,
#                     font_size=FONT_SIZE_ARABIC,
#                     duration=duration,
#                     bg_color=(0, 0, 0, 0),
#                     is_rtl=True,
#                     is_draw_bg=False,
#                     h_pad=40)
#             else:
#                 line_clip, line_width, line_height = create_slide_animation(
#                     text=wrapped_line,
#                     font_path=FONT_ENGLISH_PATH,
#                     font_size=FONT_SIZE,
#                     duration=duration,
#                     bg_color=(0, 0, 0, 0),
#                     is_rtl=False,
#                     is_draw_bg=False,
#                     h_pad=40)
#
#             # # Position each line vertically
#             # line_clip = line_clip.with_position((0, total_height))
#             # line_clips.append(line_clip)
#             # total_height += line_height
#             #
#             # line_heights.append(line_height)
#             # max_line_width = max(max_line_width, line_width)
#
#
#             # Ensure valid dimensions
#             if line_width > 0 and line_height > 0:
#                 line_clips.append(line_clip)
#                 line_heights.append(line_height)
#                 line_widths.append(line_width)
#                 total_height += line_height
#             else:
#                 print(f"Warning: Skipping line with zero dimensions: {wrapped_line}")
#
#         # Create a composite clip of all lines
#         # composite_clip = CompositeVideoClip(line_clips)
#         # return composite_clip, max_width, total_height
#
#         # Create unified background
#         # bg_width = max_line_width #+ 60  # Add padding
#         # bg_height = total_height #+ 40  # Add padding
#         #
#         # # Create background image with rounded corners
#         # bg_img = Image.new('RGBA', (bg_width, bg_height), (0, 0, 0, 0))
#         # draw_bg = ImageDraw.Draw(bg_img)
#         # draw_bg.rounded_rectangle([(0, 0), (bg_width, bg_height)],
#         #                           radius=15, fill=BG_COLOR)
#         #
#         # # Convert background to video clip
#         # def make_bg_frame(t):
#         #     return np.array(bg_img)
#         #
#         # bg_clip = VideoClip(make_bg_frame, duration=duration)
#         #
#         # # Position text clips on top of background
#         # positioned_clips = []
#         # y_offset = 20  # Start with top padding
#         #
#         # for i, line_clip in enumerate(line_clips):
#         #     x_pos = 30  # Left padding
#         #     if is_arabic:
#         #         # Right-align Arabic text
#         #         x_pos = bg_width - line_heights[i] - 30
#         #
#         #     positioned_clip = line_clip.with_position((x_pos, y_offset))
#         #     positioned_clips.append(positioned_clip)
#         #     y_offset += line_heights[i] + 10  # Add line spacing
#         #
#         # # Create final composite with background and text
#         # final_clip = CompositeVideoClip([bg_clip] + positioned_clips)
#         # return final_clip, bg_width, bg_height
#
#         # Check if we have valid clips
#         if not line_clips:
#             print("Error: No valid text clips created")
#             # Return a dummy clip with minimal dimensions
#             dummy_img = Image.new('RGBA', (10, 10), (0, 0, 0, 0))
#
#             def make_dummy_frame(t):
#                 return np.array(dummy_img)
#
#             dummy_clip = VideoClip(make_dummy_frame, duration=0.1)
#             return dummy_clip, 10, 10
#
#         # Create unified background
#         max_line_width = max(line_widths)
#         bg_width = max_line_width + 60  # Add padding
#         bg_height = total_height + 40 + (len(line_clips) * 10)  # Add padding and line spacing
#
#         # Create background image with rounded corners
#         bg_img = Image.new('RGBA', (bg_width, bg_height), (0, 0, 0, 0))
#         draw_bg = ImageDraw.Draw(bg_img)
#         draw_bg.rounded_rectangle([(0, 0), (bg_width, bg_height)],
#                                   radius=15, fill=BG_COLOR)
#
#         # Convert background to video clip
#         def make_bg_frame(t):
#             return np.array(bg_img)
#
#         bg_clip = VideoClip(make_bg_frame, duration=duration, is_mask=False)
#
#         # Position text clips on top of background
#         positioned_clips = []
#         y_offset = 20  # Start with top padding
#
#         for i, (line_clip, line_width, line_height) in enumerate(zip(line_clips, line_widths, line_heights)):
#             if is_arabic:
#                 # Right-align Arabic text
#                 x_pos = bg_width - line_width - 30
#             else:
#                 # Left-align English text
#                 x_pos = 30
#
#             positioned_clip = line_clip.with_position((x_pos, y_offset))
#             positioned_clips.append(positioned_clip)
#             y_offset += line_height + 10  # Add line spacing
#
#         # Create final composite with background and text
#         final_clip = CompositeVideoClip([bg_clip] + positioned_clips)
#         return final_clip, bg_width, bg_height


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
        line = line[::-1]

    text_bbox = font.getbbox(line)
    total_width = text_bbox[2] - text_bbox[0]
    total_height = text_bbox[3] - text_bbox[1] + 20

    return line, total_width, total_height


def create_slide_animation(text, font_path, font_size, duration, bg_color, is_rtl=True, is_draw_bg=False, h_pad=40):
    """Create sliding animation that completes within 5 seconds max and stays visible"""
    # Calculate animation duration (min of 5 seconds or total_duration)
    anim_duration = min(2.0, duration)

    # Prepare text (RTL for Arabic)
    if is_rtl:
        configuration = {
            'delete_harakat': False,
            'support_ligatures': True,
            'RIAL SIGN': True,
        }
        reshaper = arabic_reshaper.ArabicReshaper(configuration=configuration)
        reshaped_text = reshaper.reshape(text)
        display_text = get_display(reshaped_text)
        display_text = display_text[::-1] # set it for linux
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
    canvas_height = text_height + h_pad
    bg_img = Image.new("RGBA", (int(canvas_width), int(canvas_height)), bg_color)
    draw = ImageDraw.Draw(bg_img)

    # Draw background
    if is_draw_bg:
        draw.rounded_rectangle([(0, 0), (canvas_width, canvas_height)],
                               radius=15, fill=BG_COLOR)

    # Position text
    x_pos = canvas_width - text_width - 10 if is_rtl else 10
    draw.text((x_pos, 25 if is_rtl else 10), display_text, font=font, fill="white")
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

    return VideoClip(make_frame, duration=duration), canvas_width, canvas_height


def create_subtitle_clips(video, subs, font_english, font_arabic):
    """Generate subtitle clips with proper compositing"""
    subtitle_clips = []
    video_size = video.size
    max_width = video_size[0] - 100  # Leave some margin

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

        # Process Arabic lines
        arabic_line_count = 0
        for line in arabic_lines:
            try:
                line_clip, canvas_width, canvas_height = process_subtitle_line(
                    line, font_arabic, COLOR_ARABIC, True, duration, max_width)

                y_pos = video_size[1] - SUBTITLE_HEIGHT - (
                            len(english_lines) * LINE_SPACING) - arabic_line_count * LINE_SPACING - 80
                x_pos = (video_size[0] - canvas_width) / 2

                positioned_clip = line_clip.with_position((x_pos, y_pos)) \
                    .with_start(start_time) \
                    .with_duration(duration)

                positioned_clip = positioned_clip.with_effects([vfx.FadeIn(FADE_DURATION, initial_color=[0, 0, 0, 0])])
                subtitle_clips.append(positioned_clip)
                arabic_line_count += 1
            except Exception as x:
                print(x)

        # Process English lines
        for line_idx, line in enumerate(english_lines):
            try:
                line_clip, canvas_width, canvas_height = process_subtitle_line(
                    line, font_english, COLOR_ENGLISH, False, duration, max_width)

                y_pos = video_size[1] - SUBTITLE_HEIGHT - line_idx * LINE_SPACING
                x_pos = (video_size[0] - canvas_width) / 2

                positioned_clip = line_clip.with_position((x_pos, y_pos)) \
                    .with_start(start_time) \
                    .with_duration(duration)

                # positioned_clip = positioned_clip.with_effects([vfx.FadeIn(FADE_DURATION, initial_color=[0, 0, 0, 0])])
                subtitle_clips.append(positioned_clip)
            except Exception as x:
                print(x)

    return subtitle_clips

def create_header_clips_updated(video, surah_no, font_english, font_arabic):
    """Generate header clips using the new RTL animation approach"""
    header_clips = []

    with open(CHAPTERS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    data_en = data["en"][f"{surah_no}"]
    data_ar = data["ar"][f"{surah_no}"]

    surah_name_en = f'Surah {data_en["transliteratedName"]}'
    surah_name_ar = data_ar["transliteratedName"]
    surah_meaning_en = data_en["translatedName"]

    # Arabic header
    arabic_clip, canvas_width, height_ar = create_slide_animation(
        text=surah_name_ar,
        font_path=FONT_ARABIC_HEADER_PATH,
        font_size=FONT_HEADER_SIZE_ARABIC,
        duration=video.duration,
        bg_color=(0, 0, 0, 0),
        is_rtl=True,
        h_pad=130)

    base_y = 136
    # Get dimensions for positioning
    # _, width_ar, height_ar = preprocess_subtitle(surah_name_ar, font_arabic, is_arabic=True)
    header_clips.append(arabic_clip.with_position(((video.w - canvas_width) / 2, base_y)))
    base_y += height_ar + 40

    # English header (using same approach but left-to-right)
    english_clip, canvas_width, height_en = create_slide_animation(
        text=surah_name_en,
        font_path=FONT_ENGLISH_HEADER_PATH,
        font_size=FONT_HEADER_SIZE,
        duration=video.duration,
        bg_color=(0, 0, 0, 0),
        is_rtl=False,
        h_pad=40)

    # _, width_en, height_en = preprocess_subtitle(surah_name_en, font_english, is_arabic=False)
    header_clips.append(english_clip.with_position(((video.w - canvas_width) / 2, base_y)))
    base_y += height_en + 10

    # English meaning (using same approach but left-to-right)
    english_meaning_clip, canvas_width, canvas_height = create_slide_animation(
        text=surah_meaning_en,
        font_path=FONT_ENGLISH_HEADER_PATH,
        font_size=FONT_HEADER_MEANING_SIZE,
        duration=video.duration,
        bg_color=(0, 0, 0, 0),
        is_rtl=False,
        h_pad=40)

    # _, width_en, height_en = preprocess_subtitle(surah_name_en, font_english, is_arabic=False)
    header_clips.append(english_meaning_clip.with_position(((video.w - canvas_width) / 2, base_y)))

    return header_clips


# --- MAIN EXECUTION ---
def main(surah_number):
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
        if not os.path.exists(TEMP_MERGED_PATH):
            # Step 2: Merge Canva video and audio using ffmpeg-python
            print("Step 2: Merging video and audio...")

            (
                ffmpeg
                .input(INIT_VIDEO_PATH, stream_loop=-1)  # Loop video indefinitely
                .video
                .output(
                    ffmpeg.input(AUDIO_PATH).audio,
                    TEMP_MERGED_PATH,
                    vcodec="libx264",  # Video codec
                    acodec="aac",  # Audio codec
                    audio_bitrate="192k",  # Set audio bitrate to 192kbps
                    pix_fmt="yuv420p",  # Pixel format (for compatibility)
                    shortest=None,  # End when shortest stream ends
                    map_metadata="-1",  # Strip metadata
                    threads="32"
                    #**{'map': ['0:v:0', '1:a:0']}  # Explicit stream mapping (video from 1st input, audio from 2nd)
                )
                .run(overwrite_output=True)
            )

            # (
            #     ffmpeg
            #     .input(INIT_VIDEO_PATH, stream_loop=-1)  # Loop video indefinitely
            #     .video
            #     .output(
            #         ffmpeg.input(AUDIO_PATH).audio,
            #         TEMP_MERGED_PATH,
            #         vcodec="h264_nvenc",  # Use NVIDIA hardware encoding
            #         acodec="aac",  # Audio codec
            #         # video_bitrate="5M",  # Video bitrate
            #         audio_bitrate="192k",  # Set audio bitrate to 192kbps
            #         pix_fmt="yuv420p",  # Pixel format
            #         preset="fast",  # NVENC preset
            #         shortest=None,  # End when shortest stream ends
            #         map_metadata="-1",  # Strip metadata
            #         # **{'map': ['0:v:0', '1:a:0']}  # Explicit stream mapping
            #     )
            #     .run(overwrite_output=True)
            # )

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
        # final.write_videofile(
        #     OUTPUT_VIDEO_PATH,
        #     fps=video.fps,
        #     codec="libx264",
        #     audio_codec="aac",
        #     threads=8,
        #     preset="ultrafast",
        #     ffmpeg_params=[
        #         "-tune", "fastdecode",
        #         "-movflags", "+faststart",
        #         "-x264opts", "no-mbtree:sliced-threads=1"
        #     ]
        # )

        final.write_videofile(
            OUTPUT_VIDEO_PATH,
            fps=video.fps,
            codec="h264_nvenc",
            audio_codec="aac",
            threads=0,
            preset="p1",  # Fastest preset
            ffmpeg_params=[
                # "-cq", "25",  # Slightly lower quality for speed
                # "-rc", "vbr",
                # "-b:v", "8M",  # Higher bitrate for faster encoding
                "-tune", "ll",  # Low latency tuning
                "-movflags", "+faststart",
                # "-gpu", "0",  # Use GPU 0
                "-y"
            ]
        )

        # final.write_videofile(
        #     OUTPUT_VIDEO_PATH,
        #     fps=video.fps,
        #     codec="h264_nvenc",  # Use NVIDIA GPU encoder
        #     audio_codec="aac",
        #     threads=0,  # Let NVENC handle threading
        #     preset="p1",  # NVENC presets: slow, medium, fast, p1–p7
        #     ffmpeg_params=[
        #         "-movflags", "+faststart",
        #         # "-b:v", "5M",  # Target bitrate
        #         "-pix_fmt", "yuv420p",  # Ensure compatibility
        #         "-preset", "fast",  # NVENC preset again for safety
        #         # "-rc:v", "vbr_hq",  # High quality variable bitrate
        #         "-cq", "24"  # Constant quality similar to CRF
        #     ]
        # )

        ## working code
        # final.write_videofile(
        #     OUTPUT_VIDEO_PATH,
        #     fps=video.fps,
        #     codec="libx264",
        #     audio_codec="aac",
        #     threads=32,  # Use more threads if available
        #     preset="ultrafast",
        #     ffmpeg_params=[
        #         "-tune", "fastdecode",
        #         "-movflags", "+faststart",
        #         "-x264-params", "threads=32:lookahead-threads=8",  # More explicit threading
        #         "-crf", "24",  # Slightly higher CRF for faster encoding
        #         "-y"
        #     ]
        # )
        print(f"Final video created at {OUTPUT_VIDEO_PATH}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up temporary files
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
        # if os.path.exists(TEMP_MERGED_PATH):
        #     os.remove(TEMP_MERGED_PATH)
        if os.path.exists(SUBS_PATH):
            os.remove(SUBS_PATH)


if __name__ == "__main__":
    # # Setup argparse
    # parser = argparse.ArgumentParser(description="Generate a subtitled video from a JSON file and audio.")
    # parser.add_argument("surah_number", type=int, help="The number of the surah (e.g., 113)")
    # args = parser.parse_args()
    # surah_number = args.surah_number
    # for surah_number in range(36, 41):
    #     main(surah_number)
    main(36)
