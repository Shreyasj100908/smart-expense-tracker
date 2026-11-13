import hashlib
import hmac
import os
import sqlite3

import pandas as pd

DB_NAME = "expenses.db"
PBKDF2_ITERATIONS = 310_000


def connect_db():
    return sqlite3.connect(DB_NAME, timeout=30)


def _hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return salt.hex(), password_hash.hex()


def create_table():
    """Create authentication and user-specific finance tables; migrate old tables."""
    conn = connect_db()
    conn.execute("PRAGMA foreign_keys = ON")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL COLLATE NOCASE UNIQUE,
            salt TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Add user_id to an existing transactions table without deleting old records.
    transaction_columns = [row[1] for row in conn.execute("PRAGMA table_info(transactions)").fetchall()]
    if not transaction_columns:
        conn.execute("""
            CREATE TABLE transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT,
                amount REAL,
                category TEXT,
                description TEXT,
                date TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
    elif "user_id" not in transaction_columns:
        conn.execute("ALTER TABLE transactions ADD COLUMN user_id INTEGER")

    # New budgets are unique per user and month. Preserve the old table as a backup.
    budget_columns = [row[1] for row in conn.execute("PRAGMA table_info(budgets)").fetchall()]
    if not budget_columns:
        conn.execute("""
            CREATE TABLE budgets (
                user_id INTEGER NOT NULL,
                month TEXT NOT NULL,
                amount REAL NOT NULL,
                PRIMARY KEY (user_id, month),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
    elif "user_id" not in budget_columns:
        conn.execute("ALTER TABLE budgets RENAME TO budgets_legacy_backup")
        conn.execute("""
            CREATE TABLE budgets (
                user_id INTEGER NOT NULL,
                month TEXT NOT NULL,
                amount REAL NOT NULL,
                PRIMARY KEY (user_id, month),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user_date ON transactions(user_id, date DESC)")
    conn.commit()
    conn.close()


def create_user(username, password):
    salt, password_hash = _hash_password(password)
    conn = connect_db()
    try:
        cursor = conn.execute(
            "INSERT INTO users (username, salt, password_hash) VALUES (?, ?, ?)",
            (username, salt, password_hash),
        )
        conn.commit()
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "That username is already taken. Please choose another."
    finally:
        conn.close()


def authenticate_user(username, password):
    conn = connect_db()
    row = conn.execute(
        "SELECT id, username, salt, password_hash FROM users WHERE username = ? COLLATE NOCASE",
        (username,),
    ).fetchone()
    conn.close()

    if row is None:
        return None

    salt = bytes.fromhex(row[2])
    candidate = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    ).hex()
    if hmac.compare_digest(candidate, row[3]):
        return {"id": row[0], "username": row[1]}
    return None


def add_transaction(transaction_type, amount, category, description, date, user_id):
    conn = connect_db()
    conn.execute("""
        INSERT INTO transactions (user_id, type, amount, category, description, date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, transaction_type, amount, category, description, str(date)))
    conn.commit()
    conn.close()


def get_transactions(user_id):
    conn = connect_db()
    df = pd.read_sql_query(
        "SELECT id, type, amount, category, description, date FROM transactions WHERE user_id = ? ORDER BY date DESC, id DESC",
        conn,
        params=(user_id,),
    )
    conn.close()
    return df


def set_monthly_budget(month, amount, user_id):
    conn = connect_db()
    conn.execute("""
        INSERT INTO budgets (user_id, month, amount)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, month) DO UPDATE SET amount = excluded.amount
    """, (user_id, month, amount))
    conn.commit()
    conn.close()


def get_monthly_budget(month, user_id):
    conn = connect_db()
    result = conn.execute(
        "SELECT amount FROM budgets WHERE month = ? AND user_id = ?",
        (month, user_id),
    ).fetchone()
    conn.close()
    return result[0] if result else 0


def update_transaction(transaction_id, transaction_type, amount, category, description, date, user_id):
    conn = connect_db()
    conn.execute("""
        UPDATE transactions
        SET type = ?, amount = ?, category = ?, description = ?, date = ?
        WHERE id = ? AND user_id = ?
    """, (transaction_type, amount, category, description, str(date), transaction_id, user_id))
    conn.commit()
    conn.close()


def delete_transaction(transaction_id, user_id):
    conn = connect_db()
    conn.execute(
        "DELETE FROM transactions WHERE id = ? AND user_id = ?",
        (transaction_id, user_id),
    )
    conn.commit()
    conn.close()
