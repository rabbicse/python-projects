import gc
import glob
import json
import os
import random
import shutil
import subprocess
from typing import Optional, Tuple

import constants

os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"

import arabic_reshaper
from bidi.algorithm import get_display
from moviepy import *

# Load spaCy model
import spacy

nlp = spacy.load("en_core_web_sm", disable=["ner"])

# Configuration
FONT = "fonts/DejaVuSans.ttf"
FONT_REGULAR = "fonts/merriweather.regular.ttf"
FONT_BOLD = "fonts/merriweather.bold.ttf"
FONT_ULTRA_BOLD = "fonts/merriweather.ultrabold.ttf"
FONT_ARABIC = "fonts/uthmanic_hafs_v20.ttf"
FONT_ARABIC_CALIGRAPH = "fonts/ArabQuranIslamic140-K7n4W.ttf"
FONT_BANGLA = "fonts/Siyamrupali.ttf"
BASE_JSON_PATH = "quran/{}.json"
CHAPTERS_PATH = "quran/chapters.json"
BASE_OUTPUT_VIDEO_PATH = "quran-en/{}-video.mp4"
MAX_SUB_WIDTH = 1500
TARGET_MAX_HEIGHT = 1080
MAX_ALLOWED_HEIGHT = TARGET_MAX_HEIGHT / 2
FONT_SIZE = 60
FONT_SIZE_ARABIC = 90

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080

# Color scheme
COLORS = {
    "background": (0, 10, 20),
    "arabic_text": "#FFFFFF",#(255, 215, 0),
    "english_text": "#1E90FF", #(230, 230, 250),
    "bangla_text": "#FFFFFF",#(176, 224, 230),
    "meaning_text": (230, 230, 250),
    "stroke": (0, 0, 0),
    "overlay_bg": (0, 0, 0, 180)
}

dummy_sub = {
    "arabic_text": "يَـٰٓأَيُّهَا ٱلَّذِينَ ءَامَنُوٓا۟ إِذَا تَدَايَنتُم بِدَيْنٍ إِلَىٰٓ أَجَلٍ مُّسَمًّى فَٱكْتُبُوهُ ۚ وَلْيَكْتُب بَّيْنَكُمْ كَاتِبٌۢ بِٱلْعَدْلِ ۚ وَلَا يَأْبَ كَاتِبٌ أَن يَكْتُبَ كَمَا عَلَّمَهُ ٱللَّهُ ۚ فَلْيَكْتُبْ وَلْيُمْلِلِ ٱلَّذِى عَلَيْهِ ٱلْحَقُّ وَلْيَتَّقِ ٱللَّهَ رَبَّهُۥ وَلَا يَبْخَسْ مِنْهُ شَيْـًٔا ۚ فَإِن كَانَ ٱلَّذِى عَلَيْهِ ٱلْحَقُّ سَفِيهًا أَوْ ضَعِيفًا أَوْ لَا يَسْتَطِيعُ أَن يُمِلَّ هُوَ فَلْيُمْلِلْ وَلِيُّهُۥ بِٱلْعَدْلِ ۚ وَٱسْتَشْهِدُوا۟ شَهِيدَيْنِ مِن رِّجَالِكُمْ ۖ فَإِن لَّمْ يَكُونَا رَجُلَيْنِ فَرَجُلٌ وَٱمْرَأَتَانِ مِمَّن تَرْضَوْنَ مِنَ ٱلشُّهَدَآءِ أَن تَضِلَّ إِحْدَىٰهُمَا فَتُذَكِّرَ إِحْدَىٰهُمَا ٱلْأُخْرَىٰ ۚ وَلَا يَأْبَ ٱلشُّهَدَآءُ إِذَا مَا دُعُوا۟ ۚ وَلَا تَسْـَٔمُوٓا۟ أَن تَكْتُبُوهُ صَغِيرًا أَوْ كَبِيرًا إِلَىٰٓ أَجَلِهِۦ ۚ ذَٰلِكُمْ أَقْسَطُ عِندَ ٱللَّهِ وَأَقْوَمُ لِلشَّهَـٰدَةِ وَأَدْنَىٰٓ أَلَّا تَرْتَابُوٓا۟ ۖ إِلَّآ أَن تَكُونَ تِجَـٰرَةً حَاضِرَةً تُدِيرُونَهَا بَيْنَكُمْ فَلَيْسَ عَلَيْكُمْ جُنَاحٌ أَلَّا تَكْتُبُوهَا ۗ وَأَشْهِدُوٓا۟ إِذَا تَبَايَعْتُمْ ۚ وَلَا يُضَآرَّ كَاتِبٌ وَلَا شَهِيدٌ ۚ وَإِن تَفْعَلُوا۟ فَإِنَّهُۥ فُسُوقٌۢ بِكُمْ ۗ وَٱتَّقُوا۟ ٱللَّهَ ۖ وَيُعَلِّمُكُمُ ٱللَّهُ ۗ وَٱللَّهُ بِكُلِّ شَىْءٍ عَلِيمٌ",
    "english_text": "O believers! When you contract a loan for a fixed period of time, commit it to writing. Let the scribe maintain justice between the parties. The scribe should not refuse to write as Allah has taught them to write. They will write what the debtor dictates, bearing Allah in mind and not defrauding the debt. If the debtor is incompetent, weak, or unable to dictate, let their guardian dictate for them with justice. Call upon two of your men to witness. If two men cannot be found, then one man and two women of your choice will witness—so if one of the women forgets the other may remind her.<sup foot_note=76489>1</sup> The witnesses must not refuse when they are summoned. You must not be against writing ˹contracts˺ for a fixed period—whether the sum is small or great. This is more just ˹for you˺ in the sight of Allah, and more convenient to establish evidence and remove doubts. However, if you conduct an immediate transaction among yourselves, then there is no need for you to record it, but call upon witnesses when a deal is finalized. Let no harm come to the scribe or witnesses. If you do, then you have gravely exceeded ˹your limits˺. Be mindful of Allah, for Allah ˹is the One Who˺ teaches you. And Allah has ˹perfect˺ knowledge of all things.",
}


