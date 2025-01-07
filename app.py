import streamlit as st
import sqlite3

# Importing utility functions and pages
from utils.data_loader import load_data
from utils.recruiter_page import recruiter_page
from utils.jobs_page import jobs_page
from utils.submissions_page import submissions_page
from utils.single_page import single_page
from utils.path_page import path_to_file
from utils.dashboard import dashboard
from utils.ATS_Score import resume_matching_system

# Database setup
def init_db():
    conn = sqlite3.connect("mydb.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS USERS (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Sign-Up Function
def sign_up():
    st.title("Sign Up")
    user_name = st.text_input("Username", key="signup_username")
    password = st.text_input("Password", type="password", key="signup_password")

    if st.button("Sign Up"):
        conn = sqlite3.connect("mydb.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO USERS (user_name, password) VALUES (?, ?)", (user_name, password))
        conn.commit()
        conn.close()
        st.success("Sign-Up successful! You can now log in.")

# Login Function
def login():
    st.title("Login")
    user_name = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        conn = sqlite3.connect("mydb.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM USERS WHERE user_name = ? AND password = ?", (user_name, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            st.session_state.logged_in = True
            st.session_state.user_name = user_name
            st.success("Welcome to ATS!")
            st.rerun()
        else:
            st.error("Username or password is wrong")

# Main Function
def main():
    st.set_page_config(layout="wide")
    st.title("Recruitment Management Dashboard")

    init_db()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        # Display Login and Sign-Up options
        tabs = st.tabs(["Login", "Sign Up"])
        with tabs[0]:
            login()
        with tabs[1]:
            sign_up()
    else:
        # Load data
        recruiter_detail, job_requirements, submission_table = load_data()

        # Tabs for navigation
        tabs = st.tabs([
            "Dashboard",
            "Recruiter",
            "Jobs",
            "Submissions",
            "Single",
            "Folder Path",
            "ATS Score"
        ])

        with tabs[0]:
            dashboard()

        with tabs[1]:
            recruiter_page()

        with tabs[2]:
            jobs_page()

        with tabs[3]:
            submissions_page()

        with tabs[4]:
            single_page()

        with tabs[5]:
            path_to_file()

        with tabs[6]:
            resume_matching_system()

if __name__ == "__main__":
    main()
