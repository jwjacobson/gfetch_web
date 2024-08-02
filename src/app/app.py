import os

from decouple import config
from flask import Flask, render_template, request, redirect, url_for, flash
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import ipdb

app = Flask(__name__)
app.secret_key = config("SECRET_KEY")

SCOPES = config("SCOPES")
RAW_EMAIL_DIR = config("RAW_EMAIL_DIR")
CLEANED_EMAIL_DIR = config("CLEANED_EMAIL_DIR")
CREDS = config("CREDS")
TOKEN = config("TOKEN")

def get_credentials():
    creds = None
    if os.path.exists(TOKEN):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)
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
                    CREDS, SCOPES
                )
                creds = flow.run_local_server(port=0)
                with open("token.json", "w") as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"Error during OAuth flow: {e}")
                return None

    return creds

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email_address = request.form['email_address']

        creds = get_credentials()
        if not creds:
            flash('Failed to obtain credentials.')
            return redirect(url_for('index'))

        try:
            service = build('gmail', 'v1', credentials=creds)
        except Exception as e:
            flash(f'Error building Gmail service: {e}')
            return redirect(url_for('index'))

        if not os.path.exists(RAW_EMAIL_DIR):
            os.makedirs(RAW_EMAIL_DIR)

        flash(f"Processing emails for {email_address}")
        return redirect(url_for('index'))

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
