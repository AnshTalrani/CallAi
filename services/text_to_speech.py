import torch
from kokoro import KModel, KPipeline
import sounddevice as sd
import numpy as np

class TTSGenerator:
    """Generate TTS PCM audio and optionally play it out.

    Methods
    -------
    synthesize(text) -> bytes
        Return 24-kHz 32-bit float PCM bytes (little-endian) for given text.
    generate_speech(text, play=True) -> bytes
        Convenience wrapper that optionally plays audio via sounddevice and
        still returns bytes for further processing (e.g. RTP/WebRTC).
    """
    def __init__(self, default_voice: str = "af_heart"):
        print("Initializing TTS...")
        self.model = KModel().to("cpu").eval()
        self.pipeline = KPipeline(lang_code="a", model=False)
        self.voice_pack = self.pipeline.load_voice(default_voice)
        self.sample_rate = 24000
        print("TTS ready!")

    def _synthesize_ndarray(self, text: str):
        """Return concatenated numpy float32 array for the whole utterance."""
        import numpy as _np
        chunks: list[_np.ndarray] = []
        for _, ps, _ in self.pipeline(text, "af_heart", 1):
            ref_s = self.voice_pack[len(ps) - 1]
            audio = self.model(ps, ref_s, 1)
            chunks.append(audio.numpy().astype(_np.float32))
        if not chunks:
            return _np.zeros(1, dtype=_np.float32)
        return _np.concatenate(chunks)

    def synthesize(self, text: str) -> bytes:
        """Generate PCM bytes for the given text (no playback)."""
        audio_data = self._synthesize_ndarray(text)
        return audio_data.tobytes()

    def generate_speech(self, text: str, *, play: bool = True) -> bytes:
        """Generate speech and optionally play it. Always returns bytes."""
        audio_data = self._synthesize_ndarray(text)
        if play:
            try:
                sd.play(audio_data, samplerate=self.sample_rate, blocking=True)
                sd.wait()
            except KeyboardInterrupt:
                sd.stop()
        return audio_data.tobytes()
            
    def cleanup(self):
        pass  # No cleanup needed for sounddevice

def create_tts_generator():
    """Create and return a TTSGenerator instance."""
    return TTSGenerator()

if __name__ == "__main__":
    # Example usage
    tts = TTSGenerator()
    try:
        tts.generate_speech("Hello, this is a test of the text to speech system.")
    finally:
        tts.cleanup() 