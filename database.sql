-- CREATE TABLE IF NOT EXISTS Recruiter(
--     Recruiter_id INTEGER PRIMARY KEY AUTOINCREMENT,
--     Name VARCHAR(50) NOT NULL,
--     Email VARCHAR(50) NOT NULL,
--     Phone_Number INTEGER NOT NULL,
--     Location VARCHAR(50) NOT NULL,
--     Designation VARCHAR(50) NOT NULL
-- );

-- INSERT INTO Recruiter(Name, Email, Phone_Number, Location, Designation) VALUES('Alice', 'alice@gmail.com', 9937481345, 'New York', 'Recruiter');

-- CREATE TABLE IF NOT EXISTS Jobs(
--     Job_ID INTEGER PRIMARY KEY AUTOINCREMENT,
--     Job_Details VARCHAR(50) NOT NULL,
--     Job_Location VARCHAR(50) NOT NULL,
--     Bill_Rate INTEGER NOT NULL,
--     Visas VARCHAR(50) NOT NULL,
--     Description VARCHAR(50) NOT NULL,
--     Client VARCHAR(50) NOT NULL
-- );

-- INSERT INTO Jobs(Job_Details, Job_Location, Bill_Rate, Visas, Description, Client) VALUES('Data Scientist', 'New York', 100, 'H1B', 'ML Enginner with 5+ Year exp', 'Tek Systems');

-- CREATE TABLE IF NOT EXISTS Submissions(
--     Submission_ID INTEGER PRIMARY KEY AUTOINCREMENT,
--     Job_ID INTEGER,
--     Data_of_Submission DATE NOT NULL,
--     Client_Name VARCHAR(50) NOT NULL,
--     Job_title VARCHAR(50) NOT NULL,
--     Candidate_City VARCHAR(50) NOT NULL,
--     Candidate_State VARCHAR(50) NOT NULL,
--     Candidate_Country VARCHAR(50) NOT NULL,
--     Recruiter_id INTEGER,
--     Visa VARCHAR(50) NOT NULL,
--     Pay_Rate INTEGER NOT NULL,
--     Status VARCHAR(50) NOT NULL,
--     notes VARCHAR(50) NOT NULL,
--     FOREIGN KEY (Job_ID) REFERENCES Jobs(Job_ID),
--     FOREIGN KEY (Recruiter_id) REFERENCES Recruiter(Recruiter_id)
--     );

-- INSERT INTO Submissions(Job_ID, Data_of_Submission, Client_Name, Job_title, Candidate_City, Candidate_State, Candidate_Country, Recruiter_id, Visa, Pay_Rate, Status, notes) VALUES(1, '04-01-2024', 'Tek Systems', 'Data Scientist', 'New York', 'New York', 'USA', 1, 'H1B', 100, 'Submitted', 'Good Candidate');


-- CREATE TABLE IF NOT EXISTS Resumes(
--     Resume_ID INTEGER PRIMARY KEY AUTOINCREMENT,
--     Name VARCHAR(50) NOT NULL,
--     Email VARCHAR(50) NOT NULL,
--     Phone_Number INTEGER NOT NULL,
--     Job_title VARCHAR(50) NOT NULL,
--     Current_Job VARCHAR(50) NOT NULL,
--     Skills VARCHAR(50) NOT NULL,
--     Location VARCHAR(50) NOT NULL
-- );

DELETE FROM Resumes;