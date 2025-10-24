# Transdoc - ODT Translator

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
python transdoc.py -f input.odt [-s en] [-t id] [-o output.odt] [-r rules.txt]  [-e engine-translate]
```

# To enable translateion option with libretranslate:
```bash
pip install libretranslate
```
Run libretranslate service first, (for example only for translate in EN and ID)
```bash
libretranslate --load-only en,id
```
Rename berkas sample.env menjadi .env lalu tambahkan: 
`LIBRETRANSLATE_URL=http://127.0.0.1:5000/translate`

### Example
```bash
python transdoc.py -f report_en.odt -s en -t id

# If using Libretranslate
python transdoc.py -f laporan_en.odt -s en -t id -e libre
```
➡️ Output: `report_en-id.odt`

### Notes
- Uses `deep-translator`, not the official Google Cloud API.
- deep-Translatorh has limitation 5 request per second up to 200K per day
- It's recommended to use a `rules.txt` file to protect technical terms.
- It's recommended using libretranslate locally to get unlimited translation
- Still experimental
