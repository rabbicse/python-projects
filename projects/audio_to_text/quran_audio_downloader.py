import wget
import os

def download_audio(surah_no):
    """Downloads the MP3 file using wget library."""
    try:
        print(f"Downloading for surah => {surah_no:03}")
        audio_url = f"https://masjidtaqwa.org/quran/arabic-english/{surah_no:03}.mp3"
        audio_file_path = f"quran-en/{surah_no:03}.mp3"

        # Ensure directory exists
        os.makedirs("quran-en", exist_ok=True)

        # Download file
        wget.download(audio_url, audio_file_path)
        print(f"\n✅ Audio downloaded successfully to: {audio_file_path}")
        return True
    except Exception as e:
        print(f"❌ Error downloading audio: {e}")
        return False


for i in range(5, 115):
    download_audio(i)
