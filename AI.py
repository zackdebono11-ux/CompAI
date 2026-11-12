

import time

import os

import sys

import ctypes

import platform

import shutil

import urllib.request

import base64

import mimetypes

import re

import subprocess



from email.message import EmailMessage



try:

    import pyautogui

    PYAUTOGUI_AVAILABLE = True

    pyautogui.FAILSAFE = True

except ImportError:

    pyautogui = None

    PYAUTOGUI_AVAILABLE = False



try:

    from pywinauto import Desktop

    PYWinAUTO_AVAILABLE = True

except ImportError:

    Desktop = None

    PYWinAUTO_AVAILABLE = False



try:

    from google.auth.transport.requests import Request

    from google.oauth2.credentials import Credentials

    from google_auth_oauthlib.flow import InstalledAppFlow

    from googleapiclient.discovery import build

    from googleapiclient.errors import HttpError



    GMAIL_AVAILABLE = True



except ImportError:

    GMAIL_AVAILABLE = False





VERSION = "0.15.0"



DEVELOPER_SWITCH_ID = "SystemSettings_Developer_Mode_ToggleSwitch"



BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")

TOKEN_FILE = os.path.join(BASE_DIR, "token.json")



GMAIL_SCOPES = [

    "https://www.googleapis.com/auth/gmail.send"

]





print("================================")

print("          COMPAI v" + VERSION)

print("================================")

print("Hello! I'm CompAI.")

print("I can control certain features of your PC.")

print()

print("Type 'help' to see all commands.")





# HELP

def show_help():

    print("\n========== COMPAI HELP ==========")

    print("search cats              Search Google")

    print("developer mode           Open Developer Settings")

    print("developer mode status    Check Developer Mode")

    print("developer mode on        Enable Developer Mode")

    print("developer mode off       Disable Developer Mode")

    print("wallpaper C:\\Photos\\cat.jpg")

    print("                         Change wallpaper")

    print("share                    Open CompAI Share")

    print("share email              Share a file by email")

    print("share nearby             Share using Nearby Sharing")

    print("status                   Check PC capabilities")

    print("help                     Show this help")

    print("exit                     Close CompAI")

    print("open chrome              Open Google Chrome")

    print("open vscode              Open Visual Studio Code")

    print("open discord             Open Discord")

    print("open calculator          Open Calculator")

    print("open notepad             Open Notepad")

    print("open explorer            Open File Explorer")

    print("open settings            Open Windows Settings")

    print("apps                     Show supported applications")

    print("monitor                  Monitor entire PC")

    print("pc status                Show PC statistics")

    print("cpu                      Check CPU usage")

    print("memory                   Check RAM usage")

    print("disk                     Check disk space")

    print("battery                  Check battery status")

    print("processes                Show top CPU and RAM processes")

    print("top cpu                  Show highest CPU processes")

    print("top memory               Show highest RAM processes")

    print("voice                    Listen for a voice command")

    print("listen                   Listen for a voice command")

    print("wake on                  Enable continuous wake listening")

    print("wake off                 Disable wake listening (after activation)")

    print("================================")





# GOOGLE SEARCH

def search_google(search):

    if not PYAUTOGUI_AVAILABLE:

        print("CompAI: Mouse and keyboard automation is unavailable.")

        return



    if platform.system() != "Windows":

        print("CompAI: This search workflow requires Windows.")

        return



    confirm = input(

        "CompAI: Open Chrome and search for "

        + repr(search) + "? (yes/no): "

    )



    if confirm.strip().lower() != "yes":

        print("CompAI: Search cancelled.")

        return



    try:

        print("CompAI: Opening the Start menu...")

        screen_width, screen_height = pyautogui.size()



        pyautogui.moveTo(25, screen_height - 25, duration=1)

        pyautogui.click()

        time.sleep(1)



        pyautogui.write("Google Chrome", interval=0.12)

        time.sleep(2)

        pyautogui.press("enter")



        print("CompAI: Waiting for Chrome...")

        time.sleep(4)



        pyautogui.hotkey("ctrl", "l")

        time.sleep(0.5)

        pyautogui.write(search, interval=0.1)

        pyautogui.press("enter")



        print("CompAI: Search submitted!")



    except Exception as error:

        print("CompAI: Search failed:", error)





# DEVELOPER MODE UI AUTOMATION

def find_developer_mode_switch():

    if platform.system() != "Windows":

        print("CompAI: This feature requires Windows.")

        return None



    if not PYWinAUTO_AVAILABLE:

        print("CompAI: pywinauto is not installed.")

        return None



    try:

        desktop = Desktop(backend="uia")



        for window in desktop.windows():

            try:

                for control in window.descendants():

                    try:

                        if (

                            control.element_info.automation_id

                            == DEVELOPER_SWITCH_ID

                        ):

                            rect = control.rectangle()



                            if rect.width() > 0 and rect.height() > 0:

                                return control



                    except Exception:

                        continue



            except Exception:

                continue



    except Exception as error:

        print("CompAI: UI Automation error:", error)



    return None





def get_ui_developer_mode_state(control):

    try:

        state = control.iface_toggle.CurrentToggleState



        if state == 1:

            return True



        if state == 0:

            return False



        return None



    except Exception:

        return None





def get_developer_mode_state():

    if platform.system() != "Windows":

        return None



    control = find_developer_mode_switch()



    if control is not None:

        return get_ui_developer_mode_state(control)



    return None





# DEVELOPER MODE STATUS

def developer_mode_status():

    print("CompAI: Checking Developer Mode...")



    try:

        os.startfile("ms-settings:developers")

        time.sleep(5)



        control = find_developer_mode_switch()



        if control is None:

            print("CompAI: Could not locate the Developer Mode switch.")

            return



        state = get_ui_developer_mode_state(control)



        if state is True:

            print("CompAI: Developer Mode is ON.")

        elif state is False:

            print("CompAI: Developer Mode is OFF.")

        else:

            print("CompAI: Could not read the switch state.")



    except Exception as error:

        print("CompAI: Status check failed:", error)





# DEVELOPER MODE CONTROL

