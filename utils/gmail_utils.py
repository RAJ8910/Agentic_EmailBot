import os
import base64
import re
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

def get_unread_emails():
    service = get_gmail_service()
    results = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD']).execute()
    messages = results.get('messages', [])
    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_data['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
        thread_id = msg_data.get('threadId')  # <-- Add this
        body = ''
        if 'data' in msg_data['payload']['body']:
            body = base64.urlsafe_b64decode(msg_data['payload']['body']['data']).decode('utf-8')
        else:
            for part in msg_data['payload'].get('parts', []):
                if part['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
        emails.append({
            'id': msg['id'],
            'subject': subject,
            'sender': sender,
            'body': body,
            'thread_id': thread_id  
        })
    return emails

def send_email_reply(to, subject, body, thread_id):
    service = get_gmail_service()
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = "Re: " + subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message_body = {
        'raw': raw,
        'threadId': thread_id
    }
    service.users().messages().send(userId='me', body=message_body).execute()

def mark_as_read(msg_id):
    service = get_gmail_service()
    service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()

def clean_email_body(body):
    # Remove signatures, quoted text, etc. (simple version)
    body = re.split(r'On .+ wrote:', body)[0]
    body = re.sub(r'(--\s*\n.*)', '', body, flags=re.DOTALL)
    return body.strip()