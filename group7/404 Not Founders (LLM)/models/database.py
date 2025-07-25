import json
import os
import time
import uuid

DB_FILE = "emails.json"

def save_email(idea, tone, generated, improved):
    email_data = {
        "id": str(uuid.uuid4()),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "idea": idea,
        "tone": tone,
        "generated": generated,
        "improved": improved
    }

    # Load existing emails or start a new list
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            try:
                all_emails = json.load(f)
            except json.JSONDecodeError:
                all_emails = []
    else:
        all_emails = []

    # Append new email object
    all_emails.append(email_data)

    # Write updated list to file
    with open(DB_FILE, 'w') as f:
        json.dump(all_emails, f, indent=4)

    print("✅ Email saved successfully in emails.json.")

def get_all_emails():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        return json.load(f)
