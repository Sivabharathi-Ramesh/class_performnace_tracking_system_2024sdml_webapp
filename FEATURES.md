# Class Performance Tracking System - Specialized Features

## Overview
This application now features specialized dashboards and functionality for **Students** and **Teachers**, providing role-based access and tailored experiences.

---

## Student Features

### 1. Student Dashboard (`/student/dashboard`)
Personalized overview with real-time statistics:
- **Homework Summary**: Pending, Submitted, and Graded assignments count
- **Attendance Overview**: Total classes, present count, and attendance percentage
- **Doubts Tracking**: Total questions asked, answered, and pending
- **Exercism Progress**: Username display and quick access
- **Quick Actions**: Fast navigation to key features

### 2. My Homework Status (`/homework/status`)
Enhanced homework management:
- View all assigned homework with status filtering
- Mark homework as submitted
- Unsubmit if needed (before grading)
- View grades once assignments are graded
- Color-coded status badges (Pending/Submitted/Graded)
- Filter by status (All/Pending/Submitted/Graded)

### 3. My Attendance (`/student/attendance`)
Personal attendance tracking:
- View attendance records by subject and date
- Filter by month and year
- Visual summary cards showing:
  - Total classes attended
  - Present/Absent counts
  - Overall attendance percentage
- Color-coded status indicators

### 4. My Doubts & Questions (`/student/doubts`)
Interactive Q&A system:
- Ask questions about homework assignments
- Track question status (pending/answered)
- Edit or delete own questions
- View teacher responses
- Filter by homework assignment
- Floating action button for quick question posting

### 5. Homework Calendar
Visual calendar view of all homework due dates

---

## Teacher Features

### 1. Teacher Dashboard (`/teacher/dashboard`)
Comprehensive class overview:
- **Class Statistics**: Total students, subjects, active homework
- **Attendance Management**: Today's classes and marked status
- **Homework Overview**: Pending submissions and assignments to grade
- **Student Doubts**: Unanswered questions requiring attention
- **Quick Actions**: Direct access to common tasks

### 2. Mark Attendance (`/store`)
Efficient attendance marking:
- Select subject and date
- Mark all students (Present/Absent Informed/Absent Uninformed)
- Edit existing attendance
- Validation ensures all students are marked
- Visual feedback for saved attendance

### 3. View Attendance Records (`/view`)
Flexible attendance reporting:
- Filter by day, month, or year
- Subject-wise filtering
- Comprehensive attendance reports
- Export-ready table format

### 4. Manage & Grade Homework (`/homework/manage`)
Complete homework lifecycle management:
- **Post New Homework**: Create assignments with due dates
- **Edit Homework**: Update existing assignments
- **Delete Homework**: Remove assignments
- **Gradebook**: Interactive grading table
  - Grade multiple students at once
  - Real-time grade saving
  - Filter by subject and date
- **View Doubts**: Access student questions per assignment

### 5. Student Doubts Management (`/teacher/doubts`)
Centralized question handling:
- View all student questions
- Filter by status (Unanswered/Answered/All)
- Filter by homework assignment
- Answer questions directly
- Edit existing answers
- Statistics: Total questions, answered, pending

### 6. Teacher Analytics (`/teacher/analytics`)
Data-driven insights dashboard:
- **Attendance Overview**: Visual charts and statistics
- **Homework Statistics**: Submission status breakdown
- **Student Performance Ranking**:
  - By attendance percentage
  - By homework grades
  - By participation (questions asked)
- **Subject-wise Analysis**: Performance metrics per subject
- **Students Needing Attention**: Alert system for low performers
  - Low attendance warnings (<75%)
  - Low grade warnings (<60)

### 7. Individual Student Reports (`/individual`)
Detailed student analysis:
- Search by name or roll number
- Filter by subject, date, month, or year
- Comprehensive attendance history
- Performance tracking

---

## Role-Based Access Control

### Authentication & Authorization
- **Login System**: Users select role (Admin/Teacher/Student)
- **Automatic Redirects**: Users land on role-appropriate dashboard
- **Protected Routes**:
  - Students cannot access teacher/admin pages
  - Teachers cannot access student-specific pages
  - Admin has full access

### Specialized Endpoints

#### Student APIs
- `/api/student/dashboard_stats` - Dashboard statistics
- `/api/student/attendance` - Personal attendance records
- `/api/student/doubts` - Personal doubts and questions
- `/api/student/ask_doubt` - Submit new question
- `/api/student/submit_homework` - Submit homework
- `/api/student/grade/<id>` - View grade for specific homework

#### Teacher APIs
- `/api/teacher/dashboard_stats` - Teacher dashboard data
- `/api/teacher/doubts` - All student doubts with filtering
- `/api/teacher/analytics` - Class analytics and insights
- `/api/teacher/performance` - Student performance rankings

---

## Key Improvements

### For Students
1. **Simplified Navigation**: Role-specific menu and dashboard
2. **Self-Service**: Submit homework and track progress independently
3. **Better Communication**: Easy doubt posting and tracking
4. **Progress Visibility**: Clear view of grades and attendance
5. **Mobile-Friendly**: Responsive design for all devices

### For Teachers
1. **Centralized Control**: All teaching tools in one place
2. **Data Insights**: Analytics to identify struggling students
3. **Efficient Grading**: Bulk operations and quick grading
4. **Better Communication**: Centralized doubt management
5. **Time-Saving**: Quick actions and bulk operations

### Security & Privacy
1. **Row-Level Security**: Students only see their own data
2. **Role Validation**: All routes check user permissions
3. **Data Isolation**: Students cannot access other students' information
4. **Audit Trail**: Track who marks attendance and posts homework

---

## Technology Stack
- **Backend**: Python Flask with SQLite
- **Frontend**: Vanilla JavaScript with modern ES6+
- **Charts**: Chart.js for analytics visualization
- **Calendar**: FullCalendar for homework scheduling
- **Styling**: Custom CSS with responsive design

---

## Setup & Usage

### Default Accounts
- **Admin**: username: `admin`, password: `admin`, role: `admin`
- **Teacher**: Create via admin panel
- **Student**: Create via admin panel and link to student records

### First Time Setup
1. Login as admin
2. Navigate to "Manage Users"
3. Create teacher and student accounts
4. Link student accounts to student records
5. Add subjects if needed
6. Begin using the system

---

## Future Enhancements
- File upload for homework submissions
- Email notifications for grades and announcements
- Parent portal for viewing student progress
- Mobile apps (iOS/Android)
- Integration with video conferencing tools
- Advanced analytics and reporting
- Automated attendance via QR codes or face recognition
