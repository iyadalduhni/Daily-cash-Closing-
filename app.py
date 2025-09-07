import streamlit as st
import datetime
import sqlite3
import pandas as pd

# =========================
# Database Setup
# =========================
conn = sqlite3.connect("sales.db")
c = conn.cursor()

# جدول للمبيعات اليومية
c.execute('''CREATE TABLE IF NOT EXISTS daily_sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    vape REAL,
    international REAL,
    australian REAL,
    non_tobacco REAL,
    total REAL,
    cash_notes REAL,
    cash_coins REAL,
    safe_notes REAL,
    safe_coins REAL,
    eftpos_main REAL,
    eftpos_backup REAL,
    expenses REAL,
    expenses_desc TEXT,
    net_sales REAL,
    system_sales REAL,
    difference REAL
)''')
conn.commit()

# =========================
# Users (ممكن تتحول لجدول مستقل لاحقاً)
# =========================
users = {
    "employee1": {"password": "1234", "role": "employee"},
    "manager": {"password": "admin123", "role": "manager"}
}

# =========================
# Session State
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.page = None
    st.session_state.sales_data = {}

# =========================
# Login Page
# =========================
if not st.session_state.logged_in:
    st.title("🔑 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in users and users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.role = users[username]["role"]
            st.success(f"Welcome {username} ({st.session_state.role})")
        else:
            st.error("❌ Invalid username or password")

# =========================
# Employee Flow
# =========================
elif st.session_state.role == "employee":
    if st.session_state.page is None:
        st.title("📊 Daily Sales Input")
        date = st.date_input("Date", datetime.date.today())
        vape = st.number_input("Vape Sales (CG2)", min_value=0.0, step=1.0)
        international = st.number_input("International Cigarettes (CG1)", min_value=0.0, step=1.0)
        australian = st.number_input("Australian Cigarettes (TMC+RYO)", min_value=0.0, step=1.0)
        non_tobacco = st.number_input("Non-Tobacco Sales", min_value=0.0, step=1.0)
        total_sales = vape + international + australian + non_tobacco

        if st.button("Next →"):
            st.session_state.sales_data = {
                "date": date,
                "vape": vape,
                "international": international,
                "australian": australian,
                "non_tobacco": non_tobacco,
                "total": total_sales
            }
            st.session_state.page = "cash"

    elif st.session_state.page == "cash":
        st.title("💵 Cash Closing")
        cash_notes = st.number_input("Cash Left (Notes)", min_value=0.0, step=1.0)
        cash_coins = st.number_input("Cash Left (Coins)", min_value=0.0, step=1.0)
        safe_notes = st.number_input("Safe (Notes)", min_value=0.0, step=1.0)
        safe_coins = st.number_input("Safe (Coins)", min_value=0.0, step=1.0)
        eftpos_main = st.number_input("EFTPOS Main", min_value=0.0, step=1.0)
        eftpos_backup = st.number_input("EFTPOS Backup", min_value=0.0, step=1.0)
        expenses = st.number_input("Expenses", min_value=0.0, step=1.0)
        expenses_desc = st.text_input("Expense Description")
        system_sales = st.number_input("System Sales (from POS)", min_value=0.0, step=1.0)

        # Cash Left Yesterday
        last_row = c.execute("SELECT cash_notes, cash_coins FROM daily_sales ORDER BY id DESC LIMIT 1").fetchone()
        if last_row:
            cash_left_yesterday = last_row[0] + last_row[1]
        else:
            cash_left_yesterday = 0

        # الحسابات
        cash_left_total = cash_notes + cash_coins
        safe_total = safe_notes + safe_coins
        net_sales = (cash_left_total + safe_total + eftpos_main + eftpos_backup + expenses) - cash_left_yesterday
        difference = system_sales - net_sales

        if st.button("✅ Confirm & Save"):
            c.execute('''INSERT INTO daily_sales 
                (date, vape, international, australian, non_tobacco, total,
                 cash_notes, cash_coins, safe_notes, safe_coins,
                 eftpos_main, eftpos_backup, expenses, expenses_desc,
                 net_sales, system_sales, difference)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (str(st.session_state.sales_data["date"]), 
                  st.session_state.sales_data["vape"],
                  st.session_state.sales_data["international"],
                  st.session_state.sales_data["australian"],
                  st.session_state.sales_data["non_tobacco"],
                  st.session_state.sales_data["total"],
                  cash_notes, cash_coins, safe_notes, safe_coins,
                  eftpos_main, eftpos_backup, expenses, expenses_desc,
                  net_sales, system_sales, difference))
            conn.commit()
            st.success("✅ Data saved successfully!")
            st.session_state.page = None  # reset flow
            st.session_state.sales_data = {}

# =========================
# Manager Flow
# =========================
elif st.session_state.role == "manager":
    st.title("📊 Manager Dashboard")
    df = pd.read_sql("SELECT * FROM daily_sales ORDER BY id DESC", conn)
    st.dataframe(df)
