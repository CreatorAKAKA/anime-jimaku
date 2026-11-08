import easyocr
import streamlit as st
from PIL import Image
from PIL import ImageEnhance #makes subtitles easier to read by enhancing contrast
import numpy as np
import hashlib #gives images unique fingerprints based on their content, so that the same image will always have the same name
from token_test import extract_vocabulary #extracts vocabulary from Japanese text using SudachiPy
from dictionary_test import get_definitions #fetches definitions for Japanese words using Jamdict

@st.cache_resource
def load_reader():
    return easyocr.Reader(["ja"], gpu=False) #initialize the reader with Japanese language recognition, use cpu

reader = load_reader()

if "ocr_text" not in st.session_state: # Initialize the session state variable for storing OCR text
    st.session_state["ocr_text"] = ""

if "previous_image_id" not in st.session_state:
    st.session_state["previous_image_id"] = None

st.title("アニメ字幕クイズ")
st.write("Learn Japanese through anime screenshots!")

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

    if st.button("Extract Japanese Text"):
        with st.spinner("Recognizing subtitles..."):
            grayscale = subtitle_region.convert("L")# Convert to grayscale for easier text recognition
            enhancer = ImageEnhance.Contrast(grayscale)
            processed = enhancer.enhance(2.0) 

            results = reader.readtext(
                np.array(processed),
                detail=0
            )
        st.session_state["ocr_text"] = "".join(results)
    st.text_area(
        "Edit recognized Japanese text",
        key = "ocr_text",
        height = 150
    )
    if st.session_state["ocr_text"].strip():
        vocabulary = extract_vocabulary(st.session_state["ocr_text"])
        for entry in vocabulary:
            entry["meanings"] = get_definitions(entry["dictionary"], entry["reading"]) #get definitions for each word in the vocabulary, specifying with the reading form of the word

        st.subheader("Extracted Vocabulary")
        st.dataframe(vocabulary, hide_index=True)