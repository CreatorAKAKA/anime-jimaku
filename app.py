import streamlit as st

st.title("アニメ字幕クイズ")
st.write("Learn Japanese through anime screenshots!")

screenshot = st.file_uploader(
    "Upload an anime screenshot",
    type=["png", "jpg", "jpeg"]
)

if screenshot is not None:
    st.image(screenshot)
    st.success("Screenshot uploaded successfully!")