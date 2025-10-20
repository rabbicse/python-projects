# import spacy
# from moviepy import TextClip, CompositeVideoClip, ColorClip
#
# FONT = "fonts/DejaVuSans.ttf"
#
# # Load spaCy model
# nlp = spacy.load("en_core_web_sm")
#
# # Input paragraph
# text = """
# The innovative developer built a powerful application using Python and MoviePy.
# It automatically highlights important words like nouns and adjectives to make the text more expressive.
# This is a dynamic text that will automatically wrap and center itself within the video frame regardless of the resolution used for the final output.
# """
#
# # Video dimensions
# VIDEO_WIDTH = 1920
# VIDEO_HEIGHT = 1080
#
#
# def analyze_text(text: str):
#     doc = nlp(text)
#     highlight_pos = {"NOUN", "ADJ", "PROPN"}
#     return doc, highlight_pos
#
#
# def create_centered_paragraph(doc, highlight_pos, video_width=VIDEO_WIDTH, video_height=VIDEO_HEIGHT):
#     # Create individual word clips
#     word_clips = []
#
#     for token in doc:
#         word = token.text + " "  # Add space after each word
#
#         if token.pos_ in highlight_pos:
#             word_clip = TextClip(
#                 text=word.upper(),
#                 font=FONT,
#                 font_size=36,  # Slightly larger for 1080p
#                 color='yellow',
#                 stroke_color='yellow',
#                 stroke_width=1,
#                 method='label'
#             )
#         else:
#             word_clip = TextClip(
#                 text=word.upper(),
#                 font=FONT,
#                 font_size=36,
#                 color='white',
#                 method='label'
#             )
#
#         word_clips.append(word_clip)
#
#     # Calculate total width of all words
#     total_width = sum(clip.w for clip in word_clips)
#
#     # Center the entire paragraph horizontally
#     start_x = (video_width - total_width) // 2
#     y_pos = video_height // 2  # Center vertically
#
#     # Position all clips
#     positioned_clips = []
#     current_x = start_x
#
#     for clip in word_clips:
#         positioned_clip = clip.with_position((current_x, y_pos)).with_duration(8)
#         positioned_clips.append(positioned_clip)
#         current_x += clip.w
#
#     return positioned_clips
#
#
# def create_centered_paragraph_with_wrapping(doc, highlight_pos, video_width=VIDEO_WIDTH, video_height=VIDEO_HEIGHT):
#     lines = []
#     current_line = []
#     current_line_width = 0
#
#     # Calculate maximum width for text (90% of video width for margins)
#     max_line_width = int(video_width * 0.9)
#     font_size = 36 if video_height >= 1080 else 24
#     line_height = 60 if video_height >= 1080 else 50
#
#     # Group words into lines based on max_line_width
#     for token in doc:
#         word = token.text + " "
#
#         # Create temporary clip to measure width
#         if token.pos_ in highlight_pos:
#             temp_clip = TextClip(
#                 text=word.upper(),
#                 font=FONT,
#                 font_size=font_size,
#                 color='yellow',
#                 stroke_color='yellow',
#                 stroke_width=1,
#                 method='label'
#             )
#         else:
#             temp_clip = TextClip(
#                 text=word.upper(),
#                 font=FONT,
#                 font_size=font_size,
#                 color='white',
#                 method='label'
#             )
#
#         word_width = temp_clip.w
#
#         # If adding this word would exceed max width, start a new line
#         if current_line_width + word_width > max_line_width and current_line:
#             lines.append(current_line)
#             current_line = [(token, word)]
#             current_line_width = word_width
#         else:
#             current_line.append((token, word))
#             current_line_width += word_width
#
#     # Add the last line
#     if current_line:
#         lines.append(current_line)
#
#     # Create and position clips for each line
#     all_clips = []
#     total_text_height = len(lines) * line_height
#     start_y = (video_height - total_text_height) // 2
#
#     for i, line in enumerate(lines):
#         line_clips = []
#         line_total_width = 0
#
#         # Create clips for each word in the line
#         for token, word in line:
#             if token.pos_ in highlight_pos:
#                 word_clip = TextClip(
#                     text=word.upper(),
#                     font=FONT,
#                     font_size=font_size,
#                     color='yellow',
#                     stroke_color='yellow',
#                     stroke_width=1,
#                     method='label'
#                 )
#             else:
#                 word_clip = TextClip(
#                     text=word.upper(),
#                     font=FONT,
#                     font_size=font_size,
#                     color='white',
#                     method='label'
#                 )
#
#             line_clips.append(word_clip)
#             line_total_width += word_clip.w
#
#         # Center the line horizontally
#         start_x = (video_width - line_total_width) // 2
#         current_x = start_x
#         y_pos = start_y + (i * line_height)
#
#         # Position each word in the line
#         for clip in line_clips:
#             positioned_clip = clip.with_position((current_x, y_pos)).with_duration(8)
#             all_clips.append(positioned_clip)
#             current_x += clip.w
#
#     return all_clips
#
#
# def create_video_with_dynamic_resolution(text, width=1920, height=1080):
#     """Main function to create video with any resolution"""
#     # Update global dimensions
#     global VIDEO_WIDTH, VIDEO_HEIGHT
#     VIDEO_WIDTH = width
#     VIDEO_HEIGHT = height
#
#     # Process text
#     doc, highlight_pos = analyze_text(text)
#
#     # Choose method based on text length and video width
#     total_chars = len(text)
#
#     if total_chars < 100:  # Short text - single line
#         text_clips = create_centered_paragraph(doc, highlight_pos, width, height)
#     else:  # Longer text - multi-line with wrapping
#         text_clips = create_centered_paragraph_with_wrapping(doc, highlight_pos, width, height)
#
#     # Create background
#     bg = ColorClip(size=(width, height), color=(75, 75, 75), duration=8)
#
#     # Combine all clips
#     final = CompositeVideoClip([bg] + text_clips)
#     return final
#
#
# # Example usage with different resolutions
# resolutions = [
#     (1920, 1080),  # Full HD
#     (1280, 720),  # HD
#     (3840, 2160),  # 4K
#     (1080, 1920),  # Vertical (for social media)
# ]
#
# # Create video for each resolution
# for width, height in resolutions:
#     print(f"Creating video with resolution: {width}x{height}")
#
#     final_video = create_video_with_dynamic_resolution(text, width, height)
#
#     # Preview (uncomment to preview)
#     # final_video.preview()
#
#     # Export (uncomment to save)
#     filename = f"highlighted_paragraph_{width}x{height}.mp4"
#     # final_video.write_videofile(filename, fps=24)
#
# # Create default 1920x1080 video for preview
# final_1080p = create_video_with_dynamic_resolution(text, 1920, 1080)
# final_1080p.preview()
#
# # Optional: Export the 1080p version
# # final_1080p.write_videofile("highlighted_paragraph_1080p.mp4", fps=24)


