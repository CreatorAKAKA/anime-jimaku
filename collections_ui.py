import streamlit as st

st.markdown("""
<style>
/* Space for the cards stacked behind */
[class*="st-key-collection_deck_"] {
    position: relative;
    margin-bottom: 22px;
}

/* Back layers */
[class*="st-key-collection_deck_"]::before,
[class*="st-key-collection_deck_"]::after {
    content: "";
    position: absolute;
    border: 2px solid rgba(255, 255, 255, 0.65);
    border-radius: 12px;
    background: #171717;
    pointer-events: none;
}

[class*="st-key-collection_deck_"]::before {
    inset: 8px -8px -8px 8px;
    z-index: 0;
}

[class*="st-key-collection_deck_"]::after {
    inset: 15px -15px -15px 15px;
    z-index: -1;
}

[class*="st-key-collection_deck_"] > div {
    position: relative;
    z-index: 1;
}
</style>
""", unsafe_allow_html=True)

# Temporary sample data — we'll replace this with SQLite later.
SAMPLE_GROUPS = {
    "アニメ": [
        {"title": "物語–Monogatari", "cards": 23, "mastered": 10, "learning": 8, "new": 5},
        {"title": "葬送のフリーレン", "cards": 42, "mastered": 24, "learning": 12, "new": 6},
    ],
    "歌": [
        {"title": "優しい彗星", "cards": 10, "mastered": 5, "learning": 3, "new": 2},
    ],
    "漫画": [
        {"title": "会長はメイド様！", "cards": 72, "mastered": 35, "learning": 22, "new": 15},
    ],
    "好き": [
        {"title": "君の特別の", "cards": 7, "mastered": 7, "learning": 0, "new": 0},
    ],
}


def show_collections():
    st.subheader("My Collections")

    if "collection_positions" not in st.session_state:
        st.session_state["collection_positions"] = {}

    left, right = st.columns(2, gap="large")

    for index, (group_name, sets) in enumerate(SAMPLE_GROUPS.items()):
        column = left if index % 2 == 0 else right

        with column:
            st.markdown(f"### {group_name}")

            position = st.session_state["collection_positions"].get(
                group_name, 0
            ) % len(sets)

            current = sets[position]

            with st.container(key=f"collection_deck_{index}", border=True):
                st.markdown(f"#### {current['title']}")
                st.write(f"Cards: {current['cards']}")

                a, b, c = st.columns(3)
                a.markdown(f"🟢 完璧: {current['mastered']}")
                b.markdown(f"🟡 まだ: {current['learning']}")
                c.markdown(f"🔴 全然: {current['new']}")

                if st.button(
                    "Reveal next set",
                    key=f"next_set_{index}",
                    use_container_width=True,
                ):
                    st.session_state["collection_positions"][group_name] = (
                        position + 1
                    ) % len(sets)
                    st.rerun()

            st.caption(f"Sets: {len(sets)}")
