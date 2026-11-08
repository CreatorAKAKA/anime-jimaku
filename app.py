import easyocr
import streamlit as st
from PIL import Image
from PIL import ImageEnhance #makes subtitles easier to read by enhancing contrast
import numpy as np

@st.cache_resource
def load_reader():
    return easyocr.Reader(["ja"], gpu=False) #initialize the reader with Japanese language recognition, use cpu

reader = load_reader()



st.title("アニメ字幕クイズ")
st.write("Learn Japanese through anime screenshots!")

screenshot = st.file_uploader(
    "Upload an anime screenshot",
    type=["png", "jpg", "jpeg"]
)

if screenshot is not None:
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

        st.subheader("Recognized Text")
        st.write("\n".join(results))