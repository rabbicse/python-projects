import sys

import pysrt
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M", use_auth_token=False)
model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M", use_auth_token=False)

def translate_ar_to_en(text):
    tokenizer.src_lang = "ar"
    encoded = tokenizer(text, return_tensors="pt")
    generated_tokens = model.generate(**encoded, forced_bos_token_id=tokenizer.get_lang_id("en"))
    return tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]

subs = pysrt.open("data/001_arabic.srt")
for sub in subs:
    arabic_text = sub.text
    english_text = translate_ar_to_en(arabic_text)
    sub.text = f"{arabic_text}\n{english_text}"

subs.save("data/001_combined.srt", encoding="utf-8")
print("✅ Combined Arabic + English SRT")
sys.exit(0)