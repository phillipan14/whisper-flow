"""Audio recording from the default microphone."""

import threading

import numpy as np
import sounddevice as sd


class AudioRecorder:
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self._frames: list[np.ndarray] = []
        self._recording = False
        self._stream = None
        self._lock = threading.Lock()

    @property
    def is_recording(self) -> bool:
        return self._recording

    def get_audio_snapshot(self) -> np.ndarray:
        """Return a copy of audio captured so far without stopping."""
        with self._lock:
            if self._frames:
                return np.concatenate(self._frames, axis=0).flatten()
            return np.array([], dtype="float32")

    def start(self):
        with self._lock:
            self._frames = []
            self._recording = True
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
                callback=self._callback,
            )
            self._stream.start()

    def stop(self) -> np.ndarray:
        with self._lock:
            self._recording = False
            if self._stream:
                self._stream.stop()
                self._stream.close()
                self._stream = None
            if self._frames:
                return np.concatenate(self._frames, axis=0).flatten()
            return np.array([], dtype="float32")

    def _callback(self, indata, frames, time, status):
        if self._recording:
            self._frames.append(indata.copy())
