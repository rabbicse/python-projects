import json
import os
from typing import Optional, List, Tuple

import constants

os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"

import arabic_reshaper
from bidi.algorithm import get_display
from moviepy import *

# get path to default font of the system. Make sure to change it
FONT = "fonts/DejaVuSans.ttf"
FONT_ARABIC = "fonts/Amiri-Regular.ttf"
FONT_BANGLA = "fonts/Siyamrupali.ttf"
BASE_JSON_PATH = "quran/{}.json"
CHAPTERS_PATH = "quran/chapters.json"

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


def generate_srt(data):
    verse_timings = data["audio"]["audio_files"][0]["verse_timings"]
    verses = {v["verse_key"]: v for v in data["surah_verses"]}

    srt_lines = []

    for timing in verse_timings:
        verse_key = timing["verse_key"]
        if verse_key not in verses:
            continue

        srt_lines.append(verses[verse_key]["arabic_text"])

    return srt_lines


def json_to_srt(json_file):
    with open(json_file, "r+", encoding="utf-8") as f:
        data = json.load(f)
    return generate_srt(data)


def create_animated_text(text, text_arabic, duration=5, fps=30):
    # Create a background
    background = ColorClip(size=(1920, 1080), color=(0, 0, 0, 0))
    background = background.with_duration(duration)
    background = background.with_opacity(0.3)  # 30% opacity

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
        text=arabic_display_text,
        color="white",
        font_size=50,
        size=(1800, None),
        method='caption',  # Enable word wrapping
        text_align="center",
        stroke_color="#030303",
        stroke_width=3,  # Gold stroke
        interline=30,
        margin=(10, 20, 10, 20)  # left, top, right, bottom
    )

    # Set the clip duration
    text_clip_arabic = text_clip_arabic.with_duration(duration)

    # Apply the movement
    text_clip_arabic = text_clip_arabic.with_position(
        (background.w / 2 - text_clip_arabic.w / 2, background.h / 2 - text_clip_arabic.h - 50))

    # Apply effects
    text_clip_arabic = text_clip_arabic.with_effects([vfx.CrossFadeIn(0.5), vfx.CrossFadeOut(0.5)])

    # English Caption
    # Create the text clip without a font parameter
    text_clip = TextClip(
        font=FONT,
        text=text,
        color="white",
        font_size=35,
        size=(1800, None),
        method='caption',  # Enable word wrapping
        text_align="center",
        stroke_color="#030303",
        stroke_width=3,
        interline=30,
        margin=(10, 20, 10, 20)  # left, top, right, bottom
    )

    # Set the clip duration
    text_clip = text_clip.with_duration(duration)

    # Apply the movement
    text_clip = text_clip.with_position((background.w / 2 - text_clip.w / 2, background.h / 2 + 50))

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
                            margin: Optional[Tuple[int, int, int, int]] = (10, 10, 10, 10)):
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
        text=arabic_display_text,
        color=text_color,
        font_size=font_size,
        text_align="center",
        stroke_color=stroke_color,
        stroke_width=3,
        margin=margin  # left, top, right, bottom
    )

    # Set the clip duration
    text_clip_arabic = text_clip_arabic.with_duration(duration)

    # # Apply the movement
    # text_clip_arabic = text_clip_arabic.with_position(position)

    # Apply effects
    text_clip_arabic = text_clip_arabic.with_effects([vfx.CrossFadeIn(0.5), vfx.CrossFadeOut(0.5)])

    return text_clip_arabic


def create_text_clip(text: str,
                     font: str,
                     font_size: int,
                     duration: int = 5,
                     text_color=(255, 255, 255),
                     stroke_color=(0, 0, 0),
                     margin: Optional[Tuple[int, int, int, int]] = (10, 10, 10, 10)):
    # English Caption
    # Create the text clip without a font parameter
    text_clip = TextClip(
        font=font,
        text=text,
        color=text_color,
        font_size=font_size,
        text_align="center",
        stroke_color=stroke_color,
        stroke_width=3,
        margin=margin,  # left, top, right, bottom
        method='label',  # Use 'label' for cleaner text rendering
        interline=2,  # Add interline spacing
    )

    # Set the clip duration
    text_clip = text_clip.with_duration(duration)

    # Apply effects
    text_clip = text_clip.with_effects([vfx.CrossFadeIn(0.5), vfx.CrossFadeOut(0.5)])

    return text_clip


