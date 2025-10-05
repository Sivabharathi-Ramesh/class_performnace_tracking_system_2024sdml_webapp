# Quick Start Guide - Class Performance Tracking System

## Getting Started

### Starting the Application

```bash
cd cpts_latest_october
python app.py
```

The application will be available at: `http://localhost:5001`

---

## Student Guide

### Logging In
1. Open browser to `http://localhost:5001`
2. Enter your username
3. Enter your password
4. Select **Student** from the role dropdown
5. Click **Login**

### Your Dashboard
After login, you'll see:
- **Homework Summary**: How many assignments are pending, submitted, or graded
- **Attendance Stats**: Your attendance percentage
- **Doubts Tracker**: Questions you've asked and their answers
- **Quick Actions**: Buttons to common features

### Submitting Homework
1. Click **View All Homework** or **Submit Homework**
2. Find the assignment
3. Click **Mark as Submitted** button
4. Confirm your submission

### Checking Your Grades
1. Go to **My Homework Status**
2. Look for assignments marked as **Graded**
3. Your grade will be displayed in the card

### Viewing Your Attendance
1. Click **Check Attendance** or **My Attendance**
2. Use filters to select:
   - Subject (or All Subjects)
   - Month and Year
3. Click **Apply Filters**
4. View your attendance summary and detailed records

### Asking Questions (Doubts)
1. Click the **+** floating button or **Ask a Doubt**
2. Select the homework assignment
3. Type your question
4. Click **Submit Question**
5. Check back later for the teacher's answer

### Tracking Your Questions
1. Go to **My Doubts & Questions**
2. See all your questions
3. Green cards = Answered
4. Yellow cards = Waiting for answer
5. Edit or delete your questions if needed

---

## Teacher Guide

### Logging In
1. Open browser to `http://localhost:5001`
2. Enter your username
3. Enter your password
4. Select **Teacher** from the role dropdown
5. Click **Login**

### Your Dashboard
View important metrics:
- **Total Students & Subjects**
- **Active Homework Assignments**
- **Today's Attendance Status**
- **Unanswered Student Questions**

### Marking Attendance
1. Click **Mark Attendance** or **Store Attendance**
2. Select the subject
3. Select the date (defaults to today)
4. Mark each student:
   - **Present**
   - **Absent Informed**
   - **Absent Uninformed**
5. Click **Save Attendance**

### Posting New Homework
1. Go to **Manage Homework**
2. Fill in the form:
   - Title
   - Subject
   - Due Date
   - Description
3. Click **Save Homework**

### Grading Homework
1. Go to **Manage & Grade Homework**
2. Click the **Gradebook & Assignments** tab
3. Find the assignment row
4. Enter grades in the student columns
5. Grades save automatically as you type

### Answering Student Questions
1. Go to **Answer Doubts** or **Manage Student Doubts**
2. Filter by:
   - **Unanswered Only** (recommended)
   - Specific homework
3. Read each question
4. Type your answer in the text box
5. Click **Submit Answer**

### Viewing Analytics
1. Click **View Analytics**
2. Explore:
   - **Attendance Overview** (pie chart)
   - **Homework Statistics** (bar chart)
   - **Student Performance Rankings**
   - **Subject-wise Analysis**
   - **Students Needing Attention** (alerts)

### Identifying Students Who Need Help
1. Go to **Analytics**
2. Scroll to **Students Needing Attention**
3. See students with:
   - Low attendance (<75%)
   - Low grades (<60)
4. Take appropriate action

### Viewing Individual Student Reports
1. Click **Student Reports** or **Individual**
2. Search by name or roll number
3. Select filters (subject, date range)
4. Click **Search**
5. View detailed attendance history

### Viewing All Attendance Records
1. Go to **View Records** or **View Attendance**
2. Select:
   - Subject
   - Filter type (Day/Month/Year)
   - Date/Month/Year
3. Click **Show Records**
4. View comprehensive attendance table

