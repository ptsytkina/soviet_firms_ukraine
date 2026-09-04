import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Firms database", layout="wide")
st.title("Soviet Ukrainian firms Database (1920-1990)")

# Підключення до бази даних
conn = sqlite3.connect("enterprises.db")

# Пошуковий рядок
search = st.text_input("🔍 Search by info/city:")

# Зчитування даних
df = pd.read_sql_query("SELECT * FROM enterprises", conn)

# Фільтрація в режимі реального часу
if search:
    df = df[
        df['firm_name'].str.contains(search, case=False, na=False) |
        df['firm_city'].str.contains(search, case=False, na=False)
    ]

# Відображення інтерактивної таблиці
st.dataframe(df, use_container_width=True)

conn.close()