import requests
from bs4 import BeautifulSoup
import os
import re

# ---------- CONFIG ----------
input_html = "verses.html"   # Your HTML file containing the snippet
output_dir = "quran/verse-by-verse"        # Directory to store txt files
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

session = requests.Session()
# ----------------------------

def strip_leading_number(line: str) -> str:
    """Remove leading English numbers like '1.' or '12.' from a verse."""
    return re.sub(r"^\s*\d+\s*[.)]?\s*", "", line).strip()

def crawl_verses_by_surah(surah_no: int):
    url = f"https://quran411.com/mobile/verse-by-verse.php?sn={surah_no}"
    response = session.get(url, headers=HEADERS, verify=False)

    if response.status_code != 200:
        print(f"⚠️ Failed to fetch All Surah info")
        return

    # Parse with BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all headers
    headers = soup.find_all("div", class_="collapsible-header")

    arabic_body = None
    for h in headers:
        icon = h.find("i", class_="mdi mdi-islam")
        if icon and "Arabic" in h.get_text(strip=True):
            # Next sibling body
            arabic_body = h.find_next_sibling("div", class_="collapsible-body")
            break

    if not arabic_body:
        print("⚠️ No Arabic body found after header")

    # Extract <span> text
    span = arabic_body.find("span")
    if not span:
        print("⚠️ No <span> found inside Arabic body")
        return

    # Alternative more reliable: replace <br> with newline
    html_with_br = str(span)
    html_with_br = html_with_br.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    lines = [strip_leading_number(line.strip()) for line in
             BeautifulSoup(html_with_br, "html.parser").get_text().splitlines() if line.strip()]

    # print(lines)
    # print(lines)
    for line in lines:
        print(line)

    # Clean and save verses
    os.makedirs(output_dir, exist_ok=True)
    total = len(lines)
    pad = len(str(total))

    for idx, line in enumerate(lines, 1):
        verse = strip_leading_number(line)
        if not verse:
            continue
        filename = os.path.join(output_dir, f"{surah_no:03}-{idx:03}.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(verse + "\n")

    print(f"✅ Extracted {total} verses into '{output_dir}/'")

if __name__ == "__main__":
    for i in range(1, 115):
        crawl_verses_by_surah(i)
