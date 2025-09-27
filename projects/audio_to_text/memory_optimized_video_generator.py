import glob
import json
import os
import random
from typing import Optional, List, Tuple
import gc
import tempfile
import shutil

import constants

os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"

import arabic_reshaper
from bidi.algorithm import get_display
from moviepy import *

# Configuration
FONT = "fonts/DejaVuSans.ttf"
FONT_ARABIC = "fonts/Amiri-Regular.ttf"
FONT_BANGLA = "fonts/Siyamrupali.ttf"
BASE_JSON_PATH = "quran/{}.json"
CHAPTERS_PATH = "quran/chapters.json"
BASE_OUTPUT_VIDEO_PATH = "quran-en/{}-video.mp4"
MAX_SUB_WIDTH = 1500
TARGET_MAX_HEIGHT = 1080
FONT_SIZE = 50
FONT_SIZE_ARABIC = 70

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080

# Color scheme
COLORS = {
    "background": (0, 10, 20),
    "arabic_text": (255, 215, 0),
    "english_text": (230, 230, 250),
    "bangla_text": (176, 224, 230),
    "meaning_text": (230, 230, 250),
    "stroke": (0, 0, 0),
    "overlay_bg": (0, 0, 0, 180)
}

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

    def create_temp_file(self, suffix='.mp4'):
        temp_file = tempfile.mktemp(suffix=suffix, dir=self.session_dir)
        self.temp_files.append(temp_file)
        return temp_file

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
    verse_timings = data["audio"]["audio_files"][0]["verse_timings"]
    verses = {v["verse_key"]: v for v in data["surah_verses"]}

    srt_lines = []
    for timing in verse_timings:
        verse_key = timing["verse_key"]
        if verse_key in verses:
            srt_lines.append(verses[verse_key]["arabic_text"])
    return srt_lines


def json_to_srt(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return generate_srt(data)


def create_animated_text(text, text_arabic, duration=5):
    # Create a background
    # background = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(0, 0, 0, 255))
    # background = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=CHROMA_KEY_COLOR)
    # background = background.with_duration(duration)
    # background = background.with_opacity(0.2)  # 30% opacity

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
        (VIDEO_WIDTH / 2 - text_clip_arabic.w / 2, VIDEO_HEIGHT / 2 - text_clip_arabic.h))

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
    text_clip = text_clip.with_position((VIDEO_WIDTH / 2 - text_clip.w / 2, VIDEO_HEIGHT / 2))

    # Apply effects
    text_clip = text_clip.with_effects([vfx.CrossFadeIn(1.5), vfx.CrossFadeOut(1.5)])

    # Combine background and text
    # final_clip = CompositeVideoClip([background, text_clip, text_clip_arabic])
    final_clip = CompositeVideoClip([text_clip, text_clip_arabic], size=(VIDEO_WIDTH, VIDEO_HEIGHT), bg_color=None)

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
    min_duration = 5
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
    # background = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=CHROMA_KEY_COLOR)
    # background = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(0, 0, 0, 0))
    # background = background.with_duration(duration)
    # background = background.with_opacity(0.0)  # 0% opacity

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
    surah_clip_arabic = surah_clip_arabic.with_position((VIDEO_WIDTH - surah_clip_arabic.w, 5))
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
                                            font=FONT,
                                            font_size=18,
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


