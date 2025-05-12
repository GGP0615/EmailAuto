import os

MODE = os.getenv("EMAIL_MODE", "test")  # "test", "send", "reminder", "reset", or "followup"
SENDER_EMAIL = "gnanendraprasadgopi0615@gmail.com"
SENDER_NAME = "Gnanendra Prasad Gopi"
SENDER_PASSWORD = os.getenv("07_GMAIL_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Use relative path for resume
RESUME_PATH = os.path.join(os.path.dirname(__file__), "Gnanendra_Prasad_Gopi_Product_Manager.pdf")
ATTACHMENTS = [RESUME_PATH] if os.path.exists(RESUME_PATH) else []

DB_PATH = "email_automator.db"
RATE_LIMIT_DELAY = 2

# Debug prints
print("Environment Variables Debug:")
print(f"MODE: {MODE}")
print(f"SENDER_PASSWORD exists: {SENDER_PASSWORD is not None}")
print(f"OPENAI_API_KEY exists: {OPENAI_API_KEY is not None}")
print(f"Resume path exists: {os.path.exists(RESUME_PATH)}")