def create_animated_surah(surah_arabic, surah_english, surah_bangla, meaning_en, duration=5, fps=30):
    """Create an attractive overlay for surah information with GIF"""
    # Calculate how many loops needed
    num_loops = int(duration / 5) + 1  # +1 to ensure it covers full duration

    # Load and prepare GIF
    try:
        # Load a PNG file with transparency
        logo_clip = ImageClip("quran/quran-logo.png", transparent=True)

        # Resize the clip to your desired dimensions
        logo_clip = logo_clip.resized(width=100)

        # Position the resized clip
        logo_clip = logo_clip.with_position((20, 20))

        logo_clip = logo_clip.with_duration(5)

        # Apply fade animations (1 second fade in, 1 second fade out)
        logo_clip = logo_clip.with_start(0).with_effects([vfx.CrossFadeIn(1.0), vfx.CrossFadeOut(1.0)])

        # logo_clip.loop(duration=duration)

        # Create looped version
        logo_clip = logo_clip.with_effects([vfx.Loop(n=num_loops)])
    except Exception as ex:
        print(ex)
        # Fallback if GIF is not available
        logo_clip = None

    # Create a background
    width, height = 1920, 1080
    background = ColorClip(size=(width, height), color=(0, 0, 0, 0))
    background = background.with_duration(duration)
    # background = background.with_opacity(0.0)  # 0% opacity

    # Arabic surah
    surah_clip_arabic = create_arabic_text_clip(text=surah_arabic,
                                                font=FONT_ARABIC,
                                                font_size=30,
                                                duration=5,
                                                margin=(10, 10, 10, 10),
                                                text_color=COLORS["arabic_text"],
                                                stroke_color=COLORS["stroke"]
                                                )
    # Apply the movement
    surah_clip_arabic = surah_clip_arabic.with_position((width - surah_clip_arabic.w, 5))
    surah_clip_arabic = surah_clip_arabic.with_effects([vfx.Loop(n=num_loops)])

    # English Surah
    surah_clip_english = create_text_clip(text=surah_english,
                                          font=FONT,
                                          font_size=20,
                                          duration=5,
                                          margin=(10, 10, 10, 10),
                                          text_color=COLORS["english_text"],
                                          stroke_color=COLORS["stroke"])
    # Apply the movement
    surah_clip_english = surah_clip_english.with_position((width - surah_clip_english.w, surah_clip_arabic.h))
    surah_clip_english = surah_clip_english.with_effects([vfx.Loop(n=num_loops)])

    # Bangla Surah
    surah_clip_bangla = create_text_clip(text=surah_bangla,
                                         font=FONT_BANGLA,
                                         font_size=20,
                                         duration=5,
                                         margin=(10, 0, 10, 0),
                                         text_color=COLORS["bangla_text"],
                                         stroke_color=COLORS["stroke"])
    # Apply the movement
    surah_clip_bangla = surah_clip_bangla.with_position(
        (width - surah_clip_bangla.w, surah_clip_arabic.h + surah_clip_english.h))
    surah_clip_bangla = surah_clip_bangla.with_effects([vfx.Loop(n=num_loops)])

    # English Meaning
    meaning_clip_english = create_text_clip(text=meaning_en,
                                            font=FONT,
                                            font_size=15,
                                            duration=5,
                                            margin=(10, 0, 10, 10),
                                            text_color=COLORS["meaning_text"],
                                            stroke_color=COLORS["stroke"])
    # Apply the movement
    meaning_clip_english = meaning_clip_english.with_position(
        (width - meaning_clip_english.w, surah_clip_arabic.h + surah_clip_english.h + surah_clip_bangla.h))
    meaning_clip_english = meaning_clip_english.with_effects([vfx.Loop(n=num_loops)])

    # Combine background and text
    all_clips = [background, surah_clip_arabic, surah_clip_english, surah_clip_bangla, meaning_clip_english]
    if logo_clip:
        all_clips.append(logo_clip)
    final_clip = CompositeVideoClip(all_clips)

    return final_clip


def generate_bismillah(subtitle_arabic: str, subtitle_english: str):
    # Load bismillah
    audio_arabic = AudioFileClip("/mnt/7A4CEE3F674E3964/quran/000_versebyverse/001001.mp3")

    audio_english = AudioFileClip("/mnt/7A4CEE3F674E3964/quran/quran-in-english-verse-by-verse-mp3-allah/001-001.mp3")

    # All clip will play one after the other
    concat = concatenate_audioclips([audio_arabic, audio_english])

    # audio_arabic.with_volume_scaled(1.0)
    # audio = CompositeAudioClip([audio_arabic.with_volume_scaled(1), audio_english.with_volume_scaled(1)])

    # Create your text animation
    subtitle_video = create_animated_text(
        text=subtitle_english,
        text_arabic=subtitle_arabic,
        duration=concat.duration,  # Match your background video duration
        fps=30
    )

    final_video = subtitle_video.with_audio(concat)

    return final_video


