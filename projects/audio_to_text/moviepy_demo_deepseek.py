import arabic_reshaper
from bidi.algorithm import get_display
from moviepy import *

import numpy as np

# Font paths - make sure these exist on your system
FONT = "fonts/DejaVuSans.ttf"  # Using bold font for better appearance
FONT_ARABIC = "fonts/Amiri-Regular.ttf"  # Using bold Arabic font


def create_animated_text(text="Hello World!", text_arabic="بسم الله الرحمن الرحيم", duration=5, fps=30):
    # Create a gradient background for more visual interest
    # We'll create this with a gradient from dark blue to black
    def make_gradient_background(duration):
        # Create a gradient using a simple linear gradient function
        def gradient(t):
            progress = t / duration
            color_top = np.array([10, 20, 60])  # Dark blue
            color_bottom = np.array([0, 0, 0])  # Black
            color = color_top * (1 - progress) + color_bottom * progress
            return color.astype(int)

        # Create a clip with the gradient
        gradient_clip = ColorClip(size=(1920, 1080), color=gradient(0))
        gradient_clip = gradient_clip.with_duration(duration)

        # Animate the gradient
        def update_background(get_frame, t):
            frame = get_frame(t)
            color = gradient(t)
            frame[:, :] = color
            return frame

        return gradient_clip.with_make_frame(lambda t: update_background(gradient_clip.get_frame, t))

    background = make_gradient_background(duration)

    # Create the main English text clip with stroke
    text_clip = TextClip(
        font=FONT, text=text, color="white", font_size=80,
        stroke_color="#FFD700", stroke_width=2  # Gold stroke
    )
    text_clip = text_clip.with_duration(duration)

    # Create a glow effect for the English text
    glow_clip = TextClip(
        font=FONT, text=text, color="#FFD700", font_size=80,  # Gold color for glow
    )
    glow_clip = glow_clip.with_duration(duration)
    glow_clip = glow_clip.with_effects([vfx.Blur(radius=10)])  # Blur for glow effect

    # Create a shadow for the English text
    shadow_clip = TextClip(
        font=FONT, text=text, color=(30, 30, 30), font_size=80,  # Dark gray shadow
    )
    shadow_clip = shadow_clip.with_duration(duration)
    shadow_clip = shadow_clip.with_effects([vfx.Blur(radius=5)])  # Slight blur for soft shadow

    # Define the movement function for floating animation
    def move_text(t):
        # Start position (center of screen)
        start_x = 1920 / 2 - text_clip.w / 2
        start_y = 1080 / 2 - text_clip.h / 2

        # Add floating movement using sine waves for both x and y
        x_offset = np.sin(t * 1.5 * np.pi) * 15  # Slower horizontal movement
        y_offset = np.sin(t * 2 * np.pi) * 25  # Faster vertical movement

        return (start_x + x_offset, start_y + y_offset)

    # Apply movement to all English text elements
    text_clip = text_clip.with_position(move_text)
    glow_clip = glow_clip.with_position(move_text)
    shadow_clip = shadow_clip.with_position(lambda t: (move_text(t)[0] + 5, move_text(t)[1] + 5))

    # Process Arabic text for proper rendering
    configuration = {
        'delete_harakat': False,
        'support_ligatures': True,
        'RIAL SIGN': True,
    }
    reshaper = arabic_reshaper.ArabicReshaper(configuration=configuration)
    reshaped_text = reshaper.reshape(text_arabic)
    arabic_display_text = get_display(reshaped_text)

    # Create the main Arabic text clip with stroke
    text_clip_arabic = TextClip(
        font=FONT_ARABIC, text=arabic_display_text, color="white", font_size=80,
        stroke_color="#FFD700", stroke_width=2  # Gold stroke
    )
    text_clip_arabic = text_clip_arabic.with_duration(duration)

    # Create a glow effect for the Arabic text
    glow_clip_arabic = TextClip(
        font=FONT_ARABIC, text=arabic_display_text, color="#FFD700", font_size=80,
    )
    glow_clip_arabic = glow_clip_arabic.with_duration(duration)
    glow_clip_arabic = glow_clip_arabic.with_effects([vfx.Blur(radius=10)])

    # Create a shadow for the Arabic text
    shadow_clip_arabic = TextClip(
        font=FONT_ARABIC, text=arabic_display_text, color=(30, 30, 30), font_size=80,
    )
    shadow_clip_arabic = shadow_clip_arabic.with_duration(duration)
    shadow_clip_arabic = shadow_clip_arabic.with_effects([vfx.Blur(radius=5)])

    # Position Arabic text elements at the top of the screen
    arabic_x = 1920 / 2 - text_clip_arabic.w / 2
    arabic_y = 80

    # Add subtle movement to Arabic text
    def move_arabic_text(t):
        y_offset = np.sin(t * 1.8 * np.pi) * 10  # Subtle vertical movement
        return (arabic_x, arabic_y + y_offset)

    text_clip_arabic = text_clip_arabic.with_position(move_arabic_text)
    glow_clip_arabic = glow_clip_arabic.with_position(move_arabic_text)
    shadow_clip_arabic = shadow_clip_arabic.with_position(
        lambda t: (move_arabic_text(t)[0] + 5, move_arabic_text(t)[1] + 5)
    )

    # Apply fade effects to Arabic text
    text_clip_arabic = text_clip_arabic.with_effects([vfx.CrossFadeIn(1.5), vfx.CrossFadeOut(1.5)])
    glow_clip_arabic = glow_clip_arabic.with_effects([vfx.CrossFadeIn(1.5), vfx.CrossFadeOut(1.5)])

    # Add a subtle pulsing effect to the English text
    def pulse_effect(get_frame, t):
        frame = get_frame(t)
        # Calculate pulse intensity (varies between 0.9 and 1.1)
        pulse = 0.95 + 0.05 * np.sin(t * 3 * np.pi)
        # Apply pulse to the frame
        frame = frame * pulse
        # Ensure values stay within valid range
        frame = np.clip(frame, 0, 255)
        return frame.astype('uint8')

    text_clip = text_clip.with_make_frame(lambda t: pulse_effect(text_clip.get_frame, t))
    glow_clip = glow_clip.with_make_frame(lambda t: pulse_effect(glow_clip.get_frame, t))

    # Combine all elements (order matters - render from back to front)
    final_clip = CompositeVideoClip([
        background,
        # English text elements (shadow -> glow -> main text)
        shadow_clip, glow_clip, text_clip,
        # Arabic text elements (shadow -> glow -> main text)
        shadow_clip_arabic, glow_clip_arabic, text_clip_arabic
    ])

    return final_clip


def main():
    # Create the animation
    video = create_animated_text(
        text="Welcome to Python Animation!",
        text_arabic="بسم الله الرحمن الرحيم",
        duration=5,
        fps=30
    )

    # Preview the video
    video.preview()

    # Write the video file
    video.write_videofile(
        "animated_text.mp4",
        fps=30,
        codec="libx264",
        audio=False,
        threads=4,  # Use multiple threads for faster rendering
        preset='medium',  # Balance between speed and quality
        ffmpeg_params=['-crf', '18']  # High quality
    )


if __name__ == "__main__":
    main()