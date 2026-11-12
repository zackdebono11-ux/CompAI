
import os
import json
import re
import queue

import sounddevice as sd
from vosk import Model, KaldiRecognizer, SetLogLevel

SAMPLE_RATE = 16000

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "vosk-model-small-en-us-0.15"
)


def main():
    print("================================")
    print("  COMPAI CONTINUOUS WAKE TEST")
    print("================================")

    if not os.path.isdir(MODEL_PATH):
        print("CompAI: Vosk model not found.")
        return

    try:
        SetLogLevel(-1)

        print("CompAI: Loading wake detector...")
        model = Model(MODEL_PATH)

        # Only listen for the chosen wake phrase.
        recognizer = KaldiRecognizer(
            model,
            SAMPLE_RATE,
            json.dumps(["hey computer"])
        )

        audio_queue = queue.Queue()

        def audio_callback(indata, frames, time_info, status):
            if status:
                print("CompAI: Audio status:", status)

            audio_queue.put(bytes(indata))

        print("CompAI: Microphone:", sd.query_devices(kind="input")["name"])
        print()
        print("CompAI: Wake detector is ACTIVE.")
        print('CompAI: Say "Hey computer!"')
        print("CompAI: Press Ctrl+C to stop.")
        print()

        with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=audio_callback
        ):
            while True:
                try:
                    audio_data = audio_queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                if recognizer.AcceptWaveform(audio_data):
                    result = json.loads(recognizer.Result())
                    spoken = result.get("text", "")

                    normalized = " ".join(
                        re.findall(r"[a-z]+", spoken.lower())
                    )

                    if normalized == "hey computer":
                        print()
                        print("================================")
                        print("       WAKE PHRASE DETECTED!")
                        print("================================")
                        print("CompAI: Yes? I'm listening.")

                        try:
                            import winsound
                            winsound.Beep(880, 180)
                        except Exception:
                            pass

                        break

    except KeyboardInterrupt:
        print("\nCompAI: Wake detector stopped.")

    except Exception as error:
        print("CompAI: Wake detection failed:", error)


if __name__ == "__main__":
    main()
