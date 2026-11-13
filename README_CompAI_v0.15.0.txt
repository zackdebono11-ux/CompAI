COMPAI v0.15.0 GUI

FILES
- AI.py: your existing CompAI command engine, retained and labelled v0.15.0.
- CompAI_GUI.py: new dark emerald desktop interface.
- Launcher.bat: starts the GUI and plays startup_voice.ps1 if it is present.

INSTALL
1. Extract these files into C:\Projects\Comp AI\CompAI_v0.15.0_GUI, replacing the old AI.py and Launcher.bat when prompted.
2. Keep credentials.json and token.json in this folder for Gmail Share. Never share those files.
3. Keep your existing startup.wav, startup_voice.ps1, voice scripts, and other test files.
4. Double-click Launcher.bat.

The GUI starts the existing command engine in the background. Type commands or answers to confirmation prompts in the input box. Quick-action buttons send the same commands as the console version. The right panel shows live CPU, RAM, disk, and battery readings when psutil is installed.

CONSOLE FALLBACK
Open PowerShell in this folder and run: py -3 AI.py

NOTES
- The Vosk wake-word model is not included. If it is missing, ordinary commands and manual Whisper voice commands remain available, but continuous wake-word mode needs the Vosk model restored.
- Python syntax checks passed. The GUI and Windows automation still need to be tested on your Windows PC.
