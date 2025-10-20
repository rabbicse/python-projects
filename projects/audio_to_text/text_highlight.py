# # Set ImageMagick binary path (if needed)
# import os
# os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"
#
# import spacy
# from moviepy import TextClip, CompositeVideoClip, ColorClip
#
#
# # Load spaCy model
# nlp = spacy.load("en_core_web_sm")
#
# # Input paragraph
# text = """
# The innovative developer built a powerful application using Python and MoviePy.
# It automatically highlights important words like nouns and adjectives to make the text more expressive.
# """
#
# # Run NLP analysis
# doc = nlp(text)
#
# # Define which POS to highlight
# highlight_pos = {"NOUN", "ADJ", "PROPN"}
#
# # Build styled text with HTML-like markup
# styled_lines = []
# for token in doc:
#     word = token.text
#     if token.pos_ in highlight_pos:
#         # styled_lines.append(f"<b><font color='yellow'>{word}</font></b>")
#         # ImageMagick uses different markup syntax
#         styled_lines.append(f"<span foreground='yellow' weight='bold'>{word}</span>")
#     else:
#         styled_lines.append(word)
#
# # Join tokens and preserve punctuation spacing
# styled_text = " ".join(styled_lines)
#
# # Create wrapped caption-style text clip (supports multiline)
# txt_clip = TextClip(
#     styled_text,
#     font_size=48,
#     color="white",
#     method="label",  # automatically wraps long text
#     text_align="center",
#     size=(1280, 720),  # target resolution for wrapping
# )
#
# # Add black background
# bg = ColorClip(size=txt_clip.size, color=(0, 0, 0), duration=8)
#
# # Combine text and background
# final = CompositeVideoClip([bg, txt_clip.set_position("center")])
#
# final.preview()
#
# # Export final video
# # final.write_videofile("highlighted_paragraph.mp4", fps=24)


import spacy
from moviepy import TextClip, CompositeVideoClip, ColorClip

FONT = "fonts/DejaVuSans.ttf"

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Input paragraph
text = """
The innovative developer built a powerful application using Python and MoviePy.
It automatically highlights important words like nouns and adjectives to make the text more expressive.
"""


def analyze_text(text: str):
    # Run NLP analysis
    doc = nlp(text)

    # Define which POS to highlight
    highlight_pos = {"NOUN", "ADJ", "PROPN"}

    return doc, highlight_pos


# Create individual text clips for highlighted and normal words
text_clips = []
x_pos, y_pos = 100, 200
line_height = 60
max_width = 1080

doc, highlight_pos = analyze_text(text)

for token in doc:
    word = token.text + " "  # Add space after each word

    if token.pos_ in highlight_pos:
        word_clip = TextClip(text=word.upper(),
                             font=FONT,
                             font_size=24,
                             color='yellow',
                             stroke_color='yellow',
                             stroke_width=1,
                             margin=(5, 10, 5, 10))
    else:
        word_clip = TextClip(text=word.upper(),
                             font=FONT,
                             font_size=24,
                             color='white',
                             margin=(5, 10, 5, 10))

    # Check if we need to wrap to next line
    if x_pos + word_clip.w > max_width:
        x_pos = 100
        y_pos += line_height

    word_clip = word_clip.with_position((x_pos, y_pos)).with_duration(8)
    text_clips.append(word_clip)

    x_pos += word_clip.w

# Create background
bg = ColorClip(size=(1280, 720), color=(75, 75, 75), duration=8)

# Combine all clips
final = CompositeVideoClip([bg] + text_clips)
final.preview()
# final.write_videofile("highlighted_paragraph.mp4", fps=24)