import spacy
from moviepy import TextClip, CompositeVideoClip, ColorClip

FONT = "fonts/DejaVuSans.ttf"
FONT_REGULAR = "fonts/merriweather.regular.ttf"
FONT_BOLD = "fonts/merriweather.bold.ttf"
FONT_ULTRA_BOLD = "fonts/merriweather.ultrabold.ttf"

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Input paragraph
# text = """
# The innovative developer built a powerful application using Python and MoviePy.
# It automatically highlights important words like nouns and adjectives to make the text more expressive.
# This is a dynamic text that will automatically wrap and center itself within the video frame regardless of the resolution used for the final output.
# """


text = """
The innovative developer built a powerful application using Python and MoviePy. It automatically highlights important
"""


def analyze_text(text: str):
    """Analyze text and return tokens with highlight information"""
    doc = nlp(text)
    highlight_pos = {"NOUN", "ADJ", "PROPN"}
    return doc, highlight_pos


def create_individual_words_video(text, width=1920, height=1080, duration=10):
    """Create video with individual word clips for precise highlighting"""
    doc, highlight_pos = analyze_text(text)

    # Create individual word clips
    text_clips = []
    x_pos, y_pos = 0, height // 3
    max_line_width = width - 200

    for token in doc:
        word = token.text_with_ws

        # Create word clip with appropriate styling
        if token.pos_ in highlight_pos:
            word_clip = TextClip(
                text=word.upper(),
                font=FONT_ULTRA_BOLD,
                font_size=36,
                color='yellow',
                method='label',
                text_align="center",
                stroke_color="#030303",
                stroke_width=2,  # Gold stroke
                interline=20,
                margin=(10, 20, 10, 20)  # left, top, right, bottom
            )
        else:
            word_clip = TextClip(
                text=word.upper(),
                font_size=36,
                color='white',
                method='label',
                text_align="center",
                stroke_color="#030303",
                stroke_width=2,  # Gold stroke
                interline=20,
                margin=(10, 20, 10, 20)  # left, top, right, bottom
            )

        # Check if we need to wrap to next line
        if x_pos + word_clip.w > max_line_width:
            x_pos = 0
            y_pos += word_clip.h

        # Position the word clip
        positioned_clip = word_clip.with_position((x_pos, y_pos)).with_duration(duration)
        text_clips.append(positioned_clip)

        # Move x position for next word
        x_pos += word_clip.w

    # Create background
    # bg = ColorClip(size=(width, height), color=(30, 30, 45), duration=duration)

    # Combine all clips
    final = CompositeVideoClip(text_clips)
    return final


