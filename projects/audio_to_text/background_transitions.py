import glob
import os
os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"
from moviepy import *


def generate_processed_backgrounds():
    """Create background video loop from background files using ffmpeg for concatenation"""
    print("🎨 Generating background video...")

    # Get all background videos
    background_files = sorted(glob.glob("data/backgrounds/*.mp4"))

    if not background_files:
        raise

    for bg_video_file in background_files:
        try:
            bg_video_clip = VideoFileClip(bg_video_file)
            bg_video_clip = bg_video_clip.with_effects([vfx.CrossFadeIn(2.0), vfx.CrossFadeOut(2.0)])

            temp_file = f"data/processed-backgrounds/{bg_video_file.split('/')[-1]}"

            print(f"Writing file to: {temp_file}...")

            bg_video_clip.write_videofile(
                temp_file,
                fps=30,
                codec="hevc_nvenc",
                audio=False,
                preset="p7",
                bitrate="50M",
                ffmpeg_params=[
                    "-tune", "hq",
                    "-movflags", "+faststart",
                    "-profile:v", "main10",
                    "-cq", "0",           # fix here
                    "-pix_fmt", "yuv420p",
                    "-y"
                ]
            )

            bg_video_clip.close()

        except Exception as e:
            print(f"⚠️ Error loading background {bg_video_file}: {e}")

generate_processed_backgrounds()