import streamlit as st
import sqlite3

# Create a connection object
conn = sqlite3.connect('data.db')
# Create a cursor object
c = conn.cursor()

# Create a table
c.execute('''CREATE TABLE IF NOT EXISTS data
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL, age INTEGER NOT NULL)''')

with st.form("my_form"):
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0, max_value=100)
    submitted = st.form_submit_button("Submit")

    if submitted:
        c.execute("INSERT INTO data (name, age) VALUES (?, ?)", (name, age))
        conn.commit()
        st.success("Data inserted successfully!")