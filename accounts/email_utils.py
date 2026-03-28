import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


def send_gmail(to, subject, message_text):
    creds = Credentials.from_authorized_user_file(
        'token.json',
        ['https://www.googleapis.com/auth/gmail.send']
    )

    service = build('gmail', 'v1', credentials=creds)

    message = MIMEText(message_text)
    message['to'] = to
    message['subject'] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    service.users().messages().send(
        userId='me',
        body={'raw': raw}
    ).execute()
