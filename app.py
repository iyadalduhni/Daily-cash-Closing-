import streamlit as st
import datetime

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
st.write(f"**Total Sales (calculated):** {total_sales}")

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
expenses = st.number_input("Expenses", min_value=0.0, step=1.0)
expenses_desc = st.text_input("Expense Description")

# System Sales (من POS)
system_sales = st.number_input("System Sales (from POS)", min_value=0.0, step=1.0)

# الحسابات
net_sales = (cash_left_total + safe_total + eftpos_main + eftpos_backup + expenses)
difference = system_sales - net_sales

# النتائج
st.subheader("Summary")
st.write(f"📌 **Net Sales (calculated):** {net_sales}")
st.write(f"📌 **System Sales (POS):** {system_sales}")
st.write(f"📌 **Difference:** {difference}")
