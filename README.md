Class Performance Tracking System
This web application provides a comprehensive system for tracking class performance, including attendance, homework, and student progress. It is designed for use by administrators, teachers, and students, with different levels of access and functionality for each role.

Features
User Authentication: Secure login system for administrators, teachers, and students.

Role-Based Access Control:

Admin: Can manage users, including adding, deleting, and assigning roles.

Teacher: Can manage homework, track attendance, and grade assignments.

Student: Can view homework status and ask questions about assignments.

Attendance Tracking:

Teachers can record daily attendance for different subjects.

View attendance records by day, month, or year.

Generate individual student attendance reports.

Homework Management:

Teachers can post, edit, and delete homework assignments.

Students can view their homework status and submit assignments.

A Q&A section for each assignment allows students to ask questions and teachers to provide answers.

Calendar view for a clear overview of assignment due dates.

Exercism Progress Tracking:

View public profiles of students on Exercism.org to track their progress.

Technology Stack
Backend: Flask (a Python web framework)

Database: SQLite

Frontend: HTML, CSS, JavaScript

Dependencies:

gunicorn==21.2.0

Flask==2.3.3

requests==2.31.0

Setup and Installation
Clone the repository:

Bash

git clone https://github.com/sivabharathi-ramesh/class_performnace_tracking_system_2024sdml_webapp.git
Navigate to the project directory:

Bash

cd cpts_latest_october
Install the required dependencies:

Bash

pip install -r requirements.txt
Run the application:

Bash

python app.py
Access the application:
Open your web browser and go to http://127.0.0.1:5001.


Admin Dashboard:

After logging in as an admin, you can manage users from the "Manage Users" link on the home page.

Teacher Dashboard:

Teachers can access attendance tracking and homework management features from the main menu.

Student Dashboard:

Students can view their homework status and other relevant information from the home page.







