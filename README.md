# /live-workshop

> Turn any lecture into a structured, searchable knowledge base -- in real time.

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) custom skill that sets up a JupyterBook-based workshop journal with live audio transcription, keyword extraction, and structured knowledge base.

## Quick Install

```bash
# 1. Clone into Claude Code skills directory
git clone https://github.com/nasqret/live-workshop-skill.git ~/.claude/skills/live-workshop

# 2. Install dependencies
brew install sox ffmpeg          # macOS (Linux: apt install sox ffmpeg)
pip3 install openai-whisper jupyter-book

# 3. Use in any project
cd ~/my-project
# Then in Claude Code:
/live-workshop "Workshop Title" --lang en --modules "Topic1,Topic2,Topic3"
```

## What It Does

### Four-Phase Pipeline

| Phase | Action |
|-------|--------|
| **INIT** | Creates JupyterBook project with modules, journal, exercises, and git repo |
| **RECORD** | Live audio capture (sox) + real-time Whisper transcription + keyword prompter |
| **ORGANIZE** | Auto-classifies your notes into theory/tools/exercises, updates journal, commits |
| **ANALYZE** | Iterative transcript analysis, decodes Whisper errors, extracts speaker insights |

### Project Structure Generated

```
your-project/
├── _config.yml              # JupyterBook config
├── _toc.yml                 # Auto-updated table of contents
├── intro.md                 # Landing page
├── journal/                 # Daily meeting notes
├── modules/
│   ├── 01_topic/
│   │   ├── theory.md        # Concepts and frameworks
│   │   ├── tools.md         # Software and commands
│   │   └── exercises.md     # Hands-on tasks
│   └── ...
├── exercises/index.md
└── live_audio/
    ├── start.sh             # Launch recording + transcription
    ├── record_chunks.sh     # sox audio recorder
    └── transcribe_live.py   # Whisper + keyword extraction
```

## Usage

### Start a workshop session

```
/live-workshop "Machine Learning Fundamentals" --lang en --modules "Regression,Neural Networks,Transformers"
```

### With a workshop URL (auto-fetches agenda)

```
/live-workshop "DevOps Workshop" --url https://workshop.example.com/agenda
```

### Start live recording (in a separate terminal)

```bash
./live_audio/start.sh              # defaults: small model, 30s chunks, English
./live_audio/start.sh turbo 45     # better quality, 45s chunks
./live_audio/start.sh tiny 15 de   # fast, 15s chunks, German
```

### During the workshop

Just type your notes in Claude Code. The skill will:
- Classify them into the right module (theory/tools/exercises)
- Update today's journal entry
- Rebuild the JupyterBook
- Commit to git

### Analyze transcripts

Say "iterate notes" or "analyze transcripts" to process new audio fragments.

## Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `<title>` | required | Workshop/meeting title |
| `--lang` | `en` | Whisper transcription language |
| `--modules` | auto-detect | Comma-separated module names |
| `--url` | - | Workshop URL to fetch agenda from |
| `--chunk-duration` | `30` | Audio chunk length in seconds |
| `--whisper-model` | `small` | Whisper model (tiny/base/small/medium/turbo) |

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- [sox](https://sox.sourceforge.net/) - audio recording
- [OpenAI Whisper](https://github.com/openai/whisper) - transcription
- [ffmpeg](https://ffmpeg.org/) - audio processing
- [JupyterBook](https://jupyterbook.org/) - output format
- Python 3.10+
- Git

## Tech Stack

sox | Whisper | JupyterBook | Git | Python | zsh

## License

MIT
