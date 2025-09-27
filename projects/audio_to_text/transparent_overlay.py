from moviepy import VideoFileClip, CompositeVideoClip

# Load background video
background = VideoFileClip("data/backgrounds/001.mp4")

# Load the transparent video we created
overlay = VideoFileClip("transparent.mov", has_mask=True)

# Resize / position overlay if needed
overlay = overlay.with_position(("center", "center"))

# Composite them together
final = CompositeVideoClip([background, overlay])

# Export final video
final.write_videofile(
    "final_output.mp4",
    codec="libx264",
    fps=30
)
