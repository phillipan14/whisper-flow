"""Floating on-screen overlay — dark pill with live transcription."""

import threading

import objc
from AppKit import (
    NSPanel,
    NSView,
    NSTextField,
    NSColor,
    NSFont,
    NSScreen,
    NSWindowStyleMaskBorderless,
    NSBackingStoreBuffered,
    NSFloatingWindowLevel,
    NSWindowCollectionBehaviorCanJoinAllSpaces,
    NSWindowCollectionBehaviorStationary,
    NSLineBreakByTruncatingTail,
    NSAnimationContext,
)
from Foundation import NSMakeRect, NSObject
import Quartz
from Quartz import CABasicAnimation


# ── Thread-safe main-thread dispatch ──────────────────────────────────────

class _Invoker(NSObject):
    def initWithBlock_(self, block):
        self = objc.super(_Invoker, self).init()
        if self is None:
            return None
        self._block = block
        return self

    def invoke_(self, _):
        self._block()


def _on_main(fn):
    inv = _Invoker.alloc().initWithBlock_(fn)
    inv.performSelectorOnMainThread_withObject_waitUntilDone_(b"invoke:", None, False)


# ── Overlay ───────────────────────────────────────────────────────────────

class Overlay:
    WIDTH = 560
    HEIGHT = 52
    DOT_SIZE = 10

    # Skylarq palette
    BG_COLOR = Quartz.CGColorCreateGenericRGB(0.055, 0.06, 0.09, 0.94)
    BORDER_COLOR = Quartz.CGColorCreateGenericRGB(0.18, 0.20, 0.28, 0.45)
    TEXT_COLOR = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.90, 0.91, 0.94, 1.0)
    MUTED_COLOR = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.55, 0.58, 0.65, 1.0)
    DOT_RED = Quartz.CGColorCreateGenericRGB(0.92, 0.22, 0.20, 1.0)
    DOT_GREEN = Quartz.CGColorCreateGenericRGB(0.20, 0.82, 0.40, 1.0)
    DOT_AMBER = Quartz.CGColorCreateGenericRGB(0.95, 0.75, 0.20, 1.0)

    def __init__(self):
        screen = NSScreen.mainScreen().frame()
        x = (screen.size.width - self.WIDTH) / 2
        y = screen.size.height * 0.10

        self._panel = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(x, y, self.WIDTH, self.HEIGHT),
            NSWindowStyleMaskBorderless,
            NSBackingStoreBuffered,
            False,
        )
        self._panel.setLevel_(NSFloatingWindowLevel + 2)
        self._panel.setOpaque_(False)
        self._panel.setBackgroundColor_(NSColor.clearColor())
        self._panel.setHasShadow_(True)
        self._panel.setIgnoresMouseEvents_(True)
        self._panel.setHidesOnDeactivate_(False)
        self._panel.setCollectionBehavior_(
            NSWindowCollectionBehaviorCanJoinAllSpaces
            | NSWindowCollectionBehaviorStationary
        )
        self._panel.setAlphaValue_(0.0)

        # ── Background pill ──
        content = NSView.alloc().initWithFrame_(
            NSMakeRect(0, 0, self.WIDTH, self.HEIGHT)
        )
        content.setWantsLayer_(True)
        bg = content.layer()
        bg.setCornerRadius_(self.HEIGHT / 2)
        bg.setBackgroundColor_(self.BG_COLOR)
        bg.setBorderColor_(self.BORDER_COLOR)
        bg.setBorderWidth_(0.5)

        # ── Colored dot (recording indicator) ──
        dot_y = (self.HEIGHT - self.DOT_SIZE) / 2
        self._dot = NSView.alloc().initWithFrame_(
            NSMakeRect(20, dot_y, self.DOT_SIZE, self.DOT_SIZE)
        )
        self._dot.setWantsLayer_(True)
        self._dot.layer().setCornerRadius_(self.DOT_SIZE / 2)
        self._dot.layer().setBackgroundColor_(self.DOT_RED)

        # ── Primary text ──
        self._label = NSTextField.alloc().initWithFrame_(
            NSMakeRect(40, (self.HEIGHT - 20) / 2, self.WIDTH - 60, 20)
        )
        self._label.setStringValue_("")
        self._label.setFont_(NSFont.monospacedSystemFontOfSize_weight_(14, 0.0))
        self._label.setTextColor_(self.TEXT_COLOR)
        self._label.setBezeled_(False)
        self._label.setDrawsBackground_(False)
        self._label.setEditable_(False)
        self._label.setSelectable_(False)
        self._label.setLineBreakMode_(NSLineBreakByTruncatingTail)

        content.addSubview_(self._dot)
        content.addSubview_(self._label)
        self._panel.setContentView_(content)

        self._hide_timer = None

    # ── Public API ────────────────────────────────────────────────────────

    def show_recording(self):
        def _do():
            self._cancel_hide()
            self._dot.layer().setBackgroundColor_(self.DOT_RED)
            self._start_pulse()
            self._label.setTextColor_(self.TEXT_COLOR)
            self._label.setStringValue_("Listening...")
            self._fade_in()
        _on_main(_do)

    def show_streaming(self, text):
        """Update overlay with partial transcription while still recording."""
        def _do():
            display = text if len(text) < 70 else text[-67:] + "..."
            self._label.setStringValue_(display + " \u258C")  # block cursor
            self._label.setTextColor_(self.TEXT_COLOR)
        _on_main(_do)

    def show_transcribing(self):
        def _do():
            self._stop_pulse()
            self._dot.layer().setBackgroundColor_(self.DOT_AMBER)
            self._label.setTextColor_(self.MUTED_COLOR)
            self._label.setStringValue_("Transcribing...")
        _on_main(_do)

    def show_result(self, text):
        def _do():
            self._stop_pulse()
            self._dot.layer().setBackgroundColor_(self.DOT_GREEN)
            self._label.setTextColor_(self.TEXT_COLOR)
            display = text if len(text) < 70 else text[:67] + "..."
            self._label.setStringValue_(display)
            self._schedule_hide(3.5)
        _on_main(_do)

    def show_error(self, msg):
        def _do():
            self._stop_pulse()
            self._dot.layer().setBackgroundColor_(self.DOT_RED)
            self._label.setTextColor_(self.MUTED_COLOR)
            self._label.setStringValue_(msg)
            self._schedule_hide(3.0)
        _on_main(_do)

    def hide(self):
        _on_main(self._fade_out)

    def cancel(self):
        def _do():
            self._stop_pulse()
            self._cancel_hide()
            self._fade_out()
        _on_main(_do)

    # ── Animations ────────────────────────────────────────────────────────

    def _fade_in(self):
        self._panel.orderFrontRegardless()
        NSAnimationContext.beginGrouping()
        NSAnimationContext.currentContext().setDuration_(0.2)
        self._panel.animator().setAlphaValue_(1.0)
        NSAnimationContext.endGrouping()

    def _fade_out(self):
        NSAnimationContext.beginGrouping()
        NSAnimationContext.currentContext().setDuration_(0.3)
        self._panel.animator().setAlphaValue_(0.0)
        NSAnimationContext.endGrouping()

    def _start_pulse(self):
        anim = CABasicAnimation.animationWithKeyPath_("opacity")
        anim.setFromValue_(1.0)
        anim.setToValue_(0.25)
        anim.setDuration_(0.6)
        anim.setAutoreverses_(True)
        anim.setRepeatCount_(1e9)
        self._dot.layer().addAnimation_forKey_(anim, "pulse")

    def _stop_pulse(self):
        self._dot.layer().removeAnimationForKey_("pulse")
        self._dot.layer().setOpacity_(1.0)

    # ── Timers ────────────────────────────────────────────────────────────

    def _schedule_hide(self, seconds):
        self._cancel_hide()
        self._hide_timer = threading.Timer(seconds, self.hide)
        self._hide_timer.start()

    def _cancel_hide(self):
        if self._hide_timer:
            self._hide_timer.cancel()
            self._hide_timer = None
