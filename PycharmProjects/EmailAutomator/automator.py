import time
from config import (
    MODE, ATTACHMENTS, RATE_LIMIT_DELAY, SENDER_EMAIL
)
from database import (
    init_db, get_pending_recipients, log_email_sent,
    get_followup_candidates, log_followup_sent, reset_db
)
from openai_client import OpenAIClient
from emailer import send_email
from openai_usage import print_openai_usage  # see below

from utils import import_yaml_to_db

def build_email_html(ai_body, recipient_info):
    job_url_section = ""
    if recipient_info.get('job_url'):
        job_url_section = f"""
<div style="margin: 20px 0; padding: 15px; background-color: #f5f5f5; border-left: 4px solid #2B579A; border-radius: 4px;">
    <p style="margin: 0; font-weight: bold;">Job Posting Link:</p>
    <p style="margin: 5px 0 0 0;">
        <a href="{recipient_info['job_url']}" style="color: #2B579A; text-decoration: none;">
            {recipient_info['job_title']} at {recipient_info['company']}
        </a>
    </p>
</div>
"""

    signature = f"""
<div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e0e0e0;">
    <p style="margin: 0; color: #333;">
        Best regards,<br>
        <strong style="color: #2B579A; font-size: 16px;">Gnanendra Prasad Gopi</strong><br>
        <span style="color: #666;">Product Manager</span> |
        <span style="color: #666;">Changing The Present</span>
    </p>
    <div style="margin-top: 15px;">
        <a href="https://www.linkedin.com/in/gnanendra-prasad-gopi" style="color: #2B579A; text-decoration: none; margin-right: 15px;">LinkedIn</a> |
        <a href="https://github.com/GGP0615/Class-Team-Up" style="color: #2B579A; text-decoration: none; margin-right: 15px;">GitHub</a> |
        <a href="mailto:gnanendraprasadgopi0615@gmail.com" style="color: #2B579A; text-decoration: none;">gnanendraprasadgopi0615@gmail.com</a>
    </div>
</div>
"""
    html = f"""
<html>
  <head>
    <style>
      body {{
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 15px;
        line-height: 1.6;
        color: #333;
        max-width: 600px;
        margin: 0 auto;
        padding: 20px;
      }}
      p {{
        margin: 0 0 15px 0;
      }}
      ul {{
        margin: 10px 0;
        padding-left: 20px;
      }}
      li {{
        margin-bottom: 8px;
      }}
      strong {{
        color: #2B579A;
      }}
      em {{
        color: #666;
        font-style: italic;
      }}
      a {{
        color: #2B579A;
        text-decoration: none;
      }}
      a:hover {{
        text-decoration: underline;
      }}
      .section-header {{
        font-weight: bold;
        color: #2B579A;
        margin: 12px 0 4px 0;
        font-size: 16px;
      }}
    </style>
  </head>
  <body>
    {ai_body}
    {job_url_section}
    {signature}
  </body>
</html>
"""
    return html