def to_arabic(num: int) -> str:
    # Western to Arabic-Indic digits map (Unicode escapes)
    digits = ["\u0660", "\u0661", "\u0662", "\u0663", "\u0664",
              "\u0665", "\u0666", "\u0667", "\u0668", "\u0669"]
    return "".join(digits[int(d)] for d in str(num))


# New Chroma Key Color: Bright Cyan (RGB)
CHROMA_KEY_COLOR = (0, 255, 0)
CHROMA_KEY_HEX = "00FF00"  # Bright Cyan


class TempFileManager:
    def __init__(self, surah_no: int):
        self.temp_files = []
        # Create tmp directory in current working directory
        current_dir = os.getcwd()
        self.temp_dir = os.path.join(current_dir, "tmp")

        # Create tmp directory if it doesn't exist
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

        # Create a unique subdirectory for this session
        self.session_dir = os.path.join(self.temp_dir, f"session_{surah_no}")
        if not os.path.exists(self.session_dir):
            os.makedirs(self.session_dir)

        self.temp_files.append(self.session_dir)
        print(f"📁 Temporary files directory: {self.session_dir}")

    def get_or_create_temp_file(self, suffix='.mp4'):
        # temp_file = tempfile.mktemp(suffix=suffix, dir=self.session_dir)
        temp_file = os.path.join(self.session_dir, suffix)
        self.temp_files.append(temp_file)
        return temp_file, os.path.exists(temp_file)

    def cleanup(self):
        print("🧹 Cleaning up temporary files...")
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    if os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                    else:
                        os.remove(file_path)
                    print(f"  Deleted: {file_path}")
            except Exception as e:
                print(f"⚠️ Warning: Could not delete {file_path}: {e}")
        self.temp_files = []
        gc.collect()


def generate_srt(data):
    srt_lines = []
    # print(f"Total verses: {len(data['surah_verses'])}")
    for verse in data["surah_verses"]:
        # print(f"verse key: {verse['verse_key']}")
        srt_lines.append(verse["arabic_text"])
    return srt_lines