def create_caption_method_video(text, width=1920, height=1080, duration=10):
    """Create video using caption method for automatic text wrapping"""
    doc, highlight_pos = analyze_text(text)

    # Build the text with simple formatting indicators
    formatted_text = ""
    for token in doc:
        word = token.text
        if token.pos_ in highlight_pos:
            # Using asterisks to indicate highlighted words
            formatted_text += f"*{word.upper()}* "
        else:
            formatted_text += f"{word.upper()} "

    # Create text clip with caption method
    txt_clip = TextClip(
        formatted_text,
        font_size=38,
        color='white',
        method='caption',
        size=(width - 100, None),  # Width for text wrapping
        stroke_color='black',
        stroke_width=1
    )

    # Create background
    bg = ColorClip(size=(width, height), color=(30, 30, 45), duration=duration)

    # Center the text
    txt_clip = txt_clip.with_position('center').with_duration(duration)

    # Combine clips
    final = CompositeVideoClip([bg, txt_clip])
    return final


def create_label_method_video(text, width=1920, height=1080, duration=10):
    """Create video using label method with manual line breaks"""
    doc, highlight_pos = analyze_text(text)

    # Build text with manual line breaks
    lines = []
    current_line = []
    current_line_length = 0
    max_chars_per_line = 60

    for token in doc:
        word = token.text
        word_length = len(word)

        # Check if adding this word would exceed line length
        if current_line_length + word_length > max_chars_per_line and current_line:
            lines.append(" ".join(current_line))
            current_line = [word.upper()]
            current_line_length = word_length
        else:
            current_line.append(word.upper())
            current_line_length += word_length + 1  # +1 for space

    # Add the last line
    if current_line:
        lines.append(" ".join(current_line))

    # Join lines with newline characters
    final_text = "\n".join(lines)

    # Create text clip
    txt_clip = TextClip(
        final_text,
        font_size=36,
        color='white',
        method='label',
        stroke_color='black',
        stroke_width=1
    )

    # Create background
    bg = ColorClip(size=(width, height), color=(30, 30, 45), duration=duration)

    # Center the text
    txt_clip = txt_clip.with_position('center').with_duration(duration)

    # Combine clips
    final = CompositeVideoClip([bg, txt_clip])
    return final


