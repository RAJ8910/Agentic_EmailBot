import time
import re
import requests
from utils.gmail_utils import get_unread_emails, mark_as_read, send_email_reply

# Your FastAPI endpoint
QUERY_API_URL = "http://localhost:8000/query"

# Allowed customer emails
ALLOWED_CUSTOMERS = {"rajbharmani@gmail.com", "client@example.com", "foo@bar.com"}

def clean_email_body(body: str) -> str:
    body = body.replace("\r", "").replace("\n", " ").strip()                      # Remove line breaks
    body = re.sub(r'<.*?>', '', body)                                             # Strip HTML tags
    body = re.split(r'On .+ wrote:', body)[0]                                     # Remove quoted replies
    body = re.sub(r'(--\s*\n.*)', '', body, flags=re.DOTALL)                      # Remove signatures
    return body.strip()

def send_to_query_api(email_body, email_id):
    try:
        payload = {
            "query": email_body,
            "email": email_id
        }
        response = requests.post(QUERY_API_URL, json=payload)
        print("LLM Response:", response.json())
        return response.json().get("answer", "")
    except Exception as e:
        print(f"Failed to call /query API: {e}")
        return ""

def run_email_watcher(poll_interval=10):
    print("📬 Email watcher started...")
    while True:
        try:
            emails = get_unread_emails()
            if not emails:
                time.sleep(poll_interval)
                continue

            for email in sorted(emails, key=lambda x: x['id']):
                sender = email['sender'].split('<')[-1].replace('>', '').strip()
                if sender in ALLOWED_CUSTOMERS:
                    print(f"✅ Processing email from {sender}")
                    cleaned_body = clean_email_body(email['body'])
                    answer = send_to_query_api(cleaned_body, sender)

                    # Optional: Reply to sender
                    send_email_reply(
                        to=email['sender'],
                        subject=email['subject'],
                        body=answer,
                        thread_id=email['thread_id']
                    )
                else:
                    print(f"⛔ Ignored email from {sender}")
                mark_as_read(email['id'])

        except Exception as e:
            print(f"❌ Error in watcher loop: {e}")

        time.sleep(poll_interval)

if __name__ == "__main__":
    run_email_watcher()
