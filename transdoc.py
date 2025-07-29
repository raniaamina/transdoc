import argparse
import os
import zipfile
import tempfile
import shutil
from lxml import etree as ET
from concurrent.futures import ThreadPoolExecutor
from deep_translator import GoogleTranslator
from tqdm import tqdm
import re
import logging

logging.basicConfig(level=logging.INFO)

TEXT_NS = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
ODT_BLOCK_TAGS = ['text:p', 'text:h', 'text:list-item']

URL_PATTERN = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)
FILE_PATH_PATTERN = re.compile(
    r"([A-Z]:\\(?:[^\\\s]+\\)*[^\\\s]+|/(?:[^/\s]+/)*[^/\s]+)",
    re.IGNORECASE
)

RULE_RESTORE_PATTERN = re.compile(r"\[<\|(.*?)\|>]", re.DOTALL)

# Placeholder map for temporary replacement
placeholder_map = {}
placeholder_counter = [1]  # list agar bisa diubah dalam nested function

# Manual post-fix replacements (at end of process)
MANUAL_REPLACEMENTS = [
    (r"\s+\\\s+", r"\\"),
    (r" \.", "."),
    (r"\.\s+/", "./"),
]


def obfuscate_rule(text):
    return f"[<|{'␞'.join(text)}|>]"

def unobfuscate_rules(text):
    def restore(m):
        return m.group(1).replace("␞", "")
    return RULE_RESTORE_PATTERN.sub(restore, text)

def replace_paths_with_placeholders(text):
    local_map = {}
    def replacer(match):
        key = f"~#{placeholder_counter[0]}"
        local_map[key] = match.group(0)
        placeholder_counter[0] += 1
        return key

    text = URL_PATTERN.sub(replacer, text)
    text = FILE_PATH_PATTERN.sub(replacer, text)
    return text, local_map

def restore_placeholders(text, local_map):
    if not isinstance(text, str):
        return ""
    for key, value in local_map.items():
        text = text.replace(key, value)
    return text

def mark_rules(text, rules):
    def replacement(match):
        return obfuscate_rule(match.group(0))
    for rule in rules:
        if not rule.strip():
            continue
        pattern = re.compile(fr"(?<!\w){re.escape(rule)}(?!\w)")
        text = pattern.sub(replacement, text)
    return text

def translate_chunks(chunks, source, target):
    translated = [None] * len(chunks)
    def translate(i, text):
        try:
            translated[i] = GoogleTranslator(source=source, target=target).translate(text)
        except Exception as e:
            logging.warning(f"Failed to translate chunk {i}: {e}")
            translated[i] = text or ""

    with ThreadPoolExecutor() as executor:
        list(tqdm(executor.map(lambda args: translate(*args), enumerate(chunks)), total=len(chunks), desc="Translating"))
    return translated

def collect_translatable_texts(elem, rules, items):
    if elem.text and elem.text.strip():
        raw = elem.text
        protected_text, local_map = replace_paths_with_placeholders(raw)
        marked = mark_rules(protected_text, rules)
        leading = re.match(r"^\s+", raw)
        trailing = re.search(r"\s+$", raw)
        items.append((elem, 'text', leading, trailing, marked, local_map))

    for child in elem:
        collect_translatable_texts(child, rules, items)

    if elem.tail and elem.tail.strip():
        raw = elem.tail
        protected_text, local_map = replace_paths_with_placeholders(raw)
        marked = mark_rules(protected_text, rules)
        leading = re.match(r"^\s+", raw)
        trailing = re.search(r"\s+$", raw)
        items.append((elem, 'tail', leading, trailing, marked, local_map))

def translate_block_elements(tree, source, target, rules):
    root = tree.getroot()
    text_items = []

    for tag in ODT_BLOCK_TAGS:
        prefix, local = tag.split(':')
        ns_uri = root.nsmap[prefix]
        for elem in root.findall(f'.//{{{ns_uri}}}{local}'):
            collect_translatable_texts(elem, rules, text_items)

    texts_to_translate = [item[4] for item in text_items]
    translated = translate_chunks(texts_to_translate, source, target)

    for (elem, kind, leading, trailing, _, local_map), trans in zip(text_items, translated):
        text = restore_placeholders(trans, local_map)
        text = unobfuscate_rules(text)
        if not isinstance(text, str):
            text = ""
        result = (leading.group(0) if leading else '') + text + (trailing.group(0) if trailing else '')
        for pattern, repl in MANUAL_REPLACEMENTS:
            result = re.sub(pattern, repl, result)
        if kind == 'text':
            elem.text = result
        else:
            elem.tail = result

def extract_odt(odt_file, extract_dir):
    with zipfile.ZipFile(odt_file, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

def compress_odt(source_dir, output_odt):
    with zipfile.ZipFile(output_odt, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(source_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, source_dir)
                zipf.write(full_path, rel_path)

def translate_content_xml(content_path, source, target, rules):
    parser = ET.XMLParser(remove_blank_text=False)
    tree = ET.parse(content_path, parser)
    translate_block_elements(tree, source, target, rules)
    with open(content_path, 'w', encoding='utf-8') as f:
        content = ET.tostring(tree.getroot(), encoding='unicode', pretty_print=True)
        content = unobfuscate_rules(content)
        f.write(content)

def main():
    parser = argparse.ArgumentParser(description="Translate ODT documents.")
    parser.add_argument('-s', '--source', default='en', help='Source language (default: EN)')
    parser.add_argument('-t', '--target', default='id', help='Target language (default: ID)')
    parser.add_argument('-f', '--file', required=True, help='Input file (ODT format)')
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('-r', '--rules', help='Path to the rule file (optional)')

    args = parser.parse_args()

    odt_file = args.file
    base_name = os.path.splitext(os.path.basename(odt_file))[0]
    output_file = args.output or os.path.splitext(odt_file)[0] + f'-{args.target.lower()}.odt'
    temp_dir = os.path.join(os.path.dirname(odt_file), f"{base_name}_tmp")

    rules = []
    if args.rules and os.path.exists(args.rules):
        with open(args.rules, encoding='utf-8') as f:
            rules = [line.strip() for line in f if line.strip()]

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    extract_odt(odt_file, temp_dir)
    content_path = os.path.join(temp_dir, 'content.xml')
    translate_content_xml(content_path, args.source, args.target, rules)
    compress_odt(temp_dir, output_file)
    shutil.rmtree(temp_dir)

    print(f"✅ Translation complete: {output_file}")

if __name__ == '__main__':
    main()