def open_developer_settings(action=""):

    if platform.system() != "Windows":

        print("CompAI: Developer Settings requires Windows.")

        return



    if not PYWinAUTO_AVAILABLE:

        print("CompAI: Please install pywinauto first.")

        return



    if not PYAUTOGUI_AVAILABLE:

        print("CompAI: Please install pyautogui first.")

        return



    if action not in ("", "on", "off"):

        return



    target_state = None



    if action == "on":

        target_state = True

        target_name = "ON"

    elif action == "off":

        target_state = False

        target_name = "OFF"



    try:

        print("CompAI: Opening Developer Settings...")

        os.startfile("ms-settings:developers")

        time.sleep(5)



        control = find_developer_mode_switch()



        if control is None:

            print("CompAI: Could not find Developer Mode switch.")

            print("CompAI: No settings were changed.")

            return



        current_state = get_ui_developer_mode_state(control)



        if current_state is None:

            print("CompAI: Could not read the current switch state.")

            print("CompAI: No settings were changed.")

            return



        print(

            "CompAI: Developer Mode is currently",

            "ON." if current_state else "OFF."

        )



        if action == "":

            print("CompAI: Developer Settings opened.")

            return



        if current_state == target_state:

            print("CompAI: Developer Mode is already", target_name + ".")

            return



        rect = control.rectangle()



        x = (rect.left + rect.right) // 2

        y = (rect.top + rect.bottom) // 2



        print("CompAI: Developer Mode switch found.")

        print("CompAI: Moving pointer to the switch...")



        pyautogui.moveTo(x, y, duration=1.5)



        print("CompAI: Pointer moved successfully!")

        print()

        print("Requested change:", target_name)

        print("Current state:", "ON" if current_state else "OFF")



        control = find_developer_mode_switch()



        if control is None:

            print("CompAI: Switch disappeared. Nothing was clicked.")

            return



        latest_state = get_ui_developer_mode_state(control)



        if latest_state is None:

            print("CompAI: Could not verify the switch before clicking.")

            return



        if latest_state == target_state:

            print("CompAI: The requested state is already active.")

            return



        print("CompAI: Clicking Developer Mode switch...")

        control.click_input()



        print("CompAI: Waiting for Windows...")

        time.sleep(5)



        updated_control = find_developer_mode_switch()



        if updated_control is None:

            print("CompAI: Could not find the switch after clicking.")

            return



        new_state = get_ui_developer_mode_state(updated_control)



        if new_state is None:

            print("CompAI: Could not verify the final state.")



        elif new_state == target_state:

            print("CompAI: Developer Mode successfully changed!")

            print("CompAI: New state:", target_name)



        else:

            print("CompAI: The requested state was not reached.")

            print("CompAI: Windows may require confirmation.")

            print(

                "CompAI: Current state:",

                "ON" if new_state else "OFF"

            )



    except Exception as error:

        print("CompAI: Developer Mode operation failed:", error)





# WALLPAPER

def change_wallpaper(path):

    if platform.system() != "Windows":

        print("CompAI: Wallpaper control requires Windows.")

        return



    path = path.strip().strip('"')



    if not os.path.isfile(path):

        print("CompAI: Image file not found!")

        return



    extensions = (".jpg", ".jpeg", ".png", ".bmp")



    if not path.lower().endswith(extensions):

        print("CompAI: Unsupported image format!")

        return



    confirm = input("CompAI: Change wallpaper? (yes/no): ")



    if confirm.strip().lower() != "yes":

        print("CompAI: Cancelled.")

        return



    try:

        result = ctypes.windll.user32.SystemParametersInfoW(

            20,

            0,

            os.path.abspath(path),

            3

        )



        if result:

            print("CompAI: Wallpaper changed!")

        else:

            print("CompAI: Windows could not change wallpaper.")



    except Exception as error:

        print("CompAI: Wallpaper change failed:", error)





# FILE PICKER

def select_share_file():

    try:

        import tkinter as tk

        from tkinter import filedialog



        root = tk.Tk()

        root.withdraw()

        root.attributes("-topmost", True)



        print("CompAI: Opening file selection...")

        path = filedialog.askopenfilename(

            title="Select a file to share"

        )



        root.destroy()



        if not path:

            print("CompAI: File selection cancelled.")

            return None



        if not os.path.isfile(path):

            print("CompAI: Selected file does not exist.")

            return None



        return os.path.abspath(path)



    except Exception as error:

        print("CompAI: File selection failed:", error)

        return None





# GMAIL CONNECTION

def get_gmail_service():

    if not GMAIL_AVAILABLE:

        print("CompAI: Gmail libraries are not installed.")

        print("CompAI: Run the Gmail library installation command.")

        return None



    if not os.path.isfile(CREDENTIALS_FILE):

        print("CompAI: credentials.json is missing.")

        return None



    if not os.path.isfile(TOKEN_FILE):

        print("CompAI: token.json is missing.")

        print("CompAI: Run test_gmail.py to authorize Gmail first.")

        return None



    try:

        creds = Credentials.from_authorized_user_file(

            TOKEN_FILE,

            GMAIL_SCOPES

        )



        if creds.expired and creds.refresh_token:

            print("CompAI: Refreshing Gmail authorization...")

            creds.refresh(Request())



            with open(TOKEN_FILE, "w", encoding="utf-8") as token:

                token.write(creds.to_json())



        if not creds.valid:

            print("CompAI: Gmail authorization is invalid.")

            print("CompAI: Run test_gmail.py again.")

            return None



        service = build(

            "gmail",

            "v1",

            credentials=creds,

            cache_discovery=False

        )



        return service



    except Exception as error:

        print("CompAI: Gmail connection failed:", error)

        return None





# EMAIL VALIDATION

def valid_email_address(address):

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    return re.match(pattern, address) is not None





# GMAIL SEND



