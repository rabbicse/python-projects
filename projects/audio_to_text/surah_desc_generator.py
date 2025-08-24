import json
import os

# Bengali surah names mapping (surah number to Bengali name)
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

# Wikipedia URLs
WIKI_URLS = {
    "en": "https://en.wikipedia.org/wiki/List_of_chapters_in_the_Quran",
    "bn": "https://bn.wikipedia.org/wiki/%E0%A6%95%E0%A7%81%E0%A6%B0%E0%A6%86%E0%A6%A8%E0%A7%87%E0%A6%B0_%E0%A6%B8%E0%A7%82%E0%A6%B0%E0%A6%BE%E0%A6%B0_%E0%A6%A4%E0%A6%BE%E0%A6%B2%E0%A6%BF%E0%A6%95%E0%A6%BE"
}


def load_surah_data(json_file_path):
    """Load surah data from JSON file"""
    with open(json_file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def generate_markdown(surah_data, surah_number, surah_info=None):
    """Generate markdown content for a surah"""
    surah_en = surah_data["en"][str(surah_number)]
    surah_ar = surah_data["ar"][str(surah_number)]

    # Get Bengali name
    bengali_name = BENGALI_NAMES.get(str(surah_number), "")

    # Format title with Bengali
    title = f"{surah_number}. Surah {surah_en['transliteratedName']} | {surah_ar['transliteratedName']} | {bengali_name}"

    # Format description
    description = f"✨ Surah {surah_en['transliteratedName']} - {surah_en['translatedName']}\n\n"
    description += "Listen, learn, and reflect on each word.\n\n"
    description += "Understand Allah's guidance, mercy, and blessings through this short word-by-word recitation.\n\n"
    description += f"🎵 Recitation: Mishari Rashid al-`Afasy - https://quran.com/reciters/7\n"
    description += "Source: https://quran.com/\n"
    description += "All rights to the recitation belong to the respective copyright holders.\n\n"
    description += "🌙 Du'a: May Allah guide us to His light. Ameen.\n\n"
    description += "🔔 Subscribe for more Qur'an recitations and Islamic reminders!\n\n"

    # Add hashtags
    hashtags = [
        f"#surah{surah_en['slug'].replace('-','')}",
        "#holyquran",
        "#quranrecitation",
        "#tilawat",
        "#beautifulrecitation",
        f"#surah{surah_number}",
        "#soothingquran",
        "#quranhealing",
        "#quranwithtajweed",
        "#heartsoothingquran",
        "#islamicreminders",
        "#listenquran",
        "#dailyquran",
        "#peacefulrecitation",
        "#quranshorts",
        "#healingquran",
        "#islamicvideo",
        "#islamicvideos"
    ]

    description += " ".join(hashtags)

    # Add surah info if available
    if surah_info:
        description += f"\n\n## About this Surah\n\n"
        description += f"**Name**: {surah_info.get('surah_name', 'N/A')}\n\n"
        description += f"**Number of Verses**: {surah_info.get('ayah_count', 'N/A')}\n\n"
        description += f"**Revelation Place**: {surah_info.get('revelation_place', 'N/A')}\n\n"
        description += f"**Description**: {surah_info.get('description', 'N/A')}\n\n"

    return title, description


def main():
    # Load your surah data
    surah_data = load_surah_data('quran/chapters.json')  # Replace with your JSON file path

    # Create output directory if it doesn't exist
    os.makedirs('surah_descriptions', exist_ok=True)

    # Process each surah
    for surah_number in range(1, 115):  # 1 to 114
        try:
            # Try to load additional surah info if available
            surah_info_path = f'surah_info/{surah_number}.json'
            surah_info = None
            if os.path.exists(surah_info_path):
                with open(surah_info_path, 'r', encoding='utf-8') as f:
                    surah_info = json.load(f).get('surah_info', {})

            # Generate markdown content
            title, description = generate_markdown(surah_data, surah_number, surah_info)

            # Save to file
            filename = f"surah_descriptions/{surah_number:03d}_{surah_data['en'][str(surah_number)]['slug']}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n\n")
                f.write(description)

            print(f"Generated: {filename}")

        except Exception as e:
            print(f"Error processing surah {surah_number}: {e}")


if __name__ == "__main__":
    main()