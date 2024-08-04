import base64
import os

from decouple import config
from flask import Flask, flash, redirect, render_template, request, url_for
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from helpers.clean_emails import clean_email_file

app = Flask(__name__)
app.secret_key = config("SECRET_KEY")

SCOPES = config("SCOPES")
RAW_EMAIL_DIR = config("RAW_EMAIL_DIR")
CLEANED_EMAIL_DIR = config("CLEANED_EMAIL_DIR")
ATTACHMENTS_DIR = config("ATTACHMENTS_DIR")
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
                with open(TOKEN, "w") as token:
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

        query = f"to:{email_address} OR from:{email_address}"
        next_page_token = None

        while True:
            if next_page_token:
                results = service.users().messages().list(userId='me', q=query, pageToken=next_page_token).execute()
            else:
                results = service.users().messages().list(userId='me', q=query).execute()
            
            messages = results.get('messages', [])
            next_page_token = results.get('nextPageToken', None)

            if not messages:
                flash('No more messages found.')
                break
            else:
                for message in messages:
                    msg = service.users().messages().get(userId='me', id=message['id'], format='raw').execute()
                    msg_str = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
                    raw_email_path = os.path.join(RAW_EMAIL_DIR, f'email_{message["id"]}.eml')
                    with open(raw_email_path, 'wb') as f:
                        f.write(msg_str)
                    clean_email_file(raw_email_path)
                flash(f'Saved and cleaned {len(messages)} messages.')

            if not next_page_token:
                break

        return redirect(url_for('index'))

    return render_template('index.html')

@app.route('/delete/', methods=['POST'])
def delete_files():
    if os.path.exists(ATTACHMENTS_DIR):
        print(f'Attachments dir exists: {ATTACHMENTS_DIR}')
    else:
        print('No attachments dir found.')
    
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True, port=5001)
