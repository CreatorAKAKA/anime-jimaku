from jamdict import Jamdict


def get_definitions(word):
    jam = Jamdict()
    result = jam.lookup(word)
    meanings = []

    for entry in result.entries:
        for sense in entry.senses:
            definitions = []

            for gloss in sense.gloss:
                definitions.append(gloss.text)

            meanings.append(definitions)

    return meanings

if __name__ == "__main__":
    print(get_definitions("相手"))
    print(get_definitions("頑張る"))