import sqlite3
from contextlib import contextmanager
from config import DB_PATH

@contextmanager
def db_conn():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def reset_db():
    """Reset the database by dropping all tables and recreating them."""
    with db_conn() as conn:
        c = conn.cursor()
        # Drop existing tables
        c.execute("DROP TABLE IF EXISTS email_logs")
        c.execute("DROP TABLE IF EXISTS recipients")
        conn.commit()
    # Recreate tables
    init_db()
    print("[INFO] Database reset completed.")

def init_db():
    with db_conn() as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS recipients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT UNIQUE,
                company TEXT,
                job_title TEXT,
                job_description TEXT,
                job_url TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS email_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient_id INTEGER,
                sent_at TEXT,
                followup_sent INTEGER DEFAULT 0,
                followup_at TEXT,
                FOREIGN KEY (recipient_id) REFERENCES recipients(id)
            )
        ''')
        conn.commit()

def add_recipient(name, email, company, job_title, job_description, job_url=None):
    with db_conn() as conn:
        c = conn.cursor()
        c.execute('''
            INSERT OR IGNORE INTO recipients (name, email, company, job_title, job_description, job_url)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, email, company, job_title, job_description, job_url))
        conn.commit()

def get_pending_recipients():
    with db_conn() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT r.id, r.name, r.email, r.company, r.job_title, r.job_description, r.job_url
            FROM recipients r
            LEFT JOIN email_logs l ON r.id = l.recipient_id
            WHERE l.sent_at IS NULL
        ''')
        return c.fetchall()

def log_email_sent(recipient_id):
    with db_conn() as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO email_logs (recipient_id, sent_at)
            VALUES (?, datetime('now'))
        ''', (recipient_id,))
        conn.commit()

def get_followup_candidates(days=5):
    with db_conn() as conn:
        c = conn.cursor()
        c.execute(f'''
            SELECT r.id, r.name, r.email, r.company, r.job_title, r.job_description, r.job_url, l.sent_at
            FROM recipients r
            JOIN email_logs l ON r.id = l.recipient_id
            WHERE l.followup_sent = 0
              AND l.sent_at <= datetime('now', '-{days} days')
        ''')
        return c.fetchall()

def log_followup_sent(recipient_id):
    with db_conn() as conn:
        c = conn.cursor()
        c.execute('''
            UPDATE email_logs
            SET followup_sent = 1, followup_at = datetime('now')
            WHERE recipient_id = ? AND followup_sent = 0
        ''', (recipient_id,))
        conn.commit()