def share_by_email():

    import html



    print("\n========== COMPAI EMAIL SHARE ==========")



    if not GMAIL_AVAILABLE:

        print("CompAI: Gmail libraries are unavailable.")

        return



    # Recipient

    recipient = input(

        "CompAI: Recipient email address: "

    ).strip()



    if not valid_email_address(recipient):

        print("CompAI: Invalid email address.")

        return



    # Email title

    title = input(

        "CompAI: Enter the email title: "

    ).strip()



    if not title:

        print("CompAI: A title is required.")

        return



    # Email subject

    subject = input(

        "CompAI: Enter the email subject: "

    ).strip()



    if not subject:

        print("CompAI: A subject is required.")

        return



    # Email description

    description = input(

        "CompAI: Enter the email description: "

    ).strip()



    if not description:

        print("CompAI: A description is required.")

        return



    # Optional attachment

    file_path = None



    print()

    attach_choice = input(

        "CompAI: Would you like to attach a picture or file? (yes/no): "

    ).strip().lower()



    if attach_choice == "yes":

        file_path = select_share_file()



        if not file_path:

            continue_without_file = input(

                "CompAI: Continue without an attachment? (yes/no): "

            ).strip().lower()



            if continue_without_file != "yes":

                print("CompAI: Email cancelled.")

                return



    elif attach_choice != "no":

        print("CompAI: Please answer yes or no.")

        return



    file_name = None

    file_size = 0



    # Check optional attachment

    if file_path:

        file_name = os.path.basename(file_path)

        file_size = os.path.getsize(file_path)



        if file_size == 0:

            print("CompAI: The selected file is empty.")

            return



        if file_size > 20 * 1024 * 1024:

            print("CompAI: File is too large.")

            print("CompAI: Please choose a file smaller than 20 MB.")

            return



    # Build email

    message = EmailMessage()

    message["To"] = recipient

    message["From"] = "me"

    message["Subject"] = subject



    # Plain text version

    message.set_content(

        title + "\n"

        + "=" * len(title)

        + "\n\n"

        + description

    )



    # HTML version with a prominent title

    safe_title = html.escape(title)

    safe_description = html.escape(description).replace(

        "\n", "<br>"

    )



    html_body = f"""

    <!DOCTYPE html>

    <html>

    <body>

        <h2>{safe_title}</h2>

        <p>{safe_description}</p>

        <hr>

        <p>Sent using CompAI.</p>

    </body>

    </html>

    """



    message.add_alternative(html_body, subtype="html")



    # Attach file only when one was selected

    if file_path:

        mime_type, encoding = mimetypes.guess_type(file_path)



        if mime_type is None or encoding is not None:

            mime_type = "application/octet-stream"



        main_type, sub_type = mime_type.split("/", 1)



        try:

            with open(file_path, "rb") as attachment:

                message.add_attachment(

                    attachment.read(),

                    maintype=main_type,

                    subtype=sub_type,

                    filename=file_name

                )



        except Exception as error:

            print("CompAI: Attachment failed:", error)

            return



    # Email preview

    print()

    print("========== EMAIL PREVIEW ==========")

    print("Recipient:", recipient)

    print("Title:", title)

    print("Subject:", subject)

    print("Description:", description)



    if file_name:

        print("Attachment:", file_name)

        print("File size:", round(file_size / 1024, 2), "KB")

    else:

        print("Attachment: None")



    print("===================================")



    # Final confirmation

    confirm = input(

        "CompAI: Send this email? (yes/no): "

    ).strip().lower()



    if confirm != "yes":

        print("CompAI: Email cancelled.")

        return



    # Countdown

    print()

    print("CompAI: Auto sending in 3 seconds...")

    print("CompAI: Please wait.")



    for remaining in range(3, 0, -1):

        print("CompAI:", remaining)

        time.sleep(1)



    # Gmail API connection

    print("CompAI: Connecting to Gmail...")



    service = get_gmail_service()



    if service is None:

        print("CompAI: Email was not sent.")

        return



    # Send email

    try:

        raw_message = base64.urlsafe_b64encode(

            message.as_bytes()

        ).decode("utf-8")



        result = service.users().messages().send(

            userId="me",

            body={"raw": raw_message}

        ).execute()



        print()

        print("<COMPAI EMAIL SENT>")

        print("CompAI: Email successfully sent!")

        print("Recipient:", recipient)

        print("Title:", title)

        print("Subject:", subject)

        print(

            "Attachment:",

            file_name if file_name else "None"

        )

        print("Gmail message ID:", result.get("id"))



    except HttpError as error:

        print("CompAI: Gmail rejected the email:", error)



    except Exception as error:

        print("CompAI: Email sending failed:", error)





# WINDOWS NEARBY SHARING



def share_nearby():

    if platform.system() != "Windows":

        print("CompAI: Nearby Sharing requires Windows.")

        return



    if not PYWinAUTO_AVAILABLE:

        print("CompAI: pywinauto is required for Share automation.")

        return



    print("\n========== COMPAI NEARBY SHARE ==========")



    file_path = select_share_file()



    if not file_path:

        return



    file_name = os.path.basename(file_path)



    print()

    print("Selected file:", file_name)



    confirm = input(

        "CompAI: Open Windows Share for this file? (yes/no): "

    ).strip().lower()



    if confirm != "yes":

        print("CompAI: Nearby sharing cancelled.")

        return



    try:

        desktop = Desktop(backend="uia")



        # Remember existing Explorer windows.

        before_handles = set()



        for window in desktop.windows():

            try:

                if window.element_info.class_name in (

                    "CabinetWClass",

                    "ExploreWClass"

                ):

                    before_handles.add(window.handle)

            except Exception:

                continue



        # Open File Explorer with the selected file highlighted.

        print("CompAI: Opening File Explorer...")



        subprocess.Popen([

            "explorer.exe",

            "/select,",

            file_path

        ])



        explorer = None



        # Find the Explorer window opened for this file.

        for attempt in range(20):

            windows = desktop.windows()

            explorer_windows = []



            for window in windows:

                try:

                    class_name = window.element_info.class_name



                    if class_name in (

                        "CabinetWClass",

                        "ExploreWClass"

                    ):

                        explorer_windows.append(window)



                except Exception:

                    continue



            # Prefer a newly opened Explorer window.

            new_windows = [

                window for window in explorer_windows

                if window.handle not in before_handles

            ]



            if new_windows:

                explorer = new_windows[-1]

                break



            # Otherwise, look for the selected filename.

            for window in explorer_windows:

                try:

                    for control in window.descendants():

                        name = control.element_info.name



                        if name and name.casefold() == file_name.casefold():

                            explorer = window

                            break



                    if explorer is not None:

                        break



                except Exception:

                    continue



            if explorer is not None:

                break



            time.sleep(0.5)



        if explorer is None:

            print("CompAI: Could not locate the Explorer window.")

            print("CompAI: Open File Explorer and select the file manually.")

            return



        explorer.set_focus()

        time.sleep(1)



        # Find and open the Share ribbon tab.

        share_tab = None



        for control in explorer.descendants():

            try:

                control_type = control.element_info.control_type

                name = (

                    control.element_info.name

                    or control.window_text()

                )



                if (

                    control_type == "TabItem"

                    and name.strip().casefold() == "share"

                    and control.is_visible()

                    and control.is_enabled()

                ):

                    share_tab = control

                    break



            except Exception:

                continue



        if share_tab is not None:

            print("CompAI: Opening the Share tab...")

            share_tab.click_input()



        elif PYAUTOGUI_AVAILABLE:

            print("CompAI: Trying the Share keyboard shortcut...")

            pyautogui.hotkey("alt", "s")



        else:

            print("CompAI: Could not find the Share tab.")

            print("CompAI: Click the Share tab manually in Explorer.")

            return



        time.sleep(1)



        # Find the actual Share button.

        share_button = None



        for control in explorer.descendants():

            try:

                control_type = control.element_info.control_type

                name = (

                    control.element_info.name

                    or control.window_text()

                )



                if (

                    control_type == "Button"

                    and name.strip().casefold() == "share"

                    and control.is_visible()

                    and control.is_enabled()

                ):

                    share_button = control

                    break



            except Exception:

                continue



        if share_button is None:

            print("CompAI: Could not locate the Share button.")

            print("CompAI: Your file is selected in File Explorer.")

            print("CompAI: Click Share manually to continue.")

            return



        print("CompAI: Opening Windows Share...")

        share_button.click_input()



        print()

        print("<COMPAI WINDOWS SHARE OPENED>")

        print("CompAI: Select Nearby Sharing if it is available.")

        print("CompAI: Choose the receiving device.")

        print("CompAI: The receiving device must accept the transfer.")



    except Exception as error:

        print("CompAI: Nearby Sharing failed:", error)





# COMPAI SHARE MENU

