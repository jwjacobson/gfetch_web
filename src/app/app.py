import base64
import os

from decouple import config
from flask import Flask, flash, redirect, render_template, request, url_for, session
from flask_session import Session
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from helpers.clean_emails import clean_email_file
import redis

app = Flask(__name__)
app.secret_key = config("SECRET_KEY")

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True 
app.config['SESSION_KEY_PREFIX'] = 'session:'

app.config['SESSION_REDIS'] = redis.Redis(host='localhost', port=6379, db=0)

Session(app)

SCOPES = config("SCOPES")
RAW_EMAIL_DIR = config("RAW_EMAIL_DIR")
CLEANED_EMAIL_DIR = config("CLEANED_EMAIL_DIR")
ATTACHMENTS_DIR = config("ATTACHMENTS_DIR")
CREDS = config("CREDS")
TOKEN = config("TOKEN")

def create_dirs():
    if not os.path.exists(RAW_EMAIL_DIR):
        os.makedirs(RAW_EMAIL_DIR)
    if not os.path.exists(CLEANED_EMAIL_DIR):
        os.makedirs(CLEANED_EMAIL_DIR)
    if not os.path.exists(ATTACHMENTS_DIR):
        os.makedirs(ATTACHMENTS_DIR)

create_dirs()

def get_credentials():
    creds = None
    if os.path.exists(TOKEN):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)
        except Exception as e:
            print(f"Error loading credentials: {e}")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                if 'invalid_scope' in str(e):
                    print(f"Invalid scope detected: {e}")
                    if os.path.exists(TOKEN):
                        os.remove(TOKEN)
                    print("Old token deleted. Re-authenticating.")
                    return get_credentials()
                else:
                    print(f"Error refreshing credentials: {e}")
                    return None

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
    attachments = os.listdir(ATTACHMENTS_DIR)
    clean_emails = [email for email in os.listdir(CLEANED_EMAIL_DIR) if email.endswith(".txt")]
    raw_emails = [email for email in os.listdir(RAW_EMAIL_DIR) if email.endswith(".eml")]
    
    if not attachments:
        flash("No attachments found.")
    else:
        attachment_count = len(attachments)
        flash(f"Found {attachment_count} attachments.")
        for attachment in attachments:
            flash(f'Deleting {attachment}.')
            attachment_path = os.path.join(ATTACHMENTS_DIR, attachment)
            os.remove(attachment_path)
    
    if not clean_emails:
        flash("No cleaned emails found.")
    else:
        clean_count = len(clean_emails)
        flash(f"Found {clean_count} cleaned emails.")
        for email in clean_emails:
            flash(f'Deleting {email}.')
            clean_path = os.path.join(CLEANED_EMAIL_DIR, email)
            os.remove(clean_path)

    if not raw_emails:
        flash("No raw emails found.")
    else:
        raw_count = len(raw_emails)
        flash(f"Found {raw_count} raw emails.")
        for email in raw_emails:
            flash(f'Deleting {email}.')
            raw_path = os.path.join(RAW_EMAIL_DIR, email)
            os.remove(raw_path)

    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True, port=5001)
