import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import pandas as pd
import docx2txt
import re
import time
import sqlite3

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def single_page():
    # Database connection
    def init_db():
        conn = sqlite3.connect(r"mydb.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Resumes(
                Resume_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name VARCHAR(50) NOT NULL,
                Email VARCHAR(50) NOT NULL,
                Phone_Number VARCHAR(20) NOT NULL,
                Job_title VARCHAR(50) NOT NULL,
                Current_Job VARCHAR(50) NOT NULL,
                Skills TEXT NOT NULL,
                Location VARCHAR(50) NOT NULL
            )
        ''')
        conn.commit()
        return conn, cursor

    def save_to_db(data):
        conn, cursor = init_db()
        cursor.execute('''
            INSERT INTO Resumes (Name, Email, Phone_Number, Job_title, Current_Job, Skills, Location)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['Name'],
            data['Email ID'],
            data['Phone Number'],
            data['Job Title'],
            data['Current Company'],
            data['Skills'],
            data['Location']
        ))
        conn.commit()
        conn.close()

    def get_gemini_response(input_text, file_content, prompt):
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content([input_text, file_content, prompt])
        return response.text

    def input_pdf_text(uploaded_file):
        if uploaded_file is not None:
            reader = pdf.PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        else:
            raise FileNotFoundError("No file uploaded")

    def input_doc_text(uploaded_file):
        if uploaded_file is not None:
            text = docx2txt.process(uploaded_file)
            return text
        else:
            raise FileNotFoundError("No file uploaded")

    # Streamlit UI
    st.header("Smart ATS")
    input_text = st.text_area("Job Description: ", key="input")
    uploaded_file = st.file_uploader("Upload your resume (PDF/DOCX)...", type=["pdf", "docx"])

    if uploaded_file is not None:
        st.write("File Uploaded Successfully")

    submit2 = st.button("Get Percentage")
    submit1 = st.button("Submit")

    input_prompt1 =  """
    You are a highly skilled ATS (Applicant Tracking System) specializing in resume parsing. Extract the following details from the provided resume text carefully, focusing only on valid USA and India phone numbers.

    1. **Name:** The candidate's full name, typically at the top of the resume.
    2. **Phone Number:** Extract only valid phone numbers in the following formats:  
    - **USA**: +1-XXX-XXX-XXXX or (XXX) XXX-XXXX  
    - **India**: +91-XXXXX-XXXXX or XXXXX-XXXXX
    3. **Email ID:** A valid email format (e.g., example@example.com).
    4. **Job Title:** The most recent or current job title.
    5. **Current Company:** The company the candidate is currently or most recently employed with.
    6. **Skills:** A list of skills explicitly mentioned under sections like "Skills", "Technical Skills", or "Core Competencies". Extract the skills from these sections, separating them by commas.  
    7. **Location:** City, state, or region where the candidate is based.

    ### Dos:  
    - Extract USA phone numbers in the format: +1-XXX-XXX-XXXX or (XXX) XXX-XXXX.  
    - Extract India phone numbers in the format: +91-XXXXX-XXXXX or XXXXX-XXXXX.  
    - Look for the candidate’s full name at the top of the resume, using title case (e.g., "John Doe").  
    - Ensure emails include an `@` symbol and a valid domain (e.g., example@example.com).  
    - Identify job titles and current company names under "Experience" or "Work History."  
    - Extract technical and soft skills explicitly listed in sections labeled "Skills", "Technical Skills", "Core Competencies", or similar. These skills should be separated by commas.
    - Ensure skills like "Python", "SQL", "ReactJS", "Machine Learning", "AWS", etc., are extracted correctly from the relevant sections.
    - Identify the candidate’s location as the city, state, or country, avoiding company addresses.

    ### Don’ts:  
    - Don’t extract phone numbers that don’t match valid USA or India formats.  
    - Don’t assume the first word in the document is the name if it doesn't follow title case.  
    - Avoid incomplete or malformed email addresses with spaces or special characters.  
    - Don’t extract outdated job titles if current ones are available.  
    - Avoid capturing irrelevant numeric strings as phone numbers.  
    - Don’t include generic terms like “communication skills” unless explicitly listed.  
    - Ensure the location isn’t mistaken for company headquarters.

    ### Resume:
    {text}

    **Output Format:**  
    Please provide the response as a single string formatted as follows:  
    Name: [value or 'Null'],  
    Phone Number: [value or 'Null'],  
    Email ID: [value or 'Null'],  
    Job Title: [value or 'Null'],  
    Current Company: [value or 'Null'],  
    Skills: [list of values or 'Null'],  
    Location: [value or 'Null']  

    Ensure all fields are filled accurately or marked as 'Null' if missing.

    """

    input_prompt2 = """
        Evaluate the resume against the job description. Provide a percentage match, missing keywords, and final thoughts.
    """

    if submit1:
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.pdf'):
                text = input_pdf_text(uploaded_file)
            elif uploaded_file.name.endswith('.docx'):
                text = input_doc_text(uploaded_file)
            else:
                st.error("Unsupported file format.")
                return

            progress_bar = st.progress(0)
            progress_text = st.empty()
            for percent_complete in range(100):
                time.sleep(0.05)
                progress_bar.progress(percent_complete + 1)
                progress_text.text(f"Processing {uploaded_file.name}: {percent_complete + 1}% completed")

            response = get_gemini_response(input_text, text, input_prompt1)
            response = re.sub(r"'", '"', response).replace('\n', ' ')

            # Extract data using regex
            name = re.search(r"Name:\s*(.*?)(,|$)", response)
            phone = re.search(r"Phone Number:\s*(.*?)(,|$)", response)
            email = re.search(r"Email ID:\s*(.*?)(,|$)", response)
            job_title = re.search(r"Job Title:\s*(.*?)(,|$)", response)
            current_company = re.search(r"Current Company:\s*(.*?)(,|$)", response)
            skills =  re.search(r"(?:Skills|Technologies Used):\s*(.*?)(?=\s(?:Location|Phone Number|$))", response, re.IGNORECASE)
            location = re.search(r"Location:\s*(.*?)(,|$)", response)

            # Prepare data dictionary
            data = {
                'Name': name.group(1).strip() if name else 'Null',
                'Phone Number': phone.group(1).strip() if phone else 'Null',
                'Email ID': email.group(1).strip() if email else 'Null',
                'Job Title': job_title.group(1).strip() if job_title else 'Null',
                'Current Company': current_company.group(1).strip() if current_company else 'Null',
                'Skills': skills.group(1).strip() if skills else 'Null',
                'Location': location.group(1).strip() if location else 'Null'
            }

            # Display results in DataFrame
            df = pd.DataFrame([data])
            st.dataframe(df[['Name', 'Phone Number', 'Email ID', 'Job Title', 'Skills']], use_container_width=True)

            # Save to database
            try:
                save_to_db(data)
                st.success("Resume data saved to database successfully!")
            except sqlite3.Error as e:
                st.error(f"Failed to save to database: {e}")

        else:
            st.write("Please upload the resume.")

    elif submit2:
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.pdf'):
                content = input_pdf_text(uploaded_file)
            elif uploaded_file.name.endswith('.docx'):
                content = input_doc_text(uploaded_file)
            response = get_gemini_response(input_prompt2, content, input_text)
            st.subheader("The Response is:")
            st.write(response)
        else:
            st.write("Please upload the resume.")
