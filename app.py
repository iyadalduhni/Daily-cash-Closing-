import streamlit as st
import datetime
import sqlite3
import pandas as pd

# ====== Database Setup ======
conn = sqlite3.connect("sales.db")
c = conn.cursor()

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

# ====== Streamlit App ======
st.title("Daily Cash Closing System")

# اختيار التاريخ
date = st.date_input("Date", datetime.date.today())

# المبيعات
st.header("Sales")
vape = st.number_input("Vape Sales (CG2)", min_value=0.0, step=1.0)
international = st.number_input("International Cigarettes (CG1)", min_value=0.0, step=1.0)
australian = st.number_input("Australian Cigarettes (TMC+RYO)", min_value=0.0, step=1.0)
non_tobacco = st.number_input("Non-Tobacco Sales", min_value=0.0, step=1.0)
total_sales = vape + international + australian + non_tobacco

# الكاش
st.header("Cash Closing")
cash_notes = st.number_input("Cash Left (Notes)", min_value=0.0, step=1.0)
cash_coins = st.number_input("Cash Left (Coins)", min_value=0.0, step=1.0)
safe_notes = st.number_input("Safe (Notes)", min_value=0.0, step=1.0)
safe_coins = st.number_input("Safe (Coins)", min_value=0.0, step=1.0)

cash_left_total = cash_notes + cash_coins
safe_total = safe_notes + safe_coins

# EFTPOS
eftpos_main = st.number_input("EFTPOS Main", min_value=0.0, step=1.0)
eftpos_backup = st.number_input("EFTPOS Backup", min_value=0.0, step=1.0)

# المصاريف
st.header("Expenses")