def json_to_srt(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return generate_srt(data)


# def analyze_text(text: str):
#     """Analyze text and return tokens with highlight information"""
#     doc = nlp(text)
#     highlight_pos = {"NOUN", "PROPN", "ADJ", "VERB"}
#     return doc, highlight_pos

def analyze_text(text: str):
    doc = nlp(text)

    highlight_pos = {"NOUN", "PROPN", "ADJ", "VERB"}
    stopwords = nlp.Defaults.stop_words

    tokens = []
    for token in doc:
        # Fix possessive words like "Allah's"
        if token.tag_ == "POS" and tokens:  # POS = possessive
            tokens[-1]["text"] += token.text  # attach 's
            tokens[-1]["end"] = token.idx + len(token.text)
            continue

        tokens.append({
            "text": token.text,
            "start": token.idx,
            "end": token.idx + len(token.text),
            "highlight": (
                    token.pos_ in highlight_pos and
                    token.text.lower() not in stopwords and
                    token.is_alpha
            )
        })

    return tokens



def create_animated_text(text: str, text_arabic: str, duration=5):
    # Create a background
    background = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(0, 0, 0, 255))
    # background = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=CHROMA_KEY_COLOR)
    background = background.with_duration(duration)
    background = background.with_opacity(0.45)  # 30% opacity

    # Arabic Caption
    # Create the text clip without a font parameter
    # For Arabic, we need to process the text first
    configuration = {
        'delete_harakat': False,
        'support_ligatures': True,
        'RIAL SIGN': True,
    }
    reshaper = arabic_reshaper.ArabicReshaper(configuration=configuration)
    reshaped_text = reshaper.reshape(text_arabic)
    arabic_display_text = get_display(reshaped_text)
    arabic_display_text = arabic_display_text[::-1]  # Reverse for proper RTL display
    text_clip_arabic = TextClip(
        font=FONT_ARABIC,
        text=text_arabic,
        color="white",
        font_size=FONT_SIZE_ARABIC,
        size=(MAX_SUB_WIDTH, None),
        method='caption',  # Enable word wrapping
        text_align="center",
        stroke_color="#030303",
        stroke_width=3,  # Gold stroke
        interline=30,
        margin=(10, 30, 30, 50)  # left, top, right, bottom
    )

    estimated_ar_height = text_clip_arabic.h
    font_size_arabic = FONT_SIZE_ARABIC
    while estimated_ar_height > MAX_ALLOWED_HEIGHT:
        # Ensure the new size is smaller than or equal to the test size
        # scale_factor = min(1.0, TARGET_MAX_HEIGHT / estimated_ar_height)
        # Compute scale factor relative to allowed height
        scale_factor = MAX_ALLOWED_HEIGHT / estimated_ar_height
        # Clamp scale factor to a reasonable range (avoid extreme tiny/huge)
        # scale_factor = max(0.4, min(scale_factor, 1.2))
        # font_size = int(FONT_SIZE_ARABIC * scale_factor)
        font_size_arabic -= 5

        text_clip_arabic = TextClip(
            font=FONT_ARABIC,
            text=text_arabic,
            color="white",
            font_size=font_size_arabic,
            size=(MAX_SUB_WIDTH, None),
            method='caption',  # Enable word wrapping
            text_align="center",
            stroke_color="#030303",
            stroke_width=1,  # Gold stroke
            interline=20,
            margin=(10, 30, 10, 20)  # left, top, right, bottom

            # stroke_width=max(1, int(3 * scale_factor)),  # scale stroke a bit
            # interline=max(10, int(20 * scale_factor)),  # scale spacing
            # margin=(20, int(30 * scale_factor), 20, int(40 * scale_factor))
        )
        estimated_ar_height = text_clip_arabic.h
        print(f"Arabic Text height too high. Current Font Size: {font_size_arabic}")

    # Set the clip duration
    text_clip_arabic = text_clip_arabic.with_duration(duration)

    # Apply the movement
    text_clip_arabic = text_clip_arabic.with_position(
        (VIDEO_WIDTH / 2 - text_clip_arabic.w / 2, VIDEO_HEIGHT / 2 - text_clip_arabic.h))

    # Add padding (margin) around text
    # padding = 5
    # box_width = text_clip_arabic.w + 2 * padding
    # box_height = text_clip_arabic.h + 2 * padding
    #
    # # Background box
    # box = ColorClip(size=(box_width, box_height), color=(255, 0, 0))  # black box
    # box = box.with_opacity(0.6)  # transparent
    # box = box.with_position(
    #     (VIDEO_WIDTH / 2 - text_clip_arabic.w / 2 - padding, VIDEO_HEIGHT / 2 - text_clip_arabic.h - padding))
    # box = box.with_duration(duration)

    # text_clip_arabic = text_clip_arabic.with_position(
    #     ("center", "center"))

    # Apply effects
    text_clip_arabic = text_clip_arabic.with_effects([vfx.CrossFadeIn(1.5), vfx.CrossFadeOut(1.5)])

    # English Caption
    # Create the text clip without a font parameter
    text_clip = TextClip(
        font=FONT,
        text=text,
        color="white",
        font_size=FONT_SIZE,
        size=(MAX_SUB_WIDTH, None),
        method='caption',  # Enable word wrapping
        text_align="center",
        stroke_color="#030303",
        stroke_width=3,
        interline=30,
        margin=(10, 20, 10, 30)  # left, top, right, bottom
    )
    y_english = VIDEO_HEIGHT / 2

    estimated_height = text_clip.h
    font_size = FONT_SIZE
    while estimated_height > MAX_ALLOWED_HEIGHT:
        # Compute scale factor relative to allowed height
        # scale_factor = MAX_ALLOWED_HEIGHT / estimated_height
        # Ensure the new size is smaller than or equal to the test size
        # scale_factor = min(1.0, TARGET_MAX_HEIGHT / estimated_height)
        # Clamp scale factor to a reasonable range (avoid extreme tiny/huge)
        # scale_factor = max(0.45, min(scale_factor, 1.2))
        # font_size = int(FONT_SIZE * scale_factor)

        font_size -= 5

        text_clip = TextClip(
            font=FONT,
            text=text,
            color="white",
            font_size=font_size,
            size=(MAX_SUB_WIDTH, None),
            method='caption',  # Enable word wrapping
            text_align="center",
            stroke_color="#030303",
            stroke_width=2,  # Gold stroke
            interline=20,
            margin=(10, 20, 10, 20)  # left, top, right, bottom
            # stroke_width=max(1, int(3 * scale_factor)),  # scale stroke a bit
            # interline=max(10, int(20 * scale_factor)),  # scale spacing
            # margin=(10, int(30 * scale_factor), 10, int(10 * scale_factor))
        )
        estimated_height = text_clip.h
        # y_english = VIDEO_HEIGHT / 2
        print(f"English Text height too high. Current Font Size: {font_size}")

    # Set the clip duration
    text_clip = text_clip.with_duration(duration)

    # Apply the movement
    text_clip = text_clip.with_position((VIDEO_WIDTH / 2 - text_clip.w / 2, y_english))

    # text_clip = text_clip.with_position(("center", "center"))

    # Apply effects
    text_clip = text_clip.with_effects([vfx.CrossFadeIn(1.5), vfx.CrossFadeOut(1.5)])

    # box_width = text_clip_arabic.w + 2 * padding
    # box_height = text_clip_arabic.h + 2 * padding
    #
    # # Background box
    # box1 = ColorClip(size=(box_width, box_height), color=(0, 255, 0))  # black box
    # box1 = box1.with_opacity(0.6)  # transparent
    # box1 = box1.with_position(
    #     (VIDEO_WIDTH / 2 - text_clip.w / 2 - padding, VIDEO_HEIGHT / 2 - padding))
    # box1 = box1.with_duration(duration)

    # Combine background and text
    # final_clip = CompositeVideoClip([background, text_clip, text_clip_arabic])
    # final_clip = CompositeVideoClip([text_clip, text_clip_arabic], size=(VIDEO_WIDTH, VIDEO_HEIGHT),
    #                                 bg_color=None)

    final_clip = CompositeVideoClip([background, text_clip, text_clip_arabic], size=(VIDEO_WIDTH, VIDEO_HEIGHT))

    # final_clip.preview()

    return final_clip


