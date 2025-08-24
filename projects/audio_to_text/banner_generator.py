import json

import arabic_reshaper
from PIL import Image, ImageDraw, ImageFont
from bidi.algorithm import get_display

FONT_ENGLISH_HEADER_PATH = "fonts/DejaVuSans.ttf"
FONT_ARABIC_HEADER_PATH = "fonts/Amiri-Regular.ttf"
CHAPTERS_PATH = "quran/chapters.json"

def create_youtube_banner(
        image_path: str,
        arabic_text: str,
        english_text: str,
        meaning_text: str,
        output_path: str
):
    """
    Generates a YouTube banner image with custom text using the Pillow library.

    Args:
        image_path (str): The path to the input banner image file (e.g., "banner_template.jpg").
        arabic_text (str): The Surah name in Arabic.
        english_text (str): The Surah name in English.
        meaning_text (str): The meaning of the Surah name.
        output_path (str): The path to save the new banner image (e.g., "final_banner.jpg").
    """
    try:
        # Load the banner image
        base_image = Image.open(image_path).convert("RGBA")
        width, height = base_image.size
        print(f"Image loaded with dimensions: {width}x{height}")

        # --- Add a semi-transparent dark overlay to make text more readable ---
        overlay = Image.new('RGBA', base_image.size, (0, 0, 0, 75)) # Semi-transparent black
        base_image = Image.alpha_composite(base_image, overlay)

        # Create a drawing context
        draw = ImageDraw.Draw(base_image)

        # --- Text Configuration ---
        # The fonts must be present on your system. You can download free fonts from Google Fonts.
        # For Arabic, a font like "Amiri" or "Lateef" works well.
        # For English, a bold, clear font like "Montserrat-Bold" or "Roboto-Bold" is a good choice.
        # Replace the font file paths with your actual font paths.
        try:
            arabic_font = ImageFont.truetype(FONT_ARABIC_HEADER_PATH, 330)
        except IOError:
            print("Arabic font not found. Using default font.")
            arabic_font = ImageFont.load_default()

        try:
            english_font = ImageFont.truetype(FONT_ENGLISH_HEADER_PATH, 200)
        except IOError:
            print("English font not found. Using default font.")
            english_font = ImageFont.load_default()

        try:
            meaning_font = ImageFont.truetype(FONT_ENGLISH_HEADER_PATH, 120)
        except IOError:
            print("Meaning font not found. Using default font.")
            meaning_font = ImageFont.load_default()

        # --- Text Styling ---
        # Using a golden color for prominence and white for readability.
        GOLD = "#FDD017" #"#FFD700"
        WHITE = "#FFFFFF"
        SHADOW_COLOR = "#000000"  # Black shadow for a clear contrast
        OFFSET = (8, 8)  # X and Y offset for the shadow in pixels

        # --- Text Positioning ---
        # The following calculations center the text horizontally and position it vertically.
        # The coordinates are based on a standard YouTube banner size (2560x1440),
        # but the code will adapt to your image's dimensions.

        # Position for the Arabic text
        # Get the width and height of the Arabic text to calculate the center position
        # Pillow's getbbox gives (left, top, right, bottom)
        configuration = {
            'delete_harakat': False,
            'support_ligatures': True,
            'RIAL SIGN': True,
        }
        reshaper = arabic_reshaper.ArabicReshaper(configuration=configuration)
        reshaped_text = reshaper.reshape(arabic_text)
        display_text = get_display(reshaped_text)
        display_text = display_text[::-1]
        arabic_text_bbox = draw.textbbox((0, 0), display_text, font=arabic_font)
        arabic_text_width = arabic_text_bbox[2] - arabic_text_bbox[0]
        arabic_x = (width - arabic_text_width) / 2
        arabic_y = height * 0.0  # 20% down from the top

        # Position for the English text
        english_text_bbox = draw.textbbox((0, 0), english_text, font=english_font)
        english_text_width = english_text_bbox[2] - english_text_bbox[0]
        english_x = (width - english_text_width) / 2
        english_y = height * 0.50  # Adjust this position as needed

        # Position for the Meaning text
        meaning_text_bbox = draw.textbbox((0, 0), meaning_text, font=meaning_font)
        meaning_text_width = meaning_text_bbox[2] - meaning_text_bbox[0]
        meaning_x = (width - meaning_text_width) / 2
        meaning_y = height * 0.80  # Adjust this position as needed

        # --- Drawing the Text onto the Image ---
        draw.text((arabic_x, arabic_y), display_text, font=arabic_font, fill=GOLD)
        draw.text((english_x, english_y), english_text, font=english_font, fill=WHITE)
        draw.text((meaning_x, meaning_y), meaning_text, font=meaning_font, fill=WHITE)

        # --- Drawing the Text onto the Image with Shadows ---
        # Arabic Text with Shadow
        draw.text((arabic_x + OFFSET[0], arabic_y + OFFSET[1]), display_text, font=arabic_font, fill=SHADOW_COLOR)
        draw.text((arabic_x, arabic_y), display_text, font=arabic_font, fill=GOLD)

        # English Text with Shadow
        draw.text((english_x + OFFSET[0], english_y + OFFSET[1]), english_text, font=english_font, fill=SHADOW_COLOR)
        draw.text((english_x, english_y), english_text, font=english_font, fill=WHITE)

        # Meaning Text with Shadow
        draw.text((meaning_x + OFFSET[0], meaning_y + OFFSET[1]), meaning_text, font=meaning_font, fill=SHADOW_COLOR)
        draw.text((meaning_x, meaning_y), meaning_text, font=meaning_font, fill=WHITE)

        # Save the new image
        base_image = base_image.convert("RGB")
        # base_image.show()
        base_image.save(output_path, optimize=True, quality=100, compress_level=9)
        print(f"New banner saved successfully at {output_path}")

    except FileNotFoundError:
        print(f"Error: The image file '{image_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def generate_banner(surah_no):
    with open(CHAPTERS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    data_en = data["en"][f"{surah_no}"]
    data_ar = data["ar"][f"{surah_no}"]

    surah_name_en = f'Surah {data_en["transliteratedName"]}'
    surah_name_ar = data_ar["transliteratedName"]
    surah_meaning_en = data_en["translatedName"]

    # You need to provide the path to your image here.
    # Make sure "banner_template.jpg" is in the same directory as this script.
    # You can also use the full path, e.g., "C:/Users/YourName/Pictures/banner_template.jpg"
    image_file = "quran/banner-base.png"

    # # Define the text content
    # surah_arabic = "الفاتحة"
    # surah_english = "Surah Al-Fatihah"
    # surah_meaning = "The Opener"

    # Define the output file name
    output_file = f"banners/{surah_no}_banner.jpg"

    # Run the function to create the banner
    create_youtube_banner(image_file, surah_name_ar, surah_name_en, surah_meaning_en, output_file)

# --- Main script execution ---
if __name__ == "__main__":
    # # You need to provide the path to your image here.
    # # Make sure "banner_template.jpg" is in the same directory as this script.
    # # You can also use the full path, e.g., "C:/Users/YourName/Pictures/banner_template.jpg"
    # image_file = "quran/banner-base.png"
    #
    # # Define the text content
    # surah_arabic = "الفاتحة"
    # surah_english = "Surah Al-Fatihah"
    # surah_meaning = "The Opener"
    #
    # # Define the output file name
    # output_file = "data/final_banner.png"
    #
    # # Run the function to create the banner
    # create_youtube_banner(image_file, surah_arabic, surah_english, surah_meaning, output_file)

    for i in range(1, 115):
        generate_banner(i)
    # generate_banner(114)
