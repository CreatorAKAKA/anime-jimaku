import streamlit as st
from database import create_group, create_set, load_groups, delete_set, rename_set, move_set, add_word_to_set, load_set_words, load_saved_words

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


    /* Shared set card */
    [class*="st-key-set_card_"] {
        position: relative;
        background: rgba(255, 255, 255, 0.025);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        padding: 14px;
        transition: border-color 0.2s, background-color 0.2s;
    }

    [class*="st-key-set_card_"]:hover {
        border-color: rgba(249, 168, 212, 0.55);
        background: rgba(249, 168, 212, 0.035);
    }

    /* Main clickable area */
    [class*="st-key-card_open_"] button {
        width: 100% !important;
        min-height: 145px !important;
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 12px !important;
        border-radius: 10px !important;
    }

    [class*="st-key-card_open_"] button:hover {
        background: rgba(249, 168, 212, 0.06) !important;
    }

    /* Card title and content */
    [class*="st-key-card_open_"] button p {
        font-size: 17px !important;
        font-weight: 600 !important;
        line-height: 1.7 !important;
        white-space: pre-line !important;
    }

    /* Progress indicators */
    [class*="st-key-set_card_"] [data-testid="stCaptionContainer"] {
        color: #F9A8D4 !important;
        font-size: 12px !important;
    }


    /* Unified set card */
    [class*="st-key-set_card_"] {
        position: relative;
        border-radius: 14px !important;
        background: rgba(255, 255, 255, 0.025);
        transition: background 0.2s, border-color 0.2s;
    }

    [class*="st-key-set_card_"]:hover {
        border-color: rgba(249, 168, 212, 0.5) !important;
        background: rgba(249, 168, 212, 0.035);
    }

    /* Clickable card content */
    [class*="st-key-card_open_"] button {
        width: 100% !important;
        min-height: 110px !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        text-align: left !important;
        justify-content: flex-start !important;
        white-space: normal !important;
    }

    [class*="st-key-card_open_"] button:hover {
        background: rgba(249, 168, 212, 0.06) !important;
    }

    [class*="st-key-card_open_"] button p {
        font-size: 17px !important;
        font-weight: 600 !important;
    }

    /* Bookshelf set management menu */
    [class*="st-key-set_card_"] [data-testid="stPopover"] {
        position: relative;
    }

    /* Hide Streamlit's default arrow */
    [class*="st-key-set_card_"] [data-testid="stPopover"] button {
        position: relative;
        font-size: 0 !important;
        color: transparent !important;
        min-width: 30px !important;
        padding: 0 !important;
    }

    [class*="st-key-set_card_"] [data-testid="stPopover"] button svg {
        display: none !important;
    }

    /* Replace with pink dots */
    [class*="st-key-set_card_"] [data-testid="stPopover"] button::after {
        content: "⋯";
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 24px !important;
        color: #F9A8D4 !important;
        line-height: 1;
    }

    /* Only show the menu when hovering over a set */
    [class*="st-key-set_card_"] [data-testid="stPopover"] {
        opacity: 0;
        transition: opacity 0.15s ease;
    }

    [class*="st-key-set_card_"]:hover [data-testid="stPopover"],
    [class*="st-key-set_card_"] [data-testid="stPopover"]:focus-within {
        opacity: 1;
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

@st.dialog("Delete Set?")
def confirm_delete_dialog(set_id, set_title):
    st.warning(
        f'Are you sure you want to delete "{set_title}"? '
        "This action cannot be undone."
    )

    st.caption("Your saved vocabulary will not be deleted.")

    cancel_col, delete_col = st.columns(2)

    with cancel_col:
        if st.button("Cancel", use_container_width=True):
            st.rerun()

    with delete_col:
        if st.button(
            "Delete Set",
            type="primary",
            use_container_width=True
        ):
            delete_set(set_id)
            st.rerun()

@st.dialog("Rename Set")
def rename_set_dialog(set_id, current_title):
    new_title = st.text_input(
        "Set title",
        value=current_title,
        key=f"rename_input_{set_id}"
    )

    cancel_col, save_col = st.columns(2)

    with cancel_col:
        if st.button("Cancel", use_container_width=True):
            st.rerun()

    with save_col:
        if st.button(
            "Save Changes",
            type="primary",
            use_container_width=True
        ):
            if new_title.strip():
                rename_set(set_id, new_title.strip())
                st.rerun()
            else:
                st.error("Set title cannot be empty.")

@st.dialog("Move Set")
def move_set_dialog(set_id, set_title, current_group_id):
    groups = load_groups()

    destinations = [
        group for group in groups
        if group["id"] != current_group_id
    ]

    st.write(f"Moving **{set_title}**")

    if not destinations:
        st.info("Create another deck before moving this set.")
        return

    destination = st.selectbox(
        "Move to deck",
        options=destinations,
        format_func=lambda group: group["name"]
    )

    cancel_col, move_col = st.columns(2)

    with cancel_col:
        if st.button("Cancel", use_container_width=True):
            st.rerun()

    with move_col:
        if st.button(
            "Move Set",
            type="primary",
            use_container_width=True
        ):
            move_set(set_id, destination["id"])
            st.rerun()

@st.dialog("Add Vocabulary")
def add_vocabulary_dialog(set_id, set_title):
    st.write(f"Adding vocabulary to **{set_title}**")

    saved_words = load_saved_words()
    existing_words = {
        entry["word"] for entry in load_set_words(set_id)
    }

    available_words = [
        word for word in saved_words
        if word not in existing_words
    ]

    if not available_words:
        st.info("No additional saved vocabulary available.")
        if st.button("Close"):
            st.rerun()
        return

    selected_words = st.multiselect(
        "Select vocabulary",
        options=available_words,
        key=f"add_vocab_{set_id}"
    )

    cancel_col, add_col = st.columns(2)

    with cancel_col:
        if st.button("Cancel", use_container_width=True):
            st.rerun()

    with add_col:
        if st.button(
            "Add Words",
            type="primary",
            use_container_width=True,
            disabled=not selected_words
        ):
            for word in selected_words:
                add_word_to_set(word, set_id)

            st.rerun()



def render_set_card(collection_set, show_menu=False, deck_id=None):
    """Render a shared set card for Library and Bookshelf."""
    set_id = collection_set["id"]
    title = collection_set["title"]
    word_count = len(load_set_words(set_id))

    with st.container(
        key=f"set_card_{set_id}_{show_menu}",
        border=True
    ):
        content_col, menu_col = st.columns(
            [12, 1] if show_menu else [12, 0.01],
            vertical_alignment="top",
            gap="small"
        )

        with content_col:
            if st.button(
                f"▧   {title}  ·  Cards: {word_count}",
                key=f"card_open_{set_id}_{show_menu}",
                use_container_width=True
            ):
                st.session_state["open_set"] = set_id
                st.rerun()

        if show_menu:
            with menu_col:
                with st.popover("⋯"):
                    st.write("Manage Set")

                    if st.button("Rename", key=f"rename_{set_id}"):
                        rename_set_dialog(set_id, title)

                    if st.button("Move", key=f"move_{set_id}"):
                        move_set_dialog(set_id, title, deck_id)

                    if st.button("Delete", key=f"delete_{set_id}"):
                        confirm_delete_dialog(set_id, title)

        progress_cols = st.columns(3, gap="small")

        for col, label in zip(
            progress_cols,
            ["完璧", "まだ", "全然"]
        ):
            with col:
                st.caption(f"{label}: —")


def show_collections():

    apply_collections_css()

    saved_groups = load_groups()

    if "open_deck" not in st.session_state:
        st.session_state["open_deck"] = None

    if "open_set" not in st.session_state:
        st.session_state["open_set"] = None

    if st.session_state["open_deck"] is not None:
        deck = next(
            (
                group for group in saved_groups
                if group["id"] == st.session_state["open_deck"]
            ),
            None
        )

        if deck is None:
            st.session_state["open_deck"] = None
            st.rerun()

        if st.button("← Back to Library"):
            st.session_state["open_deck"] = None
            st.rerun()

        st.header(deck["name"])
        st.caption(f"{len(deck['sets'])} sets")

        if not deck["sets"]:
            st.info("This deck is empty.")
        else:
            columns = st.columns(3, gap="medium")

            for index, collection_set in enumerate(deck["sets"]):
                column = columns[index % 3]

                with column:
                    render_set_card(
                        collection_set,
                        show_menu=True,
                        deck_id=deck["id"]
                    )


        return

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

    columns = st.columns(3, gap="medium")

    for index, group in enumerate(saved_groups):
        group_name = group["name"]
        sets = group["sets"]
        column = columns[index % 3]

        with column:
            if st.button(
                group_name,
                key=f"open_deck_{group['id']}",
                type="tertiary"
            ):
                st.session_state["open_deck"] = group["id"]
                st.rerun()

            if not sets:
                st.info("No sets yet. Create one using ＋ New Set.")
                continue

            position = st.session_state["collection_positions"].get(
                group_name, 0
            ) % len(sets)

            current = sets[position]

            render_set_card(current)

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
