from jamdict import Jamdict


def get_definitions(word, reading):
    jam = Jamdict()
    result = jam.lookup(word)
    meanings = []

    for entry in result.entries:
        if not any(
            hiragana_to_katakana(kana.text) == reading
            for kana in entry.kana_forms
        ):
            continue
        for sense in entry.senses:
            definitions = []

            for gloss in sense.gloss:
                definitions.append(gloss.text)

            meanings.append(definitions)

    return meanings

def hiragana_to_katakana(text):
    result = ""

    for char in text:
        if "ぁ" <= char <= "ゖ":
            result += chr(ord(char) + 96)
        else:
            result += char

    return result


if __name__ == "__main__":
    print("Reading 1:")
    print(get_definitions("生物", "セイブツ"))

    print("Reading 2:")
    print(get_definitions("生物", "ナマモノ"))

    print("Wrong reading:")
    print(get_definitions("生物", "アイテ"))
    