def generate_audio_with_subs(surah_no: int, subtitles: Optional[List[str]]):
    # Load bismillah
    surah = f"{surah_no:03}"

    with open(CHAPTERS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data_en = data["en"][f"{surah_no}"]
    data_ar = data["ar"][f"{surah_no}"]

    surah_name_en = f'Surah {data_en["transliteratedName"]}'
    surah_name_ar = data_ar["transliteratedName"]
    surah_meaning_en = data_en["translatedName"]
    # Get Bengali name
    surah_name_bn = f'সূরা {constants.BENGALI_NAMES.get(str(surah_no), "")}'

    videos = []
    # loop through each audio
    for index, subtitle in enumerate(subtitles):
        audio_ar_index = f"{(index + 1):03}"
        audio_en_index = f"{(index + 1):03}"
        audio_arabic = AudioFileClip(f"/mnt/7A4CEE3F674E3964/quran/000_versebyverse/{surah}{audio_ar_index}.mp3")

        audio_english = AudioFileClip(
            f"/mnt/7A4CEE3F674E3964/quran/quran-in-english-clearquran-mp3-verse-by-verse-edtion-allah/{surah}-{audio_en_index}.mp3")

        # All clip will play one after the other
        concat = concatenate_audioclips([audio_arabic, audio_english])

        with open(f"quran/quran-english-verse-by-verse-allah/{surah}-{audio_en_index}.txt") as f:
            subtitle_english = f.readline().strip()

        # Create your text animation
        subtitle_video = create_animated_text(
            text=subtitle_english,
            text_arabic=subtitle,
            duration=concat.duration,  # Match your background video duration
            fps=30
        )

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

        final_video = CompositeVideoClip([final_video, surah_clip])

        return final_video
    else:
        return None


def main():
    # Generate video contents
    subtitles = json_to_srt(BASE_JSON_PATH.format(1))
    video = generate_audio_with_subs(surah_no=1, subtitles=subtitles)

    # Load your background video
    background_video = VideoFileClip("data/backgrounds/001.mp4")

    # Overlay the text animation on the background video
    final_video = CompositeVideoClip([background_video, video])

    # Mix audio - adjust volumes as needed
    # background_audio = background_audio.volumex(0.7)  # Reduce background music volume
    # You can add voiceover or other audio here if needed

    # Set the mixed audio to the final video
    # final_video = final_video.with_audio(background_audio)

    # Ensure the video duration matches the audio
    # final_video = final_video.with_duration(background_audio.duration)
    # final_video = final_video.with_duration(25)
    #
    # return final_video

    final_video.preview(fps=10)

    # # Write with audio
    # video.write_videofile(
    #     "test.mp4",
    #     fps=30,
    #     codec="h264_nvenc",
    #     audio_codec="aac",
    #     threads=1700,
    #     preset="p1",  # Fastest preset
    # )

    # # Write with audio - Simple GPU encoding
    # video.write_videofile(
    #     "test.mp4",
    #     fps=30,
    #     codec="h264_nvenc",  # This is the key for GPU encoding
    #     audio_codec="aac",
    #     threads=32,
    #     preset="p1",  # Fastest preset
    #     ffmpeg_params=[
    #         "-cq", "23",  # Quality level
    #         "-rc", "vbr",  # Variable bitrate
    #         "-profile:v", "high",  # H.264 profile
    #         "-movflags", "+faststart",  # Fast start for web
    #         "-y",  # Overwrite output
    #     ]
    # )

    # # Optimized for GTX 970 (1st gen NVENC)
    # video.write_videofile(
    #     "test.mp4",
    #     fps=30,
    #     codec="hevc_nvenc",
    #     audio_codec="aac",
    #     threads=32,  # Reduced threads for better stability
    #     preset="p1",  # Use p4 instead of p1 for GTX 970 (p1 may be too aggressive)
    #     ffmpeg_params=[
    #         # "-cq", "26",  # Slightly higher (worse) quality for speed
    #         # "-rc", "vbr",  # Variable bitrate
    #         # "-b:v", "8M",  # Set target bitrate instead of quality-based
    #         # "-maxrate", "12M",  # Maximum bitrate
    #         # "-bufsize", "16M",  # Buffer size
    #         "-profile:v", "main",  # Use main profile instead of high
    #         "-tune", "fastdecode",  # Optimize for fast decoding
    #         "-movflags", "+faststart",
    #         "-y"
    #     ]
    # )

    # When writing the final video, use higher quality settings
    final_video.write_videofile(
        "output.mp4",
        fps=30,
        codec="h264_nvenc",
        audio_codec="aac",
        preset="p4",  # Better quality preset
        ffmpeg_params=[
            "-cq", "18",  # Better quality
            "-rc", "vbr",
            "-profile:v", "high",
            "-pix_fmt", "yuv420p",  # Ensure proper pixel format
            "-movflags", "+faststart",
            "-y"
        ]
    )






if __name__ == "__main__":
    main()
