# Philoquent

Local voice-to-text for macOS. Hold Fn+Tab, speak, release — transcribed text is inserted at your cursor.

![macOS](https://img.shields.io/badge/macOS-only-blue) ![Python 3.11+](https://img.shields.io/badge/python-3.11+-green) ![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey)

**Everything runs locally. No API calls. No data leaves your machine.**

## Download

**[Download Philoquent.dmg](https://github.com/phillipan14/philoquent/releases/latest/download/Philoquent-0.1.0.dmg)** (71 MB, macOS only)

Open the DMG, drag Philoquent to Applications, double-click to launch. That's it. First launch downloads the speech model (~150MB, one time).

> On first open, macOS may say "can't be opened because it's from an unidentified developer." Right-click the app > Open > Open to bypass this.

## Alternative: Install via Terminal

```bash
curl -fsSL https://raw.githubusercontent.com/phillipan14/philoquent/main/install.sh | bash
```

Then start it:

```bash
philoquent
```

That's it. First launch downloads the speech model (~150MB, one time only).

## How it works

1. **Hold Fn+Tab** — recording starts, a floating overlay appears

   <img src="assets/recording.png" alt="Recording — listening for speech" width="500">

2. **Speak** — live transcription appears in real time as you talk

   <img src="assets/streaming.png" alt="Live streaming transcription" width="500">

3. **Release Fn+Tab** — final transcription runs for accuracy

   <img src="assets/transcribing.png" alt="Processing final transcription" width="500">

4. **Done** — text is automatically pasted at your cursor

   <img src="assets/result.png" alt="Transcription complete" width="500">

Uses [faster-whisper](https://github.com/SYSTRAN/faster-whisper) for fast local inference. Dual-model approach: `tiny` model for real-time preview, `base` (or larger) for accurate final output.

## macOS Permissions

On first run, macOS will ask you to grant two permissions in **System Settings > Privacy & Security**:

| Permission | Why |
|---|---|
| **Accessibility** | Listens for the Fn+Tab hotkey and pastes text at your cursor |
| **Microphone** | Records your voice for transcription |

## Options

```bash
# Better accuracy (slower)
philoquent --model small

# Fastest (less accurate)
philoquent --model tiny

# Transcribe in another language
philoquent --language es
```

Available models: `tiny` (fastest), `base` (default), `small`, `medium`, `large-v3` (most accurate).

## Manual Install

If you prefer to install manually:

```bash
git clone https://github.com/phillipan14/philoquent.git
cd philoquent
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install pyobjc-framework-Cocoa pyobjc-framework-Quartz
python -m whisper_flow
```

## How it's built

```
whisper_flow/
  app.py           # Menu bar app, keyboard listener, orchestration
  recorder.py      # Audio capture via sounddevice
  transcriber.py   # Dual-model Whisper transcription (tiny + base)
  inserter.py      # Clipboard-based text insertion
  overlay.py       # Floating NSPanel overlay with animations
```

## Requirements

- macOS (Apple Silicon or Intel)
- Python 3.11+ (install via `brew install python@3.11` if needed)
- A microphone (built-in works fine)

## License

MIT