def create_centered_individual_words(text:str,
                                     font_size:int,
                                     stroke_width:int=3,
                                     width=1920,
                                     height=540,
                                     duration=10):
    """Create centered individual words with better positioning"""
    # doc, highlight_pos = analyze_text(text)

    doc = analyze_text(text)

    # Group words into lines first
    lines = []
    current_line = []
    current_line_width = 0
    max_line_width = width - 420

    # First pass: group words into lines
    for token in doc:
        word = token["text"]#token.text_with_ws

        # Create temp clip to measure width
        temp_clip = TextClip(
            text=word.upper(),
            font_size=font_size,
            color='white',
            method='label',
            font=FONT_REGULAR,
            text_align="center",
            stroke_color="#030303",
            stroke_width=stroke_width,  # Gold stroke
            interline=20,
            margin=(5, 20, 5, 20)  # left, top, right, bottom
        )

        word_width = temp_clip.w

        if current_line_width + word_width > max_line_width and current_line:
            lines.append(current_line)
            current_line = [(token, word)]
            current_line_width = word_width
        else:
            current_line.append((token, word))
            current_line_width += word_width

    if current_line:
        lines.append(current_line)

    # Second pass: create and position clips
    text_clips = []
    line_height = 70
    total_text_height = len(lines) * line_height
    start_y = 0#(height - total_text_height) // 2

    for line_num, line in enumerate(lines):
        line_clips = []
        line_total_width = 0

        # Create clips for each word in the line
        for token, word in line:
            if token["highlight"]:
                word_clip = TextClip(
                    text=word.upper(),
                    font_size=font_size,
                    color='#1E90FF',
                    stroke_color='#030303',
                    stroke_width=stroke_width,
                    method='label',
                    font=FONT_BOLD,
                    text_align="center",
                    interline=20,
                    margin=(5, 20, 5, 20)  # left, top, right, bottom
                )
            else:
                word_clip = TextClip(
                    text=word.upper(),
                    font_size=font_size,
                    color='white',
                    method='label',
                    font=FONT_REGULAR,
                    text_align="center",
                    stroke_color="#030303",
                    stroke_width=stroke_width,  # Gold stroke
                    interline=20,
                    margin=(5, 20, 5, 20)  # left, top, right, bottom
                )

            line_clips.append(word_clip)
            line_total_width += word_clip.w

        # Center the line horizontally
        start_x = (width - line_total_width) // 2
        current_x = start_x
        y_pos = start_y + (line_num * line_height)

        # Position each word in the line
        for clip in line_clips:
            positioned_clip = clip.with_position((current_x, y_pos)).with_duration(duration)
            text_clips.append(positioned_clip)
            current_x += clip.w

    # Combine all clips
    final = CompositeVideoClip(text_clips, size=(width, height), bg_color=None)
    return final


def create_animated_highlight_text(text: str, text_arabic: str, duration=5):
    # Create a background
    background = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(0, 0, 0, 255))
    background = background.with_duration(duration)
    background = background.with_opacity(0.50)  # 50% opacity

    # Arabic Caption
    text_clip_arabic = TextClip(
        font=FONT_ARABIC,
        text=text_arabic,
        color="white",
        font_size=FONT_SIZE_ARABIC,
        size=(MAX_SUB_WIDTH, None),
        method='caption',  # Enable word wrapping
        text_align="center",
        stroke_color="#030303",
        stroke_width=3,  # Gold stroke
        interline=30,
        margin=(10, 30, 30, 50)  # left, top, right, bottom
    )

    estimated_ar_height = text_clip_arabic.h
    font_size_arabic = FONT_SIZE_ARABIC
    while estimated_ar_height > MAX_ALLOWED_HEIGHT:
        font_size_arabic -= 5
        text_clip_arabic = TextClip(
            font=FONT_ARABIC,
            text=text_arabic,
            color="white",
            font_size=font_size_arabic,
            size=(MAX_SUB_WIDTH, None),
            method='caption',  # Enable word wrapping
            text_align="center",
            stroke_color="#030303",
            stroke_width=1,  # Gold stroke
            interline=20,
            margin=(10, 30, 10, 20)  # left, top, right, bottom
        )
        estimated_ar_height = text_clip_arabic.h
        print(f"Arabic Text height too high. Current Font Size: {font_size_arabic}")

    # Set the clip duration
    text_clip_arabic = text_clip_arabic.with_duration(duration)

    # Apply the movement
    text_clip_arabic = text_clip_arabic.with_position(
        (VIDEO_WIDTH / 2 - text_clip_arabic.w / 2, VIDEO_HEIGHT / 2 - text_clip_arabic.h))

    # Apply effects
    text_clip_arabic = text_clip_arabic.with_effects([vfx.CrossFadeIn(1.5), vfx.CrossFadeOut(1.5)])

    # English Caption
    # Create the text clip without a font parameter
    stroke_width = 3
    text_clip = TextClip(
        font=FONT,
        text=text,
        color="white",
        font_size=FONT_SIZE,
        size=(MAX_SUB_WIDTH, None),
        method='caption',  # Enable word wrapping
        text_align="center",
        stroke_color="#030303",
        stroke_width=stroke_width,
        interline=30,
        margin=(10, 20, 10, 30)  # left, top, right, bottom
    )
    y_english = VIDEO_HEIGHT / 2

    estimated_height = text_clip.h
    font_size = FONT_SIZE
    while estimated_height > MAX_ALLOWED_HEIGHT:
        font_size -= 5
        stroke_width = 2
        text_clip = TextClip(
            font=FONT,
            text=text,
            color="white",
            font_size=font_size,
            size=(MAX_SUB_WIDTH, None),
            method='caption',  # Enable word wrapping
            text_align="center",
            stroke_color="#030303",
            stroke_width=stroke_width,  # Gold stroke
            interline=20,
            margin=(10, 20, 10, 20)  # left, top, right, bottom
        )
        estimated_height = text_clip.h
        # y_english = VIDEO_HEIGHT / 2
        print(f"English Text height too high. Current Font Size: {font_size}")

    # Set the clip duration
    # text_clip = text_clip.with_duration(duration)
    text_clip = create_centered_individual_words(text=text, font_size=font_size, stroke_width=stroke_width, duration=duration)

    # Apply the movement
    # text_clip = text_clip.with_position((VIDEO_WIDTH / 2 - text_clip.w / 2, y_english))
    text_clip = text_clip.with_position((0, y_english))

    # Apply effects
    text_clip = text_clip.with_effects([vfx.CrossFadeIn(1.5), vfx.CrossFadeOut(1.5)])

    final_clip = CompositeVideoClip([background, text_clip, text_clip_arabic], size=(VIDEO_WIDTH, VIDEO_HEIGHT))

    # final_clip.preview()

    return final_clip