def generate_verse_to_file(surah_no, verse_index, subtitle_arabic, subtitle_english, temp_manager):
    """Generate a single verse video and write it to a temporary file"""
    surah = f"{surah_no:03}"
    audio_ar_index = f"{(verse_index + 1):03}"
    audio_en_index = f"{(verse_index + 1):03}"

    temp_file = temp_manager.create_temp_file(suffix=f'_verse_{verse_index}.mov')
    duration = 0

    try:
        # Load audio with context managers
        audio_arabic = AudioFileClip(f"/mnt/7A4CEE3F674E3964/quran/000_versebyverse/{surah}{audio_ar_index}.mp3")
        audio_english = AudioFileClip(
            f"/mnt/7A4CEE3F674E3964/quran/quran-in-english-clearquran-mp3-verse-by-verse-edtion-allah/{surah}-{audio_en_index}.mp3")
        concat = concatenate_audioclips([audio_arabic, audio_english])

        # Create video
        subtitle_video = create_animated_text(
            text=subtitle_english.strip(),
            text_arabic=subtitle_arabic.strip(),
            duration=concat.duration
        )

        video = subtitle_video.with_audio(concat)
        duration = video.duration

        # # Write final video with high quality settings
        # video.write_videofile(
        #     temp_file,
        #     fps=30,
        #     codec="hevc_nvenc",
        #     audio_codec="aac",
        #     preset="p7",
        #     bitrate="50M",
        #     ffmpeg_params=[
        #         "-tune", "hq",
        #         "-movflags", "+faststart",
        #         "-profile:v", "main10",
        #         "-cq", "0",
        #         "-pix_fmt", "yuva420p",
        #         "-y"
        #     ],
        # )

        # # Write final video with high quality settings
        # video.write_videofile(
        #     temp_file,
        #     fps=30,
        #     codec="hevc_nvenc",
        #     audio_codec="aac",
        #     preset="p7",
        #     bitrate="50M",
        #     ffmpeg_params=[
        #         "-tune", "hq",
        #         "-movflags", "+faststart",
        #         "-profile:v", "main10",
        #         "-cq", "0",
        #         "-pix_fmt", "yuva420p",
        #         "-y"
        #     ],
        # )


        # video.write_videofile(
        #     temp_file,
        #     fps=30,
        #     codec="libvpx-vp9",
        #     ffmpeg_params=[
        #         "-pix_fmt", "yuva420p",  # alpha pixel format
        #         "-auto-alt-ref", "0",  # prevent VP9 from breaking alpha
        #         "-lossless", "1",  # preserve quality
        #         "-y"
        #     ]
        # )


        video.write_videofile(
            temp_file,
            fps=30,
            codec="png",
            preset="ultrafast",
            ffmpeg_params=[
                "-y"
            ]
        )

        # Close clips to free memory
        video.close()
        subtitle_video.close()
        concat.close()

        return temp_file, duration

    except Exception as e:
        print(f"Error generating verse {verse_index}: {e}")
        return None, duration


def generate_bismillah_to_file(temp_manager):
    """Generate bismillah video and write to temporary file"""
    temp_file = temp_manager.create_temp_file(suffix='_bismillah.mp4')
    duration = 0

    try:
        # Load bismillah
        audio_arabic = AudioFileClip("/mnt/7A4CEE3F674E3964/quran/000_versebyverse/001001.mp3")

        audio_english = AudioFileClip(
            "/mnt/7A4CEE3F674E3964/quran/quran-in-english-verse-by-verse-mp3-allah/001-001.mp3")

        # All clip will play one after the other
        concat = concatenate_audioclips([audio_arabic, audio_english])

        bismillah_subtitle = json_to_srt(BASE_JSON_PATH.format(1))[0]
        subtitle_english = "In the name of Allah, the Gracious, the Merciful."

        # Create your text animation
        subtitle_video = create_animated_text(
            text=subtitle_english,
            text_arabic=bismillah_subtitle,
            duration=concat.duration
        )

        video = subtitle_video.with_audio(concat)
        duration = video.duration

        # Write final video with high quality settings
        video.write_videofile(
            temp_file,
            fps=30,
            codec="hevc_nvenc",
            audio_codec="aac",
            preset="p7",
            bitrate="50M",
            ffmpeg_params=[
                "-tune", "hq",
                "-movflags", "+faststart",
                "-profile:v", "main10",
                "-cq", "0",
                "-pix_fmt", "yuv420p",
                "-y"
            ]
        )

        video.close()
        subtitle_video.close()
        concat.close()

        return temp_file, duration

    except Exception as e:
        print(f"Error generating bismillah: {e}")
        return None