def compai_share(method=""):

    if method == "email":

        share_by_email()

        return



    if method == "nearby":

        share_nearby()

        return



    print("\n========== COMPAI SHARE ==========")

    print("1. Share by email (Gmail)")

    print("2. Share with a nearby device")

    print("3. Cancel")



    choice = input("CompAI: Choose a sharing method: ").strip()



    if choice == "1":

        share_by_email()



    elif choice == "2":

        share_nearby()



    elif choice == "3":

        print("CompAI: Sharing cancelled.")



    else:

        print("CompAI: Invalid sharing option.")



# COMPAI APP LAUNCHER



def show_available_apps():

    print("\n========== COMPAI APP LAUNCHER ==========")

    print("Web browsers:")

    print("  chrome")

    print("  edge")

    print("  firefox")

    print()

    print("Development:")

    print("  vscode")

    print("  obs")

    print("  vlc")

    print()

    print("Communication:")

    print("  discord")

    print()

    print("Other applications:")

    print("  steam")

    print("  spotify")

    print("  calculator")

    print("  notepad")

    print("  paint")

    print("  explorer")

    print("  settings")

    print("  task manager")

    print("  terminal")

    print("  powershell")

    print("  command prompt")

    print("========================================")





def launch_application(app_name):

    if platform.system() != "Windows":

        print("CompAI: App Launcher currently requires Windows.")

        return



    app_name = " ".join(app_name.strip().lower().split())



    if not app_name:

        print("CompAI: Please specify an application.")

        return



    aliases = {

        "google chrome": "chrome",

        "visual studio code": "vscode",

        "vs code": "vscode",

        "code": "vscode",

        "microsoft edge": "edge",

        "ms edge": "edge",

        "file explorer": "explorer",

        "calc": "calculator",

        "cmd": "command prompt"

    }



    app_name = aliases.get(app_name, app_name)



    local = os.environ.get("LOCALAPPDATA", "")

    program_files = os.environ.get("PROGRAMFILES", r"C:\Program Files")

    program_files_x86 = os.environ.get(

        "PROGRAMFILES(X86)", r"C:\Program Files (x86)"

    )



    # Build application locations.

    applications = {

        "chrome": [

            "chrome.exe",

            os.path.join(

                program_files,

                "Google", "Chrome", "Application", "chrome.exe"

            ),

            os.path.join(

                program_files_x86,

                "Google", "Chrome", "Application", "chrome.exe"

            ),

            os.path.join(

                local,

                "Google", "Chrome", "Application", "chrome.exe"

            )

        ],



        "vscode": [

            "code.exe",

            os.path.join(

                local, "Programs", "Microsoft VS Code", "Code.exe"

            ),

            os.path.join(

                program_files, "Microsoft VS Code", "Code.exe"

            ),

            os.path.join(

                program_files_x86, "Microsoft VS Code", "Code.exe"

            )

        ],



        "edge": [

            "msedge.exe",

            os.path.join(

                program_files_x86,

                "Microsoft", "Edge", "Application", "msedge.exe"

            ),

            os.path.join(

                program_files,

                "Microsoft", "Edge", "Application", "msedge.exe"

            )

        ],



        "firefox": [

            "firefox.exe",

            os.path.join(

                program_files, "Mozilla Firefox", "firefox.exe"

            ),

            os.path.join(

                program_files_x86, "Mozilla Firefox", "firefox.exe"

            )

        ],



        "calculator": ["calc.exe"],

        "notepad": ["notepad.exe"],

        "paint": ["mspaint.exe"],

        "explorer": ["explorer.exe"],

        "task manager": ["taskmgr.exe"],

        "terminal": ["wt.exe"],

        "powershell": ["powershell.exe"],

        "command prompt": ["cmd.exe"],



        "steam": [

            "steam.exe",

            os.path.join(

                program_files_x86, "Steam", "steam.exe"

            ),

            os.path.join(

                program_files, "Steam", "steam.exe"

            )

        ],



        "spotify": [

            "Spotify.exe",

            os.path.join(

                local, "Microsoft", "WindowsApps", "Spotify.exe"

            )

        ],



        "obs": [

            "obs64.exe",

            os.path.join(

                program_files,

                "obs-studio", "bin", "64bit", "obs64.exe"

            )

        ],



        "vlc": [

            "vlc.exe",

            os.path.join(

                program_files, "VideoLAN", "VLC", "vlc.exe"

            ),

            os.path.join(

                program_files_x86, "VideoLAN", "VLC", "vlc.exe"

            )

        ]

    }



    # Windows Settings uses a special URI.

    if app_name == "settings":

        try:

            print("CompAI: Opening Windows Settings...")

            os.startfile("ms-settings:")

            print("CompAI: Settings opened successfully!")

        except Exception as error:

            print("CompAI: Could not open Settings:", error)

        return



    if app_name == "discord":

        discord_folder = os.path.join(local, "Discord")



        discord_candidates = []



        if os.path.isdir(discord_folder):

            try:

                for folder in os.listdir(discord_folder):

                    if folder.lower().startswith("app-"):

                        discord_candidates.append(

                            os.path.join(

                                discord_folder,

                                folder,

                                "Discord.exe"

                            )

                        )

            except OSError:

                pass



        discord_candidates.append("Discord.exe")

        applications["discord"] = discord_candidates



    if app_name not in applications:

        print("CompAI: I don't recognise that application.")

        print("CompAI: Type 'apps' to see supported applications.")

        return



    print("CompAI: Searching for", app_name + "...")



    for candidate in applications[app_name]:

        try:

            if os.path.isfile(candidate):

                executable = candidate

            else:

                executable = shutil.which(candidate)



            if executable:

                subprocess.Popen([executable])



                print("CompAI: Launching", app_name + "...")

                print("CompAI: Application opened successfully!")

                return



        except Exception as error:

            print("CompAI: Could not launch this location:", error)



    # Discord's updater can also launch Discord.

    if app_name == "discord":

        updater = os.path.join(

            local, "Discord", "Update.exe"

        )



        if os.path.isfile(updater):

            try:

                subprocess.Popen([

                    updater,

                    "--processStart",

                    "Discord.exe"

                ])



                print("CompAI: Launching Discord...")

                return



            except Exception as error:

                print("CompAI: Discord launch failed:", error)



    print("CompAI: Could not find", app_name + ".")

    print("CompAI: Make sure it is installed on your PC.")



# COMPAI PC MONITORING



