import sqlite3
import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import pandas as pd
import docx2txt
import re
import time


def path_to_file():
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))  # Configure the Google API key

    # Folder path
    folder_path = "D:/Resumes"

    # Gemini Pro Response
    def get_gemini_response(input_text):
        model = genai.GenerativeModel('gemini-pro')
        try:
            response = model.generate_content(input_text)
            return response.text
        except Exception as e:
            print(f"Error processing input: {e}")
            return None

    def input_pdf_text(uploaded_file):
        if uploaded_file is not None:
            reader = pdf.PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        else:
            raise FileNotFoundError("No file uploaded")

    def input_docx_text(uploaded_file):
        if uploaded_file is not None:
            text = docx2txt.process(uploaded_file)
            return text
        else:
            raise FileNotFoundError("No file uploaded")

    # Prompt
    input_prompt = """
        You are a highly skilled ATS (Applicant Tracking System) specializing in resume parsing. Extract the following details from the provided resume text carefully, focusing only on valid USA and India phone numbers.

        1. **Name:** The candidate's full name, typically at the top of the resume.
        2. **Phone Number:** Extract only valid phone numbers in the following formats:  
        - **USA**: +1-XXX-XXX-XXXX or (XXX) XXX-XXXX  
        - **India**: +91-XXXXX-XXXXX or XXXXX-XXXXX
        3. **Email ID:** A valid email format (e.g., example@example.com).
        4. **Job Title:** The most recent or current job title.
        5. **Current Company:** The company the candidate is currently or most recently employed with.
        6. **Skills:** A list of skills mentioned, separated by commas.
        7. **Location:** City, state, or region where the candidate is based.

        ### Dos:  
        - Extract USA phone numbers in the format: +1-XXX-XXX-XXXX or (XXX) XXX-XXXX.  
        - Extract India phone numbers in the format: +91-XXXXX-XXXXX or XXXXX-XXXXX.  
        - Look for the candidate’s full name at the top of the resume, using title case (e.g., "John Doe").  
        - Ensure emails include an `@` symbol and a valid domain (e.g., example@example.com).  
        - Identify job titles and current company names under "Experience" or "Work History."  
        - Extract technical and soft skills explicitly listed in the resume, separated by commas.  
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
    # Connect to the SQLite database (mydb.db)
    conn = sqlite3.connect('mydb.db')
    cursor = conn.cursor()

    # Streamlit app
    st.title("Smart ATS")
    folder_path = st.text_input("Enter the folder path containing resumes")
    submit_button = st.button("Submit", key="submit_button")

    if submit_button:
        if folder_path:
            file_list = [f for f in os.listdir(folder_path) if f.endswith('.pdf') or f.endswith('.docx')]
            total_files = len(file_list)
            data = []
            
            if total_files == 0:
                st.warning("No PDF or DOCX files found in the provided folder path.")
            else:
                progress_bar = st.progress(0)
                progress_text = st.empty()

                # Iterate through the files in the folder
                for idx, filename in enumerate(file_list):
                    file_path = os.path.join(folder_path, filename)
                    try:
                        if filename.endswith('.pdf'):
                            text = input_pdf_text(file_path)
                        elif filename.endswith('.docx'):
                            text = input_docx_text(file_path)

                        formatted_prompt = input_prompt.format(text=text)
                        response = get_gemini_response(formatted_prompt)

                        # Replace single quotes with double quotes (if necessary) and remove newlines
                        response = re.sub(r"'", '"', response)
                        response = response.replace('\n', ' ')

                        # Extract data using regex
                        name = re.search(r"Name:\s*(.*?)(,|$)", response )
                        phone = re.search(r"Phone Number:\s*(.*?)(,|$)", response)
                        email = re.search(r"Email ID:\s*(.*?)(,|$)", response)
                        job_title = re.search(r"Job Title:\s*(.*?)(,|$)", response)
                        current_company = re.search(r"Current Company:\s*(.*?)(,|$)", response)
                        skills_match = re.search(r"(?:Skills|Technologies Used):\s*(.*?)(?=\s(?:Location|Phone Number|$))", response, re.IGNORECASE)
                        location = re.search(r"Location:\s*(.*?)(,|$)", response)

                        # Prepare data for insertion into the database
                        name_value = name.group(1).strip() if name else 'Null'
                        phone_value = phone.group(1).strip() if phone else 'Null'
                        email_value = email.group(1).strip() if email else 'Null'
                        job_title_value = job_title.group(1).strip() if job_title else 'Null'
                        current_company_value = current_company.group(1).strip() if current_company else 'Null'
                        skills_value = skills_match.group(1).strip() if skills_match and skills_match.group(1).strip() else 'Null'
                        location_value = location.group(1).strip() if location else 'Null'

                        # Insert the extracted data into the Resumes table
                        cursor.execute("""
                            INSERT INTO Resumes (Name, Email, Phone_Number, Job_title, Current_Job, Skills, Location)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (name_value, email_value, phone_value, job_title_value, current_company_value, skills_value, location_value))

                    except Exception as e:
                        st.error(f"Error processing file {filename}: {e}")
                    
                    # Update progress bar
                    progress_percentage = (idx + 1) / total_files * 100
                    progress_bar.progress(int(progress_percentage))
                    progress_text.text(f"Processing file {idx + 1} of {total_files}")

                # Commit the changes to the database
                conn.commit()
                st.success("Resume data has been successfully stored in the SQLite database.")
        else:
            st.error("Please enter a valid folder path.")

    # Close the database connection after processing
    conn.close()
