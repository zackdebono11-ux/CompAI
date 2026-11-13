
import os
import tempfile
from pathlib import Path

import sounddevice as sd
import soundfile as sf
import numpy as np
from faster_whisper import WhisperModel


SAMPLE_RATE = 16000
RECORD_SECONDS = 6
MODEL_NAME = "base.en"


def main():
    print("================================")
    print("   COMPAI WHISPER VOICE TEST")
    print("================================")

    try:
        microphone = sd.query_devices(kind="input")
        print("Microphone:", microphone["name"])

        print("\nCompAI: Loading speech recognition model...")
        print("CompAI: First launch may download the model.")

        model = WhisperModel(
            MODEL_NAME,
            device="cpu",
            compute_type="int8",
            cpu_threads=4
        )

        input(
            "\nPress Enter when you're ready to speak..."
        )

        print("\nCompAI: Recording for 6 seconds!")
        print("CompAI: Say: Open Chrome.")

        recording = sd.rec(
            int(RECORD_SECONDS * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32"
        )

        sd.wait()

        peak = float(np.max(np.abs(recording)))
        rms = float(np.sqrt(np.mean(recording ** 2)))

        print("\nRecording information:")
        print("Peak level:", round(peak, 4))
        print("Average level:", round(rms, 4))

        if peak < 0.005:
            print("CompAI: Recording is extremely quiet.")
            return

        with tempfile.TemporaryDirectory() as temp_folder:
            audio_path = Path(temp_folder) / "voice.wav"

            sf.write(
                str(audio_path),
                recording,
                SAMPLE_RATE
            )

            print("\nCompAI: Understanding your speech...")

            segments, info = model.transcribe(
                str(audio_path),
                language="en",
                beam_size=5,
                vad_filter=True,
                condition_on_previous_text=False
            )

            segments = list(segments)

            recognized_text = " ".join(
                segment.text.strip()
                for segment in segments
            ).strip()

        print("\n================================")
        print("        RECOGNITION RESULT")
        print("================================")
        print("Detected language:", info.language)
        print("Language confidence:", round(info.language_probability, 3))
        print("Recognized speech:", recognized_text or "Nothing recognized")
        print("================================")

    except Exception as error:
        print("\nCompAI: Voice test failed:", error)


if __name__ == "__main__":
    main()
