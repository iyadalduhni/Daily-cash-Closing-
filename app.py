import streamlit as st
import datetime
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Database Setup
# =========================
conn = sqlite3.connect("sales.db")
c = conn.cursor()

# جدول المبيعات اليومية
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
    difference REAL,
    employee_name TEXT,
    start_time TEXT,
    end_time TEXT,
    hours REAL,
    status TEXT DEFAULT 'Pending'
)''')

# جدول المستخدمين
c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)''')
conn.commit()

# إضافة مدير افتراضي إذا الجدول فاضي
c.execute("SELECT COUNT(*) FROM users")
if c.fetchone()[0] == 0:
    c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
              ("manager", "admin123", "manager"))
    conn.commit()

# =========================
# Helper Functions
# =========================
def check_user(username, password):
    user = c.execute("SELECT role FROM users WHERE username=? AND password=?", 
                     (username, password)).fetchone()
    if user:
        return user[0]
    return None

def add_user(username, password, role):
    try:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                  (username, password, role))
        conn.commit()
        return True
    except:
        return False

# =========================
# Session State
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.page = None
    st.session_state.sales_data = {}
    st.session_state.summary_data = {}
    st.session_state.show_add_user = False
    st.session_state.selected_date = None
    st.session_state.selected_id = None

# =========================
# Login Page
# =========================
if not st.session_state.logged_in:
    st.title("🔑 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        role = check_user(username, password)
        if role:
            st.session_state.logged_in = True
            st.session_state.role = role
            st.success(f"Welcome {username} ({role})")
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
        employee_name = st.text_input("Employee Name")
        start_time = st.time_input("Start Time")
        end_time = st.time_input("End Time")

        # حساب الساعات
        hours = (datetime.datetime.combine(datetime.date.today(), end_time) -
                 datetime.datetime.combine(datetime.date.today(), start_time)).seconds / 3600.0
        st.write(f"⏱ Total Hours: {hours:.2f}")

        cash_notes = st.number_input("Cash Left (Notes)", min_value=0.0, step=1.0)
        cash_coins = st.number_input("Cash Left (Coins)", min_value=0.0, step=1.0)
        safe_notes = st.number_input("Safe (Notes)", min_value=0.0, step=1.0)
        safe_coins = st.number_input("Safe (Coins)", min_value=0.0, step=1.0)
        eftpos_main = st.number_input("EFTPOS Main", min_value=0.0, step=1.0)
        eftpos_backup = st.number_input("EFTPOS Backup", min_value=0.0, step=1.0)
        expenses = st.number_input("Expenses", min_value=0.0, s
