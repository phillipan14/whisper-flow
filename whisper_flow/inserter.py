"""Insert transcribed text at the current cursor position.

Uses CGEventPost to simulate Cmd+V — bypasses osascript/System Events
which fails silently on macOS Sequoia due to automation restrictions.
"""

import subprocess
import threading
import time

import Quartz

V_KEYCODE = 9  # macOS virtual keycode for 'v'


class TextInserter:
    def insert(self, text: str):
        if not text:
            return

        # Save current clipboard
        old = subprocess.run(["/usr/bin/pbpaste"], capture_output=True, text=True).stdout

        # Copy transcribed text to clipboard
        subprocess.run(["/usr/bin/pbcopy"], input=text, text=True)
        time.sleep(0.05)  # let pasteboard sync

        # Simulate Cmd+V via CGEvent (reliable on macOS Sequoia)
        self._paste()

        # Restore original clipboard after paste completes
        def _restore():
            time.sleep(0.5)
            subprocess.run(["/usr/bin/pbcopy"], input=old, text=True)

        threading.Thread(target=_restore, daemon=True).start()

    @staticmethod
    def _paste():
        # Use HID-level source + tap so the event reaches ANY frontmost app
        # (not just the process that spawned it)
        src = Quartz.CGEventSourceCreate(Quartz.kCGEventSourceStateHIDSystemState)
        down = Quartz.CGEventCreateKeyboardEvent(src, V_KEYCODE, True)
        up = Quartz.CGEventCreateKeyboardEvent(src, V_KEYCODE, False)
        Quartz.CGEventSetFlags(down, Quartz.kCGEventFlagMaskCommand)
        Quartz.CGEventSetFlags(up, Quartz.kCGEventFlagMaskCommand)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, down)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, up)
