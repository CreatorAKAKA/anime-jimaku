import easyocr
import streamlit as st
st.set_page_config(
    page_title="JimaQuiz | ジマクイズ",
    page_icon="🌸",
    layout="wide"
)
st.markdown("""
<style>
div.stButton button strong {
    color: #F9A8D4 !important;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)
from PIL import Image
from PIL import ImageEnhance #makes subtitles easier to read by enhancing contrast
import numpy as np
import hashlib #gives images unique fingerprints based on their content, so that the same image will always have the same name
from token_test import extract_vocabulary #extracts vocabulary from Japanese text using SudachiPy
from dictionary_test import get_definitions #fetches definitions for Japanese words using Jamdict
import html
from database import init_db, save_flashcard, load_flashcards

@st.cache_resource
def load_reader():
    return easyocr.Reader(["ja"], gpu=False) #initialize the reader with Japanese language recognition, use cpu

reader = load_reader()

def katakana_to_hiragana(text): #changes katakana to hiragana
    result = ""

    for char in text:
        if "ァ" <= char <= "ヶ":
            result += chr(ord(char) - 96)
        else:
            result += char

    return result

def highlight_word(sentence, surface): #highlights the surface form of a word for easier readability
    safe_sentence = html.escape(sentence)
    safe_surface = html.escape(surface)

    if not surface:
        return safe_sentence

    return safe_sentence.replace(
        safe_surface,
        f'<strong style="color: #F9A8D4;">{safe_surface}</strong>'
    )

def update_saved_contexts():
    current_image_id = st.session_state["previous_image_id"]
    corrected_text = st.session_state["ocr_text"]

    for info in st.session_state["word_bank"].values():
        for context in info.get("contexts", []):
            if context.get("image_id") == current_image_id:
                context["sentence"] = corrected_text

st.title("ジマクイズ 🌸")
st.write("JimaQuiz - Learn Japanese through the stories you love.")

image_bytes = None

image_col, quiz_col = st.columns([1, 1], gap="large")

init_db()

if "word_bank" not in st.session_state:
    st.session_state["word_bank"] = load_flashcards()

if "ocr_text" not in st.session_state: # Initialize the session state variable for storing OCR text
    st.session_state["ocr_text"] = ""

if "previous_image_id" not in st.session_state:
    st.session_state["previous_image_id"] = None

if "vocab_expanded" not in st.session_state:
    st.session_state["vocab_expanded"] = False

with image_col:
    st.subheader("Screenshot & OCR")

    screenshot = st.file_uploader(
        "Upload an anime screenshot",
        type=["png", "jpg", "jpeg"]
    )

    if screenshot is not None:
        image_id = hashlib.sha256(screenshot.getvalue()).hexdigest()

        if image_id != st.session_state["previous_image_id"]: #check if the uploaded image is different from the previous one
            st.session_state["ocr_text"] = ""
            st.session_state["previous_image_id"] = image_id

        image = Image.open(screenshot)
        image_bytes = screenshot.getvalue()

        st.subheader("Original Screenshot")
        st.image(image)

        width, height = image.size

        percentage = st.slider(
        "Subtitle region (%)",
        min_value=10,
        max_value=60,
        value=30)

        # Crop the bottom 30% of the screenshot
        subtitle_region = image.crop((
            0,
            int(height * (1 - percentage / 100)),
            width,
            height
        ))

        st.subheader("Detected Subtitle Region")
        st.image(subtitle_region)

        if image_id != st.session_state.get("last_ocr_image_id"):
            with st.spinner("Recognizing subtitles..."):
                grayscale = subtitle_region.convert("L")# Convert to grayscale for easier text recognition
                enhancer = ImageEnhance.Contrast(grayscale)
                processed = enhancer.enhance(2.0) 

                results = reader.readtext(
                    np.array(processed),
                    detail=0
                )
            st.session_state["ocr_text"] = "".join(results)
            st.session_state["last_ocr_image_id"] = image_id
        st.text_area(
            "Edit recognized Japanese text",
            key = "ocr_text",
            height = 150,
            on_change=update_saved_contexts #makes sure that all saved contexts of the same screenshots are updated to have the same texts when the user edits the original text
        )

with quiz_col:
    word_bank = st.session_state["word_bank"]

    st.subheader("Flashcards")

    if not word_bank:
        st.info("Save some vocabulary to start reviewing!")
    else:
        words = list(word_bank.keys())
        if "card_index" not in st.session_state:
            st.session_state["card_index"] = 0

        if "card_flipped" not in st.session_state:
            st.session_state["card_flipped"] = False

        if "context_index" not in st.session_state:
            st.session_state["context_index"] = 0

        st.session_state["card_index"] %= len(words)

        current_word = words[st.session_state["card_index"]]

        info = word_bank[current_word]

        st.write(f"Card {st.session_state['card_index'] + 1} of {len(words)}")

        with st.container(border=True):
            st.markdown(f"### {current_word}")
            contexts = info.get("contexts", [])

            if contexts:
                st.session_state["context_index"] %= len(contexts)
                context = contexts[st.session_state["context_index"]]

                if context["image"] is not None:
                    st.image(context["image"], use_container_width=True)
            if contexts:
                st.write("**Example Sentences**")

                for number, example in enumerate(contexts):
                    if st.button(
                        example["sentence"].replace(example.get("surface", current_word), f"**{example.get('surface', current_word)}**"),
                        key=f"context_{current_word}_{number}",
                        use_container_width=True
                    ):
                        st.session_state["context_index"] = number
                        st.rerun()
            if st.session_state["card_flipped"]:
                reading = katakana_to_hiragana(info["reading"])
                st.write(f"**Reading:** {reading}")

                for sense in info["meanings"][:3]:
                    st.write("; ".join(sense))


            if st.button("Flip Card"):
                st.session_state["card_flipped"] = not st.session_state["card_flipped"]
                st.rerun()

        previous_col, next_col = st.columns(2)

        with previous_col:
            if st.button("← Previous", disabled=st.session_state["card_index"] == 0):
                st.session_state["context_index"] = 0
                st.session_state["card_index"] -= 1
                st.session_state["card_flipped"] = False
                st.rerun()

        with next_col:
            if st.button("Next →", disabled=st.session_state["card_index"] == len(words) - 1):
                st.session_state["context_index"] = 0
                st.session_state["card_index"] += 1
                st.session_state["card_flipped"] = False
                st.rerun()

    with st.expander(f"Saved Vocabulary ({len(word_bank)})", expanded=st.session_state["vocab_expanded"]):
        with st.container(height=350, border=False):
            if not word_bank:
                st.write("No words saved yet!")
            else:
                for word, info in list(word_bank.items()):
                    with st.container(border=True):
                        text_col, remove_col = st.columns([5, 1])

                        with text_col:
                            reading = katakana_to_hiragana(info["reading"])
                            st.markdown(
                                f"""
                                <h3 style="color: #F9A8D4; margin-bottom: 12px;">
                                    {html.escape(word)}
                                    <span style="font-size: 16px; color: #AAAAAA;">
                                        （{html.escape(reading)}）
                                    </span>
                                </h3>
                                """,
                                unsafe_allow_html=True
                            )
                            for number, context in enumerate(info.get("contexts", []), start=1):
                                if len(info["contexts"]) > 1:
                                    st.write(f"Context {number}")

                                if context["image"] is not None:
                                    st.image(context["image"], width=250)

                                highlighted = highlight_word(context["sentence"], word)

                                st.markdown(
                                    highlighted,
                                    unsafe_allow_html=True
                                )

                        with remove_col:
                            if st.button("✕", key=f"remove_{word}"):
                                del st.session_state["word_bank"][word]
                                st.session_state["vocab_expanded"] = True
                                st.rerun()


if st.session_state["ocr_text"].strip():
    vocabulary = extract_vocabulary(st.session_state["ocr_text"])
    for entry in vocabulary:
        entry["meanings"] = get_definitions(entry["dictionary"], entry["reading"]) #get definitions for each word in the vocabulary, specifying with the reading form of the word

    st.subheader("Extracted Vocabulary")
    for entry in vocabulary:
        select, left, middle, right = st.columns([0.5, 2, 3, 4], gap="medium") #sets the proportions of the columns for the vocabulary display

        with select:
            word = entry["dictionary"]
            saved = word in st.session_state["word_bank"]

            if saved:
                contexts = st.session_state["word_bank"][word]["contexts"]
            else:
                contexts = []

            already_added = any(
                context.get("image_id") == image_id
                for context in contexts
            )

            if saved and already_added:
                st.button("✓", key=f"saved_{word}", disabled=True)

            else:
                if st.button("＋", key=f"add_{word}", disabled=image_id is None):
                    save_flashcard(
                        word,
                        entry["reading"],
                        entry["meanings"],
                        image_bytes,
                        st.session_state["ocr_text"],
                        entry["surface"]
                    )
                    new_context = {
                        "image_id": image_id,
                        "image": image_bytes,
                        "sentence": st.session_state["ocr_text"],
                        "surface": entry["surface"]
                    }

                    if saved:
                        st.session_state["word_bank"][word]["contexts"].append(new_context)
                    else:
                        st.session_state["word_bank"][word] = {
                            "reading": entry["reading"],
                            "meanings": entry["meanings"],
                            "contexts": [new_context]
                        }

                    st.rerun()

        with left:
            reading = html.escape(katakana_to_hiragana(entry["reading"]))
            word = html.escape(entry["dictionary"])

            st.markdown(
                f"""
                <div style="
                    background-color: rgba(244, 114, 182, 0.10);
                    border: 1px solid rgba(244, 114, 182, 0.25);
                    border-radius: 10px;
                    padding: 10px;
                    text-align: center;
                    color: #F9A8D4;
                ">
                    <div style="font-size: 14px;">
                        {reading}
                    </div>
                    <div style="font-size: 26px; font-weight: bold;
                                overflow-wrap: anywhere;">
                        {word}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with middle:
            st.caption(f'Original: {entry["surface"]}')

            meanings = entry["meanings"]

            for number, sense in enumerate(meanings[:3], start=1):
                st.write(f"{number}. {'; '.join(sense)}")

            if len(meanings) > 3:
                with st.expander(f"Show {len(meanings) - 3} more definitions"):
                    for number, sense in enumerate(meanings[3:], start=4):
                        st.write(f"{number}. {'; '.join(sense)}")

        with right:
            sentence = st.session_state["ocr_text"]
            highlighted = highlight_word(sentence, entry["surface"])

            st.markdown(
                f"""
                <div style="
                    background-color: rgba(244, 114, 182, 0.05);
                    border-radius: 8px;
                    padding: 12px;
                    margin-top: 8px;
                ">
                    <span style="color: #F9A8D4; font-size: 12px;">
                        EXAMPLE SENTENCE
                    </span>
                    <div style="font-size: 16px; margin-top: 5px;">
                        {highlighted}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.divider()

