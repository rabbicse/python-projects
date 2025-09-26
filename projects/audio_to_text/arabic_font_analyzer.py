# import arabic_reshaper
# from bidi.algorithm import get_display
# from moviepy import TextClip
#
# # Example ayah (Ayatul Kursi)
# text = "وَلَمَّا بَرَزُوا۟ لِجَالُوتَ وَجُنُودِهِۦ قَالُوا۟ رَبَّنَآ أَفْرِغْ عَلَيْنَا صَبْرًۭا وَثَبِّتْ أَقْدَامَنَا وَٱنصُرْنَا عَلَى ٱلْقَوْمِ ٱلْكَـٰفِرِينَ ٢٥٠"
#
# # Reshape + fix RTL
# reshaped = arabic_reshaper.reshape(text)
# bidi_text = get_display(reshaped)
#
# # Create MoviePy clip
# clip = TextClip(
#     text=bidi_text,
#     font_size=100,
#     font="fonts/AllahMuhammad2022-axnpx.ttf",   # point directly to font file
#     color="white",
#     size=(1920,None),
#     method="caption",
#     stroke_color='black',  # Add stroke for better visibility
#     stroke_width=2
# )
#
# clip = clip.with_duration(10)
# clip.preview(fps=30)
# # clip.write_videofile("out.mp4", fps=24)