def create_arabic_text_clip(text: str,
                            font: str,
                            font_size: int,
                            duration: int = 5,
                            text_color=(255, 255, 255),
                            stroke_color=(0, 0, 0),
                            margin: Optional[Tuple[int, int, int, int]] = (10, 10, 20, 10)):
    # Arabic Caption
    # Create the text clip without a font parameter
    # For Arabic, we need to process the text first
    configuration = {
        'delete_harakat': False,
        'support_ligatures': True,
        'RIAL SIGN': True,
    }
    reshaper = arabic_reshaper.ArabicReshaper(configuration=configuration)
    reshaped_text = reshaper.reshape(text)
    arabic_display_text = get_display(reshaped_text)
    arabic_display_text = arabic_display_text[::-1]  # Reverse for proper RTL display
    text_clip_arabic = TextClip(
        font=font,
        text=text,
        color=text_color,
        font_size=font_size,
        text_align="center",
        stroke_color=stroke_color,
        stroke_width=1,
        margin=margin  # left, top, right, bottom
    )

    # Set the clip duration
    text_clip_arabic = text_clip_arabic.with_duration(duration)

    # # Apply the movement
    # text_clip_arabic = text_clip_arabic.with_position(position)

    # Apply effects
    text_clip_arabic = text_clip_arabic.with_effects([vfx.CrossFadeIn(1.5), vfx.CrossFadeOut(1.5)])

    return text_clip_arabic


def create_text_clip(text: str,
                     font: str,
                     font_size: int,
                     duration: int = 5,
                     text_color=(255, 255, 255),
                     stroke_color=(0, 0, 0),
                     margin: Optional[Tuple[int, int, int, int]] = (10, 10, 20, 10)):
    # English Caption
    # Create the text clip without a font parameter
    text_clip = TextClip(
        font=font,
        text=text,
        color=text_color,
        font_size=font_size,
        text_align="center",
        stroke_color=stroke_color,
        stroke_width=1,
        margin=margin,  # left, top, right, bottom
        method='label',  # Use 'label' for cleaner text rendering
        interline=2,  # Add interline spacing
    )

    # Set the clip duration
    text_clip = text_clip.with_duration(duration)

    # Apply effects
    text_clip = text_clip.with_effects([vfx.CrossFadeIn(1.5), vfx.CrossFadeOut(1.5)])

    return text_clip


def create_animated_surah(surah_arabic, surah_english, surah_bangla, meaning_en, duration=5):
    """Create an attractive overlay for surah information with GIF"""
    # Calculate how many loops needed
    min_duration = 5
    max_duration = 10

    # Load and prepare GIF
    try:
        # Load a PNG file with transparency
        logo_clip = ImageClip("quran/quran-logo.png", transparent=True)

        # Resize the clip to your desired dimensions
        logo_clip = logo_clip.resized(width=80)

        # Position the resized clip
        logo_clip = logo_clip.with_position((20, 20))

        logo_clip = logo_clip.with_duration(random.randint(min_duration, max_duration))

        # Apply fade animations (1 second fade in, 1 second fade out)
        logo_clip = logo_clip.with_start(0).with_effects([vfx.CrossFadeIn(1.5), vfx.CrossFadeOut(1.5)])

        # logo_clip.loop(duration=duration)

        # Create looped version
        logo_clip = logo_clip.with_effects([vfx.Loop(duration=duration)])
    except Exception as ex:
        print(ex)
        # Fallback if GIF is not available
        logo_clip = None

    # Arabic surah
    surah_clip_arabic = create_arabic_text_clip(text=surah_arabic,
                                                font=FONT_ARABIC_CALIGRAPH,
                                                font_size=50,
                                                duration=random.randint(min_duration, max_duration),
                                                margin=(10, 20, 20, 10),
                                                text_color=COLORS["arabic_text"],
                                                stroke_color=COLORS["stroke"]
                                                )
    # Apply the movement
    surah_clip_arabic = surah_clip_arabic.with_position((VIDEO_WIDTH - surah_clip_arabic.w, 5))
    surah_clip_arabic = surah_clip_arabic.with_effects([vfx.Loop(duration=duration)])

    # English Surah
    surah_clip_english = create_text_clip(text=surah_english.upper(),
                                          font=FONT_BOLD,
                                          font_size=20,
                                          duration=random.randint(min_duration, max_duration),
                                          margin=(10, 10, 20, 10),
                                          text_color=COLORS["english_text"],
                                          stroke_color=COLORS["stroke"])
    # Apply the movement
    surah_clip_english = surah_clip_english.with_position((VIDEO_WIDTH - surah_clip_english.w, surah_clip_arabic.h))
    surah_clip_english = surah_clip_english.with_effects([vfx.Loop(duration=duration)])

    # Bangla Surah
    surah_clip_bangla = create_text_clip(text=surah_bangla,
                                         font=FONT_BANGLA,
                                         font_size=20,
                                         duration=random.randint(min_duration, max_duration),
                                         margin=(10, 0, 20, 10),
                                         text_color=COLORS["bangla_text"],
                                         stroke_color=COLORS["stroke"])
    # Apply the movement
    surah_clip_bangla = surah_clip_bangla.with_position(
        (VIDEO_WIDTH - surah_clip_bangla.w, surah_clip_arabic.h + surah_clip_english.h))
    surah_clip_bangla = surah_clip_bangla.with_effects([vfx.Loop(duration=duration)])

    # English Meaning
    meaning_clip_english = create_text_clip(text=meaning_en,
                                            font=FONT_REGULAR,
                                            font_size=15,
                                            duration=random.randint(min_duration, max_duration),
                                            margin=(10, 0, 20, 10),
                                            text_color=COLORS["meaning_text"],
                                            stroke_color=COLORS["stroke"])
    # Apply the movement
    meaning_clip_english = meaning_clip_english.with_position(
        (VIDEO_WIDTH - meaning_clip_english.w, surah_clip_arabic.h + surah_clip_english.h + surah_clip_bangla.h))
    meaning_clip_english = meaning_clip_english.with_effects([vfx.Loop(duration=duration)])

    # Combine background and text
    # all_clips = [background, surah_clip_arabic, surah_clip_english, surah_clip_bangla, meaning_clip_english]
    all_clips = [surah_clip_arabic, surah_clip_english, surah_clip_bangla, meaning_clip_english]
    if logo_clip:
        all_clips.append(logo_clip)
    final_clip = CompositeVideoClip(all_clips, size=(VIDEO_WIDTH, VIDEO_HEIGHT), bg_color=None)

    return final_clip