def main():
    if MODE == "reminder":
        print("[INFO] Initializing database if needed...")
        init_db()  # Just initialize the DB if it doesn't exist, don't reset
        print("[INFO] Checking for recipients due for follow-up...")
        candidates = get_followup_candidates(days=5)
        if not candidates:
            print("[INFO] No recipients are due for follow-up.")
            return
        print("Reminder: The following recipients are due for follow-up:")
        for row in candidates:
            recipient_id, name, email, company, job_title, job_description, job_url, sent_at = row
            print(f"- {name} ({email}) — {company}, {job_title} — Sent at: {sent_at}")
        confirm = input("\nDo you want to send follow-ups to these recipients now? (y/n): ").strip().lower()
        if confirm == 'y':
            openai_client = OpenAIClient()
            for row in candidates:
                recipient_id, name, email, company, job_title, job_description, job_url, sent_at = row
                recipient_info = {
                    "name": name,
                    "email": email,
                    "company": company,
                    "job_title": job_title,
                    "job_description": job_description,
                    "job_url": job_url
                }
                print(f"[INFO] Generating follow-up for: {name} ({email})")
                ai_body = openai_client.generate_ai_message(job_description, recipient_info)
                html_body = build_email_html(ai_body, recipient_info)
                print(f"[INFO] Sending follow-up email to {email}")
                send_email(email, f"Following up: {job_title} at {company}", html_body, ATTACHMENTS)
                log_followup_sent(recipient_id)
                print("[INFO] Waiting for rate limit...")
                time.sleep(RATE_LIMIT_DELAY)
            print("[INFO] All follow-ups sent.")
        else:
            print("[INFO] No follow-ups sent.")
        return

    if MODE == "reset":
        print("[INFO] Resetting database...")
        reset_db()
        print("[INFO] Importing recipients from YAML...")
        from database import add_recipient
        import_yaml_to_db('jobs_and_recipients.yaml', add_recipient)
        print("[INFO] Done.")
        return

    if MODE == "test":
        print("[INFO] Initializing database if needed...")
        init_db()  # Just initialize the DB if it doesn't exist, don't reset
        print("[INFO] Importing recipients from YAML...")
        from database import add_recipient
        import_yaml_to_db('jobs_and_recipients.yaml', add_recipient)
        print("[INFO] Initializing OpenAI client...")
        openai_client = OpenAIClient()

        print(f"[INFO] Running in {MODE.upper()} mode.")
        print("[INFO] Getting pending recipients...")
        pending = get_pending_recipients()
        print(f"[INFO] Found {len(pending)} pending recipients")

        for row in pending:
            recipient_id, name, email, company, job_title, job_description, job_url = row
            print(f"[INFO] Processing recipient: {name} ({email})")

            recipient_info = {
                "name": name,
                "email": email,
                "company": company,
                "job_title": job_title,
                "job_description": job_description,
                "job_url": job_url
            }
            print("[INFO] Generating AI message...")
            ai_body = openai_client.generate_ai_message(job_description, recipient_info)
            print("[INFO] Building email HTML...")
            html_body = build_email_html(ai_body, recipient_info)
            print(f"[INFO] Sending test email to {SENDER_EMAIL}")
            send_email(SENDER_EMAIL, f"TEST: Interest in {job_title} at {company}", html_body, ATTACHMENTS)
            print("[INFO] Waiting for rate limit...")
            time.sleep(RATE_LIMIT_DELAY)
        print("[INFO] Script completed.")
        return

    if MODE == "send":
        print("[INFO] Initializing database if needed...")
        init_db()  # Just initialize the DB if it doesn't exist, don't reset
        print("[INFO] Importing recipients from YAML...")
        from database import add_recipient
        import_yaml_to_db('jobs_and_recipients.yaml', add_recipient)
        print("[INFO] Initializing OpenAI client...")
        openai_client = OpenAIClient()
        print(f"[INFO] Running in {MODE.upper()} mode.")
        print("[INFO] Getting NEW recipients who haven't been emailed yet...")
        pending = get_pending_recipients()
        print(f"[INFO] Found {len(pending)} NEW recipients who haven't been emailed")

        for row in pending:
            recipient_id, name, email, company, job_title, job_description, job_url = row
            print(f"[INFO] Processing recipient: {name} ({email})")

            recipient_info = {
                "name": name,
                "email": email,
                "company": company,
                "job_title": job_title,
                "job_description": job_description,
                "job_url": job_url
            }
            print("[INFO] Generating AI message...")
            ai_body = openai_client.generate_ai_message(job_description, recipient_info)
            print("[INFO] Building email HTML...")
            html_body = build_email_html(ai_body, recipient_info)
            print(f"[INFO] Sending email to {email}")
            send_email(email, f"Interest in {job_title} at {company}", html_body, ATTACHMENTS)
            log_email_sent(recipient_id)
            print("[INFO] Waiting for rate limit...")
            time.sleep(RATE_LIMIT_DELAY)
        print("[INFO] Script completed.")
        return

    if MODE == "followup":
        print("[INFO] Initializing database if needed...")
        init_db()  # Just initialize the DB if it doesn't exist, don't reset
        print("[INFO] Getting followup candidates...")
        candidates = get_followup_candidates(days=5)
        print(f"[INFO] Found {len(candidates)} followup candidates")

        openai_client = OpenAIClient()
        for row in candidates:
            recipient_id, name, email, company, job_title, job_description, job_url, sent_at = row
            print(f"[INFO] Processing followup for: {name} ({email})")

            recipient_info = {
                "name": name,
                "email": email,
                "company": company,
                "job_title": job_title,
                "job_description": job_description,
                "job_url": job_url
            }
            print("[INFO] Generating AI message...")
            ai_body = openai_client.generate_ai_message(job_description, recipient_info)
            print("[INFO] Building email HTML...")
            html_body = build_email_html(ai_body, recipient_info)
            print(f"[INFO] Sending followup email to {email}")
            send_email(email, f"Following up: {job_title} at {company}", html_body, ATTACHMENTS)
            log_followup_sent(recipient_id)
            print("[INFO] Waiting for rate limit...")
            time.sleep(RATE_LIMIT_DELAY)
        print("[INFO] Script completed.")
        return

    print("[ERROR] Unknown mode. Use 'test', 'send', 'followup', 'reminder', or 'reset'.")

if __name__ == "__main__":
    main()
