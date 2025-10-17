import json

import arabic_reshaper
from PIL import Image, ImageDraw, ImageFont
from bidi.algorithm import get_display

FONT_ENGLISH_HEADER_PATH = "fonts/DejaVuSans.ttf"
FONT_BANGLA_HEADER_PATH = "fonts/Siyamrupali.ttf"
FONT_ARABIC_HEADER_PATH = "fonts/uthmanic_hafs_v20.ttf"
CHAPTERS_PATH = "quran/chapters.json"
FONT_ARABIC = "fonts/uthmanic_hafs_v20.ttf"

BENGALI_NAMES = {
    "1": "আল-ফাতিহা",
    "2": "আল-বাকারা",
    "3": "আল-ই-ইমরান",
    "4": "আন-নিসা",
    "5": "আল-মায়িদাহ",
    "6": "আল-আন'আম",
    "7": "আল-আ'রাফ",
    "8": "আল-আনফাল",
    "9": "আত-তাওবাহ",
    "10": "ইউনুস",
    "11": "হুদ",
    "12": "ইউসুফ",
    "13": "আর-রাদ",
    "14": "ইব্রাহিম",
    "15": "আল-হিজর",
    "16": "আন-নাহল",
    "17": "আল-ইসরা",
    "18": "আল-কাহফ",
    "19": "মরিয়ম",
    "20": "তাহা",
    "21": "আল-আম্বিয়া",
    "22": "আল-হাজ্জ",
    "23": "আল-মুমিনুন",
    "24": "আন-নূর",
    "25": "আল-ফুরকান",
    "26": "আশ-শু'আরা",
    "27": "আন-নামল",
    "28": "আল-কাসাস",
    "29": "আল-আনকাবুত",
    "30": "আর-রুম",
    "31": "লুকমান",
    "32": "আস-সাজদা",
    "33": "আল-আহযাব",
    "34": "সাবা",
    "35": "ফাতির",
    "36": "ইয়াসিন",
    "37": "আস-সাফফাত",
    "38": "সাদ",
    "39": "আয-যুমার",
    "40": "গাফির",
    "41": "ফুসসিলাত",
    "42": "আশ-শুরা",
    "43": "আয-যুখরুফ",
    "44": "আদ-দুখান",
    "45": "আল-জাসিয়াহ",
    "46": "আল-আহকাফ",
    "47": "মুহাম্মদ",
    "48": "আল-ফাতহ",
    "49": "আল-হুজুরাত",
    "50": "কাফ",
    "51": "আয-যারিয়াত",
    "52": "আত-তুর",
    "53": "আন-নাজম",
    "54": "আল-কামার",
    "55": "আর-রাহমান",
    "56": "আল-ওয়াকিয়াহ",
    "57": "আল-হাদিদ",
    "58": "আল-মুজাদিলাহ",
    "59": "আল-হাশর",
    "60": "আল-মুমতাহানাহ",
    "61": "আস-সাফ",
    "62": "আল-জুমু'আহ",
    "63": "আল-মুনাফিকুন",
    "64": "আত-তাগাবুন",
    "65": "আত-তালাক",
    "66": "আত-তাহরিম",
    "67": "আল-মুলক",
    "68": "আল-কালাম",
    "69": "আল-হাক্কাহ",
    "70": "আল-মা'আরিজ",
    "71": "নূহ",
    "72": "আল-জিন",
    "73": "আল-মুজাম্মিল",
    "74": "আল-মুদদাসসির",
    "75": "আল-কিয়ামাহ",
    "76": "আল-ইনসান",
    "77": "আল-মুরসালাত",
    "78": "আন-নাবা",
    "79": "আন-নাজিয়াত",
    "80": "আবাসা",
    "81": "আত-তাকভীর",
    "82": "আল-ইনফিতার",
    "83": "আল-মুতাফফিফিন",
    "84": "আল-ইনশিকাক",
    "85": "আল-বুরুজ",
    "86": "আত-তারিক",
    "87": "আল-আ'লা",
    "88": "আল-গাশিয়াহ",
    "89": "আল-ফাজর",
    "90": "আল-বালাদ",
    "91": "আশ-শামস",
    "92": "আল-লাইল",
    "93": "আদ-দুহা",
    "94": "আল-শারহ",
    "95": "আত-তিন",
    "96": "আল-আলাক",
    "97": "আল-কদর",
    "98": "আল-বাইয়িনাহ",
    "99": "আয-যালযালাহ",
    "100": "আল-আদিয়াত",
    "101": "আল-কারিয়াহ",
    "102": "আত-তাকাসুর",
    "103": "আল-আসর",
    "104": "আল-হুমাজাহ",
    "105": "আল-ফীল",
    "106": "কুরাইশ",
    "107": "আল-মাউন",
    "108": "আল-কাওসার",
    "109": "আল-কাফিরুন",
    "110": "আন-নাসর",
    "111": "আল-মাসাদ",
    "112": "আল-ইখলাস",
    "113": "আল-ফালাক",
    "114": "আন-নাস"
}

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
            arabic_font = ImageFont.truetype(FONT_ARABIC_HEADER_PATH, 450)
        except IOError:
            print("Arabic font not found. Using default font.")
            arabic_font = ImageFont.load_default()

        try:
            english_font = ImageFont.truetype(FONT_ENGLISH_HEADER_PATH, 250)
        except IOError:
            print("English font not found. Using default font.")
            english_font = ImageFont.load_default()

        try:
            meaning_font = ImageFont.truetype(FONT_ENGLISH_HEADER_PATH, 150)
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


