from PIL import Image, ImageDraw, ImageFont
# from moviepy.editor import ImageClip
import arabic_reshaper
from bidi.algorithm import get_display
from moviepy import ImageClip

# Example ayah
text = "وَكُلُّهُمۡ ءَاتِيهِ يَوۡمَ ٱلۡقِيَٰمَةِ فَرۡدٗا ۝٩٥"
# text = "وَكُلُّهُمۡ ءَاتِيهِ يَوۡمَ ٱلۡقِيَٰمَةِ فَرۡدٗا"
# text = "بسم الله"  # Simpler Arabic text for testing
# text = "ٱلْحَمْدُ لِلَّهِ رَبِّ ٱلْعَـٰلَمِينَ ٢"

text = "سورة الفاتحة"

# Step 1: Reshape (needed for proper joining of Arabic letters)
configuration = {
    'delete_harakat': False,
    'support_ligatures': True,
    'RIAL SIGN': True,
}
reshaper = arabic_reshaper.ArabicReshaper(configuration=configuration)
reshaped_text = reshaper.reshape(text)

# Step 2: Apply bidi (sometimes optional, but safe)
bidi_text = get_display(reshaped_text)

# Step 3: Load Quranic font
font = ImageFont.truetype("fonts/uthmanic_hafs_v20.ttf", 100)

# Step 4: Create canvas
W, H = 1920, 400
img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Step 5: Measure text properly
bbox = draw.textbbox((0, 0), text, font=font)
w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]

# Step 6: Draw centered text
draw.text(((W - w) // 2, (H - h) // 2), text[::-1], font=font, fill="white")

img.show()

# Save if you want
# img.save("ayah.png")

# Convert to MoviePy clip (no need to save file)
# clip = ImageClip(img).with_duration(10)

# clip.preview()  # Show preview
# clip.write_videofile("ayah.mp4", fps=24)
