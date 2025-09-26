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
FONT_ARABIC = "fonts/Amiri-Regular.ttf"
FONT_BANGLA = "fonts/Siyamrupali.ttf"
BASE_JSON_PATH = "quran/{}.json"
CHAPTERS_PATH = "quran/chapters.json"
BASE_OUTPUT_VIDEO_PATH = "quran-en/{}-video.mp4"
MAX_SUB_WIDTH = 1500
TARGET_MAX_HEIGHT = 1080
FONT_SIZE = 50
FONT_SIZE_ARABIC = 70

dummy_sub = {
    "arabic_text": "يَـٰٓأَيُّهَا ٱلَّذِينَ ءَامَنُوٓا۟ إِذَا تَدَايَنتُم بِدَيْنٍ إِلَىٰٓ أَجَلٍ مُّسَمًّى فَٱكْتُبُوهُ ۚ وَلْيَكْتُب بَّيْنَكُمْ كَاتِبٌۢ بِٱلْعَدْلِ ۚ وَلَا يَأْبَ كَاتِبٌ أَن يَكْتُبَ كَمَا عَلَّمَهُ ٱللَّهُ ۚ فَلْيَكْتُبْ وَلْيُمْلِلِ ٱلَّذِى عَلَيْهِ ٱلْحَقُّ وَلْيَتَّقِ ٱللَّهَ رَبَّهُۥ وَلَا يَبْخَسْ مِنْهُ شَيْـًٔا ۚ فَإِن كَانَ ٱلَّذِى عَلَيْهِ ٱلْحَقُّ سَفِيهًا أَوْ ضَعِيفًا أَوْ لَا يَسْتَطِيعُ أَن يُمِلَّ هُوَ فَلْيُمْلِلْ وَلِيُّهُۥ بِٱلْعَدْلِ ۚ وَٱسْتَشْهِدُوا۟ شَهِيدَيْنِ مِن رِّجَالِكُمْ ۖ فَإِن لَّمْ يَكُونَا رَجُلَيْنِ فَرَجُلٌ وَٱمْرَأَتَانِ مِمَّن تَرْضَوْنَ مِنَ ٱلشُّهَدَآءِ أَن تَضِلَّ إِحْدَىٰهُمَا فَتُذَكِّرَ إِحْدَىٰهُمَا ٱلْأُخْرَىٰ ۚ وَلَا يَأْبَ ٱلشُّهَدَآءُ إِذَا مَا دُعُوا۟ ۚ وَلَا تَسْـَٔمُوٓا۟ أَن تَكْتُبُوهُ صَغِيرًا أَوْ كَبِيرًا إِلَىٰٓ أَجَلِهِۦ ۚ ذَٰلِكُمْ أَقْسَطُ عِندَ ٱللَّهِ وَأَقْوَمُ لِلشَّهَـٰدَةِ وَأَدْنَىٰٓ أَلَّا تَرْتَابُوٓا۟ ۖ إِلَّآ أَن تَكُونَ تِجَـٰرَةً حَاضِرَةً تُدِيرُونَهَا بَيْنَكُمْ فَلَيْسَ عَلَيْكُمْ جُنَاحٌ أَلَّا تَكْتُبُوهَا ۗ وَأَشْهِدُوٓا۟ إِذَا تَبَايَعْتُمْ ۚ وَلَا يُضَآرَّ كَاتِبٌ وَلَا شَهِيدٌ ۚ وَإِن تَفْعَلُوا۟ فَإِنَّهُۥ فُسُوقٌۢ بِكُمْ ۗ وَٱتَّقُوا۟ ٱللَّهَ ۖ وَيُعَلِّمُكُمُ ٱللَّهُ ۗ وَٱللَّهُ بِكُلِّ شَىْءٍ عَلِيمٌ",
    "en_text": "O believers! When you contract a loan for a fixed period of time, commit it to writing. Let the scribe maintain justice between the parties. The scribe should not refuse to write as Allah has taught them to write. They will write what the debtor dictates, bearing Allah in mind and not defrauding the debt. If the debtor is incompetent, weak, or unable to dictate, let their guardian dictate for them with justice. Call upon two of your men to witness. If two men cannot be found, then one man and two women of your choice will witness—so if one of the women forgets the other may remind her.<sup foot_note=76489>1</sup> The witnesses must not refuse when they are summoned. You must not be against writing ˹contracts˺ for a fixed period—whether the sum is small or great. This is more just ˹for you˺ in the sight of Allah, and more convenient to establish evidence and remove doubts. However, if you conduct an immediate transaction among yourselves, then there is no need for you to record it, but call upon witnesses when a deal is finalized. Let no harm come to the scribe or witnesses. If you do, then you have gravely exceeded ˹your limits˺. Be mindful of Allah, for Allah ˹is the One Who˺ teaches you. And Allah has ˹perfect˺ knowledge of all things.",
}

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
    background = ColorClip(size=(1920, 1080), color=(0, 0, 0, 255))
    background = background.with_duration(duration)
    background = background.with_opacity(0.2)  # 30% opacity

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
        text=arabic_display_text,
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
    min_duration = 3
    max_duration = 10

    # Load and prepare GIF
    try:
        # Load a PNG file with transparency
        logo_clip = ImageClip("quran/quran-logo.png", transparent=True)

        # Resize the clip to your desired dimensions
        logo_clip = logo_clip.resized(width=100)

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

    # Create a background
    width, height = 1920, 1080
    background = ColorClip(size=(width, height), color=(0, 0, 0, 0))
    background = background.with_duration(duration)
    background = background.with_opacity(0.0)  # 0% opacity

    # Arabic surah
    surah_clip_arabic = create_arabic_text_clip(text=surah_arabic,
                                                font=FONT_ARABIC,
                                                font_size=30,
                                                duration=random.randint(min_duration, max_duration),
                                                margin=(10, 20, 20, 20),
                                                text_color=COLORS["arabic_text"],
                                                stroke_color=COLORS["stroke"]
                                                )
    # Apply the movement
    surah_clip_arabic = surah_clip_arabic.with_position((width - surah_clip_arabic.w, 5))
    surah_clip_arabic = surah_clip_arabic.with_effects([vfx.Loop(duration=duration)])

    # English Surah
    surah_clip_english = create_text_clip(text=surah_english,
                                          font=FONT,
                                          font_size=20,
                                          duration=random.randint(3, 5),
                                          margin=(10, 10, 20, 10),
                                          text_color=COLORS["english_text"],
                                          stroke_color=COLORS["stroke"])
    # Apply the movement
    surah_clip_english = surah_clip_english.with_position((width - surah_clip_english.w, surah_clip_arabic.h))
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
        (width - surah_clip_bangla.w, surah_clip_arabic.h + surah_clip_english.h))
    surah_clip_bangla = surah_clip_bangla.with_effects([vfx.Loop(duration=duration)])

    # English Meaning
    meaning_clip_english = create_text_clip(text=meaning_en,
                                            font=FONT,
                                            font_size=18,
                                            duration=random.randint(min_duration, max_duration),
                                            margin=(10, 0, 20, 10),
                                            text_color=COLORS["meaning_text"],
                                            stroke_color=COLORS["stroke"])
    # Apply the movement
    meaning_clip_english = meaning_clip_english.with_position(
        (width - meaning_clip_english.w, surah_clip_arabic.h + surah_clip_english.h + surah_clip_bangla.h))
    meaning_clip_english = meaning_clip_english.with_effects([vfx.Loop(duration=duration)])

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

    # Create your text animation
    subtitle_video = create_animated_text(
        text=subtitle_english,
        text_arabic=subtitle_arabic,
        duration=concat.duration
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
    surah_name_ar = 'سورة' + f' {data_ar["transliteratedName"]}'
    surah_meaning_en = data_en["translatedName"]
    # Get Bengali name
    surah_name_bn = f'সূরা {constants.BENGALI_NAMES.get(str(surah_no), "")}'

    videos = []
    # if not surah al-fatihah then add bismillah
    if surah_no != 1:
        bismillah_subtitle = json_to_srt(BASE_JSON_PATH.format(1))[0]
        videos.append(generate_bismillah(subtitle_arabic=bismillah_subtitle,
                                         subtitle_english="In the name of Allah, the Gracious, the Merciful."))

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
            text=subtitle_english.strip(),
            text_arabic=subtitle.strip(),
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
    background_files = sorted(glob.glob("data/backgrounds/*.mp4"))

    # Create a sequence of backgrounds with transitions
    backgrounds_with_transitions = []
    duration_left = total_duration

    while duration_left > 0:
        random.shuffle(background_files)
        for bg_video_file in background_files:
            bg_video_clip = VideoFileClip(bg_video_file)
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

    # remaining_duration = total_duration - background_video.duration
    #
    # # If the background is shorter than needed, loop it
    # if background_video.duration < remaining_duration:
    #     background_video = background_video.loop(duration=remaining_duration)
    # # If it's longer, trim it
    # elif background_video.duration > remaining_duration:
    #     background_video = background_video.subclipped(0, remaining_duration)

    return background_video


def generate_videos(surah_no: int):
    # Generate video contents
    subtitles = json_to_srt(BASE_JSON_PATH.format(surah_no))
    video = generate_audio_with_subs(surah_no=surah_no, subtitles=subtitles)

    # Load your background video
    # background_video = loop_backgrounds(video.duration)
    # 
    # if background_video.duration > video.duration:
    #     background_video = background_video.subclipped(0, video.duration)

    # Overlay the text animation on the background video
    # final_video = CompositeVideoClip([background_video, video])
    final_video = CompositeVideoClip([video])

    # final_video.preview(fps=30)

    # When writing the final video, use higher quality settings
    # final_video.write_videofile(
    #     "output.mp4",
    #     fps=30,
    #     codec="h264_nvenc",
    #     audio_codec="aac",
    #     preset="p4",  # Better quality preset
    #     ffmpeg_params=[
    #         "-cq", "18",  # Better quality
    #         "-rc", "vbr",
    #         "-profile:v", "high",
    #         "-pix_fmt", "yuv420p",  # Ensure proper pixel format
    #         "-movflags", "+faststart",
    #         "-y"
    #     ]
    # )

    OUTPUT_VIDEO_PATH = BASE_OUTPUT_VIDEO_PATH.format(surah_no)
    final_video.write_videofile(
        OUTPUT_VIDEO_PATH,
        fps=30,
        codec="hevc_nvenc",
        audio_codec="aac",
        preset="p7",
        bitrate="50M",  # Very high bitrate
        ffmpeg_params=[
            "-tune", "hq",  # Low latency tuning
            "-movflags", "+faststart",
            "-profile:v", "main10",
            "-cq", "0",  # Constant quality mode (best)
            "-pix_fmt", "yuv420p",
            "-y"
        ]
    )

    # final_video.write_videofile(
    #     OUTPUT_VIDEO_PATH,
    #     fps=video.fps,
    #     codec="hevc_nvenc",  # Best compression for text content
    #     audio_codec="aac",
    #     preset="p7",  # Maximum quality preset
    #     bitrate="30M",  # High bitrate for crisp text
    #     ffmpeg_params=[
    #         "-tune", "hq",
    #         "-movflags", "+faststart",
    #         "-profile:v", "main10",
    #         "-pix_fmt", "p010le",
    #         "-cq", "0",  # Constant quality mode (best)
    #         "-rc", "vbr",
    #         "-b:v", "30M",
    #         "-maxrate", "60M",
    #         "-bufsize", "60M",
    #         "-bf", "4",
    #         "-refs", "4",
    #         "-y"
    #     ]
    # )

    # final_video.write_videofile(
    #     OUTPUT_VIDEO_PATH,
    #     fps=video.fps,
    #     codec="libx264",  # Software encoding
    #     audio_codec="aac",
    #     threads=128,  # NOW this matters - use your CPU cores
    #     preset="ultrafast",
    #     ffmpeg_params=[
    #         "-tune", "film",
    #         "-movflags", "+faststart",
    #         "-profile:v", "high",
    #         "-pix_fmt", "yuv420p",
    #         "-y"
    #     ]
    # )


if __name__ == "__main__":
    generate_videos(36)
    # for i in range(61, 66):
    #     generate_videos(i)
