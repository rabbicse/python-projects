import glob
import json
import os
import random
from typing import Optional, List, Tuple

import constants

os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"

import arabic_reshaper
from bidi.algorithm import get_display
from moviepy import *

# get path to default font of the system. Make sure to change it
FONT = "fonts/DejaVuSans.ttf"
# FONT_ARABIC = "fonts/Amiri-Regular.ttf"
FONT_ARABIC = "fonts/uthmanic_hafs_v20.ttf"
FONT_BANGLA = "fonts/Siyamrupali.ttf"
BASE_JSON_PATH = "quran/{}.json"
CHAPTERS_PATH = "quran/chapters.json"
BASE_OUTPUT_VIDEO_PATH = "quran-shorts/{}-video.mp4"
MAX_SUB_WIDTH = 900
TARGET_MAX_HEIGHT = 1920
FONT_SIZE = 60
FONT_SIZE_ARABIC = 90
VIDEO_WIDTH, VIDEO_HEIGHT = 1080, 1920

# Color scheme - Attractive Islamic-inspired colors
COLORS = {
    "background": (0, 10, 20),  # Deep blue-black
    "arabic_text": (255, 215, 0),  # Gold
    "english_text": (230, 230, 250),  # Lavender
    "bangla_text": (176, 224, 230),  # Powder blue
    "meaning_text": (230, 230, 250),  # Light lavender
    "stroke": (0, 0, 0),  # Midnight blue
    "overlay_bg": (0, 0, 0, 180)  # Semi-transparent black
}

def to_arabic(num: int) -> str:
    # Western to Arabic-Indic digits map (Unicode escapes)
    digits = ["\u0660", "\u0661", "\u0662", "\u0663", "\u0664",
              "\u0665", "\u0666", "\u0667", "\u0668", "\u0669"]
    return "".join(digits[int(d)] for d in str(num))


def create_animated_surah(surah_arabic, surah_english, surah_bangla, meaning_en, duration=5):
    """Create an attractive overlay for surah information with GIF"""
    # Calculate how many loops needed
    min_duration = 3
    max_duration = 5

    # Load and prepare GIF
    try:
        # Load a PNG file with transparency
        logo_clip = ImageClip("quran/quran-logo.png", transparent=True)

        # Resize the clip to your desired dimensions
        logo_clip = logo_clip.resized(width=50)

        # Position the resized clip
        logo_clip = logo_clip.with_position((5, 5))

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
                                                font=FONT_ARABIC,
                                                font_size=80,
                                                duration=random.randint(min_duration, max_duration),
                                                margin=(5, 10, 5, 50),
                                                text_color=COLORS["arabic_text"],
                                                stroke_color=COLORS["stroke"]
                                                )
    # Apply the movement
    surah_clip_arabic = surah_clip_arabic.with_position((VIDEO_WIDTH / 2 - surah_clip_arabic.w / 2, 5))
    surah_clip_arabic = surah_clip_arabic.with_effects([vfx.Loop(duration=duration)])

    # English Surah
    surah_clip_english = create_text_clip(text=surah_english,
                                          font=FONT,
                                          font_size=30,
                                          duration=random.randint(3, 5),
                                          margin=(5, 10, 5, 10),
                                          text_color=COLORS["english_text"],
                                          stroke_color=COLORS["stroke"])
    # Apply the movement
    surah_clip_english = surah_clip_english.with_position((VIDEO_WIDTH / 2 - surah_clip_english.w / 2, surah_clip_arabic.h))
    surah_clip_english = surah_clip_english.with_effects([vfx.Loop(duration=duration)])

    # Bangla Surah
    surah_clip_bangla = create_text_clip(text=surah_bangla,
                                         font=FONT_BANGLA,
                                         font_size=30,
                                         duration=random.randint(min_duration, max_duration),
                                         margin=(5, 0, 5, 10),
                                         text_color=COLORS["bangla_text"],
                                         stroke_color=COLORS["stroke"])
    # Apply the movement
    surah_clip_bangla = surah_clip_bangla.with_position(
        (VIDEO_WIDTH / 2 - surah_clip_bangla.w / 2, surah_clip_arabic.h + surah_clip_english.h))
    surah_clip_bangla = surah_clip_bangla.with_effects([vfx.Loop(duration=duration)])

    # English Meaning
    meaning_clip_english = create_text_clip(text=meaning_en,
                                            font=FONT,
                                            font_size=25,
                                            duration=random.randint(min_duration, max_duration),
                                            margin=(5, 0, 5, 10),
                                            text_color=COLORS["meaning_text"],
                                            stroke_color=COLORS["stroke"])
    # Apply the movement
    meaning_clip_english = meaning_clip_english.with_position(
        (VIDEO_WIDTH / 2 - meaning_clip_english.w / 2, surah_clip_arabic.h + surah_clip_english.h + surah_clip_bangla.h))
    meaning_clip_english = meaning_clip_english.with_effects([vfx.Loop(duration=duration)])

    # Combine background and text
    all_clips = [surah_clip_arabic, surah_clip_english, surah_clip_bangla, meaning_clip_english]
    if logo_clip:
        all_clips.append(logo_clip)
    final_clip = CompositeVideoClip(all_clips, size=(VIDEO_WIDTH, VIDEO_HEIGHT), bg_color=None)

    return final_clip


