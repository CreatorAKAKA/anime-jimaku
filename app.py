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
import io
from token_test import extract_vocabulary #extracts vocabulary from Japanese text using SudachiPy
from dictionary_test import get_definitions #fetches definitions for Japanese words using Jamdict
import html
from database import init_db, save_flashcard, load_flashcards, update_context_sentences, delete_word, delete_context
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

    for info in st.session_state["word_bank"].values():
        for context in info.get("contexts", []):
            if context.get("image_id") == current_image_id:
                update_context_sentences(context["image"], corrected_text)
                return

title_col, nav_col = st.columns([2, 3], vertical_alignment="center")

with title_col:
    st.title("ジマクイズ 🌸")
    st.caption("Learn Japanese through the stories you love.")

with nav_col:
    mode = st.segmented_control(
        "Navigation",
        ["Create", "Review", "Collections"],
        default="Create",
        key="navigation",
        label_visibility="collapsed",
        width="stretch"
    )


image_bytes = None

init_db()

if "word_bank" not in st.session_state:
    st.session_state["word_bank"] = load_flashcards()

if "vocab_expanded" not in st.session_state:
    st.session_state["vocab_expanded"] = False

if "screenshots" not in st.session_state:
    st.session_state["screenshots"] = {}

if "screenshot_index" not in st.session_state:
    st.session_state["screenshot_index"] = 0

