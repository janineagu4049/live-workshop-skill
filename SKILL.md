---
name: live-workshop
description: Set up a JupyterBook-based workshop journal with live audio transcription, keyword extraction, and structured knowledge base. Use when attending lectures, workshops, or meetings that need real-time note-taking and organized output.
argument-hint: <workshop-title> [--lang en|pl|de|...] [--modules "Module1,Module2,Module3"]
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch, Agent
---

# Live Workshop - Journal & Knowledge Base Generator

You are a workshop assistant that sets up and maintains a structured JupyterBook
knowledge base with live audio transcription capabilities.

## Arguments

Parse `$ARGUMENTS` for:
- **title** (required): Workshop/meeting title
- **--lang**: Language for Whisper transcription (default: `en`)
- **--modules**: Comma-separated list of module names (default: auto-detect or ask user)
- **--url**: Workshop website URL to fetch agenda from
- **--chunk-duration**: Audio chunk duration in seconds (default: 30)
- **--whisper-model**: Whisper model to use (default: `small`)

## Phase 1: Project Initialization

### 1.1 Create JupyterBook structure

```
<project-dir>/
├── _config.yml                # JupyterBook config (title, author, language)
├── _toc.yml                   # Table of contents (updated on every note)
├── intro.md                   # Landing page with workshop overview
├── .gitignore                 # Exclude _build/, chunks/, *.wav, etc.
├── requirements.txt           # jupyter-book>=1.0
│
├── journal/                   # Meeting journals (one per date)
│   └── YYYY-MM-DD.md          # Auto-created for today
│
├── modules/                   # Thematic modules
│   ├── 01_<module>/
│   │   ├── theory.md          # Theory/concepts
│   │   ├── tools.md           # Tools & software
│   │   └── exercises.md       # Exercises
│   └── ...
│
├── exercises/
│   └── index.md               # Exercise index
│
└── live_audio/                # Audio pipeline
    ├── start.sh               # Launcher (both recorder + transcriber)
    ├── record_chunks.sh       # sox-based chunked recorder
    ├── transcribe_live.py     # Whisper transcriber + keyword extractor
    ├── chunks/                # Raw .wav files (gitignored)
    ├── transcripts/           # Text transcripts (gitignored)
    ├── live_log.jsonl          # Structured log (gitignored)
    └── live_summary.md        # Running summary (gitignored)
```

### 1.2 _config.yml template

```yaml
title: "<workshop-title>"
author: "<detect from git config or ask>"
copyright: "<current year>"
logo: ""

execute:
  execute_notebooks: "off"

html:
  use_issues_button: false
  use_repository_button: false
  use_edit_page_button: false
  home_page_in_navbar: true

sphinx:
  config:
    language: <lang>
    html_theme_options:
      navigation_depth: 3
```

### 1.3 Initialize git repository

- `git init` if not already a repo
- Create `.gitignore` with: `_build/`, `.DS_Store`, `__pycache__/`, `*.pyc`,
  `.ipynb_checkpoints/`, `live_audio/chunks/`, `live_audio/transcripts/`,
  `live_audio/live_log.jsonl`, `live_audio/live_summary.md`, `*.wav`
- Initial commit with full structure

### 1.4 If --url provided

Fetch the workshop page with WebFetch to auto-detect:
- Module titles and topics
- Agenda and schedule
- Tools and platforms mentioned
- Exercise descriptions

Use this to pre-populate module content.

## Phase 2: Live Audio Pipeline

### 2.1 Dependencies

Check and install if missing:
- `sox` (via brew/apt): audio recording
- `openai-whisper` (via pip): transcription
- `ffmpeg`: audio processing (usually already present)

### 2.2 record_chunks.sh

Records audio from default microphone in fixed-duration chunks:
- Format: 16kHz, mono, 16-bit WAV
- Command: `rec -q -r 16000 -c 1 -b 16 "$FILENAME" trim 0 "$CHUNK_DURATION"`
- Naming: `chunk_YYYYMMDD_HHMMSS_NNNN.wav`

