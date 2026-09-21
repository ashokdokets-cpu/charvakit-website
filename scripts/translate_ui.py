#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Translate static/locales/en.json into a target language via OpenAI.

Usage:
    python scripts/translate_ui.py --lang hi
    python scripts/translate_ui.py --lang te
    python scripts/translate_ui.py --all

Output: static/locales/{lang}.json

Preserves:
- JSON keys and structure
- Emojis
- Brand names (Charvak, Dokets, VouchAI, Razorpay, PayPal, etc.)
- Numbers, currency symbols, technical units
"""
import argparse
import json
import os
import sys
from datetime import datetime

# Make repo root importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import requests


SUPPORTED = ['hi','te','ta','kn','ml','mr','bn','gu','pa',
             'es','fr','de','pt','it','nl','ru','ar','zh','ja',
             'ko','tr','vi','th','id','ms','fil','sw','am','ha',
             'yo','ig','zu','so']

LANG_NAMES = {
    'hi':  'Hindi (Devanagari script)',
    'te':  'Telugu (Telugu script)',
    'ta':  'Tamil (Tamil script)',
    'kn':  'Kannada (Kannada script)',
    'ml':  'Malayalam (Malayalam script)',
    'mr':  'Marathi (Devanagari script)',
    'bn':  'Bengali (Bengali script)',
    'gu':  'Gujarati (Gujarati script)',
    'pa':  'Punjabi (Gurmukhi script)',
    'es':  'Spanish',
    'fr':  'French',
    'de':  'German',
    'pt':  'Portuguese',
    'it':  'Italian',
    'nl':  'Dutch',
    'ru':  'Russian (Cyrillic script)',
    'ar':  'Arabic (Arabic script)',
    'zh':  'Mandarin Chinese (Simplified)',
    'ja':  'Japanese (mixed scripts)',
    'ko':  'Korean (Hangul)',
    'tr':  'Turkish',
    'vi':  'Vietnamese',
    'th':  'Thai (Thai script)',
    'id':  'Indonesian',
    'ms':  'Malay',
    'fil': 'Filipino',
    'sw':  'Swahili',
    'am':  'Amharic (Ethiopic script)',
    'ha':  'Hausa',
    'yo':  'Yoruba',
    'ig':  'Igbo',
    'zu':  'Zulu',
    'so':  'Somali',
}


PROMPT_TEMPLATE = """Translate the VALUES of the following JSON object from English to {lang_name}.

STRICT RULES:
1. Preserve all JSON keys exactly as-is (they are in English).
2. Preserve the JSON structure (nested objects).
3. Preserve emoji exactly (do not translate or remove).
4. Do NOT translate these proper nouns / brand names:
   Charvak, Dokets, VouchAI, DoketsRB, Razorpay, PayPal, AuditBot, Skill-Twin,
   Micro-Squads, Globalize, Agency-Twin, Geo-Compliance, Design-Token,
   Legacy-Shift, Agent-Ready, Silent-Killer, AI-Slop, Developer Entropy,
   Team Entropy, TCS, Infosys, Wipro, GDPR, CCPA, SSL, LMS, ATS, MCQ, CEFR,
   C, C++, Java, Python, React, DevOps, AI, Blockchain, AWS, GATE, CAT, NEET,
   JEE, SSC, IBPS, RRB, UPSC, CUET, AFCAT, PMP, CFA.
5. Preserve numbers, currency symbols (Rs., Rupee), and technical units (MB, GB, ms).
6. Translate naturally - this is UI text, not literal word-for-word.
7. Keep translations concise - these are buttons, labels, and headings.
8. Return ONLY valid JSON. No markdown fences. No explanation.

Input JSON:
{source_json}
"""


def translate_language(lang, api_key, source):
    """Translate source dict into target lang. Returns translated dict or raises."""
    if lang == 'en':
        return source  # nothing to do

    if lang not in LANG_NAMES:
        raise ValueError(f'No language name mapping for: {lang}')

    lang_name = LANG_NAMES[lang]
    prompt = PROMPT_TEMPLATE.format(
        lang_name=lang_name,
        source_json=json.dumps(source, ensure_ascii=False, indent=2),
    )

    print(f'  Calling OpenAI for {lang} ({lang_name})...')
    print(f'  Prompt size: {len(prompt)} chars')

    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers={'Authorization': f'Bearer {api_key}'},
        json={
            'model': 'gpt-4o-mini',
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0.2,
            'response_format': {'type': 'json_object'},
        },
        timeout=180,
    )
    data = response.json()

    if 'error' in data:
        raise RuntimeError(f'OpenAI error: {data["error"]}')

    content = (data.get('choices', [{}])[0].get('message', {}).get('content') or '').strip()

    if not content:
        raise RuntimeError('Empty response from OpenAI')

    # Strip markdown fences if present (defensive)
    if content.startswith('```'):
        content = content.split('```', 2)[1]
        if content.startswith('json'):
            content = content[4:]
        content = content.strip()

    try:
        translated = json.loads(content)
    except json.JSONDecodeError as e:
        print(f'  JSON parse error: {e}')
        print(f'  First 500 chars: {content[:500]}')
        raise

    # Replace _meta with our own (do not translate)
    translated['_meta'] = {
        'lang': lang,
        'version': '1.0',
        'updated': datetime.now().strftime('%Y-%m-%d'),
        'source': 'translated from en.json',
    }

    return translated


def write_lang(lang, translated):
    out_path = f'static/locales/{lang}.json'
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(translated, f, ensure_ascii=False, indent=2)

    # Quick structural check
    def count_leaf(o):
        n = 0
        if isinstance(o, dict):
            for k, v in o.items():
                if k.startswith('_'):
                    continue
                if isinstance(v, dict):
                    n += count_leaf(v)
                else:
                    n += 1
        return n

    print(f'  Wrote {out_path} ({count_leaf(translated)} leaf strings)')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lang', help='Language code (e.g. hi, te, ta)')
    ap.add_argument('--all', action='store_true', help='Translate all non-en languages')
    ap.add_argument('--langs', help='Comma-separated list of language codes')
    args = ap.parse_args()

    if not args.lang and not args.all and not args.langs:
        print('Specify --lang, --langs, or --all')
        sys.exit(1)

    api_key = os.getenv('OPENAI_API_KEY', '')
    if not api_key:
        print('OPENAI_API_KEY missing from environment')
        sys.exit(1)

    with open('static/locales/en.json', 'r', encoding='utf-8') as f:
        source = json.load(f)

    # Determine target list
    if args.all:
        targets = [l for l in SUPPORTED if l != 'en']
    elif args.langs:
        targets = [l.strip() for l in args.langs.split(',') if l.strip()]
    else:
        targets = [args.lang]

    # Validate
    for t in targets:
        if t not in SUPPORTED:
            print(f'Unsupported language code: {t}')
            sys.exit(1)

    print(f'Translating {len(targets)} language(s): {", ".join(targets)}')
    print(f'Source: en.json ({len(json.dumps(source))} chars)')
    print()

    succeeded = []
    failed = []

    for lang in targets:
        print(f'[{targets.index(lang) + 1}/{len(targets)}] {lang}')
        try:
            translated = translate_language(lang, api_key, source)
            write_lang(lang, translated)
            succeeded.append(lang)
        except Exception as e:
            print(f'  FAILED: {e}')
            failed.append((lang, str(e)))
        print()

    print(f'Done. Succeeded: {len(succeeded)}, Failed: {len(failed)}')
    if failed:
        for lang, err in failed:
            print(f'  {lang}: {err}')


if __name__ == '__main__':
    main()