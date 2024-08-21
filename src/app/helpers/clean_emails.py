# gmailfetcher -- save gmail emails locally
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


import email
import os
from email import policy
from email.parser import BytesParser

OUTPUT_DIR = os.getenv("CLEANED_EMAIL_DIR")
ATTACHMENTS_DIR = os.getenv("ATTACHMENTS_DIR")


def clean_email_file(email_file):
    """
    Take an eml file and output a cleaned txt file.
    """
    with open(email_file, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)

    date = msg["Date"]
    subject = msg["Subject"]
    to = msg["To"]
    from_ = msg["From"]
    attachments = []

    if msg.is_multipart():
        for part in msg.iter_parts():
            if part.get_content_disposition() == "attachment":
                filename = part.get_filename()
                if filename:
                    attachments.append(filename)
                    filepath = os.path.join(ATTACHMENTS_DIR, filename)
                    with open(filepath, "wb") as attachment_file:
                        attachment_file.write(part.get_payload(decode=True))
                break

    if date:
        try:
            date_obj = email.utils.parsedate_to_datetime(date)
            formatted_date = date_obj.strftime("%Y-%m-%d")
        except Exception as e:
            print(f"Error parsing date: {e}")
            formatted_date = "unknown_date"
    else:
        formatted_date = "unknown_date"

    if not subject:
        formatted_subj = "no_subject"
    else:
        subj_list = []
        puncts = {
            ",",
            " ",
            ".",
            "—",
            "-",
            "'",
            '"',
            ":",
            ";",
            "!",
            "?",
            "(",
            ")",
            "/",
            "\\",
        }
        for char in subject:
            if char in puncts:
                continue
            elif char == " ":
                subj_list.append("_")
            else:
                subj_list.append(char.lower())

        formatted_subj = "".join(subj_list)

    body = ""

    if msg.is_multipart():
        for part in msg.iter_parts():
            if part.get_content_type() == "text/plain":
                charset = part.get_content_charset()
                if charset is None:
                    charset = "utf-8"
                body = part.get_payload(decode=True).decode(charset, errors="replace")
                break
    else:
        charset = msg.get_content_charset()
        if charset is None:
            charset = "utf-8"
        body = msg.get_payload(decode=True).decode(charset, errors="replace")

    if not body:
        body = (
            "This email has no text in the body. Maybe it contained only an attachment?"
        )

    body = body.split("\nOn ")[0]

    email_content = f"DATE: {date}\nSUBJECT: {subject}\nTO: {to}\nFROM: {from_}\n"

    if attachments:
        email_content += "ATTACHMENTS:\n"
        for attachment in attachments:
            email_content += f"- {attachment}\n"

    email_content += f"\n{body}"

    email_filename = os.path.join(OUTPUT_DIR, f"{formatted_date}__{formatted_subj}.txt")
    with open(email_filename, "w", encoding="utf-8") as f:
        f.write(email_content)

    if attachments:
        return len(attachments)


if __name__ == "__main__":
    OUTPUT_DIR = "."
    clean_email_file("sample_raw.eml")
