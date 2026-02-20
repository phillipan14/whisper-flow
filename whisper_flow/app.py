"""Menu bar app with hold-to-record voice transcription."""

import argparse
import threading
import time

import rumps
from pynput import keyboard

from .bundle_utils import is_frozen
from .recorder import AudioRecorder
from .transcriber import Transcriber
from .inserter import TextInserter
from .overlay import Overlay

MIN_AUDIO_SECONDS = 0.3
STREAM_INITIAL_DELAY = 0.5  # seconds before first streaming attempt
STREAM_INTERVAL = 0.7  # seconds between streaming transcription updates
SAMPLE_RATE = 16000


def log(msg):
    print(f"[philoquent] {msg}", flush=True)


class WhisperFlowApp(rumps.App):
    def __init__(self, model_size: str = "base", language: str = "en"):
        super().__init__("🎤", quit_button=None)

        self.recorder = AudioRecorder(sample_rate=SAMPLE_RATE)
        self.transcriber = Transcriber(model_size=model_size, language=language)
        self.inserter = TextInserter()
        self.overlay = Overlay()
        self._busy = False
        self._shift_held = False
        self._shift_cancelled = False
        self._recording_active = False
        self._shift_press_time = 0.0
        self._hold_threshold = 0.3  # seconds before shift-hold triggers recording

        # Menu items
        self._status = rumps.MenuItem("Ready")
        self._hotkey = rumps.MenuItem("Hold Shift to record")

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
        log("Ready — hold Shift to record")

    @staticmethod
    def _is_shift(key):
        return key in (keyboard.Key.shift, keyboard.Key.shift_r, keyboard.Key.shift_l)

    def _on_press(self, key):
        if self._is_shift(key):
            if not self._shift_held and not self._busy:
                self._shift_held = True
                self._shift_cancelled = False
                self._shift_press_time = time.monotonic()
                threading.Timer(self._hold_threshold, self._check_shift_hold).start()
        else:
            # Any other key while shift is held = normal typing (e.g. Shift+A)
            if self._shift_held and not self._recording_active:
                self._shift_cancelled = True

    def _check_shift_hold(self):
        if self._shift_held and not self._shift_cancelled and not self._busy and not self._recording_active:
            self._recording_active = True
            log("Recording started")
            self.recorder.start()
            self.title = "🔴"
            self._status.title = "Recording..."
            self.overlay.show_recording()
            threading.Thread(target=self._stream_loop, daemon=True).start()

    def _on_release(self, key):
        if self._is_shift(key) and self._shift_held:
            self._shift_held = False
            if not self._recording_active:
                return  # was a quick tap or cancelled — do nothing
            self._recording_active = False
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
        while self._recording_active and self.recorder.is_recording:
            audio = self.recorder.get_audio_snapshot()
            if len(audio) > MIN_AUDIO_SECONDS * SAMPLE_RATE:
                try:
                    text = self.transcriber.transcribe_stream(audio)
                    if text and self._recording_active:
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
    if is_frozen():
        # Bundled .app — no CLI args, check permissions
        model_size = "base"
        language = "en"
        from .first_run import check_accessibility
        from AppKit import NSApplication
        NSApplication.sharedApplication()
        check_accessibility()
    else:
        parser = argparse.ArgumentParser(description="Philoquent — local voice-to-text")
        parser.add_argument("--model", default="base", choices=["tiny", "base", "small", "medium", "large-v3"],
                            help="Whisper model size (default: base)")
        parser.add_argument("--language", default="en", help="Transcription language (default: en)")
        args = parser.parse_args()
        model_size = args.model
        language = args.language

        print("Philoquent v0.1.0")
        print("─" * 40)
        print(f"Model:    {model_size}")
        print(f"Language: {language}")
        print(f"Hotkey:   Hold Shift to record")
        print()
        print("Requires macOS permissions:")
        print("  • Accessibility (System Settings → Privacy → Accessibility)")
        print("  • Microphone   (System Settings → Privacy → Microphone)")
        print()

    app = WhisperFlowApp(model_size=model_size, language=language)
    app.run()
