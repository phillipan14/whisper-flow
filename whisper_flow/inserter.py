"""Insert transcribed text at the current cursor position."""

import subprocess
import threading
import time


class TextInserter:
    def insert(self, text: str):
        if not text:
            return

        # Save current clipboard
        old = subprocess.run(["pbpaste"], capture_output=True, text=True).stdout

        # Copy transcribed text and paste it
        subprocess.run(["pbcopy"], input=text, text=True)
        subprocess.run([
            "osascript", "-e",
            'tell application "System Events" to keystroke "v" using command down',
        ])

        # Restore original clipboard after paste completes
        def _restore():
            time.sleep(0.3)
            subprocess.run(["pbcopy"], input=old, text=True)

        threading.Thread(target=_restore, daemon=True).start()
