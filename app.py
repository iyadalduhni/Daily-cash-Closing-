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

def add_user(username, password, ro_