def generate_verse_to_file(surah_no, verse_index, subtitle_arabic, subtitle_english, temp_manager, duration_pad=1):
    """Generate a single verse video and write it to a temporary file"""
    surah = f"{surah_no:03}"
    audio_ar_index = f"{(verse_index + 1):03}"
    audio_en_index = f"{(verse_index + 1):03}"

    temp_file, is_exists = temp_manager.get_or_create_temp_file(suffix=f'verse_{(verse_index + 1):03}.mov')
    duration = 0

    try:
        # Load audio with context managers
        audio_arabic = AudioFileClip(f"/mnt/7A4CEE3F674E3964/quran/000_versebyverse/{surah}{audio_ar_index}.mp3")
        audio_english = AudioFileClip(
            f"/mnt/7A4CEE3F674E3964/quran/quran-in-english-clearquran-mp3-verse-by-verse-edtion-allah/{surah}-{audio_en_index}.mp3")
        concat = concatenate_audioclips([audio_arabic, audio_english])
        duration = concat.duration + duration_pad

        if is_exists:
            # Close clips to free memory
            audio_arabic.close()
            audio_english.close()
            concat.close()
            return temp_file, duration

        # Create video
        # subtitle_video = create_animated_text(
        #     text=subtitle_english.strip(),
        #     text_arabic=subtitle_arabic.strip(),
        #     duration=duration
        # )

        subtitle_video = create_animated_highlight_text(
            text=subtitle_english.strip(),
            text_arabic=subtitle_arabic.strip(),
            duration=duration
        )

        video = subtitle_video.with_audio(concat)

        # video.preview()

        video.write_videofile(
            temp_file,
            fps=30,
            codec="qtrle",  # qtrle or png
            preset="ultrafast",
            threads=32,
            ffmpeg_params=[
                "-y"
            ]
        )

        # Close clips to free memory
        video.close()
        subtitle_video.close()
        concat.close()
        audio_arabic.close()
        audio_english.close()

        return temp_file, duration

    except Exception as e:
        print(f"Error generating verse {verse_index}: {e}")
        return None, duration


def generate_bismillah_to_file(temp_manager):
    """Generate bismillah video and write to temporary file"""
    temp_file, is_exists = temp_manager.get_or_create_temp_file(suffix='bismillah.mov')
    duration = 0

    try:
        # Load bismillah
        audio_arabic = AudioFileClip("/mnt/7A4CEE3F674E3964/quran/000_versebyverse/001001.mp3")

        audio_english = AudioFileClip(
            "/mnt/7A4CEE3F674E3964/quran/quran-in-english-verse-by-verse-mp3-allah/001-001.mp3")

        # All clip will play one after the other
        concat = concatenate_audioclips([audio_arabic, audio_english])
        duration = concat.duration + 1

        if is_exists:
            audio_arabic.close()
            audio_english.close()
            concat.close()
            return temp_file, duration

        bismillah_subtitle = json_to_srt(BASE_JSON_PATH.format(1))[0]
        subtitle_english = "In the name of Allah, the Gracious, the Merciful."

        # Create your text animation
        # subtitle_video = create_animated_text(
        #     text=subtitle_english,
        #     text_arabic=bismillah_subtitle,
        #     duration=duration
        # )

        subtitle_video = create_animated_highlight_text(
            text=subtitle_english,
            text_arabic=bismillah_subtitle,
            duration=duration
        )

        video = subtitle_video.with_audio(concat)
        video.write_videofile(
            temp_file,
            fps=30,
            codec="qtrle",
            preset="ultrafast",
            threads=32,
            ffmpeg_params=[
                "-y"
            ]
        )

        audio_arabic.close()
        audio_english.close()
        video.close()
        subtitle_video.close()
        concat.close()

        return temp_file, duration

    except Exception as e:
        print(f"Error generating bismillah: {e}")
        return None, duration


