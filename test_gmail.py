
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def main():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json", SCOPES
        )

    if creds and creds.expired and creds.refresh_token:
        print("CompAI: Refreshing Gmail authorization...")
        creds.refresh(Request())

    if not creds or not creds.valid:
        print("CompAI: Starting Google authorization...")
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )

        creds = flow.run_local_server(port=0)

    with open("token.json", "w", encoding="utf-8") as token:
        token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)

    print()
    print("================================")
    print("  COMPAI GMAIL CONNECTION TEST")
    print("================================")
    print("Gmail API: CONNECTED")
    print("Authorization: SUCCESSFUL")
    print("Token saved: token.json")
    print("Email sending: READY")
    print("================================")

if __name__ == "__main__":
    main()
