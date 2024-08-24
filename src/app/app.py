# gfetch -- save gmail emails locally
# Copyright (C) 2024 Jeff Jacobson <jeffjacobsonhimself@gmail.com>
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import base64
import ipdb
import os

from auth import get_credentials
from clean_emails import clean_email_file
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_session import Session
from googleapiclient.discovery import build

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
RAW_EMAIL_DIR = os.getenv("RAW_EMAIL_DIR")
CLEANED_EMAIL_DIR = os.getenv("CLEANED_EMAIL_DIR")
ATTACHMENTS_DIR = os.getenv("ATTACHMENTS_DIR")

# Redis configuration
app.config["SESSION_TYPE"] = os.getenv("SESSION_TYPE")
app.config["SESSION_PERMANENT"] = os.getenv("SESSION_PERMANENT")
# app.config["SESSION_USE_SIGNER"] = os.getenv("SESSION_USE_SIGNER")
app.config["SESSION_KEY_PREFIX"] = os.getenv("SESSION_KEY_PREFIX")
app.config["SESSION_REDIS"] = os.getenv("SESSION_REDIS")

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
