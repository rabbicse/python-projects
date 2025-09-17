import arabic_reshaper
from bidi.algorithm import get_display
from moviepy import *

import numpy as np
from networkx.algorithms.distance_measures import radius

# get path to default font of the system. Make sure to change it
FONT = "fonts/DejaVuSans.ttf"
FONT_ARABIC = "fonts/Amiri-Regular.ttf"


def create_animated_text(text="Hello World!", text_arabic="بسم الله الرحمن الرحيم", duration=5, fps=30):
    # Create a background
    background = ColorClip(size=(1920, 1080), color=(0, 0, 0))
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
        font_size=70,
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
        font_size=50,
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


def overlay_on_background(text_en: str, text_arabic: str):
    # Load your background video
    background_video = VideoFileClip("data/backgrounds/001.mp4")

    # Load your background audio
    # background_audio = AudioFileClip("background_music.mp3")

    # Create your text animation
    text_animation = create_animated_text(
        text=text_en,
        text_arabic=text_arabic,
        duration=10,  # Match your background video duration
        fps=30
    )

    # # Resize text animation if needed to match background dimensions
    # if text_animation.size != background_video.size:
    #     text_animation = text_animation.resize(background_video.size)

    # Set the position for overlay (center in this case)
    text_animation = text_animation.with_position(("center", "center"))

    # Overlay the text animation on the background video
    final_video = CompositeVideoClip([background_video, text_animation])

    # Mix audio - adjust volumes as needed
    # background_audio = background_audio.volumex(0.7)  # Reduce background music volume
    # You can add voiceover or other audio here if needed

    # Set the mixed audio to the final video
    # final_video = final_video.with_audio(background_audio)

    # Ensure the video duration matches the audio
    # final_video = final_video.with_duration(background_audio.duration)
    final_video = final_video.with_duration(25)

    return final_video


def main():
    subtitle_en = "Welcome to Python Animation! Welcome to Python Animation! Welcome to Python Animation!"
    subtitle_ar = "بسم الله الرحمن الرحيم"
    # # Create the animation
    # video = create_animated_text(
    #     text=heading, duration=5, fps=30
    # )
    #
    # video.preview()

    # Write the video file
    # video.write_videofile("animated_text.mp4", fps=30, codec="libx264", audio=False)

    # Create the final video with overlay
    final_video = overlay_on_background(text_en=subtitle_en, text_arabic=subtitle_ar)

    # Preview
    final_video.preview()


if __name__ == "__main__":
    main()
