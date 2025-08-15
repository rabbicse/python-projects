import json
import re


def ms_to_srt_time(ms):
    """Convert milliseconds to SRT format: HH:MM:SS,mmm"""
    seconds, millis = divmod(ms, 1000)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"

def clean_html_tags(text):
    """Remove HTML tags like <sup ...> from text"""
    text = re.sub(r'<[^>]*>', '', text)
    return re.sub(r'˹|˺', '', text).strip()

def generate_srt(data):
    verse_timings = data["audio"]["audio_files"][0]["verse_timings"]
    verses = {v["verse_key"]: v for v in data["surah_verses"]}

    srt_lines = []
    counter = 1

    for timing in verse_timings:
        verse_key = timing["verse_key"]

        if verse_key not in verses:
            continue

        arabic = verses[verse_key]["arabic_text"]
        english = clean_html_tags(verses[verse_key]["en_text"])

        start_time = ms_to_srt_time(timing["timestamp_from"])
        end_time = ms_to_srt_time(timing["timestamp_to"])

        srt_lines.append(f"{counter}")
        srt_lines.append(f"{start_time} --> {end_time}")
        srt_lines.append(arabic)
        srt_lines.append(english)
        srt_lines.append("")  # blank line

        counter += 1

    return "\n".join(srt_lines)

def json_to_srt(json_file, srt_file):
    # Load JSON
    with open(json_file, "r+", encoding="utf-8") as f:
        data = json.load(f)

    # Generate SRT
    srt_content = generate_srt(data)

    # Save file
    with open(srt_file, "w+", encoding="utf-8") as f:
        f.write(srt_content)

# Example usage
json_to_srt("quran/113.json", "data/113_subtitles.srt")
