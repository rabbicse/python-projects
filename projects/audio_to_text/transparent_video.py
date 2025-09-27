from moviepy import *

FONT = "fonts/DejaVuSans.ttf"
# Create a text clip with transparent background
txt_clip = TextClip(
    text="Bismillah",
    font_size=80,
    color="white",
    font=FONT
).with_duration(15)

# Create a black background with opacity 0.2
background = ColorClip(
    size=(1920, 1080),
    color=(0, 0, 0)  # black background
).with_duration(15).with_opacity(0.2)

# Composite on transparent background
final = CompositeVideoClip([background, txt_clip], size=(1920, 1080))

# Export with transparency
final.write_videofile(
    "transparent.mov",
    codec="png",   # keeps alpha channel
    fps=30,
    preset="ultrafast"
)
