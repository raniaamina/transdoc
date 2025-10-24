import os
import re
import requests
import logging
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

LIBRE_URL = os.getenv("LIBRETRANSLATE_URL", "https://libretranslate.com/translate")

# regex untuk placeholder seperti [<|URL1|>] atau [<| PATH | >]
PLACEHOLDER_PATTERN = re.compile(r"\[\s*<\s*\|\s*(.*?)\s*\|\s*>\s*\]")

def normalize_placeholders(text: str) -> str:
    """
    Pastikan placeholder [<|...|>] tetap utuh seperti format aslinya.
    LibreTranslate kadang menambah spasi atau mengubah tanda.
    """
    def repl(m):
        inner = m.group(1).strip()
        return f"[<|{inner}|>]"
    return PLACEHOLDER_PATTERN.sub(repl, text)


def translate_text(text, source, target):
    try:
        payload = {
            "q": text,
            "source": source or "auto",
            "target": target,
            "format": "text",
            "alternatives": 1,
            "api_key": ""
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(LIBRE_URL, json=payload, headers=headers, timeout=40)

        if response.status_code == 200:
            data = response.json()
            translated = data.get("translatedText", text)
            # normalisasi placeholder agar bisa direstore di transdoc.py
            return normalize_placeholders(translated)
        else:
            logging.warning(f"LibreTranslate HTTP {response.status_code}: {response.text}")
            return text
    except Exception as e:
        logging.warning(f"LibreTranslate error: {e}")
        return text


def translate_chunks(chunks, source, target):
    translated = [None] * len(chunks)

    def translate(i, text):
        translated[i] = translate_text(text, source, target)

    with ThreadPoolExecutor(max_workers=5) as executor:
        list(
            tqdm(
                executor.map(lambda args: translate(*args), enumerate(chunks)),
                total=len(chunks),
                desc=f"Translating ({source}->{target}) via LibreTranslate"
            )
        )

    return translated