if mode == "Create":
    image_col = st.container()
    with image_col:
        st.subheader("Screenshot & OCR")

        screenshots = st.file_uploader(
            "Upload anime screenshots",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True
        )
        image_ids = []

        if screenshots:

            for screenshot in screenshots:
                image_bytes = screenshot.getvalue()
                image_id = hashlib.sha256(image_bytes).hexdigest()

                image_ids.append(image_id)

                if image_id not in st.session_state["screenshots"]:
                    st.session_state["screenshots"][image_id] = {
                        "image": image_bytes,
                        "ocr_text": None
                    }

                data = st.session_state["screenshots"][image_id]

                if data["ocr_text"] is None:
                    image = Image.open(io.BytesIO(image_bytes))
                    width, height = image.size

                    subtitle_region = image.crop((
                        0,
                        int(height * 0.7),
                        width,
                        height
                    ))

                    with st.spinner(f"Recognizing {screenshot.name}..."):
                        grayscale = subtitle_region.convert("L")
                        enhancer = ImageEnhance.Contrast(grayscale)
                        processed = enhancer.enhance(2.0)

                        results = reader.readtext(
                            np.array(processed),
                            detail=0
                        )

                    data["ocr_text"] = "".join(results)

            st.session_state["screenshot_index"] = min(
                st.session_state["screenshot_index"],
                len(image_ids) - 1
            )

            active_id = image_ids[st.session_state["screenshot_index"]]
            active_data = st.session_state["screenshots"][active_id]

            image_bytes = active_data["image"]
            image_id = active_id
            image = Image.open(io.BytesIO(image_bytes))

            st.caption(
                f"Screenshot {st.session_state['screenshot_index'] + 1} of {len(image_ids)}"
            )

            previous_col, next_col = st.columns(2)

            with previous_col:
                if st.button("← Previous Screenshot",
                            disabled=st.session_state["screenshot_index"] == 0):
                    st.session_state["screenshot_index"] -= 1
                    st.rerun()

            with next_col:
                if st.button("Next Screenshot →",
                            disabled=st.session_state["screenshot_index"] == len(image_ids) - 1):
                    st.session_state["screenshot_index"] += 1
                    st.rerun()

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

            if active_data["ocr_text"] is None:
                with st.spinner("Recognizing subtitles..."):
                    grayscale = subtitle_region.convert("L")# Convert to grayscale for easier text recognition
                    enhancer = ImageEnhance.Contrast(grayscale)
                    processed = enhancer.enhance(2.0) 

                    results = reader.readtext(
                        np.array(processed),
                        detail=0
                    )
                active_data["ocr_text"] = "".join(results)
            edited_text = st.text_area(
                "Edit recognized Japanese text",
                value=active_data["ocr_text"],
                key=f"ocr_text_{image_id}",
                height=150
            )

            if edited_text != active_data["ocr_text"]:
                active_data["ocr_text"] = edited_text
                update_context_sentences(image_bytes, edited_text)
                st.session_state["word_bank"] = load_flashcards()

            current_words = {
                entry["dictionary"]
                for entry in extract_vocabulary(active_data["ocr_text"])
            }

            for word, word_data in st.session_state["word_bank"].items():
                has_context = any(
                    context["image_id"] == image_id
                    for context in word_data["contexts"]
                )

                if has_context and word not in current_words:
                    st.warning(
                        f"⚠️ {word} no longer appears in this screenshot's text. "
                        "Its saved context may need to be removed."
                    )

                    if st.button(
                        f"Remove {word} context",
                        key=f"remove_context_{word}_{image_id}"
                    ):
                        delete_context(word, image_id)
                        st.session_state["word_bank"] = load_flashcards()
                        st.rerun()

    

    vocabulary = []

    for image_id in image_ids:
        data = st.session_state["screenshots"][image_id]
        text = data["ocr_text"]

        if not text or not text.strip():
            continue

        entries = extract_vocabulary(text)

        for entry in entries:
            entry["meanings"] = get_definitions(
                entry["dictionary"],
                entry["reading"]
            )

            entry["image_id"] = image_id
            entry["image"] = data["image"]
            entry["sentence"] = text

            vocabulary.append(entry)

    grouped_vocabulary = {}

    for entry in vocabulary:
        word = entry["dictionary"]

        if word not in grouped_vocabulary:
            grouped_vocabulary[word] = {
                "reading": entry["reading"],
                "meanings": entry["meanings"],
                "contexts": []
            }

        grouped_vocabulary[word]["contexts"].append(entry)

    st.subheader("Extracted Vocabulary")

    for word, group in sorted(grouped_vocabulary.items(), key=lambda item: len(item[1]["contexts"]), reverse=True): #makes the most frequent word appear on top
        contexts = group["contexts"]
        entry = contexts[0]
        
        select, left, middle, right = st.columns([0.5, 2, 3, 4], gap="medium") #sets the proportions of the columns for the vocabulary display

        
        with select:
            saved_contexts = st.session_state["word_bank"].get(
                word, {}
            ).get("contexts", [])

            saved_image_ids = {
                context["image_id"] for context in saved_contexts
            }

            unsaved_contexts = [
                context for context in contexts
                if context["image_id"] not in saved_image_ids
            ]

            if not unsaved_contexts:
                st.button("✓", key=f"saved_{word}", disabled=True)

            else:
                if st.button("＋", key=f"add_{word}"):
                    for context in unsaved_contexts:
                        save_flashcard(
                            word,
                            group["reading"],
                            group["meanings"],
                            context["image"],
                            context["sentence"],
                            context["surface"]
                        )

                    st.session_state["word_bank"] = load_flashcards()
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
            original_forms = list(dict.fromkeys(
                context["surface"] for context in contexts
            ))

            st.caption(f"Appeared as: {', '.join(original_forms)}")

            meanings = entry["meanings"]

            for number, sense in enumerate(meanings[:3], start=1):
                st.write(f"{number}. {'; '.join(sense)}")

            if len(meanings) > 3:
                with st.expander(f"Show {len(meanings) - 3} more definitions"):
                    for number, sense in enumerate(meanings[3:], start=4):
                        st.write(f"{number}. {'; '.join(sense)}")

        with right:
            first_context = contexts[0]

            highlighted = highlight_word(
                first_context["sentence"],
                first_context["surface"]
            )

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

            if len(contexts) > 1:
                with st.expander(f"Show {len(contexts) - 1} more examples"):
                    for index, context in enumerate(contexts[1:], start=2):
                        st.caption(f"Screenshot {index}")

                        highlighted = highlight_word(
                            context["sentence"],
                            context["surface"]
                        )

                        st.markdown(highlighted, unsafe_allow_html=True)

                        if index < len(contexts):
                            st.divider()

        st.divider()

elif mode == "Review":
    st.subheader("Flashcards")
    word_bank = st.session_state["word_bank"]
    
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

        first_col, previous_col, next_col, last_col = st.columns(4)

        with first_col:
            if st.button("⏮ First", disabled=st.session_state["card_index"] == 0):
                st.session_state["context_index"] = 0
                st.session_state["card_index"] = 0 
                st.session_state["card_flipped"] = False
                st.rerun()

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

        with last_col:
            if st.button("Last ⏭", disabled=st.session_state["card_index"] == len(words) - 1):
                st.session_state["context_index"] = 0
                st.session_state["card_index"] = len(words) - 1
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
                                delete_word(word)
                                del st.session_state["word_bank"][word]
                                st.session_state["vocab_expanded"] = True
                                st.rerun()
    

elif mode == "Collections":
    st.subheader("My Collections")