### 2.3 transcribe_live.py

Core transcription engine with:

**Keyword categories** - adapt these to the workshop topic:
```python
KEYWORDS = {
    "category1": ["keyword1", "keyword2", ...],
    "category2": ["keyword3", "keyword4", ...],
}
```

Generate keyword categories based on the workshop modules and topic.
If the workshop is in a non-English language, include both the native
language terms and their English equivalents.

**Output format:**
- Terminal: colored prompter with category tags and highlighted keywords
- `live_log.jsonl`: structured entries `{timestamp, file, text, keywords}`
- `live_summary.md`: running markdown summary with detected topics
- `transcripts/*.txt`: raw transcription per chunk

**Whisper configuration:**
- Model: configurable (tiny/base/small/medium/turbo)
- Language: from --lang argument
- fp16: False (for CPU/MPS compatibility)

### 2.4 start.sh

Launcher that:
- Accepts model and chunk duration as arguments
- Starts recorder in background
- Starts transcriber in foreground
- Traps Ctrl+C to cleanly stop both processes
- Prints configuration summary on start

## Phase 3: Ongoing Note Management

This is the most important phase - it runs throughout the workshop.

### 3.1 When user provides notes or keywords

When the user types observations, keywords, or raw notes:

1. **Classify** the content into the appropriate module (theory/tools/exercises)
2. **Update** the relevant module file with structured content
3. **Update** today's journal entry (`journal/YYYY-MM-DD.md`)
4. **Update** `_toc.yml` if new files are created
5. **Build** JupyterBook: `jupyter-book build .`
6. **Commit** changes to git with descriptive message

### 3.2 When analyzing transcripts

When the user asks to process transcripts from `live_audio/`:

1. **Read** `live_log.jsonl` or individual transcript files
2. **Decode** transcription errors (Whisper artifacts, garbled words)
3. **Reconstruct** the speaker's actual message with high confidence
4. **Extract** pedagogical insights, practical tips, key concepts
5. **Create/update** a dedicated notes file in the relevant module
6. **Flag** low-confidence interpretations explicitly
7. **Build** a table of transcription errors for educational purposes

### 3.3 Journal entry format

```markdown
# Journal: YYYY-MM-DD

## Workshop: <title>

**Date:** <full date>
**Location:** <if known>
**URL:** <if known>

---

## Notes

### <Topic 1>

<structured notes>

### <Topic 2>

<structured notes>

---

## Day Summary

<end-of-day summary>
```

### 3.4 Iterative transcript analysis

When user says "iterate", "update notes", or similar:

1. Check for NEW transcripts since last analysis
2. Process only the new ones
3. Append new topics/insights to existing notes file
4. Update journal with new findings
5. Rebuild book and commit

## Phase 4: Quality Guidelines

### Transcript interpretation rules

- **Never trust transcripts literally** - they contain ~20-30% errors for non-English
- **Cross-reference** garbled words with workshop context and known terminology
- **Mark uncertainty** with explicit notes when reconstruction is ambiguous
- **Build error tables** mapping Whisper artifacts to probable meanings
- **Prefer context** over phonetic similarity when decoding

### Content organization rules

- **Theory** goes in `theory.md` - concepts, frameworks, principles
- **Tools** go in `tools.md` - software, commands, configurations
- **Exercises** go in `exercises.md` - hands-on tasks, step-by-step guides
- **Speaker insights** go in dedicated `lecture_notes_*.md` files
- **Cross-reference** between files using `{doc}` directives

### Git commit rules

- Commit after every meaningful update
- Message format: what was added/changed + brief context
- Always include `Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>`

## Quickstart

After setup, tell the user:

```
Workshop ready! Commands:

  Start recording:   ./live_audio/start.sh [model] [chunk_sec]
  Open book:         open _build/html/index.html

During the workshop, type your notes and I will:
  - Organize them into the right module
  - Update the journal
  - Commit to git

To analyze transcripts, say: "iterate notes" or "analyze transcripts"
```