def show_pc_monitor(section="all"):

    try:

        import psutil

    except ImportError:

        print("CompAI: psutil is not installed.")

        print("CompAI: Run python -m pip install psutil")

        return



    print("\n================================")

    print("       COMPAI PC MONITOR")

    print("================================")



    # CPU MONITORING

    if section in ("all", "cpu"):

        try:

            print("\n[ CPU INFORMATION ]")



            cpu_usage = psutil.cpu_percent(interval=1)

            physical_cores = psutil.cpu_count(logical=False)

            logical_cores = psutil.cpu_count(logical=True)



            print("CPU Usage:", str(cpu_usage) + "%")

            print("Physical Cores:", physical_cores or "Unknown")

            print("Logical Cores:", logical_cores or "Unknown")



        except Exception as error:

            print("CompAI: CPU monitoring failed:", error)



    # RAM MONITORING

    if section in ("all", "memory"):

        try:

            print("\n[ MEMORY INFORMATION ]")



            memory = psutil.virtual_memory()



            total = memory.total / (1024 ** 3)

            used = memory.used / (1024 ** 3)

            available = memory.available / (1024 ** 3)



            print("Total RAM:", round(total, 2), "GB")

            print("Used RAM:", round(used, 2), "GB")

            print("Available RAM:", round(available, 2), "GB")

            print("RAM Usage:", str(memory.percent) + "%")



        except Exception as error:

            print("CompAI: Memory monitoring failed:", error)



    # DISK MONITORING

    if section in ("all", "disk"):

        try:

            print("\n[ DISK INFORMATION ]")



            system_drive = os.environ.get("SystemDrive", "C:")

            drive_path = system_drive + "\\"



            disk = psutil.disk_usage(drive_path)



            total = disk.total / (1024 ** 3)

            used = disk.used / (1024 ** 3)

            free = disk.free / (1024 ** 3)



            print("Drive:", system_drive)

            print("Total Space:", round(total, 2), "GB")

            print("Used Space:", round(used, 2), "GB")

            print("Free Space:", round(free, 2), "GB")

            print("Disk Usage:", str(disk.percent) + "%")



        except Exception as error:

            print("CompAI: Disk monitoring failed:", error)



    # BATTERY MONITORING

    if section in ("all", "battery"):

        try:

            print("\n[ BATTERY INFORMATION ]")



            battery = psutil.sensors_battery()



            if battery is None:

                print("Battery: Not detected")

            else:

                print("Battery Level:", str(battery.percent) + "%")



                if battery.power_plugged:

                    print("Power Status: Plugged in")

                else:

                    print("Power Status: Running on battery")



                if (

                    battery.secsleft >= 0

                    and battery.secsleft

                    not in (

                        psutil.POWER_TIME_UNKNOWN,

                        psutil.POWER_TIME_UNLIMITED

                    )

                ):

                    hours = battery.secsleft // 3600

                    minutes = (battery.secsleft % 3600) // 60



                    print(

                        "Estimated Remaining Time:",

                        str(hours) + " hours",

                        str(minutes) + " minutes"

                    )



        except Exception as error:

            print("CompAI: Battery monitoring unavailable:", error)



    print("\n================================")

    print("PC monitoring completed!")

    print("================================")



# COMPAI PROCESS MONITOR



def show_process_monitor(view="all"):

    try:

        import psutil

    except ImportError:

        print("CompAI: psutil is not installed.")

        return



    print("\n================================")

    print("      COMPAI PROCESS MONITOR")

    print("================================")



    processes = []

    logical_cpus = psutil.cpu_count() or 1



    print("CompAI: Collecting running processes...")

        # Collect process information.

    for process in psutil.process_iter(["pid", "name"]):

        try:

            info = process.info



            process_name = info["name"] or "Unknown"



            # Exclude Windows' idle process from CPU rankings.

            if (

                info["pid"] == 0

                or process_name.casefold() == "system idle process"

            ):

                continue



            process_id = info["pid"]

            memory_used = process.memory_info().rss



            cpu_usage = 0.0



            # Initialize CPU sampling when required.

            if view in ("all", "cpu"):

                process.cpu_percent(interval=None)



            processes.append({

                "process": process,

                "name": process_name,

                "pid": process_id,

                "memory": memory_used,

                "cpu": cpu_usage

            })



        except (psutil.NoSuchProcess, psutil.AccessDenied):

            continue









        except Exception:

            continue



    # Measure CPU usage over one second.

    if view in ("all", "cpu"):

        print("CompAI: Measuring CPU usage...")

        time.sleep(1)



        for item in processes:

            try:

                raw_cpu = item["process"].cpu_percent(interval=None)



                # Express CPU use relative to total logical CPU capacity.

                item["cpu"] = raw_cpu / logical_cpus



            except (psutil.NoSuchProcess, psutil.AccessDenied):

                item["cpu"] = 0.0



            except Exception:

                item["cpu"] = 0.0



    def display_processes(title, items, metric):

        print("\n[" + title + "]")

        print("-" * 65)

        print("{:<5} {:<27} {:<10} {}".format(

            "RANK", "PROCESS", "PID", metric.upper()

        ))

        print("-" * 65)



        for rank, item in enumerate(items[:10], start=1):

            name = item["name"][:25]



            if metric == "CPU":

                value = "{:.1f}%".format(item["cpu"])



            else:

                memory_mb = item["memory"] / (1024 * 1024)

                value = "{:.1f} MB".format(memory_mb)



            print("{:<5} {:<27} {:<10} {}".format(

                rank,

                name,

                item["pid"],

                value

            ))



        if not items:

            print("No processes were found.")



        print("-" * 65)



    # TOP CPU PROCESSES

    if view in ("all", "cpu"):

        cpu_sorted = sorted(

            processes,

            key=lambda item: item["cpu"],

            reverse=True

        )



        display_processes(

            "TOP 10 CPU PROCESSES",

            cpu_sorted,

            "CPU"

        )



    # TOP MEMORY PROCESSES

    if view in ("all", "memory"):

        memory_sorted = sorted(

            processes,

            key=lambda item: item["memory"],

            reverse=True

        )



        display_processes(

            "TOP 10 MEMORY PROCESSES",

            memory_sorted,

            "MEMORY"

        )



    print("\nTotal processes detected:", len(processes))

    print("CompAI: Process scan completed!")

    print("================================")



# COMPAI VOICE COMMANDS





# COMPAI WHISPER VOICE COMMANDS



_WHISPER_MODEL = None





