"""First-run setup: check permissions and show guidance."""
import ctypes
import ctypes.util
import subprocess

from AppKit import NSAlert, NSAlertFirstButtonReturn, NSApp


def _ax_is_trusted():
    """Check AXIsProcessTrusted via ctypes (avoids PyObjC framework issues)."""
    path = ctypes.util.find_library('ApplicationServices')
    if path:
        lib = ctypes.cdll.LoadLibrary(path)
        lib.AXIsProcessTrusted.restype = ctypes.c_bool
        return lib.AXIsProcessTrusted()
    return True  # assume trusted if we can't check


def check_accessibility():
    """Check Accessibility permission; show dialog and quit if not granted."""
    if _ax_is_trusted():
        return True

    alert = NSAlert.alloc().init()
    alert.setMessageText_("Accessibility Permission Required")
    alert.setInformativeText_(
        "Philoquent needs Accessibility permission to detect the Fn+Tab "
        "hotkey and paste transcribed text at your cursor.\n\n"
        "Click 'Open System Settings' below, then enable Philoquent in the list.\n"
        "Relaunch Philoquent after granting permission."
    )
    alert.addButtonWithTitle_("Open System Settings")
    alert.addButtonWithTitle_("Quit")

    response = alert.runModal()
    if response == NSAlertFirstButtonReturn:
        subprocess.run([
            '/usr/bin/open',
            'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'
        ])
    NSApp.terminate_(None)
    return False
