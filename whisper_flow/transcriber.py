"""Local Whisper transcription — tiny model for streaming, selected model for final."""

import numpy as np
from faster_whisper import WhisperModel

from .bundle_utils import get_model_cache_dir


class Transcriber:
    def __init__(self, model_size: str = "base", language: str = "en"):
        self.language = language
        cache_dir = get_model_cache_dir()

        if model_size == "tiny":
            print("Loading model (tiny)... ", end="", flush=True)
            self.final_model = WhisperModel(
                "tiny", device="cpu", compute_type="auto",
                download_root=cache_dir,
            )
            self.stream_model = self.final_model
            print("done.")
        else:
            print("Loading streaming model (tiny)... ", end="", flush=True)
            self.stream_model = WhisperModel(
                "tiny", device="cpu", compute_type="auto",
                download_root=cache_dir,
            )
            print("done.")
            print(f"Loading final model ({model_size})... ", end="", flush=True)
            self.final_model = WhisperModel(
                model_size, device="cpu", compute_type="auto",
                download_root=cache_dir,
            )
            print("done.")

    def transcribe_stream(self, audio: np.ndarray) -> str:
        """Fast streaming transcription using tiny model."""
        if len(audio) == 0:
            return ""
        segments, _ = self.stream_model.transcribe(
            audio, language=self.language, vad_filter=True,
        )
        return " ".join(seg.text for seg in segments).strip()

    def transcribe(self, audio: np.ndarray) -> str:
        """Accurate final transcription using selected model."""
        if len(audio) == 0:
            return ""
        segments, _ = self.final_model.transcribe(
            audio, language=self.language, vad_filter=True,
        )
        return " ".join(seg.text for seg in segments).strip()
