import spacy
from moviepy.editor import TextClip, CompositeVideoClip, ColorClip

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Input paragraph
text = """
The innovative developer built a powerful application using Python and MoviePy.
It automatically highlights important words like nouns and adjectives to make the text more expressive.
"""

# Run NLP analysis
doc = nlp(text)

# Define which POS to highlight
highlight_pos = {"NOUN", "ADJ", "PROPN"}

# Build styled text with HTML-like markup
styled_lines = []
for token in doc:
    word = token.text
    if token.pos_ in highlight_pos:
        styled_lines.append(f"<b><font color='yellow'>{word}</font></b>")
    else:
        styled_lines.append(word)

# Join tokens and preserve punctuation spacing
styled_text = " ".join(styled_lines)

# Create wrapped caption-style text clip (supports multiline)
txt_clip = TextClip(
    styled_text,
    fontsize=48,
    color="white",
    method="caption",  # automatically wraps long text
    align="center",
    size=(1280, 720),  # target resolution for wrapping
    font="Arial",
)

# Add black background
bg = ColorClip(size=txt_clip.size, color=(0, 0, 0), duration=8)

# Combine text and background
final = CompositeVideoClip([bg, txt_clip.set_position("center")])

# Export final video
final.write_videofile("highlighted_paragraph.mp4", fps=24)