def listen_for_voice_command():

    global _WHISPER_MODEL



    if platform.system() != "Windows":

        print("CompAI: Voice commands require Windows.")

        return None



    try:

        import sounddevice as sd

        import soundfile as sf

        import tempfile

        from faster_whisper import WhisperModel



    except ImportError as error:

        print("CompAI: Voice libraries are missing:", error)

        print(

            "CompAI: Install them with:"

            " python -m pip install faster-whisper sounddevice soundfile"

        )

        return None



    print("\n========== COMPAI WHISPER VOICE ==========")



    try:

        # Load the model only once.

        if _WHISPER_MODEL is None:

            print("CompAI: Loading Whisper base.en model...")

            print("CompAI: This may take a moment the first time.")



            _WHISPER_MODEL = WhisperModel(

                "base.en",

                device="cpu",

                compute_type="int8",

                cpu_threads=4

            )



            print("CompAI: Whisper is ready!")



        # Check the microphone.

        microphone = sd.query_devices(kind="input")

        print("CompAI: Microphone:", microphone["name"])



        sample_rate = 16000

        recording_seconds = 6



        print()

        print("CompAI: Microphone activated.")

        print("CompAI: Speak your command now!")

        print("CompAI: Recording for", recording_seconds, "seconds...")



        # Record the voice.

        recording = sd.rec(

            int(recording_seconds * sample_rate),

            samplerate=sample_rate,

            channels=1,

            dtype="float32"

        )



        sd.wait()



        # Check whether the recording contains enough audio.

        peak_level = float(abs(recording).max())



        if peak_level < 0.005:

            print("CompAI: Your microphone recording is too quiet.")

            return None



        # Save temporary audio for Whisper.

        with tempfile.TemporaryDirectory() as temp_folder:

            audio_path = os.path.join(

                temp_folder,

                "compai_voice.wav"

            )



            sf.write(

                audio_path,

                recording,

                sample_rate

            )



            print()

            print("CompAI: Understanding your speech...")



            segments, info = _WHISPER_MODEL.transcribe(

                audio_path,

                language="en",

                beam_size=5,

                vad_filter=True,

                condition_on_previous_text=False

            )



            segments = list(segments)



        # Combine the recognised segments.

        spoken_text = " ".join(

            segment.text.strip()

            for segment in segments

        ).strip()



        if not spoken_text:

            print("CompAI: I couldn't understand that command.")

            return None



        print()

        print("CompAI heard:", spoken_text)



        # Normalise the transcription.

        spoken_command = " ".join(

            spoken_text.lower().strip().split()

        )



        spoken_command = spoken_command.strip(

            " .,!?:;"

        )



        # Friendly voice-command aliases.

        aliases = {

            "check my pc": "monitor",

            "check pc": "monitor",

            "show processes": "processes",

            "show cpu": "cpu",

            "show memory": "memory",

            "show disk": "disk",

            "show battery": "battery",

            "wake off": "wake off",

            "developer mode": "developer mode",

        }



        spoken_command = aliases.get(

            spoken_command,

            spoken_command

        )



        # Only allow recognised CompAI commands.

        allowed_commands = {

            "apps",

            "help",

            "status",

            "monitor",

            "pc status",

            "cpu",

            "memory",

            "ram",

            "disk",

            "battery",

            "processes",

            "top cpu",

            "top memory",

            "share",

            "share email",

            "share nearby",

            "developer mode",

            "developer mode status"

        }



        allowed_apps = {

            "chrome",

            "google chrome",

            "edge",

            "microsoft edge",

            "firefox",

            "vscode",

            "visual studio code",

            "vs code",

            "discord",

            "calculator",

            "calc",

            "notepad",

            "paint",

            "explorer",

            "file explorer",

            "settings",

            "steam",

            "spotify",

            "obs",

            "vlc",

            "task manager",

            "terminal",

            "powershell",

            "command prompt",

            "cmd"

        }



        valid_command = (

            spoken_command in allowed_commands

        )



        # Allow opening only recognised applications.

        if spoken_command.startswith("open "):

            app_name = spoken_command[5:].strip()

            valid_command = app_name in allowed_apps



        # Allow Google searches.

        if spoken_command.startswith("search "):

            search_text = spoken_command[7:].strip()



            valid_command = (

                len(search_text) > 0

                and len(search_text) <= 200

            )



        if not valid_command:

            print("CompAI: That isn't a supported voice command.")

            print("CompAI: Please try speaking more clearly.")

            return None



        print("CompAI: Voice command accepted!")

        print("=========================================")



        return spoken_command



    except Exception as error:

        print("CompAI: Whisper voice recognition failed:", error)

        return None



# COMPAI WAKE WORD ACTIVATION



def execute_voice_command(spoken_command):

    command = spoken_command.lower().strip()



    print("\nCompAI: Executing:", command)



    if command == "wake off":

        print("CompAI: Wake listening disabled.")

        return False



    elif command == "help":

        show_help()



    elif command == "apps":

        show_available_apps()



    elif command.startswith("open "):

        launch_application(command[5:].strip())



    elif command.startswith("search "):

        search_google(command[7:].strip())



    elif command in ("monitor", "pc status"):

        show_pc_monitor()



    elif command == "cpu":

        show_pc_monitor("cpu")



    elif command in ("memory", "ram"):

        show_pc_monitor("memory")



    elif command == "disk":

        show_pc_monitor("disk")



    elif command == "battery":

        show_pc_monitor("battery")



    elif command == "processes":

        show_process_monitor()



    elif command == "top cpu":

        show_process_monitor("cpu")



    elif command == "top memory":

        show_process_monitor("memory")



    elif command == "status":

        system_status()



    elif command == "developer mode":

        open_developer_settings()



    elif command == "developer mode status":

        developer_mode_status()



    elif command == "share":

        compai_share()



    elif command == "share email":

        compai_share("email")



    elif command == "share nearby":

        compai_share("nearby")



    else:

        print("CompAI: Unsupported voice command.")



    return True





def run_wake_mode():

    import json

    import queue



    try:

        import sounddevice as sd

        from vosk import Model, KaldiRecognizer, SetLogLevel



    except ImportError as error:

        print("CompAI: Wake-word libraries are missing:", error)

        return



    model_path = os.path.join(

        BASE_DIR,

        "models",

        "vosk-model-small-en-us-0.15"

    )



    if not os.path.isdir(model_path):

        print("CompAI: Vosk model not found.")

        return



    try:

        print("\n========== COMPAI WAKE MODE ==========")

        print("CompAI: Loading wake-word model...")



        SetLogLevel(-1)

        model = Model(model_path)



        microphone = sd.query_devices(kind="input")



        print("CompAI: Microphone:", microphone["name"])

        print()

        print("CompAI: Wake listening is ACTIVE.")

        print('CompAI: Say "Hey computer!" to activate me.')

        print('CompAI: Say "wake off" after activation to disable.')

        print("CompAI: Press Ctrl+C to leave wake mode.")

        print()

        print("CompAI: Listening locally. No audio is uploaded.")



        while True:

            audio_queue = queue.Queue(maxsize=30)



            def audio_callback(indata, frames, time_info, status):

                try:

                    audio_queue.put_nowait(bytes(indata))

                except queue.Full:

                    # Skip a chunk if processing falls behind.

                    pass



            recognizer = KaldiRecognizer(

                model,

                16000,

                json.dumps(["hey computer"])

            )



            wake_detected = False



            print("\nCompAI: Waiting for wake phrase...")



            # Release this stream before Whisper starts recording.

            with sd.RawInputStream(

                samplerate=16000,

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

                            re.findall(

                                r"[a-z]+",

                                spoken.lower()

                            )

                        )



                        if normalized == "hey computer":

                            wake_detected = True

                            break



            if not wake_detected:

                continue



            # Wake phrase detected.

            try:

                import winsound

                winsound.Beep(880, 180)

            except Exception:

                pass



            print()

            print("====================================")

            print("CompAI: Yes? I'm listening.")

            print("====================================")



            # The Vosk stream is closed before Whisper records.

            spoken_command = listen_for_voice_command()



            if not spoken_command:

                print("CompAI: I didn't get a command.")

                continue



            if spoken_command == "wake off":

                print("CompAI: Wake listening disabled.")

                break



            # Execute only commands accepted by Whisper's allow-list.

            keep_running = execute_voice_command(spoken_command)



            if not keep_running:

                break



    except KeyboardInterrupt:

        print("\nCompAI: Wake mode stopped by keyboard interrupt.")



    except Exception as error:

        print("CompAI: Wake mode failed:", error)



    finally:

        print("CompAI: Wake-word listener is OFF.")





