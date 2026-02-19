# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Philoquent."""
import os
import site

block_cipher = None

# Find the venv site-packages
sp = os.path.join(SPECPATH, 'venv', 'lib', 'python3.11', 'site-packages')

a = Analysis(
    ['run.py'],
    pathex=[SPECPATH],
    binaries=[
        (os.path.join(sp, 'ctranslate2', '.dylibs', 'libctranslate2.4.7.1.dylib'), '.'),
        (os.path.join(sp, 'onnxruntime', 'capi', 'libonnxruntime.1.24.1.dylib'), '.'),
        (os.path.join(sp, '_sounddevice_data', 'portaudio-binaries', 'libportaudio.dylib'), '_sounddevice_data/portaudio-binaries/'),
    ],
    datas=[
        (os.path.join(sp, 'faster_whisper', 'assets'), 'faster_whisper/assets'),
        (os.path.join(sp, '_sounddevice_data'), '_sounddevice_data'),
    ],
    hiddenimports=[
        'whisper_flow',
        'whisper_flow.app',
        'whisper_flow.recorder',
        'whisper_flow.transcriber',
        'whisper_flow.inserter',
        'whisper_flow.overlay',
        'whisper_flow.bundle_utils',
        'whisper_flow.first_run',
        'faster_whisper',
        'ctranslate2',
        'onnxruntime',
        'sounddevice',
        '_sounddevice',
        '_sounddevice_data',
        '_cffi_backend',
        'pynput',
        'pynput.keyboard',
        'pynput.keyboard._darwin',
        'pynput._util',
        'pynput._util.darwin',
        'rumps',
        'objc',
        'AppKit',
        'Foundation',
        'Quartz',
        'Quartz.CoreGraphics',
        'Quartz.QuartzCore',
        'CoreText',
        'huggingface_hub',
        'tokenizers',
        'numpy',
        'cffi',
        'yaml',
        'tqdm',
        'certifi',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'PIL',
        'tkinter',
        'test',
        'unittest',
        'IPython',
        'jupyter',
        'notebook',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Philoquent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    target_arch='arm64',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='Philoquent',
)

app = BUNDLE(
    coll,
    name='Philoquent.app',
    icon='assets/AppIcon.icns',
    bundle_identifier='com.allstonlabs.philoquent',
    info_plist={
        'CFBundleName': 'Philoquent',
        'CFBundleDisplayName': 'Philoquent',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1.0',
        'LSUIElement': True,
        'LSMinimumSystemVersion': '12.0',
        'NSMicrophoneUsageDescription':
            'Philoquent needs microphone access to record your voice for transcription.',
        'NSAppleEventsUsageDescription':
            'Philoquent uses System Events to paste transcribed text at your cursor.',
        'NSHighResolutionCapable': True,
    },
)
