import cv2
import pysrt
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# CONFIGURATION ==============================================
INPUT_VIDEO = "data/001.mp4"
INPUT_SRT = "data/001_subtitles.srt"
OUTPUT_VIDEO = "polished_subtitles.mp4"

# Professional Style Configuration
STYLES = {
    "en": {
        "color": (255, 255, 255),  # Pure white
        "font": cv2.FONT_HERSHEY_SIMPLEX,
        "scale": 1.1,
        "thickness": 2,
        "bg_color": (20, 20, 20, 0.85),  # Dark gray with 85% opacity
        "border_color": (0, 150, 255, 0.3),  # Blue accent border
        "animation_speed": 0.05  # Characters per second
    },
    "ar": {
        "color": (255, 215, 0),  # Gold color for Arabic
        "font": cv2.FONT_HERSHEY_SIMPLEX,
        "scale": 1.3,  # Slightly larger for Arabic
        "thickness": 2,
        "bg_color": (30, 30, 30, 0.9),  # Darker background
        "border_color": (255, 100, 0, 0.3),  # Orange accent
        "animation_speed": 0.03  # Slower for Arabic
    }
}

# Layout
LINE_SPACING = 50
BOTTOM_MARGIN = 120
FADE_DURATION = 0.6  # seconds
TEXT_APPEAR_DURATION = 0.5  # seconds for typing effect

def process_video():
    # Initialize video capture
    cap = cv2.VideoCapture(INPUT_VIDEO)
    if not cap.isOpened():
        raise IOError(f"Cannot open video: {INPUT_VIDEO}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Initialize video writer (high quality)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, fps, (width, height))

    # Load subtitles
    subs = pysrt.open(INPUT_SRT)

    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        current_time = frame_count / fps
        frame_count += 1

        # Create overlay for all visual effects
        overlay = frame.copy()
        final_frame = frame.copy()

        # Process active subtitles
        y_pos = height - BOTTOM_MARGIN
        for sub in subs:
            start = sub.start.ordinal / 1000
            end = sub.end.ordinal / 1000

            if start <= current_time <= end:
                # Detect language
                lang = "ar" if any('\u0600' <= c <= '\u06FF' for c in sub.text) else "en"
                style = STYLES[lang]

                # Calculate animation progress
                anim_progress = min(1.0, (current_time - start) / TEXT_APPEAR_DURATION)
                fade_progress = min(
                    (current_time - start) / FADE_DURATION,
                    (end - current_time) / FADE_DURATION,
                    1.0
                )

                # Process each line
                for line in reversed(sub.text.split('\n')):
                    # Handle Arabic text reshaping
                    if lang == "ar":
                        line = get_display(reshape(line))

                    # Calculate visible characters for typing effect
                    visible_chars = int(len(line) * anim_progress)
                    visible_text = line[:visible_chars]

                    # Get text dimensions
                    (text_w, text_h), _ = cv2.getTextSize(
                        visible_text, style["font"],
                        style["scale"], style["thickness"]
                    )

                    # Calculate position (centered)
                    x_pos = int((width - text_w) / 2)

                    # Draw YouTube-style background
                    bg_height = text_h + 20
                    bg_width = text_w + 40
                    bg_x = x_pos - 20
                    bg_y = y_pos - text_h - 10

                    # Background with rounded corners effect
                    cv2.rectangle(
                        overlay,
                        (bg_x, bg_y),
                        (bg_x + bg_width, bg_y + bg_height),
                        style["bg_color"][:3], -1
                    )

                    # Add subtle border
                    cv2.rectangle(
                        overlay,
                        (bg_x, bg_y),
                        (bg_x + bg_width, bg_y + bg_height),
                        style["border_color"][:3], 2
                    )

                    # Draw text with shadow for readability
                    cv2.putText(
                        overlay, visible_text,
                        (x_pos, y_pos),
                        style["font"], style["scale"],
                        (0, 0, 0), style["thickness"] + 2,  # Shadow
                        cv2.LINE_AA
                    )
                    cv2.putText(
                        overlay, visible_text,
                        (x_pos, y_pos),
                        style["font"], style["scale"],
                        style["color"], style["thickness"],
                        cv2.LINE_AA
                    )

                    y_pos -= LINE_SPACING

        # Apply fade effect to the entire overlay
        final_frame = cv2.addWeighted(
            overlay, fade_progress if fade_progress < 1.0 else 1.0,
            final_frame, 1 - (fade_progress if fade_progress < 1.0 else 1.0),
            0
        )

        out.write(final_frame)

    # Release resources
    cap.release()
    out.release()
    print(f"Professional subtitles saved to {OUTPUT_VIDEO}")

if __name__ == "__main__":
    process_video()