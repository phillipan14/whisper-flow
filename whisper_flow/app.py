"""Menu bar app with hold-to-record voice transcription."""

import argparse
import threading
import time

import rumps
from pynput import keyboard

from .recorder import AudioRecorder
from .transcriber import Transcriber
from .inserter import TextInserter
from .overlay import Overlay

MIN_AUDIO_SECONDS = 0.3
STREAM_INITIAL_DELAY = 0.5  # seconds before first streaming attempt
STREAM_INTERVAL = 0.7  # seconds between streaming transcription updates
SAMPLE_RATE = 16000


def log(msg):
    print(f"[whisper-flow] {msg}", flush=True)


class WhisperFlowApp(rumps.App):
    def __init__(self, model_size: str = "base", language: str = "en"):
        super().__init__("🎤", quit_button=None)

        self.recorder = AudioRecorder(sample_rate=SAMPLE_RATE)
        self.transcriber = Transcriber(model_size=model_size, language=language)
        self.inserter = TextInserter()
        self.overlay = Overlay()
        self._busy = False
        self._tab_held = False

        # Menu items
        self._status = rumps.MenuItem("Ready")
        self._hotkey = rumps.MenuItem("Hold Tab to record")

        self.menu = [
            self._status,
            None,
            self._hotkey,
            None,
            rumps.MenuItem("Quit", callback=self._quit),
        ]

        log("Starting keyboard listener...")
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.daemon = True
        self._listener.start()
        log("Ready — hold Tab to record")

    def _on_press(self, key):
        if key == keyboard.Key.tab and not self._busy and not self._tab_held:
            self._tab_held = True
            log("Recording started")
            self.recorder.start()
            self.title = "🔴"
            self._status.title = "Recording..."
            self.overlay.show_recording()

            # Start streaming transcription in background
            threading.Thread(target=self._stream_loop, daemon=True).start()

    def _on_release(self, key):
        if key == keyboard.Key.tab and self._tab_held:
            self._tab_held = False
            audio = self.recorder.stop()
            duration = len(audio) / SAMPLE_RATE if len(audio) > 0 else 0
            log(f"Recording stopped — {duration:.1f}s")

            if len(audio) > MIN_AUDIO_SECONDS * SAMPLE_RATE:
                self._busy = True
                self.title = "⏳"
                self._status.title = "Transcribing..."
                self.overlay.show_transcribing()
                threading.Thread(target=self._final_transcribe, args=(audio,), daemon=True).start()
            else:
                log("Too short, discarding")
                self.title = "🎤"
                self._status.title = "Ready"
                self.overlay.cancel()

    def _stream_loop(self):
        """Periodically transcribe accumulated audio for live text feedback."""
        time.sleep(STREAM_INITIAL_DELAY)
        while self._tab_held and self.recorder.is_recording:
            audio = self.recorder.get_audio_snapshot()
            if len(audio) > MIN_AUDIO_SECONDS * SAMPLE_RATE:
                try:
                    text = self.transcriber.transcribe_stream(audio)
                    if text and self._tab_held:
                        log(f"Stream: '{text[:60]}'")
                        self.overlay.show_streaming(text)
                except Exception:
                    pass
            time.sleep(STREAM_INTERVAL)

    def _final_transcribe(self, audio):
        """Final transcription after recording stops."""
        try:
            t0 = time.monotonic()
            text = self.transcriber.transcribe(audio)
            elapsed = time.monotonic() - t0
            log(f"Final transcription ({elapsed:.1f}s): '{text}'")

            if text:
                self.inserter.insert(text)
                self.title = "✅"
                self._status.title = f"✓ {text[:50]}"
                self.overlay.show_result(text)
            else:
                self.title = "🎤"
                self._status.title = "No speech detected"
                self.overlay.show_error("No speech detected")
        except Exception as e:
            log(f"Error: {e}")
            self.title = "❌"
            self._status.title = f"Error: {str(e)[:40]}"
            self.overlay.show_error(str(e)[:60])
        finally:
            self._busy = False
            threading.Timer(3.5, self._reset).start()

    def _reset(self):
        self.title = "🎤"
        self._status.title = "Ready"

    def _quit(self, _):
        self._listener.stop()
        rumps.quit_application()


def main():
    parser = argparse.ArgumentParser(description="Whisper Flow — local voice-to-text")
    parser.add_argument("--model", default="base", choices=["tiny", "base", "small", "medium", "large-v3"],
                        help="Whisper model size (default: base)")
    parser.add_argument("--language", default="en", help="Transcription language (default: en)")
    args = parser.parse_args()

    print("Whisper Flow v0.1.0")
    print("─" * 40)
    print(f"Model:    {args.model}")
    print(f"Language: {args.language}")
    print(f"Hotkey:   Hold Tab to record")
    print()
    print("Requires macOS permissions:")
    print("  • Accessibility (System Settings → Privacy → Accessibility)")
    print("  • Microphone   (System Settings → Privacy → Microphone)")
    print()

    app = WhisperFlowApp(model_size=args.model, language=args.language)
    app.run()
