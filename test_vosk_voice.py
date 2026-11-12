
import os
import json
import sounddevice as sd
import numpy as np
from vosk import Model, KaldiRecognizer

SAMPLE_RATE = 16000
RECORD_SECONDS = 5

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "models",
    "vosk-model-small-en-us-0.15"
)


def main():
    print("================================")
    print("    COMPAI VOSK WAKE TEST")
    print("================================")

    if not os.path.isdir(MODEL_PATH):
        print("CompAI: Vosk model folder not found.")
        return

    try:
        print("CompAI: Loading Vosk model...")
        model = Model(MODEL_PATH)

        print(
            "CompAI: Microphone:",
            sd.query_devices(kind="input")["name"]
        )

        input("\nPress Enter when ready...")

        print("\nCompAI: Recording for 5 seconds.")
        print('CompAI: Say "Hey Computer"')

        recording = sd.rec(
            int(RECORD_SECONDS * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16"
        )

        sd.wait()

        peak = int(np.max(np.abs(recording.astype(np.int32))))
        print("Recording peak:", peak)

        if peak < 100:
            print("CompAI: Recording is too quiet.")
            return

        recognizer = KaldiRecognizer(
            model,
            SAMPLE_RATE
        )

        audio_bytes = recording.tobytes()

        for start in range(0, len(audio_bytes), 8000):
            chunk = audio_bytes[start:start + 8000]
            recognizer.AcceptWaveform(chunk)

        result = json.loads(recognizer.FinalResult())

        print("\n================================")
        print("       VOSK TEST RESULT")
        print("================================")
        print("Recognised:", result.get("text", ""))
        print("================================")

    except Exception as error:
        print("CompAI: Vosk test failed:", error)


if __name__ == "__main__":
    main()
