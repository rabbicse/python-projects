import arabic_reshaper
from bidi.algorithm import get_display
from moviepy import TextClip

# Example ayah (Ayatul Kursi)
text = " وَلَمَّا بَرَزُوا۟ لِجَالُوتَ وَجُنُودِهِۦ قَالُوا۟ رَبَّنَآ أَفْرِغْ عَلَيْنَا صَبْرًۭا وَثَبِّتْ أَقْدَامَنَا وَٱنصُرْنَا عَلَى ٱلْقَوْمِ ٱلْكَـٰفِرِينَ ٢٥٠"
# text = "وَكُلُّهُمۡ ءَاتِيهِ يَوۡمَ ٱلۡقِيَٰمَةِ فَرۡدٗا"
# Reshape + fix RTL
configuration = {
    'delete_harakat': False,
    'support_ligatures': True,
    'RIAL SIGN': True,
}
reshaper = arabic_reshaper.ArabicReshaper(configuration=configuration)
reshaped_text = reshaper.reshape(text)
bidi_text = get_display(reshaped_text)

# Create MoviePy clip
clip = TextClip(
    text=bidi_text,
    font_size=100,
    font="fonts/UthmanicHafs1Ver18v1.woff2",   # point directly to font file
    # font="KFGQPC_HAFS_Uthmanic_Script_H",
    color="white",
    size=(1920,None),
    method="caption",
    stroke_color='red',  # Add stroke for better visibility
    stroke_width=2,
    margin=(10, 50, 10, 50)
)

clip = clip.with_duration(10)
clip.preview(fps=30)
# clip.write_videofile("out.mp4", fps=24)




