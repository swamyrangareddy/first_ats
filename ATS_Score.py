import streamlit as st
import sqlite3
import pandas as pd


# SQLite Database path
DATABASE_PATH = "mydb.db"

def resume_matching_system():
    """
    A Streamlit app to match candidates' resumes to a job description based on skill overlap.
    """
    def calculate_match_percentage(job_skills, candidate_skills):
        job_skills_set = set(job_skills.lower().split(", "))
        candidate_skills_set = set(candidate_skills.lower().split(", "))
        matched_skills = job_skills_set.intersection(candidate_skills_set)
        return round((len(matched_skills) / len(job_skills_set)) * 100, 2)

    st.header("Match Candidates to Job Skills")

    # User Inputs
    job_description = st.text_area("Enter Skills:")
    match_percentage = st.number_input(
        "Enter Minimum Match Percentage:",
        min_value=0,
        max_value=100,
        value=None,
        step=1
    )

    if st.button("Find Matching Resumes"):
        if not job_description:
            st.error("Please provide a job description.")
            return

        # Connect to SQLite Database
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
        except sqlite3.Error as e:
            st.error(f"Error connecting to database: {e}")
            return

        # Query the Resumes table
        try:
            cursor.execute("SELECT * FROM Resumes")
            resume_data = cursor.fetchall()
            column_names = [description[0] for description in cursor.description]
        except sqlite3.Error as e:
            st.error(f"Error fetching data from database: {e}")
            return
        finally:
            conn.close()

        if "Skills" not in column_names:
            st.error("Database table does not contain a 'Skills' column.")
            return

        # Process each resume and calculate match percentage
        results = []
        for row in resume_data:
            candidate_name = row[column_names.index("Name")] if "Name" in column_names else "N/A"
            candidate_phone = row[column_names.index("Phone_Number")] if "Phone_Number" in column_names else "N/A"
            candidate_email = row[column_names.index("Email")] if "Email" in column_names else "N/A"
            candidate_job_title = row[column_names.index("Job_title")] if "Job_title" in column_names else "N/A"
            candidate_current_company = row[column_names.index("Current_Job")] if "Current_Job" in column_names else "N/A"
            candidate_skills = row[column_names.index("Skills")] if "Skills" in column_names else ""
            candidate_location = row[column_names.index("Location")] if "Location" in column_names else "N/A"

            match_score = calculate_match_percentage(job_description, candidate_skills)
            if match_score >= match_percentage:
                results.append({
                    "Name": candidate_name,
                    "Phone_Number": candidate_phone,
                    "Email": candidate_email,
                    "Job_title": candidate_job_title,
                    "Current_Job ": candidate_current_company,
                    "Skills": candidate_skills,
                    "Location": candidate_location,
                    "Match Percentage": match_score
                })

        # Display results
        if results:
            results_df = pd.DataFrame(results)
            st.success(f"Found {len(results)} matching candidates!")
            st.dataframe(results_df)

            # Provide download option
            csv_data = results_df.to_csv(index=False)
            st.download_button(
                "Download Results as CSV",
                data=csv_data,
                file_name="matching_candidates.csv",
                mime="text/csv"
            )
        else:
            st.warning("No candidates matched the specified criteria.")

# Run the app
if __name__ == "__main__":
    resume_matching_system()
