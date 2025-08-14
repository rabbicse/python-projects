import pysrt
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.tools.segmenting import findObjects
from langdetect import detect

video = VideoFileClip("surah_fatihah.mp4")
subs = pysrt.open("combined.srt")

subtitle_clips = []

for sub in subs:
    start = sub.start.ordinal / 1000
    end = sub.end.ordinal / 1000
    lines = sub.text.split('\n')
    base_y = video.h - 100
    line_spacing = 50

    for idx, line in enumerate(lines):
        y_pos = base_y - idx*line_spacing
        try:
            lang = detect(line)
        except:
            lang = "en"

        font = "Arial-Bold" if lang=="ar" else "Arial"
        color = "yellow" if lang=="ar" else "white"

        txt_clip = TextClip(line, fontsize=40, font=font, color=color, method='label')
        txt_clip = txt_clip.set_start(start).set_end(end).set_position(('center', y_pos))

        letters = findObjects(txt_clip)
        letter_clips = [
            letter.set_start(start + i*0.05)
                  .set_end(end)
                  .fadein(0.1)
                  .fadeout(0.1)
            for i, letter in enumerate(letters)
        ]
        subtitle_clips.extend(letter_clips)

final = CompositeVideoClip([video] + subtitle_clips)
final.write_videofile("animated_subs_video.mp4", fps=24)