def create_centered_individual_words(text, width=1920, height=1080, duration=10):
    """Create centered individual words with better positioning"""
    doc, highlight_pos = analyze_text(text)

    # Group words into lines first
    lines = []
    current_line = []
    current_line_width = 0
    max_line_width = width - 200

    # First pass: group words into lines
    for token in doc:
        word = token.text_with_ws

        # Create temp clip to measure width
        temp_clip = TextClip(
            text=word.upper(),
            font_size=36,
            color='white',
            method='label',
            font=FONT_BOLD,
            text_align="center",
            stroke_color="#030303",
            stroke_width=2,  # Gold stroke
            interline=20,
            margin=(0, 20, 0, 20)  # left, top, right, bottom
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
    start_y = (height - total_text_height) // 2

    for line_num, line in enumerate(lines):
        line_clips = []
        line_total_width = 0

        # Create clips for each word in the line
        for token, word in line:
            if token.pos_ in highlight_pos:
                word_clip = TextClip(
                    text=word.upper(),
                    font_size=36,
                    color='green',
                    stroke_color='#030303',
                    stroke_width=2,
                    method='label',
                    font=FONT_BOLD,
                    text_align="center",
                    interline=20,
                    margin=(0, 20, 0, 20)  # left, top, right, bottom
                )
            else:
                word_clip = TextClip(
                    text=word.upper(),
                    font_size=36,
                    color='white',
                    method='label',
                    font=FONT_REGULAR,
                    text_align="center",
                    stroke_color="#030303",
                    stroke_width=2,  # Gold stroke
                    interline=20,
                    margin=(0, 20, 0, 20)  # left, top, right, bottom
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

    # Create background
    # bg = ColorClip(size=(width, height), color=(0, 0, 0, 0), duration=duration)

    # Combine all clips
    final = CompositeVideoClip(text_clips, size = (width, height), bg_color=None)
    return final


# Demo function to test all methods
def demo_all_methods():
    """Demo all available text rendering methods"""
    methods = [
        # ("Individual Words", create_individual_words_video),
        ("Caption Method", create_caption_method_video),
        ("Label Method", create_label_method_video),
        ("Centered Individual Words", create_centered_individual_words),
    ]

    for method_name, method_func in methods:
        print(f"Creating video using {method_name}...")
        try:
            video = method_func(text, 1920, 1080, 8)
            print(f"✓ {method_name} successful! Previewing...")
            video.preview()
            video.close()
        except Exception as e:
            print(f"✗ {method_name} failed: {e}")


# Quick preview with best method
def quick_preview():
    """Quick preview with the recommended method"""
    print("Creating text video with centered individual words...")

    # Recommended method: centered individual words
    final_video = create_centered_individual_words(
        text,
        width=1920,
        height=1080,
        duration=8
    )

    print("Previewing... (Close the preview window to continue)")
    final_video.preview()

    return final_video


# Simple one-liner for common use
def create_text_video(text_content, width=1920, height=1080, method="centered"):
    """Simple function to create text videos with chosen method"""
    methods = {
        "individual": create_individual_words_video,
        "caption": create_caption_method_video,
        "label": create_label_method_video,
        "centered": create_centered_individual_words,
    }

    method_func = methods.get(method, create_centered_individual_words)
    return method_func(text_content, width, height)


if __name__ == "__main__":
    print("Text Video Generator")
    print("=" * 50)
    print("Available methods:")
    print("1. centered - Centered individual words (recommended)")
    print("2. individual - Individual words with highlighting")
    print("3. caption - Automatic text wrapping")
    print("4. label - Manual line breaks")
    print()

    # Use the recommended method
    video = quick_preview()

    # Uncomment to export
    # video.write_videofile("text_video.mp4", fps=24)

    # Uncomment to test all methods
    # demo_all_methods()

    # Uncomment to create vertical video for social media
    # vertical_video = create_text_video(text, 1080, 1920, "centered")
    # vertical_video.preview()