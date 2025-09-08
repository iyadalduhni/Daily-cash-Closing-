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
                 net_sales, system_sales, difference,
                 employee_name, start_time, end_time, hours, status)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (str(st.session_state.sales_data["date"]), 
                  st.session_state.sales_data["vape"],
                  st.session_state.sales_data["international"],
                  st.session_state.sales_data["australian"],
                  st.session_state.sales_data["non_tobacco"],
                  st.session_state.sales_data["total"],
                  cash_notes, cash_coins, safe_notes, safe_coins,
                  eftpos_main, eftpos_backup, expenses, expenses_desc,
                  net_sales, system_sales, difference,
                  employee_name, str(start_time), str(end_time), hours, "Pending"))
            conn.commit()

            st.success("✅ Data saved successfully! Pending Manager Approval")
            st.session_state.page = None

# =========================
# Manager Flow
# =========================
elif st.session_state.role == "manager":
    st.title("📊 Manager Dashboard")

    # إضافة مستخدم جديد
    if st.button("➕ Add User"):
        st.session_state.show_add_user = not st.session_state.show_add_user

    if st.session_state.show_add_user:
        st.subheader("👥 Add New User")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        role = st.selectbox("Role", ["employee", "manager"])
        if st.button("Save User"):
            if add_user(new_username, new_password, role):
                st.success(f"User {new_username} added successfully!")
                st.session_state.show_add_user = False
            else:
                st.error("⚠️ Username already exists")

    # Daily Records
    st.subheader("📑 Daily Records")
    df = pd.read_sql("SELECT * FROM daily_sales ORDER BY id DESC", conn)

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        df["week"] = df["date"].dt.isocalendar().week
        df["year"] = df["date"].dt.isocalendar().year
        df["day_name"] = df["date"].dt.strftime("%A")

        today = datetime.date.today()
        current_week = today.isocalendar()[1]
        current_year = today.isocalendar()[0]

        current_df = df[(df["week"] == current_week) & (df["year"] == current_year)]

        st.write(f"### Week {current_week} ({current_year})")

        if not current_df.empty:
            for _, row in current_df.iterrows():
                label = f"{row['date'].date()} ({row['day_name']}) - {row['employee_name']} - {row['hours']:.2f}h - Total: {row['total']}$ - Status: {row['status']}"
                if st.button(label, key=f"view_{row['id']}"):
                    st.session_state.selected_date = str(row['date'].date())
                    st.session_state.selected_id = row['id']
        else:
            st.info("⚠️ No records for this week yet")

        # تفاصيل اليوم + Approve
        if st.session_state.selected_date:
            st.subheader(f"📅 Details for {st.session_state.selected_date}")
            details = df[df["date"].dt.strftime("%Y-%m-%d") == st.session_state.selected_date]
            st.dataframe(details)

            if st.button("✅ Approve This Record"):
                c.execute("UPDATE daily_sales SET status='Approved' WHERE id=?", (st.session_state.selected_id,))
                conn.commit()
                st.success("Record approved successfully!")

        # تقرير الساعات الأسبوعية
        st.subheader("📊 Weekly Hours Report")
        weekly_hours = df[(df["week"] == current_week) & (df["year"] == current_year) & (df["status"] == "Approved")]
        if not weekly_hours.empty:
            report = weekly_hours.groupby("employee_name")["hours"].sum().reset_index()
            report.columns = ["Employee", "Total Hours"]
            st.table(report)
        else:
            st.info("⚠️ No approved records for this week")

    # Charts Section
    if not df.empty:
        st.subheader("📈 Sales Charts")
        categories = ["vape", "international", "australian", "non_tobacco"]
        values = [df[c].sum() for c in categories]

        if sum(values) > 0:
            fig1, ax1 = plt.subplots()
            ax1.pie(values, labels=categories, autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')
            st.pyplot(fig1)
        else:
            st.info("⚠️ No sales data available for Pie Chart")
