"""Conversational pipeline glueing STT → LLM → TTS

This module provides a high-level orchestration class so other layers
(e.g., CLI demo, telephony integrations, REST API) can call a *single*
method to transform audio ↔ text ↔ audio.

Design goals
------------
1. Keep it simple: only three moving parts (VoiceRecognizer, LLMThinker,
   TTSGenerator) that already exist in the codebase.
2. No direct I/O assumptions – caller decides whether to use live
   microphones or pre-recorded WAVs.
3. Stateless: a new instance can be spun up per call/session, but we
   expose shared instances for efficiency.
4. Thin LangChain layer: the heavy LangChain usage lives in
   `LLMThinker` (it wraps ChatOllama + ReAct agent).  The pipeline is
   agnostic – it just calls `LLMThinker.get_response()`.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional
import wave
import numpy as np

# Local service wrappers
from services.voice_recognition import VoiceRecognizer
from services.llm_thinking import LLMThinker
from services.text_to_speech import TTSGenerator


class ConversationPipeline:
    """End-to-end processing from audio-in to audio-out."""

    def __init__(self,
                 device_id: int = -1,
                 sample_rate: int = 16000,
                 default_voice: str = "af_heart",
                 eager: bool = True):
        """Create the pipeline.

        Parameters
        ----------
        device_id : int
            PvRecorder index (−1 = default) if using live mic.
        sample_rate : int
            Whisper sample-rate (re-sample recorded audio if needed).
        default_voice : str
            Voicepack name for Kokoro.
        eager : bool
            If *True* (default) initialise all components immediately;
            if *False* they will be lazily instantiated when first used.
        """
        self._device_id = device_id
        self._sample_rate = sample_rate
        self._default_voice = default_voice
        self._eager = eager

        self.recognizer: Optional[VoiceRecognizer] = None
        self.thinker: Optional[LLMThinker] = None
        self.tts: Optional[TTSGenerator] = None

        if eager:
            self._ensure_components()

    # ------------------------------------------------------------------
    # Lazy-init helpers
    # ------------------------------------------------------------------
    def _ensure_components(self):
        if self.recognizer is None:
            self.recognizer = VoiceRecognizer(device_id=self._device_id)
        if self.thinker is None:
            self.thinker = LLMThinker()
        if self.tts is None:
            self.tts = TTSGenerator(default_voice=self._default_voice)

    # ------------------------------------------------------------------
    # High-level API
    # ------------------------------------------------------------------
    def process_audio_file(self, input_wav: str | Path,
                           output_wav: str | Path,
                           cleanup: bool = True) -> str:
        """Transcribe *input_wav* → get LLM answer → synthesize to *output_wav*.

        Returns the transcription string (Whisper output).
        """
        self._ensure_components()

        # 1. Load & normalise audio (16-bit PCM mono expected)
        with wave.open(str(input_wav), "rb") as wf:
            sr = wf.getframerate()
            raw = wf.readframes(wf.getnframes())
        audio_np = (np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0)

        # 2. Transcribe
        text = self.recognizer.transcribe_audio(audio_np)

        # 3. Get LLM response
        answer = self.thinker.get_response(text)

        # 4. Synthesize
        self._generate_wav(answer, output_wav)

        # 5. Optionally free GPU resources etc.
        if cleanup:
            self.cleanup()
        return text

    def interactive_loop(self):
        """Live mic → LLM → speakers loop.  Press Ctrl-C to stop."""
        self._ensure_components()
        print("\nConversation loop ready – speak into the microphone…")
        try:
            while True:
                audio = self.recognizer.record_audio()
                if audio is None:
                    continue
                text = self.recognizer.transcribe_audio(audio)
                if text.lower() in {"quit", "exit", "bye"}:
                    break
                answer = self.thinker.get_response(text)
                self.tts.generate_speech(answer)
        finally:
            self.cleanup()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _generate_wav(self, text: str, out_path: str | Path):
        """Generate a TTS file to *out_path* without playback."""
        # Kokoro plays audio by default – we need a non-blocking path.
        # We'll mimic Kokoro code but collect arrays and write to wav.
        import soundfile as sf
        from kokoro import KModel, KPipeline

        model = KModel().to("cpu").eval()
        pipe = KPipeline(lang_code="a", model=False)
        vp = pipe.load_voice(self._default_voice)

        segments = []
        for _, ps, _ in pipe(text, self._default_voice, 1):
            segments.append(model(ps, vp[len(ps)-1], 1).numpy())
        if not segments:
            raise RuntimeError("TTS produced no audio")
        audio = np.concatenate(segments)
        sf.write(str(out_path), audio, 24000)
        print(f"Saved synthesized speech → {out_path}")

    # ------------------------------------------------------------------
    # Teardown
    # ------------------------------------------------------------------
    def cleanup(self):
        if self.recognizer:
            self.recognizer.cleanup()
        if self.tts:
            self.tts.cleanup()


# ----------------------------------------------------------------------
# Quick CLI for ad-hoc file processing
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Audio→LLM→Audio pipeline")
    parser.add_argument("input_wav", help="Path to input WAV @16k/mono")
    parser.add_argument("output_wav", help="Path to save synthesized WAV")
    args = parser.parse_args()

    pipe = ConversationPipeline(eager=True)
    transcription = pipe.process_audio_file(args.input_wav, args.output_wav)
    print("Transcription:", transcription)
