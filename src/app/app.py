import base64
import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_session import Session
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from helpers.clean_emails import clean_email_file
from redis import Redis

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
SCOPES = os.getenv("SCOPES")
RAW_EMAIL_DIR = os.getenv("RAW_EMAIL_DIR")
CLEANED_EMAIL_DIR = os.getenv("CLEANED_EMAIL_DIR")
ATTACHMENTS_DIR = os.getenv("ATTACHMENTS_DIR")
CREDS = os.getenv("CREDS")
TOKEN = os.getenv("TOKEN")

# Redis configuation
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_KEY_PREFIX"] = "session:"
app.config["SESSION_REDIS"] = Redis(host="localhost", port=6379)

# Start redis
Session(app)


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

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
                if os.path.exists(TOKEN):
                    os.remove(TOKEN)
                creds = None

        if not creds:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CREDS, SCOPES)
                creds = flow.run_local_server(port=0)
                with open(TOKEN, "w") as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"Error during OAuth flow: {e}")

    return creds


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        email_address = request.form["email_address"]

        creds = get_credentials()
        if not creds:
            flash("Failed to obtain credentials.")
            return redirect(url_for("index"))

        try:
            service = build("gmail", "v1", credentials=creds)
        except Exception as e:
            flash(f"Error building Gmail service: {e}")
            return redirect(url_for("index"))

        query = f"to:{email_address} OR from:{email_address}"
        next_page_token = None
        total_messages = 0
        total_attachments = 0

        while True:
            if next_page_token:
                results = (
                    service.users()
                    .messages()
                    .list(userId="me", q=query, pageToken=next_page_token)
                    .execute()
                )
            else:
                results = (
                    service.users().messages().list(userId="me", q=query).execute()
                )

            messages = results.get("messages", [])
            next_page_token = results.get("nextPageToken", None)

            if not messages:
                print("No messages remain.")
                break
            else:
                for message in messages:
                    msg = (
                        service.users()
                        .messages()
                        .get(userId="me", id=message["id"], format="raw")
                        .execute()
                    )
                    msg_str = base64.urlsafe_b64decode(msg["raw"].encode("ASCII"))
                    raw_email_path = os.path.join(
                        RAW_EMAIL_DIR, f'email_{message["id"]}.eml'
                    )
                    with open(raw_email_path, "wb") as f:
                        f.write(msg_str)
                    attachments = clean_email_file(raw_email_path)
                    if attachments:
                        total_attachments += attachments

                total_messages += len(messages)

            if not next_page_token:
                break

        flash(f"Saved and cleaned {total_messages} messages.")
        flash(f"Saved {total_attachments} attachments.")

        return redirect(url_for("index"))

    return render_template("index.html")


@app.route("/delete/", methods=["POST"])
def delete_files():
    attachments = os.listdir(ATTACHMENTS_DIR)
    clean_emails = [
        email for email in os.listdir(CLEANED_EMAIL_DIR) if email.endswith(".txt")
    ]
    raw_emails = [
        email for email in os.listdir(RAW_EMAIL_DIR) if email.endswith(".eml")
    ]
    deleted_emails = 0
    deleted_attachments = 0

    if not attachments:
        flash("No attachments found.")
    else:
        for attachment in attachments:
            attachment_path = os.path.join(ATTACHMENTS_DIR, attachment)
            os.remove(attachment_path)
            deleted_attachments += 1

    if not clean_emails:
        flash("No cleaned emails found.")
    else:
        for email in clean_emails:
            clean_path = os.path.join(CLEANED_EMAIL_DIR, email)
            os.remove(clean_path)
            deleted_emails += 1

    if not raw_emails:
        flash("No raw emails found.")
    else:
        for email in raw_emails:
            raw_path = os.path.join(RAW_EMAIL_DIR, email)
            os.remove(raw_path)

    if deleted_emails and deleted_attachments:
        flash(f"Deleted {deleted_emails} emails and {deleted_attachments} attachments.")
    elif deleted_emails:
        flash(f"Deleted {deleted_emails} emails.")
    elif deleted_attachments:
        flash(f"Deleted {deleted_attachments} attachments.")

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
