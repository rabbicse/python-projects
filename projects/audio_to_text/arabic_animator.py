#!/usr/bin/env python3
"""
animated_subs_eased.py
Arabic + English subtitle animation (fade + slide + easing).
"""

import os
import numpy as np
from moviepy import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

# Font configuration
FONT_ENGLISH_HEADER_PATH = "fonts/DejaVuSans.ttf"
FONT_ENGLISH_PATH = "fonts/DejaVuSans.ttf"
FONT_ARABIC_HEADER_PATH = "fonts/Amiri-Regular.ttf"
FONT_ARABIC_PATH = "fonts/NotoSansArabic-Regular.ttf"
FALLBACK_FONT_PATH = "fonts/DejaVuSans.ttf"

# ---------- Subtitle Data (example) ----------
SUBS = [
    (0.0, 4.5,
     "أَلَمْ تَرَ كَيْفَ فَعَلَ رَبُّكَ بِأَصْحَابِ ٱلْفِيلِ",
     "Have you not seen how your Lord dealt with the companions of the elephant?"),
    (4.6, 9.5,
     "أَلَمْ يَجْعَلْ كَيْدَهُمْ فِي تَضْلِيلٍ",
     "Did He not make their plan go astray?"),
]

# ---------- Helpers ----------
def shape_arabic(text: str) -> str:
    return get_display(arabic_reshaper.reshape(text))

def render_text_image(text, font_path, size, color=(255,255,255)):
    font = ImageFont.truetype(font_path, size)
    dummy = Image.new("RGBA", (10,10))
    draw = ImageDraw.Draw(dummy)
    # w, h = draw.textsize(text, font=font)
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    img = Image.new("RGBA", (w+20, h+20), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.text((10,10), text, font=font, fill=color)
    return img

def ease_out_quad(t):
    """Quadratic ease-out curve (0→1)."""
    return 1 - (1-t)*(1-t)

def make_text_clip(img, start, end, y_target, delay=0, slide=20, fade=0.5):
    """Create a fade+slide+ease text animation."""
    dur = end - start
    np_img = np.array(img.convert("RGBA"))

    def make_frame(t):
        if t < 0 or t > dur:  # outside range
            return None
        alpha = 1.0
        # Fade in/out
        if t < fade:
            alpha = t / fade
        elif t > dur - fade:
            alpha = (dur - t) / fade
        # Slide + ease
        progress = ease_out_quad(min(1, t / fade))
        y_offset = slide * (1 - progress)
        frame = np_img.copy()
        # apply alpha
        if alpha < 1:
            frame = frame.astype(float)
            frame[:,:,3] = frame[:,:,3] * alpha
            frame = frame.astype(np.uint8)
        return frame, y_offset

    # Wrap in ImageClip
    clip = ImageClip(np_img, duration=(end-start)).with_start(start+delay)

    def pos_func(t):
        res = make_frame(t)
        if res is None:
            return ("center","center")
        _, y_off = res
        return ("center", y_target + y_off)

    def img_func(t):
        res = make_frame(t)
        if res is None:
            return np.zeros_like(np_img)
        frame, _ = res
        return frame

    # Frame function (fade in/out)
    def frame_func(get_frame, t):
        frame = get_frame(t)
        t_rel = t - start - delay
        alpha = 1.0
        if t_rel < fade:
            alpha = t_rel / fade
        elif t_rel > dur - fade:
            alpha = (dur - t_rel) / fade
        frame = frame.astype(float)
        frame[...,3] = frame[...,3] * alpha
        return frame.astype(np.uint8)

    return clip.with_position(pos_func)#.fl(frame_func)

# ---------- Main ----------
def main():
    # Load base video or image+audio background
    base = VideoFileClip("data/quran.mp4")  # change to your file
    W, H = base.size

    arabic_font = FONT_ARABIC_HEADER_PATH #"Amiri-Regular.ttf"   # <-- set proper font path
    english_font = FONT_ENGLISH_HEADER_PATH #"Arial.ttf"

    clips = [base]

    for start, end, ar, en in SUBS:
        # Arabic
        arab_img = render_text_image(shape_arabic(ar), arabic_font, 54, (255,255,255))
        arab_clip = make_text_clip(arab_img, start, end, int(H*0.62), delay=0, slide=40, fade=0.7)

        # English (delayed slightly)
        eng_img = render_text_image(en, english_font, 32, (220,220,220))
        eng_clip = make_text_clip(eng_img, start, end, int(H*0.72), delay=0.3, slide=30, fade=0.5)

        clips.extend([arab_clip, eng_clip])

    final = CompositeVideoClip(clips).with_duration(base.duration)
    final.write_videofile("data/output.mp4", codec="libx264", audio_codec="aac", fps=24)

if __name__ == "__main__":
    main()