def create_youtube_banner_updated(
        image_path: str,
        arabic_text: str,
        english_text: str,
        bangla_text: str,
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
        :param image_path:
        :param arabic_text:
        :param english_text:
        :param bangla_text:
        :param meaning_text:
        :param output_path:
    """
    try:
        # Load the banner image
        base_image = Image.open(image_path).convert("RGBA")
        # Resize to 1920x1080
        base_image = base_image.resize((1920, 1080), Image.Resampling.LANCZOS)
        width, height = base_image.size
        print(f"Image loaded with dimensions: {width}x{height}")

        # --- Add a semi-transparent dark overlay to make text more readable ---
        overlay = Image.new('RGBA', base_image.size, (0, 0, 0, 128)) # Semi-transparent black
        base_image = Image.alpha_composite(base_image, overlay)

        # Create a drawing context
        draw = ImageDraw.Draw(base_image)

        # --- Text Configuration ---
        # The fonts must be present on your system. You can download free fonts from Google Fonts.
        # For Arabic, a font like "Amiri" or "Lateef" works well.
        # For English, a bold, clear font like "Montserrat-Bold" or "Roboto-Bold" is a good choice.
        # Replace the font file paths with your actual font paths.
        try:
            arabic_font = ImageFont.truetype(FONT_ARABIC_HEADER_PATH, 350)
        except IOError:
            print("Arabic font not found. Using default font.")
            arabic_font = ImageFont.load_default()

        try:
            english_font = ImageFont.truetype(FONT_ENGLISH_HEADER_PATH, 150)
        except IOError:
            print("English font not found. Using default font.")
            english_font = ImageFont.load_default()

        try:
            bangla_font = ImageFont.truetype(FONT_BANGLA_HEADER_PATH, 150)
        except IOError:
            print("English font not found. Using default font.")
            bangla_font = ImageFont.load_default()

        try:
            meaning_font = ImageFont.truetype(FONT_ENGLISH_HEADER_PATH, 100)
        except IOError:
            print("Meaning font not found. Using default font.")
            meaning_font = ImageFont.load_default()

        # --- Text Styling ---
        # Using a golden color for prominence and white for readability.
        GOLD = "#FDD017" #"#FFD700"
        WHITE = "#FFFFFF"
        BANGLA_TEXT_COLOR = "#FFFFFF"
        MEANING_TEXT_COLOR = "#06D6A0"
        SHADOW_COLOR = "#000000"  # Black shadow for a clear contrast
        OFFSET = (9, 9)  # X and Y offset for the shadow in pixels

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
        arabic_text_bbox = draw.textbbox((0, 0), arabic_text, font=arabic_font)
        arabic_text_width = arabic_text_bbox[2] - arabic_text_bbox[0]
        arabic_x = (width - arabic_text_width) / 2
        arabic_y = height * 0.0  # 20% down from the top
        arabic_y = -90

        # Position for the English text
        english_text_bbox = draw.textbbox((0, 0), english_text, font=english_font)
        english_text_width = english_text_bbox[2] - english_text_bbox[0]
        english_x = (width - english_text_width) / 2
        english_y = height * 0.50  # Adjust this position as needed

        # Position for the English text
        bangla_text_bbox = draw.textbbox((0, 0), bangla_text, font=bangla_font)
        bangla_text_width = bangla_text_bbox[2] - bangla_text_bbox[0]
        bangla_x = (width - bangla_text_width) / 2
        bangla_y = height * 0.65  # Adjust this position as needed

        # Position for the Meaning text
        meaning_text_bbox = draw.textbbox((0, 0), meaning_text, font=meaning_font)
        meaning_text_width = meaning_text_bbox[2] - meaning_text_bbox[0]
        meaning_x = (width - meaning_text_width) / 2
        meaning_y = height * 0.88  # Adjust this position as needed

        # --- Drawing the Text onto the Image ---
        draw.text((arabic_x, arabic_y), arabic_text, font=arabic_font, fill=GOLD)
        draw.text((english_x, english_y), english_text, font=english_font, fill=WHITE)
        draw.text((bangla_x, bangla_y), bangla_text, font=bangla_font, fill=WHITE)
        draw.text((meaning_x, meaning_y), meaning_text, font=meaning_font, fill=WHITE)

        # --- Drawing the Text onto the Image with Shadows ---
        # Arabic Text with Shadow
        draw.text((arabic_x + OFFSET[0], arabic_y + OFFSET[1]), arabic_text, font=arabic_font, fill=SHADOW_COLOR)
        draw.text((arabic_x, arabic_y), arabic_text, font=arabic_font, fill=GOLD)

        # English Text with Shadow
        draw.text((english_x + OFFSET[0], english_y + OFFSET[1]), english_text, font=english_font, fill=SHADOW_COLOR)
        draw.text((english_x, english_y), english_text, font=english_font, fill=WHITE)

        draw.text((bangla_x + OFFSET[0], bangla_y + OFFSET[1]), bangla_text, font=bangla_font, fill=SHADOW_COLOR)
        draw.text((bangla_x, bangla_y), bangla_text, font=bangla_font, fill=BANGLA_TEXT_COLOR)

        # Meaning Text with Shadow
        draw.text((meaning_x + OFFSET[0], meaning_y + OFFSET[1]), meaning_text, font=meaning_font, fill=SHADOW_COLOR)
        draw.text((meaning_x, meaning_y), meaning_text, font=meaning_font, fill=MEANING_TEXT_COLOR)

        # Save the new image
        base_image = base_image.convert("RGB")
        # base_image.show()
        base_image.save(output_path, optimize=True, quality=95, compress_level=9)
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
    surah_name_ar = f'{data_ar["transliteratedName"]} ' + 'سُورَةٌ'
    surah_meaning_en = f'সূরা {data_en["translatedName"]}'

    # Get Bengali name
    surah_name_bn = BENGALI_NAMES.get(str(surah_no), "")

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

def generate_banner_en(surah_no):
    with open(CHAPTERS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    data_en = data["en"][f"{surah_no}"]
    data_ar = data["ar"][f"{surah_no}"]

    surah_name_en = f'Surah {data_en["transliteratedName"]}'
    surah_name_ar = 'سورة' + f' {data_ar["transliteratedName"]}'
    surah_meaning_en = f'{data_en["translatedName"]}'

    # Get Bengali name
    surah_name_bn = f'সূরা {BENGALI_NAMES.get(str(surah_no), "")}'

    # You need to provide the path to your image here.
    # Make sure "banner_template.jpg" is in the same directory as this script.
    # You can also use the full path, e.g., "C:/Users/YourName/Pictures/banner_template.jpg"
    image_file = "quran/banner-base-ai.png"

    # Define the output file name
    output_file = f"banners/{surah_no}_en_banner_new.jpg"

    # Run the function to create the banner
    create_youtube_banner_updated(image_file, surah_name_ar, surah_name_en, surah_name_bn, surah_meaning_en, output_file)

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
        generate_banner_en(i)
    # generate_banner_en(36)
