# Whisper Flow

Local voice-to-text for macOS. Hold Tab, speak, release — transcribed text is inserted at your cursor.

![macOS](https://img.shields.io/badge/macOS-only-blue) ![Python 3.11+](https://img.shields.io/badge/python-3.11+-green) ![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey)

## How it works

1. **Hold Tab** — recording starts, a floating overlay shows a pulsing red dot
2. **Speak** — live streaming transcription appears in the overlay as you talk
3. **Release Tab** — final transcription runs and text is pasted at your cursor

Uses [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (CTranslate2) for fast local inference. Dual-model approach: `tiny` model for real-time streaming preview, `base` (or larger) model for accurate final transcription.

**Everything runs locally. No API calls. No data leaves your machine.**

## Demo

<p align="center">
  <img src="assets/demo.gif" alt="Whisper Flow demo" width="600">
</p>

## Install

```bash
git clone https://github.com/phillipan14/whisper-flow.git
cd whisper-flow
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python -m whisper_flow
```

### Options

```
--model {tiny,base,small,medium,large-v3}   Whisper model size (default: base)
--language LANG                               Transcription language (default: en)
```

Larger models are more accurate but slower. `base` is a good balance for most use cases.

```bash
# Use the small model for better accuracy
python -m whisper_flow --model small

# Transcribe in Spanish
python -m whisper_flow --language es
```

## macOS Permissions

You'll need to grant two permissions in **System Settings > Privacy & Security**:

- **Accessibility** — for keyboard listening and text insertion
- **Microphone** — for audio recording

## Architecture

```
whisper_flow/
  app.py           # Menu bar app, keyboard listener, orchestration
  recorder.py      # Audio capture via sounddevice
  transcriber.py   # Dual-model Whisper transcription (tiny + base)
  inserter.py      # Clipboard-based text insertion
  overlay.py       # Floating NSPanel overlay with animations
```

## Requirements

- macOS (uses AppKit/PyObjC for the overlay, rumps for menu bar)
- Python 3.11+
- A microphone

## License

MIT
