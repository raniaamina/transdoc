# transutils/deeptrans.py
from deep_translator import GoogleTranslator
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO)

def translate_chunks(chunks, source, target):
    """
    Translate list of text chunks concurrently using GoogleTranslator.
    """
    translated = [None] * len(chunks)

    def translate(i, text):
        try:
            translated[i] = GoogleTranslator(source=source, target=target).translate(text)
        except Exception as e:
            logging.warning(f"Failed to translate chunk {i}: {e}")
            translated[i] = text or ""

    with ThreadPoolExecutor() as executor:
        list(
            tqdm(
                executor.map(lambda args: translate(*args), enumerate(chunks)),
                total=len(chunks),
                desc=f"Translating ({source}->{target})"
            )
        )

    return translated
