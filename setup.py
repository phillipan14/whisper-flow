"""py2app build configuration for Philoquent."""
from setuptools import setup

VENV = 'venv/lib/python3.11/site-packages'

APP = ['run.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'assets/AppIcon.icns',
    'plist': {
        'CFBundleName': 'Philoquent',
        'CFBundleDisplayName': 'Philoquent',
        'CFBundleIdentifier': 'com.allstonlabs.philoquent',
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
    'packages': [
        'whisper_flow',
        'faster_whisper',
        'faster_whisper.assets',
        'ctranslate2',
        'onnxruntime',
        'onnxruntime.capi',
        '_sounddevice_data',
        '_sounddevice_data.portaudio-binaries',
        'huggingface_hub',
        'tokenizers',
        'hf_xet',
        'numpy',
        'pynput',
        'pynput.keyboard',
        'pynput._util',
        'rumps',
        'objc',
        'AppKit',
        'Foundation',
        'Quartz',
        'Quartz.CoreGraphics',
        'Quartz.QuartzCore',
        'CoreText',
        'cffi',
        'yaml',
        'tqdm',
        'certifi',
        'packaging',
        'sympy',
        'flatbuffers',
    ],
    'includes': [
        'sounddevice',
        '_sounddevice',
        '_cffi_backend',
    ],
    'frameworks': [
        f'{VENV}/ctranslate2/.dylibs/libctranslate2.4.7.1.dylib',
        f'{VENV}/onnxruntime/capi/libonnxruntime.1.24.1.dylib',
    ],
    'strip': False,
    'semi_standalone': False,
    'site_packages': True,
    'arch': 'arm64',
}

setup(
    name='Philoquent',
    version='0.1.0',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
