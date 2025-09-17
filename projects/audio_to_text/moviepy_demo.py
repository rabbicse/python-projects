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
    # text = text[::-1]  # Reverse for proper RTL display
    text_clip_arabic = TextClip(
        font=FONT_ARABIC, text=arabic_display_text, color="white", font_size=85, text_align="center",
        stroke_color="#000000", stroke_width=2  # Gold stroke
    )

    # Set the clip duration
    text_clip_arabic = text_clip_arabic.with_duration(duration)

    # Apply the movement
    text_clip_arabic = text_clip_arabic.with_position((1920 / 2 - text_clip_arabic.w / 2, 120))

    # Apply effects
    text_clip_arabic = text_clip_arabic.with_effects([vfx.CrossFadeIn(1.5), vfx.CrossFadeOut(1.5)])

    # English Caption
    # Create the text clip without a font parameter
    text_clip = TextClip(
        font=FONT, text=text, color="white", font_size=70, size=(1800, None), method='caption',  # Enable word wrapping
        text_align="center",
        stroke_color="#FFD700", stroke_width=2,  # Gold stroke
        interline=30
    )

    # Set the clip duration
    text_clip = text_clip.with_duration(duration)

    # Apply the movement
    text_clip = text_clip.with_position((1920 / 2 - text_clip.w / 2, 1080 - text_clip.h))

    # Combine background and text
    final_clip = CompositeVideoClip([background, text_clip, text_clip_arabic])

    return final_clip


def main():
    heading = "Welcome to Python Animation! Welcome to Python Animation! Welcome to Python Animation!"
    # Create the animation
    video = create_animated_text(
        text=heading, duration=5, fps=30
    )

    video.preview()

    # Write the video file
    # video.write_videofile("animated_text.mp4", fps=30, codec="libx264", audio=False)


if __name__ == "__main__":
    main()
