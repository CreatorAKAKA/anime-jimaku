# ジマクイズ (JimaQuiz) 🌸

*Learn Japanese through the stories you love.*

JimaQuiz is a Python-based Japanese vocabulary learning app that transforms anime screenshots into interactive flashcards with readings, English definitions, and contextual examples.

Currently focused on anime subtitles, with plans to support manga, song lyrics, light novels, and more.

*「単語だけじゃなく、出会った瞬間も覚える。」*

*"Remember not just the word, but the moment you encountered it."*

## Features

- **Japanese Subtitle Recognition:** Upload anime screenshots and automatically extract Japanese subtitles using OCR.
- **Vocabulary Extraction:** Analyze recognized text using Japanese morphological analysis to identify individual vocabulary words.
- **Dictionary Integration:** Retrieve word readings and English definitions.
- **Interactive Flashcards:** Review saved vocabulary alongside the original screenshots and example sentences.
- **Multiple Contexts:** Associate the same vocabulary word with multiple screenshots and sentences.
- **Editable Subtitles:** Correct OCR results and update saved example sentences.
- **Persistent Storage:** Save vocabulary, screenshots, and contextual information locally using SQLite.
- **Batch Processing:** Upload multiple screenshots and extract vocabulary across them.

## Screenshots

<img width="1710" height="920" alt="image" src="https://github.com/user-attachments/assets/9d76b572-b882-497f-a759-c6a3b7cb5dfd" />

<img width="1710" height="898" alt="image" src="https://github.com/user-attachments/assets/3a85eac8-b97c-426a-a1bd-66148e425880" />

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Streamlit | Interactive web interface |
| EasyOCR | Japanese subtitle recognition |
| SudachiPy | Japanese morphological analysis |
| Jamdict | Japanese dictionary lookups |
| SQLite | Persistent vocabulary and screenshot storage |
| Pillow / NumPy | Image processing |

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/CreatorAKAKA/jimaquiz.git
cd jimaquiz
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run JimaQuiz

```bash
streamlit run app.py
```

The application will open in your browser. Initial setup may take longer while OCR and dictionary resources are initialized.

## How It Works

1. **Upload** one or more anime screenshots.
2. **Extract** Japanese subtitles using OCR.
3. **Correct** any recognition errors in the editable text field.
4. **Explore** the vocabulary identified in the subtitles.
5. **Save** interesting words along with their original screenshot contexts.
6. **Review** your flashcards and revisit the scenes where you encountered each word.

## Future Development

- Customizable vocabulary collections and folders
- Additional flashcard review and practice options
- Support for manga panels, song lyrics, and light novels
- Improved subtitle recognition and image preprocessing

## License

This project is licensed under the MIT License.
