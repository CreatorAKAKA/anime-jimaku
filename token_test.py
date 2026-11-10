from sudachipy import dictionary, tokenizer

analyzer = dictionary.Dictionary().tokenizer()

def extract_vocabulary(text):

    tokens = analyzer.tokenize(text, tokenizer.Tokenizer.SplitMode.C)
    tokens = list(tokens)
    
    vocabulary = []
    seen_words = {}

    consumed = set()
    for i, token in enumerate(tokens):
        if i in consumed:
            continue
        pos = token.part_of_speech()[0]

        if pos in ("名詞", "動詞", "形容詞", "形状詞", "代名詞"):
            dictionary_form = token.dictionary_form()

            if dictionary_form not in seen_words:
                new_tokens = analyzer.tokenize(dictionary_form)
                dictionary_reading = new_tokens[0].reading_form()

                original = token.surface()
                if pos == "動詞":
                    j = i + 1

                    while j < len(tokens):
                        next_token = tokens[j]
                        next_pos = next_token.part_of_speech()[0]

                        if next_pos == "助動詞":
                            original += next_token.surface()

                        elif (
                            next_pos == "形容詞"
                            and next_token.dictionary_form() == "ない"
                            and original.endswith("たく")
                        ):
                            original += next_token.surface()

                        else:
                            break
                        consumed.add(j)
                        j += 1
                entry = {
                    "surface": original,
                    "dictionary": dictionary_form,
                    "reading": dictionary_reading
                }   
                seen_words[dictionary_form] = entry
                vocabulary.append(entry)
    return vocabulary

if __name__ == "__main__":
    # text = "頑張った。そしてまた頑張った。俺は、頑張ることをやめない。"
    # result = extract_vocabulary(text)
    # print(result)
    # text = "頑張った。食べなかった。行きませんでした。食べさせられなかった。"
    # for token in analyzer.tokenize(text):
    #     print(
    #         token.surface(),
    #         token.dictionary_form(),
    #         token.part_of_speech()[0]
    #     )
    if __name__ == "__main__":
        text = """昨日は全然眠れなかった。
            先生に怒られてしまいました。
            彼女は泣きながら走っていた。
            そんなこと言われたくなかった。
            明日も頑張ってみようと思います。
            食べさせられなかった。
            勉強しなければならない。
            もう帰っちゃった。"""
        # text = "言われたくなかった。食べたくなかった。頑張ってみよう。"
        print(extract_vocabulary(text))