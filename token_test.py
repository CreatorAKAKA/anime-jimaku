from sudachipy import dictionary, tokenizer

text = "頑張った。そしてまた頑張った。俺は、頑張ることをやめない。"

analyzer = dictionary.Dictionary().tokenizer()

tokens = analyzer.tokenize(text, tokenizer.Tokenizer.SplitMode.C)

vocabulary = []
seen_words = {}

for token in tokens:
    pos = token.part_of_speech()[0]

    if pos in ("名詞", "動詞", "形容詞", "形状詞"):
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
for entry in vocabulary:
    print(entry)