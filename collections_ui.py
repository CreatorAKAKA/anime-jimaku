import streamlit as st
from database import create_group, create_set, load_groups

def apply_collections_css():
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

    /* Floating button position */
    .st-key-library_add_menu {
        position: fixed !important;
        bottom: 28px !important;
        right: 32px !important;
        width: 64px !important;
        z-index: 9999 !important;
    }

    /* Solid pink circular button */
    .st-key-library_add_menu [data-testid="stPopover"] button {
        position: relative !important;
        width: 60px !important;
        min-width: 60px !important;
        height: 60px !important;
        min-height: 60px !important;
        border-radius: 50% !important;
        background: #F9A8D4 !important;
        border: none !important;
        padding: 0 !important;
    }

    /* Hide Streamlit's original button contents */
    .st-key-library_add_menu [data-testid="stPopover"] button > * {
        visibility: hidden !important;
    }

    /* Draw a centered plus independently of Streamlit's layout */
    .st-key-library_add_menu [data-testid="stPopover"] button::after {
        content: "+";
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        visibility: visible !important;
        color: #171717;
        font-size: 38px;
        font-weight: 400;
        line-height: 1;
    }

    /* Change plus to minus when opened */
    .st-key-library_add_menu [data-testid="stPopover"] button[aria-expanded="true"]::after {
        content: "−";
    }

    /* Hover effect */
    .st-key-library_add_menu [data-testid="stPopover"] button:hover {
        background: #F472B6 !important;
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


def submit_new_set():
    title = st.session_state["new_set_title"].strip()
    group_id = st.session_state["new_set_group"]

    if title:
        create_set(group_id, title)

        group_name = next(
            group["name"]
            for group in load_groups()
            if group["id"] == group_id
        )

        st.session_state["new_set_title"] = ""
        st.session_state["set_added_message"] = (
            f"{title} added to {group_name}!"
        )

def show_collections():

    apply_collections_css()

    saved_groups = load_groups()

    with st.container(key="library_add_menu"):
        with st.popover("＋", help="Add a deck or set"):
            st.markdown("**Add to Library**")

            choice = st.radio(
                "Create",
                ["Add Set", "Add Deck"],
                horizontal=True,
                label_visibility="collapsed",
                key="library_add_choice"
            )

            if choice == "Add Deck":
                with st.form("new_group_form", clear_on_submit=True):
                    group_name = st.text_input(
                        "Deck name",
                        placeholder="e.g. アニメ"
                    )

                    if st.form_submit_button("Create Deck"):
                        if group_name.strip():
                            create_group(group_name)
                            st.session_state["deck_added_message"] = (
                                f"{group_name.strip()} added to library!"
                            )
                            st.rerun()
                if st.session_state.get("deck_added_message"):
                    st.markdown(
                        f'<span style="color:#F9A8D4;">'
                        f'{st.session_state["deck_added_message"]}'
                        f'</span>',
                        unsafe_allow_html=True
                    )

            elif saved_groups:
                with st.form("new_set_form", clear_on_submit=False):
                    st.text_input(
                        "Set title",
                        placeholder="e.g. 物語シリーズ",
                        key="new_set_title"
                    )

                    st.selectbox(
                        "Add to deck",
                        options=[group["id"] for group in saved_groups],
                        format_func=lambda group_id: next(
                            group["name"]
                            for group in saved_groups
                            if group["id"] == group_id
                        ),
                        key="new_set_group"
                    )

                    st.form_submit_button(
                        "Create Set",
                        on_click=submit_new_set
                    )

                if st.session_state.get("set_added_message"):
                    st.markdown(
                        f'<span style="color:#F9A8D4;">'
                        f'{st.session_state["set_added_message"]}'
                        f'</span>',
                        unsafe_allow_html=True
                    )

            else:
                st.info("Create a deck before adding sets.")


    if "collection_positions" not in st.session_state:
        st.session_state["collection_positions"] = {}

    left, right = st.columns(2, gap="large")

    for index, group in enumerate(saved_groups):
        group_name = group["name"]
        sets = group["sets"]
        column = left if index % 2 == 0 else right

        with column:
            st.markdown(f"### {group_name}")

            if not sets:
                st.info("No sets yet. Create one using ＋ New Set.")
                continue

            position = st.session_state["collection_positions"].get(
                group_name, 0
            ) % len(sets)

            current = sets[position]

            with st.container(key=f"collection_deck_{index}", border=True):
                st.markdown(f"#### {current['title']}")
                st.write("Cards: 0")
                st.caption("Progress tracking coming later")

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