# CAPABILITY DETECTION

def system_status():

    print("\n================================")

    print("       COMPAI SYSTEM STATUS")

    print("================================")



    print("Operating System:", platform.system())

    print("OS Version:", platform.version())

    print("Python Version:", sys.version.split()[0])



    if PYAUTOGUI_AVAILABLE:

        try:

            width, height = pyautogui.size()

            position = pyautogui.position()



            print("Mouse Control: READY")

            print("Screen Resolution:", str(width) + "x" + str(height))

            print("Current Mouse Position:", position)

            print("Keyboard Control: LIBRARY READY")



        except Exception as error:

            print("Mouse Control: CHECK FAILED")

            print("Keyboard Control: NOT VERIFIED")

            print("Details:", error)



    else:

        print("Mouse Control: UNAVAILABLE")

        print("Keyboard Control: UNAVAILABLE")



    if PYWinAUTO_AVAILABLE:

        print("Windows UI Automation: READY")

    else:

        print("Windows UI Automation: UNAVAILABLE")



    if GMAIL_AVAILABLE:

        print("Gmail API Library: READY")

    else:

        print("Gmail API Library: UNAVAILABLE")



    print(

        "Gmail Credentials:",

        "FOUND" if os.path.isfile(CREDENTIALS_FILE) else "MISSING"

    )



    print(

        "Gmail Authorization:",

        "FOUND" if os.path.isfile(TOKEN_FILE) else "MISSING"

    )



    if platform.system() == "Windows":

        try:

            ctypes.windll.user32.SystemParametersInfoW

            print("Wallpaper Control: WINDOWS API FOUND")

        except Exception:

            print("Wallpaper Control: UNAVAILABLE")

    else:

        print("Wallpaper Control: NOT SUPPORTED")



    chrome_paths = []



    for variable in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):

        folder = os.environ.get(variable)



        if folder:

            chrome_paths.append(

                os.path.join(

                    folder,

                    "Google",

                    "Chrome",

                    "Application",

                    "chrome.exe"

                )

            )



    chrome_found = shutil.which("chrome") is not None



    if not chrome_found:

        chrome_found = any(

            os.path.isfile(path) for path in chrome_paths

        )



    print(

        "Google Chrome:",

        "FOUND" if chrome_found else "NOT FOUND"

    )



    print("Internet Connection: CHECKING...")



    try:

        request = urllib.request.Request(

            "https://www.google.com/generate_204",

            headers={"User-Agent": "CompAI/" + VERSION}

        )



        with urllib.request.urlopen(request, timeout=4):

            print("Internet Connection: AVAILABLE")



    except Exception:

        print("Internet Connection: NOT VERIFIED")



    print("\nDeveloper Mode:")



    if platform.system() == "Windows" and PYWinAUTO_AVAILABLE:

        print("Status: Use 'developer mode status' to check")

    else:

        print("Status: UI AUTOMATION UNAVAILABLE")



    print("================================")

    print("Capability check completed!")

# ==========================================
# COMPAI FILE MANAGEMENT
# ==========================================

def resolve_file_path(path):
    """Resolve common Windows folders and user-supplied paths."""

    path = os.path.expandvars(
        os.path.expanduser(path.strip().strip('"').strip("'"))
    )

    home = os.path.expanduser("~")

    known_folders = {
        "desktop": os.path.join(home, "Desktop"),
        "documents": os.path.join(home, "Documents"),
        "downloads": os.path.join(home, "Downloads"),
        "pictures": os.path.join(home, "Pictures"),
        "music": os.path.join(home, "Music"),
        "videos": os.path.join(home, "Videos"),
    }

    if path.lower() in known_folders:
        return known_folders[path.lower()]

    return os.path.abspath(path)


def open_managed_path(path, expect_file=None):
    """Open a file or folder using its Windows default application."""

    path = resolve_file_path(path)

    if not os.path.exists(path):
        print("CompAI: That path does not exist.")
        return

    if expect_file is True and not os.path.isfile(path):
        print("CompAI: That path is not a file.")
        return

    if expect_file is False and not os.path.isdir(path):
        print("CompAI: That path is not a folder.")
        return

    if platform.system() != "Windows":
        print("CompAI: This feature currently requires Windows.")
        return

    try:
        os.startfile(path)
        print("CompAI: Opening:", path)

    except Exception as error:
        print("CompAI: Could not open that path:", error)


def list_managed_files(folder):
    """List files and folders in a selected directory."""

    folder = resolve_file_path(folder)

    if not os.path.isdir(folder):
        print("CompAI: Folder not found.")
        return

    try:
        entries = sorted(
            os.scandir(folder),
            key=lambda item: (not item.is_dir(), item.name.lower())
        )

        print("\n========== FILE LIST ==========")
        print("Folder:", folder)
        print()

        if not entries:
            print("This folder is empty.")

        for entry in entries[:100]:
            if entry.is_dir():
                print("[Folder] " + entry.name)
            else:
                size = entry.stat().st_size
                print(
                    "[File] " + entry.name
                    + " (" + str(round(size / 1024, 2)) + " KB)"
                )

        if len(entries) > 100:
            print("\nShowing the first 100 entries.")

        print("===============================")

    except OSError as error:
        print("CompAI: Could not list this folder:", error)


def search_managed_files(name, folder):
    """Search for matching filenames inside one selected folder."""

    folder = resolve_file_path(folder)
    name = name.strip().strip('"').strip("'")

    if not os.path.isdir(folder):
        print("CompAI: Search folder not found.")
        return

    if not name:
        print("CompAI: Please provide a filename to search for.")
        return

    print("\nCompAI: Searching inside:", folder)

    matches = []
    visited = 0
    limit = 50

    try:
        for root, directories, files in os.walk(folder):

            visited += 1

            if visited > 5000:
                print("CompAI: Search stopped after reaching its folder limit.")
                break

            for filename in files:
                if name.lower() in filename.lower():
                    matches.append(os.path.join(root, filename))

                    if len(matches) >= limit:
                        break

            if len(matches) >= limit:
                break

        print("\n========== SEARCH RESULTS ==========")

        if matches:
            for match in matches:
                print(match)
        else:
            print("No matching files found.")

        print("Results:", len(matches))
        print("====================================")

    except OSError as error:
        print("CompAI: Search failed:", error)


