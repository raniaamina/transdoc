# Transdoc - ODT Translator

Skrip **ODT Translator** ini menerjemahkan dokumen **OpenDocument Text (.odt)** secara otomatis menggunakan **Google Translate API (via `deep-translator`)**, tanpa merusak struktur dokumen asli.  
Didesain untuk menjaga **format teks, URL, dan path file**, serta mendukung **aturan perlindungan kata (rule file)** agar istilah tertentu tidak diterjemahkan.

### Fitur
- Terjemahan otomatis dokumen `.odt`
- Struktur dokumen tetap utuh
- Dukungan file aturan (`rules.txt`)
- Multithreading untuk performa tinggi
- Progress bar interaktif

### Instalasi
```bash
pip install -r requirements.txt
```

### Cara Pakai
```bash
python translate_odt.py -f input.odt [-s en] [-t id] [-o output.odt] [-r rules.txt]
```

### Contoh
```bash
python translate_odt.py -f laporan_en.odt -s en -t id
```
➡️ Hasil: `laporan_en-id.odt`

### Catatan
- Tidak menggunakan API resmi Google Cloud Translate.
- Disarankan membuat `rules.txt` agar istilah penting tidak berubah.
- Masih eksperimental

### To do
- Tambah opsi libretranslator