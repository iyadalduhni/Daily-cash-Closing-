import streamlit as st
import sqlite3
import pandas as pd
import datetime
import os
import shutil

# ========== Database Setup ==========
DB_FILE = "sales.db"
BACKUP_FILE = "sales_backup.db"

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS daily_sales (
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
    expense_desc TEXT,
    net_sales REAL,
    system_sales REAL,
    difference REAL,
    employee_name TEXT,
    start_time TEXT,
    end_time TEXT,
    hours REAL,
    status TEXT
)
""")

conn.commit()

# ========== Helper Functions ==========
def login_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return c.fetchone()

def add_user(username, password, role):
    try:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# ========== App ==========
st.set_page_config(page_title="Daily Cash Closing", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None
    st.session_state.start_time = None
    st.session_state.selected_date = None
    st.session_state.selected_id = None

# ========== Login ==========
if not st.session_state.logged_in:
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = login_user(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.username = user[1]
            st.session_state.role = user[3]
            st.success(f"Welcome {user[1]}! Role: {user[3]}")
        else:
            st.error("Invalid credentials!")

# ========== Employee Section ==========
elif st.session_state.role == "employee":
    st.title("🧾 Cash Closing")

    today = datetime.date.today()

    # Start time auto-set once
    if not st.session_state.start_time:
        st.session_state.start_time = datetime.datetime.now().time()

    st.text_input("Employee Name", st.session_state.username, disabled=True)
    st.text_input("Start Time", str(st.session_state.start_time), disabled=True)
    end_time = st.time_input("End Time")

    # Hours calculation
    hours = (datetime.datetime.combine(today, end_time) -
             datetime.datetime.combine(today, st.session_state.start_time)).seconds / 3600.0
    st.write(f"⏱ Total Hours: {hours:.2f}")

    vape = st.number_input("Vape Sales (CG2)", 0.0)
    international = st.number_input("International Cigarettes (CG1)", 0.0)
    australian = st.number_input("Australian Cigarettes (TMC+RYO)", 0.0)
    non_tobacco = st.number_input("Non-Tobacco Sales", 0.0)
    cash_notes = st.number_input("Cash Left (Notes)", 0.0)
    cash_coins = st.number_input("Cash Left (Coins)", 0.0)
    safe_notes = st.number_input("Safe (Notes)", 0.0)
    safe_coins = st.number_input("Safe (Coins)", 0.0)
    eftpos_main = st.number_input("EFTPOS Main", 0.0)
    eftpos_backup = st.number_input("EFTPOS Backup", 0.0)
    expenses = st.number_input("Expenses", 0.0)
    expense_desc = st.text_input("Expense Description")
    system_sales = st.number_input("System Sales (from POS)", 0.0)

    total_sales = vape + international + australian + non_tobacco
    net_sales = cash_notes + cash_coins + safe_notes + safe_coins + eftpos_main + eftpos_backup - expenses
    difference = system_sales - net_sales

    if st.button("✅ Confirm & Save"):
        c.execute("""
        INSERT INTO daily_sales (
            date, vape, international, australian, non_tobacco, total,
            cash_notes, cash_coins, safe_notes, safe_coins,
            eftpos_main, eftpos_backup, expenses, expense_desc,
            net_sales, system_sales, difference,
            employee_name, start_time, end_time, hours, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(today), vape, international, australian, non_tobacco, total_sales,
            cash_notes, cash_coins, safe_notes, safe_coins,
            eftpos_main, eftpos_backup, expenses, expense_desc,
            net_sales, system_sales, difference,
            st.session_state.username, str(st.session_state.start_time), str(end_time), hours, "Pending"
        ))
        conn.commit()
        st.success("✅ Data saved successfully!")

# ========== Manager Section ==========
elif st.session_state.role == "manager":
    st.title("📊 Manager Dashboard")

    # Admin tools
    st.subheader("⚠️ Admin Tools")
    if st.button("🗑 Reset Database"):
        conn.close()
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        c = conn.cursor()
        st.success("✅ Database has been reset successfully!")

    # Backup & Restore
    st.subheader("💾 Backup & Restore")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📤 Backup Database"):
            if os.path.exists(DB_FILE):
                shutil.copy(DB_FILE, BACKUP_FILE)
                st.success("✅ Backup created successfully")
            else:
                st.error("⚠️ No database file found!")
    with col2:
        if st.button("📥 Restore Backup"):
            if os.path.exists(BACKUP_FILE):
                shutil.copy(BACKUP_FILE, DB_FILE)
                st.success("✅ Database restored successfully!")
            else:
                st.error("⚠️ No backup file found!")

    # Add user
    if st.button("➕ Add User"):
        with st.form("add_user_form"):
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password")
            new_role = st.selectbox("Role", ["employee", "manager"])
            submitted = st.form_submit_button("Add User")
            if submitted:
                if add_user(new_username, new_password, new_role):
                    st.success(f"User {new_username} added successfully!")
                else:
                    st.error("⚠️ Username already exists!")

    # Daily Records
    st.subheader("📑 Daily Records")
    df = pd.read_sql("SELECT * FROM daily_sales ORDER BY id DESC", conn)

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        df["week"] = df["date"].dt.isocalendar().week
        df["year"] = df["date"].dt.isocalendar().year
        df["day_name"] = df["date"].dt.strftime("%A")

        today = datetime.date.today()
        current_week = today.isocalendar().week
        current_year = today.isocalendar().year

        st.write(f"### 📅 Current Week {current_week} ({current_year})")
        current_df = df[(df["week"] == current_week) & (df["year"] == current_year)]

        if not current_df.empty:
            for _, row in current_df.iterrows():
                label = f"{row['date'].date()} ({row['day_name']}) - {row['employee_name']} - {row['hours']:.2f}h - Total: {row['total']}$ - Status: {row['status']}"
                if st.button(label, key=f"view_{row['id']}"):
                    st.session_state.selected_date = str(row['date'].date())
                    st.session_state.selected_id = row['id']
        else:
            st.info("⚠️ No records for this week yet")

        # Calendar to view past records
        st.subheader("📆 View Past Records")
        selected_date = st.date_input("Select a date to view its week")
        if selected_date:
            week_num = selected_date.isocalendar()[1]
            year_num = selected_date.isocalendar()[0]
            past_df = df[(df["week"] == week_num) & (df["year"] == year_num)]
            st.write(f"### Results for Week {week_num} ({year_num})")
            if not past_df.empty:
                for _, row in past_df.iterrows():
                    label = f"{row['date'].date()} ({row['day_name']}) - {row['employee_name']} - {row['hours']:.2f}h - Total: {row['total']}$ - Status: {row['status']}"
                    if st.button(label, key=f"past_{row['id']}"):
                        st.session_state.selected_date = str(row['date'].date())
                        st.session_state.selected_id = row['id']
            else:
                st.warning("No records found for that week")

        # Details
        if st.session_state.selected_date:
            st.subheader(f"📅 Details for {st.session_state.selected_date}")
            details = df[df["date"].dt.strftime("%Y-%m-%d") == st.session_state.selected_date]
            st.dataframe(details)
            if st.button("✅ Approve This Record"):
                c.execute("UPDATE daily_sales SET status='Approved' WHERE id=?", (st.session_state.selected_id,))
                conn.commit()
                st.success("Record approved successfully!")
