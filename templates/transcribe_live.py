#!/usr/bin/env python3
"""
Live transcription pipeline for workshops.

Monitors chunks/ directory for new .wav files, transcribes them with Whisper,
extracts keywords, and outputs a live "prompter" view.

Usage:
    python3 transcribe_live.py [--model small] [--lang pl] [--keywords-file keywords.json]

Models (speed vs quality tradeoff):
    tiny   - ~1s/chunk  (lowest quality, fast iteration)
    base   - ~2s/chunk  (ok for keywords)
    small  - ~5s/chunk  (good balance) <- default
    medium - ~15s/chunk (high quality)
    turbo  - ~8s/chunk  (best quality/speed ratio)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import whisper

SCRIPT_DIR = Path(__file__).parent
CHUNKS_DIR = SCRIPT_DIR / "chunks"
TRANSCRIPTS_DIR = SCRIPT_DIR / "transcripts"
LOG_FILE = SCRIPT_DIR / "live_log.jsonl"
SUMMARY_FILE = SCRIPT_DIR / "live_summary.md"
KEYWORDS_FILE = SCRIPT_DIR / "keywords.json"


def load_keywords() -> dict[str, list[str]]:
    """Load keyword categories from JSON file or use defaults."""
    if KEYWORDS_FILE.exists():
        with open(KEYWORDS_FILE, encoding="utf-8") as f:
            return json.load(f)

    # Default generic workshop keywords (English)
    return {
        "security": ["security", "threat", "attack", "exploit", "vulnerab", "malware", "phishing"],
        "encryption": ["encrypt", "decrypt", "aes", "rsa", "cipher", "key", "hash", "certificate"],
        "tools": ["tool", "install", "config", "setup", "framework", "library", "package"],
        "data": ["data", "file", "backup", "restore", "storage", "database", "archive"],
        "network": ["network", "vpn", "ssh", "protocol", "firewall", "dns", "proxy"],
    }


def find_keywords(text: str, keyword_map: dict) -> dict[str, list[str]]:
    """Find keywords in transcribed text."""
    text_lower = text.lower()
    found = {}
    for category, keywords in keyword_map.items():
        matches = [kw for kw in keywords if kw in text_lower]
        if matches:
            found[category] = matches
    return found


def update_summary(entries: list[dict], title: str = "Workshop"):
    """Write a running markdown summary of the session."""
    all_keywords: dict[str, set] = {}
    for entry in entries:
        for cat, kws in entry.get("keywords", {}).items():
            all_keywords.setdefault(cat, set()).update(kws)

    lines = [
        f"# Live Prompter - {title}",
        f"\n**Last update:** {datetime.now().strftime('%H:%M:%S')}",
        f"**Processed fragments:** {len(entries)}",
        "",
        "## Detected topics",
        "",
    ]

    for cat, kws in sorted(all_keywords.items()):
        lines.append(f"- **{cat}**: {', '.join(sorted(kws))}")

    lines.extend(["", "---", "", "## Recent transcriptions", ""])

    for entry in entries[-10:]:
        ts = entry.get("timestamp", "")
        text = entry.get("text", "").strip()
        kw_str = ""
        if entry.get("keywords"):
            kw_flat = [f"[{cat}]" for cat in entry["keywords"]]
            kw_str = " " + " ".join(kw_flat)
        if text:
            lines.append(f"**{ts}**{kw_str}")
            lines.append(f"> {text}")
            lines.append("")

    SUMMARY_FILE.write_text("\n".join(lines), encoding="utf-8")


def print_prompter(text: str, keywords: dict, timestamp: str):
    """Print formatted prompter output to terminal."""
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RED = "\033[91m"
    RESET = "\033[0m"
    DIM = "\033[2m"

    colors = [RED, YELLOW, GREEN, CYAN]

    print(f"\n{DIM}{'─' * 70}{RESET}")
    print(f"{BOLD}[{timestamp}]{RESET} ", end="")

    if keywords:
        tags = []
        for i, cat in enumerate(keywords):
            color = colors[i % len(colors)]
            tags.append(f"{color}#{cat}{RESET}")
        print(" ".join(tags))
    else:
        print()

    if text.strip():
        print(f"  {text.strip()}")
    else:
        print(f"  {DIM}(silence / unrecognized){RESET}")

    if keywords:
        print(f"\n  {BOLD}Keywords:{RESET} ", end="")
        all_kw = []
        for i, (cat, kws) in enumerate(keywords.items()):
            color = colors[i % len(colors)]
            all_kw.extend(f"{color}{kw}{RESET}" for kw in kws)
        print(", ".join(all_kw))


def main():
    parser = argparse.ArgumentParser(description="Live transcription + keyword prompter")
    parser.add_argument("--model", default="small", help="Whisper model")
    parser.add_argument("--lang", default="en", help="Language code")
    parser.add_argument("--chunks-dir", default=str(CHUNKS_DIR))
    parser.add_argument("--title", default="Workshop", help="Workshop title for summary")
    args = parser.parse_args()

    chunks_dir = Path(args.chunks_dir)
    TRANSCRIPTS_DIR.mkdir(exist_ok=True)

    keyword_map = load_keywords()

    print(f"\033[1m=== LIVE PROMPTER - {args.title} ===\033[0m")
    print(f"Model: {args.model} | Language: {args.lang}")
    print(f"Keywords: {len(keyword_map)} categories")
    print(f"Loading Whisper '{args.model}'...")

    model = whisper.load_model(args.model)
    print("Model loaded. Waiting for audio files...\n")

    processed: set[str] = set()
    entries: list[dict] = []

    try:
        while True:
            wav_files = sorted(chunks_dir.glob("*.wav"))
            for wav_file in wav_files:
                if wav_file.name in processed:
                    continue
                size1 = wav_file.stat().st_size
                time.sleep(0.5)
                try:
                    size2 = wav_file.stat().st_size
                except FileNotFoundError:
                    continue
                if size1 != size2 or size1 == 0:
                    continue

                timestamp = datetime.now().strftime("%H:%M:%S")
                try:
                    result = model.transcribe(str(wav_file), language=args.lang, fp16=False)
                    text = result.get("text", "").strip()
                except Exception as e:
                    print(f"  [ERROR] {e}")
                    processed.add(wav_file.name)
                    continue

                keywords = find_keywords(text, keyword_map)

                transcript_file = TRANSCRIPTS_DIR / f"{wav_file.stem}.txt"
                transcript_file.write_text(text, encoding="utf-8")

                entry = {
                    "timestamp": timestamp,
                    "file": wav_file.name,
                    "text": text,
                    "keywords": keywords,
                }
                entries.append(entry)

                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

                print_prompter(text, keywords, timestamp)
                update_summary(entries, args.title)
                processed.add(wav_file.name)

            time.sleep(2)

    except KeyboardInterrupt:
        print(f"\n\n\033[1mStopped. Processed {len(entries)} fragments.\033[0m")
        print(f"Log: {LOG_FILE}")
        print(f"Summary: {SUMMARY_FILE}")
        update_summary(entries, args.title)


if __name__ == "__main__":
    main()
