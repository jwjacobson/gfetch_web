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
import os

from auth import get_credentials
from emails import fetch_emails, create_dirs
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


create_dirs()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        email_address = request.form["email_address"]

        final_count = fetch_emails(email_address)

        flash(f"Saved and cleaned {final_count['total_messages']} messages.")
        flash(f"Saved {final_count['total_attachments']} attachments.")

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