def loop_backgrounds(total_duration: int, temp_manager):
    """Create background video loop from background files using ffmpeg for concatenation"""
    print("🎨 Generating background video...")

    # Get all background videos
    background_files = sorted(glob.glob("data/backgrounds/*.mp4"))

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
        for bg_video_file in background_files:
            try:
                bg_video_clip = VideoFileClip(bg_video_file)
                bg_video_clip = bg_video_clip.with_effects([vfx.CrossFadeIn(2.0), vfx.CrossFadeOut(2.0)])

                if duration_left < bg_video_clip.duration:
                    bg_video_clip = bg_video_clip.subclipped(0, duration_left)
                    backgrounds_with_transitions.append(bg_video_clip)
                else:
                    backgrounds_with_transitions.append(bg_video_clip)

                duration_left -= bg_video_clip.duration

                if duration_left <= 0:
                    break

            except Exception as e:
                print(f"⚠️ Error loading background {bg_video_file}: {e}")
                continue

    # Concatenate with transitions using ffmpeg instead of MoviePy
    if backgrounds_with_transitions:
        try:
            # Create temporary directory for intermediate files
            import tempfile
            import os
            temp_dir = tempfile.mkdtemp()

            # Write each clip to temporary file
            temp_files = []
            for i, clip in enumerate(backgrounds_with_transitions):
                temp_file = temp_manager.create_temp_file(suffix=f"_bg_{i:04d}.mp4")
                clip.write_videofile(
                    temp_file,
                    fps=30,
                    codec="hevc_nvenc",
                    preset="p7",
                    bitrate="50M",
                    ffmpeg_params=[
                        "-tune", "hq",
                        "-movflags", "+faststart",
                        "-profile:v", "main10",
                        "-cq", "0",
                        "-pix_fmt", "yuva420p",
                        "-y"
                    ]
                )
                temp_files.append(temp_file)
                clip.close()  # Free memory immediately

            # Create ffmpeg concat file list
            concat_list_path = temp_manager.create_temp_file(suffix='_concat_bg.txt')
            with open(concat_list_path, 'w') as f:
                for temp_file in temp_files:
                    f.write(f"file '{os.path.abspath(temp_file)}'\n")

            # Use ffmpeg to concatenate with stream copy (no re-encoding)
            import subprocess
            output_temp = temp_manager.create_temp_file(suffix=f"_final_background.mp4")

            concat_command = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_list_path,
                '-c', 'copy',  # Stream copy - fastest and lossless
                '-y',
                output_temp
            ]

            result = subprocess.run(concat_command, capture_output=True, text=True)

            if result.returncode == 0:
                # Load the final concatenated video
                # background_video = VideoFileClip(output_temp)
                # print(f"✅ Background video created with ffmpeg: {background_video.duration:.1f}s")

                # Clean up temporary files
                # for temp_file in temp_files + [concat_list_path, output_temp]:
                #     try:
                #         os.remove(temp_file)
                #     except:
                #         pass
                # try:
                #     os.rmdir(temp_dir)
                # except:
                #     pass

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
    else:
        print("⚠️ No valid background clips, using fallback")
        background = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(0, 10, 20))
        return background.with_duration(total_duration)

    return None


