"""System-level Tab key interceptor using macOS CGEventTap.

Suppresses Tab from reaching other apps while held for recording.
Quick taps (< hold threshold) re-inject Tab so normal typing works.
"""

import threading
import time

import Quartz

TAB_KEYCODE = 48
HOLD_THRESHOLD = 0.25  # seconds — taps shorter than this pass through as normal Tab


class TabInterceptor:
    def __init__(self, on_hold_start, on_hold_end, on_quick_tap=None):
        self._on_hold_start = on_hold_start
        self._on_hold_end = on_hold_end
        self._on_quick_tap = on_quick_tap
        self._active = False
        self._press_time = 0.0
        self._loop = None

    def start(self):
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

    def stop(self):
        if self._loop:
            Quartz.CFRunLoopStop(self._loop)

    def _run(self):
        def callback(proxy, event_type, event, refcon):
            keycode = Quartz.CGEventGetIntegerValueField(
                event, Quartz.kCGKeyboardEventKeycode
            )
            if keycode != TAB_KEYCODE:
                return event

            if event_type == Quartz.kCGEventKeyDown:
                is_repeat = Quartz.CGEventGetIntegerValueField(
                    event, Quartz.kCGKeyboardEventAutorepeat
                )
                if not is_repeat and not self._active:
                    self._active = True
                    self._press_time = time.monotonic()
                    self._on_hold_start()
                return None  # suppress all Tab key-downs

            if event_type == Quartz.kCGEventKeyUp and self._active:
                self._active = False
                duration = time.monotonic() - self._press_time
                if duration < HOLD_THRESHOLD:
                    # Quick tap — re-inject Tab and cancel recording
                    self._reinject_tab()
                    if self._on_quick_tap:
                        self._on_quick_tap()
                else:
                    self._on_hold_end()
                return None  # suppress key-up

            return event

        mask = (
            Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown)
            | Quartz.CGEventMaskBit(Quartz.kCGEventKeyUp)
        )
        tap = Quartz.CGEventTapCreate(
            Quartz.kCGSessionEventTap,
            Quartz.kCGHeadInsertEventTap,
            Quartz.kCGEventTapOptionDefault,
            mask,
            callback,
            None,
        )
        if tap is None:
            print("ERROR: Could not create event tap.")
            print("Grant Accessibility permissions: System Settings → Privacy → Accessibility")
            return

        source = Quartz.CFMachPortCreateRunLoopSource(None, tap, 0)
        self._loop = Quartz.CFRunLoopGetCurrent()
        Quartz.CFRunLoopAddSource(self._loop, source, Quartz.kCFRunLoopDefaultMode)
        Quartz.CGEventTapEnable(tap, True)
        Quartz.CFRunLoopRun()

    @staticmethod
    def _reinject_tab():
        down = Quartz.CGEventCreateKeyboardEvent(None, TAB_KEYCODE, True)
        up = Quartz.CGEventCreateKeyboardEvent(None, TAB_KEYCODE, False)
        Quartz.CGEventPost(Quartz.kCGAnnotatedSessionEventTap, down)
        Quartz.CGEventPost(Quartz.kCGAnnotatedSessionEventTap, up)