---

## Admin Guide

### Managing Users
1. Login as **Admin**
2. Click **Manage Users**
3. Create new accounts:
   - Enter username and password
   - Select role (Admin/Teacher/Student)
   - For students, link to student record
4. Delete users if needed

### Best Practices
- Create one account per student
- Link student accounts to their records
- Use secure passwords in production
- Regularly backup the database

---

## Common Tasks

### For Students

| Task | Navigation Path |
|------|----------------|
| Submit homework | Dashboard → View All Homework → Mark as Submitted |
| Check grades | Dashboard → My Homework Status → View Graded |
| View attendance | Dashboard → Check Attendance → Apply Filters |
| Ask question | Dashboard → Ask a Doubt → + Button |
| Track questions | Dashboard → My Doubts & Questions |

### For Teachers

| Task | Navigation Path |
|------|----------------|
| Mark attendance | Dashboard → Mark Attendance → Select Subject & Date |
| Post homework | Dashboard → Post Homework → Fill Form |
| Grade assignments | Dashboard → Manage Homework → Gradebook Tab |
| Answer questions | Dashboard → Answer Doubts → Type Answer |
| View analytics | Dashboard → View Analytics |
| Student report | Dashboard → Student Reports → Search |

---

## Tips & Tricks

### For Students
- Check your dashboard daily for updates
- Submit homework before the due date
- Ask questions early if you don't understand
- Monitor your attendance percentage
- Review graded assignments for feedback

### For Teachers
- Mark attendance at the start of each class
- Post homework with clear descriptions
- Answer student questions within 24 hours
- Review analytics weekly
- Identify struggling students early

---

## Troubleshooting

### Cannot Login
- Check username and password
- Verify you selected the correct role
- Contact admin if password forgotten

### Cannot See Dashboard
- Clear browser cache
- Try a different browser
- Check if JavaScript is enabled

### Homework Not Showing
- Refresh the page
- Check if homework was posted
- Verify you're logged in as the correct user

### Grades Not Visible
- Ensure homework is marked as "Graded"
- Teacher must assign a grade first
- Refresh the page

### Attendance Not Updating
- Teacher must mark and save attendance first
- Check the correct date is selected
- Refresh the page

---

## Support

### For Technical Issues
- Check the console for error messages (F12 in browser)
- Review the application logs
- Contact your system administrator

### For Feature Requests
- Document your request clearly
- Explain the benefit to students/teachers
- Submit to the development team

---

## Security Best Practices

### For All Users
- Never share your password
- Logout when finished
- Use a strong password
- Report suspicious activity

### For Admins
- Change default admin password immediately
- Backup database regularly
- Monitor user activity
- Review permissions quarterly

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Focus search | Ctrl + K |
| Submit form | Enter (in form) |
| Close modal | Esc |
| Scroll to top | Home |
| Scroll to bottom | End |

---

## Mobile Usage

The application is mobile-friendly:
- Responsive design adapts to screen size
- Touch-optimized buttons and forms
- Swipe gestures supported
- Works on tablets and phones

---

## Getting Help

### In-App Help
- Hover over icons for tooltips
- Read placeholder text in forms
- Check status messages for feedback

### Documentation
- **FEATURES.md** - Complete feature documentation
- **IMPLEMENTATION_SUMMARY.md** - Technical details
- **QUICK_START_GUIDE.md** - This guide

---

## Next Steps

After getting familiar with the basics:

### Students
1. Explore the homework calendar
2. Set up your Exercism username
3. Track your progress over time

### Teachers
1. Experiment with different analytics views
2. Set up your subject preferences
3. Customize grading scales if needed

### Admins
1. Import student data (if available)
2. Configure system settings
3. Set up backup schedule

---

## Conclusion

This guide covers the essential operations for getting started. For more detailed information, refer to the FEATURES.md documentation. If you encounter issues not covered here, contact your system administrator.

Happy tracking!
