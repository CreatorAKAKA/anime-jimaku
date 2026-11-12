import streamlit as st
from database import create_group, create_set, load_groups, delete_set, rename_set, move_set

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

    /* Hide set management menus by default */
    [class*="st-key-bookshelf_set_"] [data-testid="stPopover"] {
        opacity: 0;
        transition: opacity 0.2s ease;
        pointer-events: none;
    }

    /* Reveal menu when hovering over a set */
    [class*="st-key-bookshelf_set_"]:hover [data-testid="stPopover"],
    [class*="st-key-bookshelf_set_"]:focus-within [data-testid="stPopover"] {
        opacity: 1;
        pointer-events: auto;
    }

    /* Hide the bookshelf popover's dropdown arrow */
    [class*="st-key-bookshelf_set_"] [data-testid="stPopover"] button svg,
    [class*="st-key-bookshelf_set_"] [data-testid="stPopover"] button [data-testid="stIconMaterial"],
    [class*="st-key-bookshelf_set_"] [data-testid="stPopover"] button [data-testid="stIcon"] {
        display: none !important;
    }

    /* Compact, centered three-dot button */
    [class*="st-key-bookshelf_set_"] [data-testid="stPopover"] button {
        position: relative !important;
        min-width: 40px !important;
        width: 40px !important;
        height: 40px !important;
        min-height: 40px !important;
        padding: 0 !important;
        border-radius: 10px !important;
    }

    /* Hide original contents without removing their layout */
    [class*="st-key-bookshelf_set_"] [data-testid="stPopover"] button > * {
        visibility: hidden !important;
    }

    /* Draw dots at the exact center */
    [class*="st-key-bookshelf_set_"] [data-testid="stPopover"] button::after {
        content: "⋯";
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        visibility: visible !important;
        color: #F9A8D4;
        font-size: 26px;
        line-height: 1;
        pointer-events: none;
    }

    /* Move bookshelf management buttons closer to the right edge */
    [class*="st-key-bookshelf_set_"] [data-testid="stPopover"] {
        margin-left: auto !important;
        width: fit-content !important;
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

def show_collections():

    apply_collections_css()

    saved_groups = load_groups()

    if "open_deck" not in st.session_state:
        st.session_state["open_deck"] = None

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
                    with st.container(
                        key=f"bookshelf_set_{collection_set['id']}",
                        border=True
                    ):
                        title_col, menu_col = st.columns(
                            [12, 1],
                            vertical_alignment="center",
                            gap="small"
                        )

                        with title_col:
                            st.markdown(f"### {collection_set['title']}")

                        with menu_col:
                            with st.popover("⋯"):
                                st.write("Manage Set")
                                if st.button(
                                    "Rename",
                                    key=f"rename_{collection_set['id']}"
                                ):
                                    rename_set_dialog(
                                        collection_set["id"],
                                        collection_set["title"]
                                    )
                                if st.button(
                                    "Move",
                                    key=f"move_{collection_set['id']}"
                                ):
                                    move_set_dialog(
                                        collection_set["id"],
                                        collection_set["title"],
                                        deck["id"]
                                    )
                                if st.button(
                                    "Delete",
                                    key=f"delete_{collection_set['id']}"
                                ):
                                    confirm_delete_dialog(
                                        collection_set["id"],
                                        collection_set["title"]
                                    )

                        st.caption("Cards: 0")

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
