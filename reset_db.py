import sqlite3

# امسح الملف sales.db يدويًا أو خليه ينعمل Overwrite
conn = sqlite3.connect("sales.db")
c = conn.cursor()

# احذف الجداول القديمة إذا موجودة
c.execute("DROP TABLE IF EXISTS daily_sales")
c.execute("DROP TABLE IF EXISTS users")

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

# إضافة مدير افتراضي
c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
          ("manager", "admin123", "manager"))

conn.commit()
conn.close()

print("✅ Database reset and recreated successfully!")
