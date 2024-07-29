import os

from decouple import config
from flask import Flask, render_template
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

app = Flask(__name__)

SECRET_KEY = config("SECRET_KEY")
SCOPES = config("SCOPES")
RAW_EMAIL_DIR = config("RAW_EMAIL_DIR")
CLEANED_EMAIL_DIR = config("CLEANED_EMAIL_DIR")


def get_credentials():
    creds = None
    if os.path.exists("token.json"):
        try:
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        except Exception as e:
            print(f"Error loading credentials: {e}")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing credentials: {e}")

        if not creds:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
                with open("token.json", "w") as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"Error during OAuth flow: {e}")
                return None

    return creds

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
