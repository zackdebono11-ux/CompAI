
import time
import os
import pyautogui
from pywinauto import Desktop

pyautogui.FAILSAFE = True

print("CompAI: Opening Developer Settings...")
os.startfile("ms-settings:developers")
time.sleep(5)

desktop = Desktop(backend="uia")
target_id = "SystemSettings_Developer_Mode_ToggleSwitch"

found = False

for window in desktop.windows():
    try:
        for control in window.descendants():
            try:
                if control.element_info.automation_id != target_id:
                    continue

                found = True
                print("\nCompAI: Switch found!")

                try:
                    state = control.iface_toggle.CurrentToggleState

                    if state == 1:
                        print("Developer Mode: ON")
                    elif state == 0:
                        print("Developer Mode: OFF")
                    else:
                        print("Developer Mode: INDETERMINATE")

                except Exception as error:
                    print("UI Automation state unavailable:", error)

                break

            except Exception:
                continue

        if found:
            break

    except Exception:
        continue

if not found:
    print("CompAI: Switch not found.")

print("\nCompAI: No settings were changed.")
