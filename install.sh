#!/bin/bash
# Philoquent — One-click installer for macOS
# Usage: curl -fsSL https://raw.githubusercontent.com/phillipan14/philoquent/main/install.sh | bash

set -e

INSTALL_DIR="$HOME/.philoquent"
REPO="https://github.com/phillipan14/philoquent.git"

echo ""
echo "  ╔═══════════════════════════════════════╗"
echo "  ║         Philoquent Installer          ║"
echo "  ║    Local voice-to-text for macOS      ║"
echo "  ╚═══════════════════════════════════════╝"
echo ""

# ── Check macOS ──
if [[ "$(uname)" != "Darwin" ]]; then
    echo "Error: Philoquent only runs on macOS."
    exit 1
fi

# ── Find Python 3.11+ ──
PYTHON=""
for cmd in python3.11 python3.12 python3.13 python3; do
    if command -v "$cmd" &>/dev/null; then
        version=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        if [[ "$major" -ge 3 && "$minor" -ge 11 ]]; then
            PYTHON="$cmd"
            break
        fi
    fi
done

if [[ -z "$PYTHON" ]]; then
    echo "Python 3.11+ is required but not found."
    echo ""
    echo "Install it with Homebrew:"
    echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo "  brew install python@3.11"
    echo ""
    echo "Then run this installer again."
    exit 1
fi

echo "Using $PYTHON ($($PYTHON --version))"

# ── Clone or update ──
if [[ -d "$INSTALL_DIR" ]]; then
    echo "Updating existing installation..."
    git -C "$INSTALL_DIR" pull --quiet
else
    echo "Downloading Philoquent..."
    git clone --quiet "$REPO" "$INSTALL_DIR"
fi

# ── Create virtual environment ──
echo "Setting up Python environment..."
"$PYTHON" -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install --quiet -r "$INSTALL_DIR/requirements.txt"
"$INSTALL_DIR/venv/bin/pip" install --quiet pyobjc-framework-Cocoa pyobjc-framework-Quartz

# ── Create launch script ──
LAUNCH="$INSTALL_DIR/start.sh"
cat > "$LAUNCH" << 'SCRIPT'
#!/bin/bash
cd "$(dirname "$0")"
./venv/bin/python -m whisper_flow "$@"
SCRIPT
chmod +x "$LAUNCH"

# ── Create symlink in /usr/local/bin ──
SYMLINK="/usr/local/bin/philoquent"
if [[ -w "/usr/local/bin" ]] || [[ -w "$SYMLINK" ]]; then
    ln -sf "$LAUNCH" "$SYMLINK"
    echo "Created command: philoquent"
else
    sudo ln -sf "$LAUNCH" "$SYMLINK" 2>/dev/null || true
    if [[ -L "$SYMLINK" ]]; then
        echo "Created command: philoquent"
    else
        echo "Tip: Run 'sudo ln -sf $LAUNCH /usr/local/bin/philoquent' to add the 'philoquent' command."
    fi
fi

echo ""
echo "  ✓ Philoquent installed!"
echo ""
echo "  To start:  philoquent"
echo "  Or:        ~/.philoquent/start.sh"
echo ""
echo "  Hotkey:    Hold Fn+Tab to record, release to transcribe"
echo ""
echo "  First run will download the Whisper model (~150MB)."
echo "  You'll need to grant Accessibility + Microphone permissions."
echo ""