def loop_backgrounds(total_duration: int, temp_manager):
    """Create background video loop from background files using ffmpeg for concatenation"""
    print("🎨 Generating background video...")

    # Get all background videos
    background_files = sorted(glob.glob("data/processed-backgrounds/*.mp4"))

    if not background_files:
        print("⚠️ No background files found, using solid color background")
        # Fallback to solid color background
        background = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(0, 10, 20))
        return background.with_duration(total_duration)

    # Create a sequence of backgrounds with transitions
    backgrounds_with_transitions = []
    duration_left = total_duration

    while duration_left > 0:
        random.shuffle(background_files)
        for i, bg_video_file in enumerate(background_files):
            try:
                bg_video_clip = VideoFileClip(bg_video_file)
                if duration_left < bg_video_clip.duration:
                    temp_file, is_exists = temp_manager.get_or_create_temp_file(suffix=f"bg_{i:04d}.mp4")
                    if not is_exists:
                        print(f"Generating background video from: {bg_video_file}")
                        bg_video_clip = bg_video_clip.subclipped(0, duration_left)
                        bg_video_clip = bg_video_clip.with_effects([vfx.CrossFadeIn(2.0), vfx.CrossFadeOut(2.0)])
                        bg_video_clip.write_videofile(
                            temp_file,
                            fps=30,
                            codec="hevc_nvenc",
                            audio=False,
                            preset="p7",
                            bitrate="30M",
                            ffmpeg_params=[
                                "-tune", "hq",
                                "-movflags", "+faststart",
                                "-profile:v", "main10",
                                "-cq", "0",
                                "-pix_fmt", "yuv420p",
                                "-y"
                            ]
                        )
                    backgrounds_with_transitions.append(temp_file)
                else:
                    print(f"Adding background video: {bg_video_file}")
                    backgrounds_with_transitions.append(bg_video_file)

                duration_left -= bg_video_clip.duration

                bg_video_clip.close()

                if duration_left <= 0:
                    break

            except Exception as e:
                print(f"⚠️ Error loading background {bg_video_file}: {e}")
                continue

    # Concatenate with transitions using ffmpeg instead of MoviePy
    if backgrounds_with_transitions:
        try:
            # Create ffmpeg concat file list
            concat_list_path, _ = temp_manager.get_or_create_temp_file(suffix='video_concat_bg.txt')
            with open(concat_list_path, 'w') as f:
                for temp_file in backgrounds_with_transitions:
                    f.write(f"file '{os.path.abspath(temp_file)}'\n")

            # Use ffmpeg to concatenate with stream copy (no re-encoding)
            output_temp, _ = temp_manager.get_or_create_temp_file(suffix=f"video_final_background.mp4")

            concat_command = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_list_path,
                '-c', 'copy',  # Stream copy - fastest and lossless
                '-y',
                output_temp
            ]

            result = subprocess.run(concat_command)
            if result.returncode == 0:
                return output_temp
            else:
                print(f"⚠️ FFmpeg concatenation failed: {result.stderr}")
                # Fallback to MoviePy concatenation
                print("🔄 Falling back to MoviePy concatenation...")
                background_video = concatenate_videoclips(backgrounds_with_transitions)
                print(f"✅ Background video created with MoviePy: {background_video.duration:.1f}s")
                return background_video

        except Exception as e:
            print(f"⚠️ FFmpeg concatenation error, using MoviePy fallback: {e}")
            background_video = concatenate_videoclips(backgrounds_with_transitions)
            print(f"✅ Background video created with MoviePy fallback: {background_video.duration:.1f}s")
            return background_video

    return None


