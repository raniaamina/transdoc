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
python transdoc.py -f input.odt [-s en] [-t id] [-o output.odt] [-r rules.txt] [-e engine-translate]
```

# Jika ingin menggunakan Libretranslate, pasang juga
```bash
pip install libretranslate
```

Jalankan terlebih dahulu service libretranslate (misal hanya untuk en dan id)
```bash
libretranslate --load-only en,id
```
Rename berkas sample.env menjadi .env lalu tambahkan: 
`LIBRETRANSLATE_URL=http://127.0.0.1:5000/translate`

### Contoh
```bash
python transdoc.py -f laporan_en.odt -s en -t id

# Jika menggunakan Libretranslate
python transdoc.py -f laporan_en.odt -s en -t id -e libre
```
➡️ Hasil: `laporan_en-id.odt`

### Catatan
- Menggunakan `deep-translator`, Tidak menggunakan API resmi Google Cloud Translate.
- Deeptranslate memiliki limit penggunaan 5 Request per detik dengan maksimal reqest harian 200ribu
- Disarankan membuat `rules.txt` agar istilah penting tidak berubah.
- Untuk terjemahan tanpa batas pasaang Libretranslate di lokal
- Masih eksperimental
