import re

import requests
from bs4 import BeautifulSoup
import json

from requests import session
from tqdm import tqdm
import time

BASE_URL = "https://quran.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

session = requests.Session()


def get_all_surah_info():
    """Scrape Surah details like name, meaning, revelation type, and ayah count."""
    url = f"https://quran.com/_next/data/aU_WE3nqYKk2YCDt4qgcc/ar/1.json"
    response = session.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"⚠️ Failed to fetch All Surah info")
        return {}

    json_data = response.json()

    arabic_chapters = json_data["pageProps"]["chaptersData"]

    url = f"https://quran.com/_next/data/aU_WE3nqYKk2YCDt4qgcc/en/1.json"
    response = session.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"⚠️ Failed to fetch All Surah info")
        return {}

    json_data = response.json()

    en_chapters = json_data["pageProps"]["chaptersData"]

    data = {
        "en": en_chapters,
        "ar": arabic_chapters
    }

    # Save to JSON
    with open(f"quran/chapters.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("✅ Quran data saved successfully!")


def get_surah_info(surah_number):
    """Scrape Surah details like name, meaning, revelation type, and ayah count."""
    url = f"{BASE_URL}/surah/{surah_number}/info"
    response = session.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"⚠️ Failed to fetch Surah {surah_number} info")
        return {}

    soup = BeautifulSoup(response.text, "html.parser")

    basic = {}

    try:
        basic["surah_name"] = soup.find("div", class_=re.compile(r"Info_surahName__.*")).text.strip()

        detail_headers = soup.find_all("p", class_=re.compile(r"Info_detailHeader__.*"))
        for detail_header in detail_headers:
            if 'Ayahs' in detail_header:
                basic["ayah_count"] = detail_header.find_next_sibling('p').text.strip()
            elif 'Revelation Place' in detail_header:
                basic["revelation_place"] = detail_header.find_next_sibling('p').text.strip()

        basic["description"] = "".join(
            [str(content) for content in soup.find('div', class_=re.compile(r"Info_textBody__.*")).text.strip()])
    except Exception as ex:
        print(ex)

    return basic


def get_audio_segments(surah_number):
    """Scrape Ayahs from a given Surah page."""
    # url = f"https://quran.com/api/proxy/content/api/qdc/verses/by_chapter/{surah_number}?words=true&translation_fields=resource_name%2Clanguage_id&per_page=500000&fields=text_uthmani%2Cchapter_id%2Chizb_number%2Ctext_imlaei_simple&translations=131&reciter=7&word_translation_language=en&page=1"
    url = f'https://quran.com/api/proxy/content/api/qdc/audio/reciters/7/audio_files?chapter={surah_number}&segments=true'
    response = session.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"⚠️ Failed to fetch Surah {surah_number}")
        return None

    return response.json()


def get_surah_ayahs(surah_number):
    """Scrape Ayahs from a given Surah page."""
    # url = f"https://quran.com/api/proxy/content/api/qdc/verses/by_chapter/{surah_number}?words=true&translation_fields=resource_name%2Clanguage_id&per_page=500000&fields=text_uthmani%2Cchapter_id%2Chizb_number%2Ctext_imlaei_simple&translations=131&reciter=7&word_translation_language=en&page=1"
    # https://quran.com/api/proxy/content/api/qdc/verses/by_page/7?words=true&per_page=all&fields=text_uthmani%2Cchapter_id%2Chizb_number%2Ctext_imlaei_simple&reciter=7&word_translation_language=en&word_fields=verse_key%2Cverse_id%2Cpage_number%2Clocation%2Ctext_uthmani%2Ctext_imlaei_simple%2Ccode_v1%2Cqpc_uthmani_hafs&mushaf=2&filter_page_words=true&from=2%3A38&to=2%3A48
    url = f'https://quran.com/_next/data/aU_WE3nqYKk2YCDt4qgcc/en/{surah_number}.json'
    response = session.get(url, headers=HEADERS)

    # print(response.json())

    if response.status_code != 200:
        print(f"⚠️ Failed to fetch Surah {surah_number}")
        return []

    json_data = response.json()
    verse_response = json_data["pageProps"]["versesResponse"]
    verses = verse_response["verses"]
    # print(f"Total verses: {len(verses)}")
    # print(f"json response: {json.dumps(json_data)}")

    ayahs_data = []
    for verse in verses:
        ayahs_data.append({
            "verse_key": verse["verseKey"],
            "verse_num": verse["verseKey"],
            "arabic_text": verse["textUthmani"],
            "en_text": "".join([translation["text"] for translation in verse["translations"]]),
        })
    return ayahs_data


