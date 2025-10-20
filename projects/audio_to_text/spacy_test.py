import spacy
nlp = spacy.load("en_core_web_sm", disable=["ner"])

def analyze_text(text: str):
    doc = nlp(text)

    highlight_pos = {"NOUN", "PROPN", "ADJ", "VERB"}
    stopwords = nlp.Defaults.stop_words

    tokens = []
    for token in doc:
        # Fix possessive words like "Allah's"
        if token.tag_ == "POS" and tokens:  # POS = possessive
            tokens[-1]["text"] += token.text  # attach 's
            tokens[-1]["end"] = token.idx + len(token.text)
            continue

        tokens.append({
            "text": token.text,
            "start": token.idx,
            "end": token.idx + len(token.text),
            "highlight": (
                token.pos_ in highlight_pos and
                token.text.lower() not in stopwords and
                token.is_alpha
            )
        })

    return tokens


text = "Allah's guidance is the best."
print(analyze_text(text))
