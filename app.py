import streamlit as st
from PIL import Image

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