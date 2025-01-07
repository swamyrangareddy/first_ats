import streamlit as st
import pandas as pd
import sqlite3

# Database connection
def get_db_connection():
    return sqlite3.connect('mydb.db')

# Fetch submission details
def load_submission_data():
    conn = get_db_connection()
    query = "SELECT * FROM Submissions"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Update submission notes
def update_submission_notes(submission_id, new_notes):
    conn = get_db_connection()
    query = """
        UPDATE Submissions
        SET notes = ?
        WHERE Submission_ID = ?
    """
    conn.execute(query, (new_notes, submission_id))
    conn.commit()
    conn.close()

# Add a new submission
def add_new_submission(job_id, date_of_submission, client_name, job_title, city, state, country, recruiter_id, visa, pay_rate, status, notes):
    conn = get_db_connection()
    query = """
        INSERT INTO Submissions (Job_ID, Data_of_Submission, Client_Name, Job_title, Candidate_City, Candidate_State, Candidate_Country, Recruiter_id, Visa, Pay_Rate, Status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    conn.execute(query, (job_id, date_of_submission, client_name, job_title, city, state, country, recruiter_id, visa, pay_rate, status, notes))
    conn.commit()
    conn.close()

# Remove a submission
def remove_submission(submission_id):
    conn = get_db_connection()
    query = "DELETE FROM Submissions WHERE Submission_ID = ?"
    conn.execute(query, (submission_id,))
    conn.commit()
    conn.close()

# Submissions Page
def submissions_page():
    st.header("Submission Table")

    submission_data = load_submission_data()

    # Search functionality
    search_term = st.text_input("Search by Client Name:")
    filtered_df = submission_data[
        submission_data['Client_Name'].str.contains(search_term, case=False, na=False)
    ]
    st.dataframe(filtered_df, hide_index=True, use_container_width=True)

    # Action selection
    action = st.radio(
        "Choose Action:",
        options=["Edit Notes for a Submission", "Add a New Submission", "Remove Submission"]
    )

    if action == "Edit Notes for a Submission":
        st.subheader("Edit Notes for a Submission")
        submission_ids = filtered_df['Submission_ID'].tolist()
        submission_ids.insert(0, "Select a Submission ID")

        selected_submission_id = st.selectbox("Select Submission ID:", submission_ids)
        if selected_submission_id != "Select a Submission ID":
            current_notes = submission_data.loc[
                submission_data['Submission_ID'] == selected_submission_id, 'notes'
            ].values[0]

            new_notes = st.text_area("Update Notes:", value=current_notes)

            if st.button("Save Notes"):
                update_submission_notes(selected_submission_id, new_notes)
                st.success("Notes updated successfully!")
                st.experimental_rerun()

    elif action == "Add a New Submission":
        st.subheader("Add a New Submission")
        with st.form("add_submission_form"):
            job_id = st.number_input("Job ID:", min_value=1, step=1)
            date_of_submission = st.date_input("Date of Submission:")
            client_name = st.text_input("Client Name:")
            job_title = st.text_input("Job Title:")
            city = st.text_input("Candidate City:")
            state = st.text_input("Candidate State:")
            country = st.text_input("Candidate Country:")
            recruiter_id = st.number_input("Recruiter ID:", min_value=1, step=1)
            visa = st.text_input("Visa:")
            pay_rate = st.number_input("Pay Rate:", min_value=0, step=1)
            status = st.selectbox("Status:", ["Initial discussion", "Interview", "Submitted", 'Selected'])
            notes = st.text_area("Notes:")

            if st.form_submit_button("Add Submission"):
                add_new_submission(job_id, date_of_submission, client_name, job_title, city, state, country, recruiter_id, visa, pay_rate, status, notes)
                st.success("New submission added successfully!")
                st.experimental_rerun()

    elif action == "Remove Submission":
        st.subheader("Remove a Submission")
        submission_ids = filtered_df['Submission_ID'].tolist()
        submission_ids.insert(0, "Select a Submission ID")

        selected_submission_id = st.selectbox("Select Submission ID:", submission_ids)
        if selected_submission_id != "Select a Submission ID":
            if st.button("Remove Submission"):
                remove_submission(selected_submission_id)
                st.success("Submission removed successfully!")
                st.experimental_rerun()

# Main Execution
def main():
    if "updated" not in st.session_state:
        st.session_state.updated = False

    submissions_page()

if __name__ == "__main__":
    main()
