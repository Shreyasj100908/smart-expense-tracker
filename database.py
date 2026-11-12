    
import sqlite3
import pandas as pd

# Connect to database
def connect_db():
    conn = sqlite3.connect("expenses.db")
    return conn


# Create transactions table
def create_table():

    conn = connect_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            amount REAL,
            category TEXT,
            description TEXT,
            date TEXT
        )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS budgets (
        month TEXT PRIMARY KEY,
        amount REAL
    )
""")

    conn.commit()
    conn.close()


# Add transaction
def add_transaction(type, amount, category, description, date):

    conn = connect_db()

    conn.execute("""
        INSERT INTO transactions
        (type, amount, category, description, date)
        VALUES (?, ?, ?, ?, ?)
    """, (type, amount, category, description, str(date)))

    conn.commit()
    conn.close()


# Retrieve transactions
def get_transactions():

    conn = connect_db()

    df = pd.read_sql_query(
        "SELECT * FROM transactions ORDER BY date DESC",
        conn
    )

    conn.close()

    return df

# --------------------------------
# MONTHLY BUDGET FUNCTIONS
# --------------------------------

def set_monthly_budget(month, amount):

    conn = connect_db()

    conn.execute("""
        INSERT OR REPLACE INTO budgets (month, amount)
        VALUES (?, ?)
    """, (month, amount))

    conn.commit()
    conn.close()


def get_monthly_budget(month):

    conn = connect_db()

    cursor = conn.execute(
        "SELECT amount FROM budgets WHERE month = ?",
        (month,)
    )

    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]

    return 0
    
# --------------------------------
# EDIT TRANSACTION
# --------------------------------

def update_transaction(
    transaction_id,
    transaction_type,
    amount,
    category,
    description,
    date
):

    conn = connect_db()

    conn.execute("""
        UPDATE transactions
        SET type = ?,
            amount = ?,
            category = ?,
            description = ?,
            date = ?
        WHERE id = ?
    """, (
        transaction_type,
        amount,
        category,
        description,
        str(date),
        transaction_id
    ))

    conn.commit()
    conn.close()


# --------------------------------
# DELETE TRANSACTION
# --------------------------------

def delete_transaction(transaction_id):

    conn = connect_db()

    conn.execute("""
        DELETE FROM transactions
        WHERE id = ?
    """, (transaction_id,))

    conn.commit()
    conn.close()