def create_animated_text(text, text_arabic, duration=5, fps=30):
    # Create a background
    background = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(0, 0, 0, 255))
    background = background.with_duration(duration)
    background = background.with_opacity(0.4)  # 30% opacity

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
        margin=(10, 30, 10, 30)  # left, top, right, bottom
    )

    estimated_ar_height = text_clip_arabic.h
    if estimated_ar_height > TARGET_MAX_HEIGHT / 2:
        # Ensure the new size is smaller than or equal to the test size
        scale_factor = min(1.0, TARGET_MAX_HEIGHT / estimated_ar_height)
        font_size = int(FONT_SIZE_ARABIC * scale_factor)

        text_clip_arabic = TextClip(
            font=FONT_ARABIC,
            text=arabic_display_text,
            color="white",
            font_size=font_size,
            size=(MAX_SUB_WIDTH, None),
            method='caption',  # Enable word wrapping
            text_align="center",
            stroke_color="#030303",
            stroke_width=1,  # Gold stroke
            interline=20,
            margin=(10, 20, 10, 20)  # left, top, right, bottom
        )

    # Set the clip duration
    text_clip_arabic = text_clip_arabic.with_duration(duration)

    # Apply the movement
    text_clip_arabic = text_clip_arabic.with_position(
        (background.w / 2 - text_clip_arabic.w / 2, background.h / 2 - text_clip_arabic.h))

    # Apply effects
    text_clip_arabic = text_clip_arabic.with_effects([vfx.CrossFadeIn(0.5), vfx.CrossFadeOut(0.5)])

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

    estimated_height = text_clip.h
    if estimated_height > TARGET_MAX_HEIGHT / 2:
        # Ensure the new size is smaller than or equal to the test size
        scale_factor = min(1.0, TARGET_MAX_HEIGHT / estimated_ar_height)
        font_size = int(FONT_SIZE * scale_factor)

        text_clip = TextClip(
            font=FONT,
            text=text,
            color="white",
            font_size=font_size,
            size=(MAX_SUB_WIDTH, None),
            method='caption',  # Enable word wrapping
            text_align="center",
            stroke_color="#030303",
            stroke_width=1,  # Gold stroke
            interline=20,
            margin=(10, 20, 10, 20)  # left, top, right, bottom
        )

    # Set the clip duration
    text_clip = text_clip.with_duration(duration)

    # Apply the movement
    text_clip = text_clip.with_position((background.w / 2 - text_clip.w / 2, background.h / 2))

    # Apply effects
    text_clip = text_clip.with_effects([vfx.CrossFadeIn(0.5), vfx.CrossFadeOut(0.5)])

    # Combine background and text
    final_clip = CompositeVideoClip([background, text_clip, text_clip_arabic])

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


def generate_bismillah(subtitle_arabic: str, subtitle_english: str):
    # Load bismillah
    audio_arabic = AudioFileClip("/mnt/7A4CEE3F674E3964/quran/000_versebyverse/001001.mp3")

    audio_english = AudioFileClip("/mnt/7A4CEE3F674E3964/quran/quran-in-english-verse-by-verse-mp3-allah/001-001.mp3")

    # All clip will play one after the other
    concat = concatenate_audioclips([audio_arabic, audio_english])

    # Create your text animation
    subtitle_video = create_animated_text(
        text=subtitle_english,
        text_arabic=subtitle_arabic,
        duration=concat.duration
    )

    final_video = subtitle_video.with_audio(concat)

    return final_video