def concatenate_video_files(video_files, output_path, surah_info, total_duration, temp_manager):
    """Concatenate video files using ffmpeg for memory efficiency"""
    if not video_files:
        print("❌ No video files to concatenate")
        return None

    try:
        print(f"🔗 Concatenating {len(video_files)} video files using ffmpeg...")

        # Step 1: Create file list for ffmpeg concat
        file_list_path, is_exists = temp_manager.get_or_create_temp_file(suffix='video_filelist.txt')

        with open(file_list_path, 'w', encoding='utf-8') as f:
            for video_file in video_files:
                if os.path.exists(video_file):
                    # ffmpeg concat format: file 'path/to/file.mp4'
                    f.write(f"file '{os.path.abspath(video_file)}'\n")

        # Check if we have valid files in the list
        with open(file_list_path, 'r', encoding='utf-8') as f:
            file_count = len(f.readlines())

        if file_count == 0:
            print("❌ No valid video files found for concatenation")
            return None

        # Step 2: Use ffmpeg to concatenate all videos
        temp_concat_file, _ = temp_manager.get_or_create_temp_file(suffix='video_concat.mov')

        # First pass: Simple concatenation
        concat_command = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', file_list_path,
            '-c', 'copy',  # Stream copy (no re-encoding)
            '-y',  # Overwrite output file
            temp_concat_file
        ]

        print("📦 Concatenating videos (stream copy)...")
        import subprocess
        result = subprocess.run(concat_command, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ FFmpeg concatenation failed: {result.stderr}")
            return

        # Add surah overlay if needed
        overlay_temp, is_exists = temp_manager.get_or_create_temp_file(suffix='video_overlay.mov')
        surah_name_ar, surah_name_en, surah_name_bn, surah_meaning_en = surah_info

        if not is_exists:
            surah_clip = create_animated_surah(
                surah_name_ar, surah_name_en, surah_name_bn, surah_meaning_en, 15
            )

            if surah_clip.duration > total_duration:
                surah_clip = surah_clip.subclipped(0, total_duration)

            surah_clip.write_videofile(
                overlay_temp,
                fps=30,
                codec="qtrle",
                audio=False,
                preset="ultrafast",
                threads=32,
                ffmpeg_params=[
                    "-y"
                ]
            )

            surah_clip.close()

        # Step 4: Concatenated background video files
        background_video = loop_backgrounds(total_duration=total_duration, temp_manager=temp_manager)

        # Step 4: Use ffmpeg to composite everything
        final_command = [
            'ffmpeg',
            '-i', background_video,  # Background video
            '-i', temp_concat_file,  # Main content video
            '-stream_loop', '-1',
            '-i', overlay_temp,  # Overlay video (transparent)
            '-filter_complex',
            '[0:v]setpts=PTS-STARTPTS[bg];'  # Background
            '[1:v]setpts=PTS-STARTPTS[main];'  # Main content
            '[2:v]setpts=PTS-STARTPTS[overlay_with_alpha];'  # Overlay with alpha
            '[bg][main]overlay=0:0:format=auto[bg_main];'  # Overlay main on background
            '[bg_main][overlay_with_alpha]overlay=0:0:format=auto[outv]'  # Overlay surah info
        ]

        # Add audio from the main content
        final_command.extend([
            '-map', '[outv]',  # Use the composed video
            '-map', '1:a?',  # Audio from main content (if exists)
            '-c:v', 'hevc_nvenc',  # Your preferred encoder
            '-c:a', 'aac',
            '-preset', 'p7',
            '-b:v', '30M',
            '-tune', 'hq',
            '-movflags', '+faststart',
            '-profile:v', 'main10',
            '-pix_fmt', 'yuv420p',
            '-shortest',
            '-y',
            output_path
        ])

        print("🎬 Final compositing with ffmpeg...")
        print(f'FFMPEG Command: {" ".join(final_command)}')
        result = subprocess.run(final_command)

        if result.returncode == 0:
            return True

        print(f"❌ Final compositing failed: {result.stderr}")

    except Exception as ex:
        print(ex)

    return False


def generate_videos(surah_no: int):
    """Main function that writes each verse to file to save memory"""
    temp_manager = TempFileManager(surah_no=surah_no)
    success = False

    try:
        print(f"Processing Surah {surah_no}...")

        # Load chapter info
        with open(CHAPTERS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data_en = data["en"][f"{surah_no}"]
        data_ar = data["ar"][f"{surah_no}"]
        verse_count = int(data["en"][f"{surah_no}"]["versesCount"])
        print(f"Total verses: {verse_count}")

        surah_info = (
            # 'سورة' + f' {data_ar["transliteratedName"]}',
            f"{surah_no}",
            f'Surah {data_en["transliteratedName"]}',
            f'সূরা {constants.BENGALI_NAMES.get(str(surah_no), "")}',
            data_en["translatedName"]
        )

        video_files = []
        total_duration = 0

        # Generate bismillah if needed
        if surah_no not in (1, 9):
            bismillah_file, duration = generate_bismillah_to_file(temp_manager)
            if bismillah_file:
                video_files.append(bismillah_file)
                # Estimate duration (you could get actual duration if needed)
                total_duration += duration

        # Generate each verse to separate file
        # for index, subtitle in enumerate(subtitles):
        for index in range(verse_count):
            print(f"Processing verse {index + 1}/{verse_count}")

            # Load English subtitle
            surah = f"{surah_no:03}"
            subtitle_file = f"quran/quran-english-verse-by-verse-allah/{surah}-{index + 1:03}.txt"
            if os.path.exists(subtitle_file):
                with open(subtitle_file, 'r', encoding='utf-8') as f:
                    subtitle_english = f.readline().strip()
            else:
                subtitle_english = ""

            subtitle_ar_file = f"quran/verse-by-verse/{surah}-{index + 1:03}.txt"
            if os.path.exists(subtitle_ar_file):
                with open(subtitle_ar_file, 'r', encoding='utf-8') as f:
                    subtitle_ar = f.readline().strip() + " " + to_arabic(index + 1)
            else:
                subtitle_ar = ""

            # Generate verse video to file
            if index + 1 == verse_count:
                verse_file, duration = generate_verse_to_file(
                    surah_no, index, subtitle_ar, subtitle_english, temp_manager, duration_pad=3
                )
            else:
                verse_file, duration = generate_verse_to_file(
                    surah_no, index, subtitle_ar, subtitle_english, temp_manager
                )

            # verse_file, duration = generate_verse_to_file(
            #     surah_no, index, dummy_sub["arabic_text"], dummy_sub["english_text"], temp_manager
            # )

            if verse_file:
                video_files.append(verse_file)
                total_duration += duration  # Estimate

            # Force garbage collection every few verses
            if index % 10 == 0:
                gc.collect()

        print(f"Generated {len(video_files)} video files, concatenating...")

        # Concatenate all temporary files
        output_path = BASE_OUTPUT_VIDEO_PATH.format(surah_no)
        success = concatenate_video_files(video_files, output_path, surah_info, total_duration,
                                          temp_manager=temp_manager)

        print(f"Successfully created: {output_path}")

    except Exception as e:
        print(f"Error processing Surah {surah_no}: {e}")
        raise
    finally:
        # Clean up temporary files
        if success:
            temp_manager.cleanup()
        gc.collect()


if __name__ == "__main__":
    generate_videos(110)

    # For multiple surahs:
    # for i in range(14, 18):
    #     generate_videos(i)
    #     gc.collect()
