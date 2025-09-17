import json

import whisper

model = whisper.load_model("small", device="cpu")  # small model is faster
# result = model.transcribe("data/quran-en-verse-by-verse/001-001.mp3", language="en", word_timestamps=True)
result = model.transcribe("data/quran-arabic-english/001.mp3", language="en", word_timestamps=False)

# Save to JSON
with open(f"data/001_001_segments_en.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=4)

# with open("data/001_arabic_test.srt", "w", encoding="utf-8") as f:
#     for idx, segment in enumerate(result["segments"], start=1):
#         start = segment["start"]
#         end = segment["end"]
#         text = segment["text"].strip()
#         start_srt = f"{int(start // 3600):02d}:{int((start % 3600) // 60):02d}:{int(start % 60):02d},{int((start * 1000) % 1000):03d}"
#         end_srt = f"{int(end // 3600):02d}:{int((end % 3600) // 60):02d}:{int(end % 60):02d},{int((end * 1000) % 1000):03d}"
#         f.write(f"{idx}\n{start_srt} --> {end_srt}\n{text}\n\n")
print("✅ Arabic SRT generated")