def generate_audio_with_subs(surah_no: int):
    # Load bismillah
    surah = f"{surah_no:03}"

    with open(CHAPTERS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data_en = data["en"][f"{surah_no}"]
    data_ar = data["ar"][f"{surah_no}"]

    surah_name_en = f'Surah {data_en["transliteratedName"]}'
    surah_name_ar = 'سورة' + f' {data_ar["transliteratedName"]}'
    surah_meaning_en = data_en["translatedName"]
    # Get Bengali name
    surah_name_bn = f'সূরা {constants.BENGALI_NAMES.get(str(surah_no), "")}'
    verse_count = int(data["en"][f"{surah_no}"]["versesCount"])
    print(f"Total verses: {verse_count}")

    videos = []
    # if not surah al-fatihah then add bismillah
    num = 0
    if surah_no != 1:
        subtitle_ar_file = f"quran/verse-by-verse/001-001.txt"
        if os.path.exists(subtitle_ar_file):
            with open(subtitle_ar_file, 'r', encoding='utf-8') as f:
                subtitle_ar = f.readline().strip() + " " + to_arabic(1)
        else:
            subtitle_ar = ""
        bismillah_subtitle = subtitle_ar
        videos.append(generate_bismillah(subtitle_arabic=bismillah_subtitle,
                                         subtitle_english="In the name of Allah, the Gracious, the Merciful."))
        num += 1

    # loop through each audio
    for index in range(verse_count):
        audio_ar_index = f"{(index + 1):03}"
        audio_en_index = f"{(index + 1):03}"
        audio_arabic = AudioFileClip(f"/mnt/7A4CEE3F674E3964/quran/000_versebyverse/{surah}{audio_ar_index}.mp3")

        audio_english = AudioFileClip(
            f"/mnt/7A4CEE3F674E3964/quran/quran-in-english-clearquran-mp3-verse-by-verse-edtion-allah/{surah}-{audio_en_index}.mp3")

        # All clip will play one after the other
        concat = concatenate_audioclips([audio_arabic, audio_english])

        with open(f"quran/quran-english-verse-by-verse-allah/{surah}-{audio_en_index}.txt") as f:
            subtitle_english = f.readline().strip()

        subtitle_ar_file = f"quran/verse-by-verse/{surah}-{index + 1:03}.txt"
        if os.path.exists(subtitle_ar_file):
            with open(subtitle_ar_file, 'r', encoding='utf-8') as f:
                subtitle_ar = f.readline().strip() + " " + to_arabic(index + num + 1)
        else:
            subtitle_ar = ""

        # Create your text animation
        subtitle_video = create_animated_text(
            text=subtitle_english.strip(),
            text_arabic=subtitle_ar,
            duration=concat.duration
        )

        # subtitle_video = create_animated_text(
        #     text=dummy_sub["en_text"],
        #     text_arabic=dummy_sub["arabic_text"],
        #     duration=concat.duration
        # )

        video = subtitle_video.with_audio(concat)
        videos.append(video)

    # Concatenate the final video clips, playing them one after the other
    if videos:
        final_video = concatenate_videoclips(videos)

        surah_clip = create_animated_surah(surah_arabic=surah_name_ar,
                                           surah_english=surah_name_en,
                                           surah_bangla=surah_name_bn,
                                           meaning_en=surah_meaning_en,
                                           duration=final_video.duration)

        if surah_clip.duration > final_video.duration:
            surah_clip = surah_clip.subclipped(0, final_video.duration)

        final_video = CompositeVideoClip([final_video, surah_clip])

        return final_video
    else:
        return None


def loop_backgrounds(total_duration: int):
    # Get all background videos
    background_files = sorted(glob.glob("data/short-backgrounds/*.mp4"))

    # Create a sequence of backgrounds with transitions
    backgrounds_with_transitions = []
    duration_left = total_duration

    while duration_left > 0:
        random.shuffle(background_files)
        for bg_video_file in background_files:
            bg_video_clip = VideoFileClip(bg_video_file).without_audio()
            bg_video_clip = bg_video_clip.with_effects([vfx.CrossFadeIn(1.0), vfx.CrossFadeOut(1.0)])

            if duration_left < bg_video_clip.duration:
                bg_video_clip = bg_video_clip.subclipped(0, duration_left)
                backgrounds_with_transitions.append(bg_video_clip)
            else:
                backgrounds_with_transitions.append(bg_video_clip)

            duration_left -= bg_video_clip.duration

            if duration_left <= 0:
                break

    # Concatenate with transitions
    background_video = concatenate_videoclips(backgrounds_with_transitions)

    return background_video


def generate_videos(surah_no: int):
    # Generate video contents
    video = generate_audio_with_subs(surah_no=surah_no)

    # Load your background video
    background_video = loop_backgrounds(video.duration)
    if background_video.duration > video.duration:
        background_video = background_video.subclipped(0, video.duration)

    # Overlay the text animation on the background video
    final_video = CompositeVideoClip([background_video, video])
    # final_video = CompositeVideoClip([video])

    # final_video.preview()

    OUTPUT_VIDEO_PATH = BASE_OUTPUT_VIDEO_PATH.format(surah_no)
    final_video.write_videofile(
        OUTPUT_VIDEO_PATH,
        fps=30,
        codec="hevc_nvenc",
        audio_codec="aac",
        preset="p7",
        bitrate="30M",  # Very high bitrate
        ffmpeg_params=[
            "-tune", "hq",  # Low latency tuning
            "-movflags", "+faststart",
            "-profile:v", "main10",
            "-cq", "0",  # Constant quality mode (best)
            "-pix_fmt", "yuv420p",
            "-y"
        ]
    )


if __name__ == "__main__":
    generate_videos(108)
