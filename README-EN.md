The **ODT Translator** script automatically translates **OpenDocument Text (.odt)** files using **Google Translate API (via `deep-translator`)** while preserving document structure.  
It keeps **text format, URLs, and file paths** intact and supports **custom rule files** to protect certain words from translation.

### Features
- Automatic `.odt` translation
- Document structure preservation
- Optional rule file support (`rules.txt`)
- Multithreaded translation for performance
- Interactive progress bar

### Installation
```bash
pip install -r requirements.txt
```

### Usage
```bash
python translate_odt.py -f input.odt [-s en] [-t id] [-o output.odt] [-r rules.txt]
```

### Example
```bash
python translate_odt.py -f report_en.odt -s en -t id
```
➡️ Output: `report_en-id.odt`

### Notes
- Uses `deep-translator`, not the official Google Cloud API.
- It's recommended to use a `rules.txt` file to protect technical terms.
- Still experimental

