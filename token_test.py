from sudachipy import dictionary, tokenizer

analyzer = dictionary.Dictionary().tokenizer()

def extract_vocabulary(text):

    tokens = analyzer.tokenize(text, tokenizer.Tokenizer.SplitMode.C)

    vocabulary = []
    seen_words = {}

    for token in tokens:
        pos = token.part_of_speech()[0]

        if pos in ("名詞", "動詞", "形容詞", "形状詞", "代名詞"):
            dictionary_form = token.dictionary_form()

            if dictionary_form not in seen_words:
                new_tokens = analyzer.tokenize(dictionary_form)
                dictionary_reading = new_tokens[0].reading_form()
                entry = {
                    "surface": token.surface(),
                    "dictionary": dictionary_form,
                    "reading": dictionary_reading
                }   
                seen_words[dictionary_form] = entry
                vocabulary.append(entry)
    return vocabulary

if __name__ == "__main__":
    text = "頑張った。そしてまた頑張った。俺は、頑張ることをやめない。"
    result = extract_vocabulary(text)
    print(result)