def get_surah_ayahs_by_page(surah_number, page=1, per_page=5):
    """Scrape Ayahs from a given Surah page."""
    url = f'https://quran.com/api/proxy/content/api/qdc/verses/by_chapter/{surah_number}?words=true&translation_fields=resource_name%2Clanguage_id&per_page={per_page}&fields=text_uthmani%2Cchapter_id%2Chizb_number%2Ctext_imlaei_simple&translations=131&reciter=7&word_translation_language=en&page={page}&word_fields=verse_key%2Cverse_id%2Cpage_number%2Clocation%2Ctext_uthmani%2Ctext_imlaei_simple%2Ccode_v1%2Cqpc_uthmani_hafs&mushaf=2'
    response = session.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"⚠️ Failed to fetch Surah {surah_number} with page {page} and per page={per_page}")
        return None

    json_data = response.json()
    verses = json_data["verses"]
    # print(f"Total verses: {len(verses)}")
    # print(f"json response: {json.dumps(json_data)}")

    ayahs_data = []
    for verse in verses:
        ayahs_data.append({
            "verse_key": verse["verse_key"],
            "verse_num": verse["verse_key"],
            "arabic_text": verse["text_uthmani"],
            "en_text": "".join([translation["text"] for translation in verse["translations"]]),
        })
    return ayahs_data


def crawl_quran():
    """Crawl all 114 Surahs (info + Ayahs) and save them in JSON."""
    quran_data = []

    for surah_number in tqdm(range(1, 115), desc="Crawling Quran"):
        surah_info = get_surah_info(surah_number)
        ayahs = get_surah_ayahs(surah_number)
        audio_segments = get_audio_segments(surah_number)
        surah_data = {"audio": audio_segments}

        if surah_info and ayahs:
            quran_data.append({**surah_info})
            surah_data["surah_info"] = surah_info
            surah_data["surah_verses"] = ayahs
            for ayah in ayahs:
                quran_data.append({"surah_name": surah_info["surah_name"], "ayah": ayah})

        # Save to JSON
        with open(f"quran/{surah_number}.json", "w", encoding="utf-8") as f:
            json.dump(surah_data, f, ensure_ascii=False, indent=4)

    # Save to JSON
    with open("quran/quran_data.json", "w", encoding="utf-8") as f:
        json.dump(quran_data, f, ensure_ascii=False, indent=4)

    print("✅ Quran data saved successfully!")


def crawl_quran_by_surah(surah_number, per_page=5):
    """Crawl all 114 Surahs (info + Ayahs) and save them in JSON."""
    print(f"Processing surah: {surah_number} ...")
    surah_info = get_surah_info(surah_number)
    ayahs = []

    orig_verses = get_surah_ayahs(surah_number)


    if int(surah_info["ayah_count"]) > len(orig_verses):
        success_count = 0
        page = 1

        while True:
            verses = get_surah_ayahs_by_page(surah_number, page=page, per_page=per_page)

            if not verses or len(verses) == 0:
                per_page += 1
                if per_page > int(surah_info["ayah_count"]) - success_count:
                    print(f"per page exceeded!")
                    break
                continue

            print(f"✅ Paging data success for page: {page} and page number: {per_page}!")
            success_count += len(verses)
            ayahs.extend(verses)
            page += 1

        if int(surah_info["ayah_count"]) > len(ayahs):
            print(f"Surah data mismatch!")
    else:
        ayahs = orig_verses

    audio_segments = get_audio_segments(surah_number)
    surah_data = {"audio": audio_segments}

    if surah_info and ayahs:
        surah_data["surah_info"] = surah_info
        surah_data["surah_verses"] = ayahs

    # Save to JSON
    with open(f"quran/{surah_number}.json", "w", encoding="utf-8") as f:
        json.dump(surah_data, f, ensure_ascii=False, indent=4)

    print("✅ Quran data saved successfully!")


# Run the crawler
# crawl_quran()
# crawl_quran_by_surah(92, per_page=14) # download by surah

for i in range(1, 81):
    crawl_quran_by_surah(i, per_page=1)

# crawl_quran_by_surah(92, per_page=3)

# get_all_surah_info()

# get_surah_info(45)
# ayah_data = get_surah_ayahs(45)
# print(ayah_data)
