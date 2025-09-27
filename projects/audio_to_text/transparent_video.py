from moviepy import TextClip, CompositeVideoClip

FONT = "fonts/DejaVuSans.ttf"
# Create a text clip with transparent background
txt_clip = TextClip(
    text="Bismillah",
    font_size=80,
    color="white",
    font=FONT
).with_duration(15)

# Convert to RGBA (adds alpha channel)
# txt_clip = txt_clip.with_opacity(1).with_mask()

# Composite on transparent background
final = CompositeVideoClip([txt_clip], size=(1920, 1080), bg_color=None)

# Export with transparency
final.write_videofile(
    "transparent.mov",
    codec="png",   # keeps alpha channel
    fps=30,
    preset="ultrafast"
)
