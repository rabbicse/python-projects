import arabic_reshaper
from bidi.algorithm import get_display
from moviepy import TextClip


def to_arabic(num: int) -> str:
    # Western to Arabic-Indic digits map (Unicode escapes)
    digits = ["\u0660", "\u0661", "\u0662", "\u0663", "\u0664",
              "\u0665", "\u0666", "\u0667", "\u0668", "\u0669"]
    return "".join(digits[int(d)] for d in str(num))


# Example ayah (Ayatul Kursi)
# text = "وَلَمَّا بَرَزُوا۟ لِجَالُوتَ وَجُنُودِهِۦ قَالُوا۟ رَبَّنَآ أَفْرِغْ عَلَيْنَا صَبْرًۭا وَثَبِّتْ أَقْدَامَنَا وَٱنصُرْنَا عَلَى ٱلْقَوْمِ ٱلْكَـٰفِرِينَ ٢٥٠"


text = "بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ ١"
# Reshape + fix RTL
# Arabic Caption
# Create the text clip without a font parameter
# For Arabic, we need to process the text first
configuration = {
    'delete_harakat': False,
    'support_ligatures': True,
    # 'RIAL SIGN': True,
}
reshaper = arabic_reshaper.ArabicReshaper(configuration=configuration)
reshaped_text = reshaper.reshape(text)
arabic_display_text = get_display(reshaped_text)
arabic_display_text = arabic_display_text[::-1]  # Reverse for proper RTL display

subtitle_ar_file = f"quran/verse-by-verse/002-286.txt"
with open(subtitle_ar_file, 'r', encoding='utf-8') as f:
    subtitle_ar = f.readline().strip()

# Create MoviePy clip
clip = TextClip(
    # text=" ".join([to_arabic(i) for i in range(50)]),
    text=subtitle_ar + " " + to_arabic(1),
    font_size=70,
    font="fonts/uthmanic_hafs_v20.ttf",  # point directly to font file
    # font="fonts/UthmanicHafs1Ver18.woff2",   # point directly to font file
    color="white",
    size=(1500, None),
    method="caption",
    stroke_color='black',  # Add stroke for better visibility
    stroke_width=2,
    margin=(30, 0, 30, 50)
)

clip = clip.with_duration(30)
clip.preview(fps=30)
# clip.write_videofile("out.mp4", fps=24)
