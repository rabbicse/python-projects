import spacy
from moviepy import TextClip, CompositeVideoClip, ColorClip
import os

os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"

FONT = "fonts/DejaVuSans.ttf"

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Input paragraph
text = """
The innovative developer built a powerful application using Python and MoviePy.
It automatically highlights important words like nouns and adjectives to make the text more expressive.
This is a dynamic text that will automatically wrap and center itself within the video frame regardless of the resolution used for the final output.
"""


def analyze_text(text: str):
    """Analyze text and return tokens with highlight information"""
    doc = nlp(text)
    highlight_pos = {"NOUN", "ADJ", "PROPN"}
    return doc, highlight_pos


def create_pango_text_clip(text, video_width=1920, video_height=1080):
    """Create a perfectly formatted text clip using Pango markup"""

    # Process text with spaCy
    doc, highlight_pos = analyze_text(text)

    # Build Pango markup with proper formatting
    pango_lines = []
    current_line = []

    for token in doc:
        word = token.text_with_ws

        # Apply highlighting
        if token.pos_ in highlight_pos:
            styled_word = f"<b><span foreground='#FFFF00' size='large'>{word}</span></b>"
        else:
            styled_word = f"<span foreground='white'>{word}</span>"

        current_line.append(styled_word)

        # Check for sentence boundaries or manual line breaks
        if token.is_sent_end or token.text == '\n':
            pango_lines.append(''.join(current_line))
            current_line = []

    # Add any remaining text
    if current_line:
        pango_lines.append(''.join(current_line))

    # Join lines with proper spacing
    pango_text = '\n'.join(pango_lines)

    # Calculate optimal font size based on resolution
    base_font_size = max(28, min(48, video_height // 25))

    # Create the text clip with Pango
    txt_clip = TextClip(
        pango_text.upper(),
        font=FONT,
        font_size=base_font_size,
        method='pango',
        size=(video_width - 100, None),  # Width with small margins
        align='center',
        color='white',
        stroke_color='black',
        stroke_width=1,
        kerning=2,  # Better letter spacing
        line_height=1.4  # Better line spacing
    )

    return txt_clip


def create_video_with_pango(text, width=1920, height=1080, duration=10):
    """Create complete video with Pango-rendered text"""

    # Create text clip
    txt_clip = create_pango_text_clip(text, width, height)

    # Create background (dark gradient-like color)
    bg = ColorClip(size=(width, height), color=(30, 30, 45), duration=duration)

    # Center the text clip
    txt_clip = txt_clip.with_position('center').with_duration(duration)

    # Combine clips
    final = CompositeVideoClip([bg, txt_clip])
    return final


def create_video_with_advanced_styling(text, width=1920, height=1080, duration=10):
    """Advanced version with better styling and effects"""

    doc, highlight_pos = analyze_text(text)

    # Build advanced Pango markup
    pango_text = ""
    for token in doc:
        word = token.text_with_ws

        if token.pos_ in highlight_pos:
            # Enhanced highlighting with shadow effect
            pango_text += f"<b><span foreground='#FFD700' size='large' weight='heavy'>{word}</span></b>"
        elif token.pos_ == "VERB":
            # Optional: Different color for verbs
            pango_text += f"<span foreground='#87CEEB'>{word}</span>"
        else:
            pango_text += f"<span foreground='#FFFFFF'>{word}</span>"

    # Calculate dynamic font size
    base_font_size = max(32, min(56, height // 20))

    # Create advanced text clip
    txt_clip = TextClip(
        text=pango_text.upper(),
        font=FONT,
        font_size=base_font_size,
        method='caption',
        size=(width - 80, None),  # Smaller margins for more text area
        text_align='center',
        color='white',
        stroke_color='black',
        stroke_width=2,
    )

    # Create gradient background
    bg = ColorClip(size=(width, height), color=(20, 25, 35), duration=duration)

    # Position text perfectly centered
    txt_clip = txt_clip.with_position('center').with_duration(duration)

    return CompositeVideoClip([bg, txt_clip])


# Demo with different resolutions
def demo_multiple_resolutions():
    """Demo the Pango text rendering with different video sizes"""

    resolutions = [
        (1920, 1080, "Full HD"),
        (1280, 720, "HD"),
        (3840, 2160, "4K"),
        (1080, 1920, "Vertical"),
        (2560, 1440, "2K"),
    ]

    for width, height, name in resolutions:
        print(f"Creating {name} ({width}x{height})...")

        # Create video
        video = create_video_with_pango(text, width, height)

        # Preview the first one (Full HD)
        if name == "Full HD":
            video.preview()

        # Export if needed
        # filename = f"pango_text_{width}x{height}.mp4"
        # video.write_videofile(filename, fps=24, verbose=False, logger=None)


# Quick test function
def quick_preview():
    """Quick preview of the Pango text rendering"""
    print("Creating Pango-styled text video...")

    # Use advanced styling
    final_video = create_video_with_advanced_styling(
        text,
        width=1920,
        height=1080,
        duration=8
    )

    print("Previewing... (Close the preview window to continue)")
    final_video.preview()

    return final_video


# Alternative: Simple one-liner for quick use
def create_text_video(text_content, width=1920, height=1080):
    """Simple one-liner function to create text videos"""
    return create_video_with_pango(text_content, width, height)


if __name__ == "__main__":
    # Quick preview
    video = quick_preview()

    # Uncomment to export
    # video.write_videofile("pango_text_video.mp4", fps=24)

    # Uncomment to test multiple resolutions
    # demo_multiple_resolutions()