def create_managed_folder(folder):
    """Create a new folder without overwriting existing folders."""

    folder = resolve_file_path(folder)

    if os.path.exists(folder):
        print("CompAI: A file or folder already exists at that location.")
        return

    try:
        os.makedirs(folder, exist_ok=False)
        print("CompAI: Folder created successfully:")
        print(folder)

    except OSError as error:
        print("CompAI: Could not create the folder:", error)


        

def transfer_managed_file(source, destination, action):
    """Copy or move a file without overwriting existing files."""

    source = resolve_file_path(source)
    destination = resolve_file_path(destination)

    if not os.path.isfile(source):
        print("CompAI: Source file not found.")
        return

    # If destination is a folder, place the file inside it.
    if os.path.isdir(destination):
        destination = os.path.join(
            destination,
            os.path.basename(source)
        )

    if os.path.exists(destination):
        print("CompAI: Destination already exists. Nothing was changed.")
        return

    parent = os.path.dirname(destination)

    if not os.path.isdir(parent):
        print("CompAI: Destination folder does not exist.")
        return

    try:
        if action == "copy":
            shutil.copy2(source, destination)
        elif action == "move":
            shutil.move(source, destination)
        else:
            print("CompAI: Unknown file operation.")
            return

        print("CompAI: File " + action + " completed:")
        print(destination)

    except OSError as error:
        print("CompAI: File operation failed:", error)


def rename_managed_file(source, new_name):
    """Rename a file without overwriting another file."""

    source = resolve_file_path(source)
    new_name = new_name.strip().strip('"').strip("'")

    if not os.path.isfile(source):
        print("CompAI: Source file not found.")
        return

    if not new_name:
        print("CompAI: Please provide a new filename.")
        return

    # A simple filename stays in the original folder.
    if not os.path.dirname(new_name):
        destination = os.path.join(
            os.path.dirname(source),
            new_name
        )
    else:
        destination = resolve_file_path(new_name)

    if os.path.exists(destination):
        print("CompAI: That filename already exists.")
        return

    if not os.path.isdir(os.path.dirname(destination)):
        print("CompAI: Destination folder does not exist.")
        return

    try:
        os.rename(source, destination)

        print("CompAI: File renamed successfully:")
        print(destination)

    except OSError as error:
        print("CompAI: Rename failed:", error)





# MAIN PROGRAM

while True:

    try:

        command = input("\nYou: ").strip()

        lower_command = command.lower()



        # VOICE COMMAND INPUT

        if lower_command in ("voice", "listen", "voice command"):

            spoken_command = listen_for_voice_command()



            if not spoken_command:

                continue



            command = spoken_command

            lower_command = command.lower()

        if lower_command == "exit":

            print("CompAI: Goodbye!")

            break

        elif lower_command in ("wake", "wake on"):

            run_wake_mode()



        elif lower_command == "help":

            show_help()

        # FILE MANAGEMENT

        elif lower_command.startswith("open file "):

            path = command[len("open file "):].strip()
            open_managed_path(path, expect_file=True)


        elif lower_command.startswith("open folder "):

            path = command[len("open folder "):].strip()
            open_managed_path(path, expect_file=False)


        elif lower_command.startswith("list files "):

            folder = command[len("list files "):].strip()
            list_managed_files(folder)


        elif lower_command.startswith("search files "):

            search_request = command[len("search files "):].strip()

            parts = re.split(
                r"\s+in\s+",
                search_request,
                maxsplit=1,
                flags=re.IGNORECASE
            )

            if len(parts) == 2:
                search_managed_files(parts[0], parts[1])
            else:
                print(
                    "CompAI: Usage: search files <name> in <folder>"
                )


        elif lower_command.startswith("create folder "):

            folder = command[len("create folder "):].strip()
            create_managed_folder(folder)




        # APP LAUNCHER

        elif lower_command == "apps":

            show_available_apps()



        elif lower_command == "open":

            print("CompAI: Usage: open <application>")



        elif lower_command.startswith("open "):

            app_name = command[5:].strip()

            launch_application(app_name)

        # FILE TRANSFER COMMANDS

        elif lower_command.startswith("copy file "):

            request = command[len("copy file "):].strip()
            parts = re.split(r"\s+to\s+", request, maxsplit=1, flags=re.IGNORECASE)

            if len(parts) == 2:
                transfer_managed_file(parts[0], parts[1], "copy")
            else:
                print("CompAI: Usage: copy file <source> to <destination>")


        elif lower_command.startswith("move file "):

            request = command[len("move file "):].strip()
            parts = re.split(r"\s+to\s+", request, maxsplit=1, flags=re.IGNORECASE)

            if len(parts) == 2:
                transfer_managed_file(parts[0], parts[1], "move")
            else:
                print("CompAI: Usage: move file <source> to <destination>")


        elif lower_command.startswith("rename file "):

            request = command[len("rename file "):].strip()
            parts = re.split(r"\s+to\s+", request, maxsplit=1, flags=re.IGNORECASE)

            if len(parts) == 2:
                rename_managed_file(parts[0], parts[1])
            else:
                print("CompAI: Usage: rename file <source> to <new name>")




        # PC MONITORING

        elif lower_command in ("monitor", "pc status"):

            show_pc_monitor()

        elif lower_command == "processes":

            show_process_monitor()



        elif lower_command == "top cpu":

            show_process_monitor("cpu")



        elif lower_command == "top memory":

            show_process_monitor("memory")



        elif lower_command == "cpu":

            show_pc_monitor("cpu")



        elif lower_command in ("memory", "ram"):

            show_pc_monitor("memory")



        elif lower_command == "disk":

            show_pc_monitor("disk")



        elif lower_command == "battery":

            show_pc_monitor("battery")



        # GOOGLE SEARCH

        elif lower_command.startswith("search "):

            search = command[7:].strip()



            if search:

                search_google(search)

            else:

                print("CompAI: What should I search for?")



        # DEVELOPER MODE

        elif lower_command == "developer mode":

            open_developer_settings()



        elif lower_command == "developer mode status":

            developer_mode_status()



        elif lower_command == "developer mode on":

            open_developer_settings("on")



        elif lower_command == "developer mode off":

            open_developer_settings("off")



        # WALLPAPER

        elif lower_command.startswith("wallpaper "):

            path = command[10:].strip()



            if path:

                change_wallpaper(path)

            else:

                print("CompAI: Please provide an image path.")



        # COMPAI SHARE

        elif lower_command == "share":

            compai_share()



        elif lower_command == "share email":

            compai_share("email")



        elif lower_command == "share nearby":

            compai_share("nearby")



        # EXISTING SYSTEM STATUS

        elif lower_command == "status":

            system_status()



        else:

            print("CompAI: I don't understand that command yet.")



    except KeyboardInterrupt:

        print("\nCompAI: Stopped by keyboard interrupt.")

        break



    except Exception as error:

        print("CompAI: An unexpected error occurred:", error)