def concatenate_video_files(video_files, output_path, surah_info, total_duration, temp_manager):
    """Concatenate video files using ffmpeg for memory efficiency"""
    if not video_files:
        print("❌ No video files to concatenate")
        return None

    try:
        print(f"🔗 Concatenating {len(video_files)} video files using ffmpeg...")

        # Step 1: Create file list for ffmpeg concat
        file_list_path = temp_manager.create_temp_file(suffix='_filelist.txt')

        with open(file_list_path, 'w', encoding='utf-8') as f:
            for video_file in video_files:
                if os.path.exists(video_file) and os.path.getsize(video_file) > 1024:
                    # ffmpeg concat format: file 'path/to/file.mp4'
                    f.write(f"file '{os.path.abspath(video_file)}'\n")

        # Check if we have valid files in the list
        with open(file_list_path, 'r', encoding='utf-8') as f:
            file_count = len(f.readlines())

        if file_count == 0:
            print("❌ No valid video files found for concatenation")
            return None

        # Step 2: Use ffmpeg to concatenate all videos
        temp_concat_file = temp_manager.create_temp_file(suffix='_concat.mov')

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
        surah_name_ar, surah_name_en, surah_name_bn, surah_meaning_en = surah_info
        surah_clip = create_animated_surah(
            surah_name_ar, surah_name_en, surah_name_bn, surah_meaning_en, 10
        )

        if surah_clip.duration > total_duration:
            surah_clip = surah_clip.subclipped(0, total_duration)

        overlay_temp = temp_manager.create_temp_file(suffix='_overlay.mov')

        # surah_clip.write_videofile(
        #     overlay_temp,
        #     fps=30,
        #     codec="libvpx-vp9",
        #     # preset="p7",
        #     # bitrate="50M",  # Very high bitrate
        #     ffmpeg_params=[
        #         # "-tune", "hq",  # Low latency tuning
        #         # "-quality", "good",
        #         # "-movflags", "+faststart",
        #         # "-profile:v", "main10",
        #         "-cq", "0",  # Constant quality mode (best)
        #         "-pix_fmt", "yuva420p",
        #         "-auto-alt-ref", "0",   # important for alpha with VP9
        #         "-lossless", "1",
        #         "-y"
        #     ]
        # )

        # surah_clip.write_videofile(
        #     overlay_temp,
        #     fps=30,
        #     codec="libvpx-vp9",
        #     ffmpeg_params=[
        #         "-pix_fmt", "yuva420p",  # alpha pixel format
        #         "-auto-alt-ref", "0",  # prevent VP9 from breaking alpha
        #         "-lossless", "1",  # preserve quality
        #         "-y"
        #     ]
        # )

        surah_clip.write_videofile(
            overlay_temp,
            fps=30,
            codec="png",
            ffmpeg_params=[
                "-y"
            ]
        )


        # surah_clip.write_videofile(
        #     overlay_temp,
        #     fps=30,
        #     codec="hevc_nvenc",
        #     preset="p7",
        #     bitrate="50M",  # Very high bitrate
        #     ffmpeg_params=[
        #         "-tune", "hq",  # Low latency tuning
        #         "-movflags", "+faststart",
        #         "-profile:v", "main10",
        #         "-cq", "0",  # Constant quality mode (best)
        #         "-pix_fmt", "yuva420p",
        #         "-y"
        #     ]
        # )
        surah_clip.close()

        # Step 4: Concatenated background video files
        background_video = loop_backgrounds(total_duration=total_duration, temp_manager=temp_manager)

        # Step 4: Use ffmpeg to composite everything
        # final_command = [
        #     'ffmpeg',
        #     '-i', background_video,      # Background video
        #     '-i', temp_concat_file,     # Main content video
        #     '-i', overlay_temp,         # Overlay video (transparent)
        #     '-filter_complex',
        #     '[0:v]setpts=PTS-STARTPTS[bg];'  # Background
        #     '[1:v]setpts=PTS-STARTPTS[main];'  # Main content
        #     '[2:v]setpts=PTS-STARTPTS,format=yuva420p[overlay];'  # Overlay with alpha
        #     '[bg][main]overlay[bg_main];'  # Overlay main on background
        #     '[bg_main][overlay]overlay[outv]'  # Overlay surah info
        # ]

        # final_command = [
        #     'ffmpeg',
        #     '-i', background_video,      # Background video
        #     '-i', temp_concat_file,     # Main content video
        #     '-i', overlay_temp,         # Overlay video (transparent)
        #     '-filter_complex',
        #     '[0:v]setpts=PTS-STARTPTS[bg];'  # Background
        #     '[1:v]setpts=PTS-STARTPTS,format=yuva420p,colorkey=0x' + CHROMA_KEY_HEX + ':similarity=0.1:blend=0.6[main];'  # Main content
        #     # '[1:v]setpts=PTS-STARTPTS,format=yuva420p[main];'  # Main content
        #     '[2:v]setpts=PTS-STARTPTS,format=yuva420p,colorkey=0x' + CHROMA_KEY_HEX + ':similarity=0.1:blend=0.6[overlay_with_alpha];'  # Overlay with alpha
        #     '[bg][main]overlay=shortest=1[bg_main];'  # Overlay main on background
        #     '[bg_main][overlay_with_alpha]overlay[outv]'  # Overlay surah info
        # ]


        # final_command = [
        #     'ffmpeg',
        #     '-i', background_video,      # Background video
        #     '-i', temp_concat_file,     # Main content video
        #     '-i', overlay_temp,         # Overlay video (transparent)
        #     '-filter_complex',
        #     '[0:v]setpts=PTS-STARTPTS[bg];'  # Background
        #     '[1:v]setpts=PTS-STARTPTS,format=yuva420p,colorkey=0x' + CHROMA_KEY_HEX + ':similarity=0.1:blend=0.6[main];'  # Main content
        #     # '[1:v]setpts=PTS-STARTPTS,format=yuva420p[main];'  # Main content
        #     '[2:v]setpts=PTS-STARTPTS,format=yuva420p,colorkey=0x' + CHROMA_KEY_HEX + ':similarity=0.1:blend=0.6[overlay_with_alpha];'  # Overlay with alpha
        #     '[bg][main]overlay[bg_main];'  # Overlay main on background
        #     '[bg_main][overlay_with_alpha]overlay[outv]'  # Overlay surah info
        # ]


        # final_command = [
        #     'ffmpeg',
        #     '-i', background_video,      # Background video
        #     '-i', temp_concat_file,     # Main content video
        #     # '-i', overlay_temp,         # Overlay video (transparent)
        #     '-filter_complex',
        #     '[0:v]setpts=PTS-STARTPTS[bg];'  # Background
        #     '[1:v]setpts=PTS-STARTPTS[main];'  # Main content
        #     # '[1:v]setpts=PTS-STARTPTS,format=yuva420p[main];'  # Main content
        #     # '[2:v]setpts=PTS-STARTPTS,format=yuva420p[overlay_with_alpha];'  # Overlay with alpha
        #     '[bg][main]overlay:format=yuva420p[bg_main];'  # Overlay main on background
        #     # '[bg_main][overlay_with_alpha]overlay[outv]'  # Overlay surah info
        # ]


        final_command = [
            'ffmpeg',
            '-i', background_video,      # Background video
            '-i', temp_concat_file,     # Main content video
            '-i', overlay_temp,         # Overlay video (transparent)
            '-filter_complex',
            '[0:v]setpts=PTS-STARTPTS[bg];'  # Background
            '[1:v]setpts=PTS-STARTPTS[main];'  # Main content
            '[2:v]setpts=PTS-STARTPTS[overlay_with_alpha];'  # Overlay with alpha
            '[bg][main] overlay=0:0:format=auto[bg_main];'  # Overlay main on background
            '[bg_main][overlay_with_alpha] overlay=0:0:format=auto[outv]'  # Overlay surah info
        ]


        # final_command = [
        #     'ffmpeg',
        #     '-i', background_video,  # Background video
        #     '-i', temp_concat_file,  # Main content video
        #     '-i', overlay_temp,  # Overlay video (transparent)
        #     '-filter_complex',
        #     '[0:v]setpts=PTS-STARTPTS[bg];'  # Background
        #     '[1:v]setpts=PTS-STARTPTS,format=yuva420p[main];'  # Main content
        #     '[2:v]setpts=PTS-STARTPTS,format=yuva420p[overlay_with_alpha];'  # Overlay with alpha
        #     '[bg][main]overlay=shortest=1[bg_main];'  # Overlay main on background
        #     '[bg_main][overlay_with_alpha]overlay[outv]'  # Overlay surah info
        # ]

        # Add audio from the main content
        final_command.extend([
            '-map', '[outv]',  # Use the composed video
            '-map', '1:a?',  # Audio from main content (if exists)
            '-c:v', 'hevc_nvenc',  # Your preferred encoder
            '-c:a', 'aac',
            '-preset', 'p7',
            '-b:v', '50M',
            '-tune', 'hq',
            '-movflags', '+faststart',
            '-profile:v', 'main10',
            '-pix_fmt', 'yuv420p',
            '-y',
            output_path
        ])

        print("🎬 Final compositing with ffmpeg...")
        print(f'FFMPEG Command: {" ".join(final_command)}')
        result = subprocess.run(final_command, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ Final compositing failed: {result.stderr}")


    except Exception as ex:
        print(ex)


def generate_videos(surah_no: int):
    """Main function that writes each verse to file to save memory"""
    temp_manager = TempFileManager(surah_no=surah_no)

    try:
        print(f"Processing Surah {surah_no}...")

        # Load subtitles
        subtitles = json_to_srt(BASE_JSON_PATH.format(surah_no))
        print(f"Loaded {len(subtitles)} verses")

        # Load chapter info
        with open(CHAPTERS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data_en = data["en"][f"{surah_no}"]
        data_ar = data["ar"][f"{surah_no}"]

        surah_info = (
            'سورة' + f' {data_ar["transliteratedName"]}',
            f'Surah {data_en["transliteratedName"]}',
            f'সূরা {constants.BENGALI_NAMES.get(str(surah_no), "")}',
            data_en["translatedName"]
        )

        video_files = []
        total_duration = 0

        # Generate bismillah if needed
        # if surah_no != 1:
        #     bismillah_file, duration = generate_bismillah_to_file(temp_manager)
        #     if bismillah_file:
        #         video_files.append(bismillah_file)
        #         # Estimate duration (you could get actual duration if needed)
        #         total_duration += duration

        # Generate each verse to separate file
        for index, subtitle in enumerate(subtitles):
            print(f"Processing verse {index + 1}/{len(subtitles)}")

            # Load English subtitle
            surah = f"{surah_no:03}"
            subtitle_file = f"quran/quran-english-verse-by-verse-allah/{surah}-{index + 1:03}.txt"
            if os.path.exists(subtitle_file):
                with open(subtitle_file, 'r', encoding='utf-8') as f:
                    subtitle_english = f.readline().strip()
            else:
                subtitle_english = "Translation not available"

            # Generate verse video to file
            verse_file, duration = generate_verse_to_file(
                surah_no, index, subtitle, subtitle_english, temp_manager
            )

            if verse_file:
                video_files.append(verse_file)
                total_duration += duration  # Estimate

            # # Force garbage collection every few verses
            # if index % 10 == 0:
            #     gc.collect()
            break

        print(f"Generated {len(video_files)} video files, concatenating...")

        # Concatenate all temporary files
        output_path = BASE_OUTPUT_VIDEO_PATH.format(surah_no)
        concatenate_video_files(video_files, output_path, surah_info, total_duration, temp_manager=temp_manager)

        print(f"Successfully created: {output_path}")

    except Exception as e:
        print(f"Error processing Surah {surah_no}: {e}")
        raise
    finally:
        # Clean up temporary files
        # temp_manager.cleanup()
        gc.collect()


if __name__ == "__main__":
    generate_videos(108)

    # For multiple surahs:
    # for i in range(61, 66):
    #     generate_videos(i)
    #     gc.collect()
