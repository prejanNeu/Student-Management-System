# Student-Centric Attendance System API Documentation

## Overview
This document describes the **student-centric** attendance system where students mark their own attendance, while teachers and admins can view reports and statistics. The system maintains backward compatibility with existing frontend implementations.

## 🔄 **Existing APIs (Unchanged - Frontend Compatible)**

### 1. Student Self-Attendance
```
GET /api/attendance_detail/
POST /api/mark_attendance/
```
**Purpose:** Students mark their own attendance
**Permissions:** Students only
**Status:** ✅ **Unchanged** - Frontend compatibility maintained

### 2. Device-Based Attendance
```
POST /api/mark_attendance_by_id/
```
**Purpose:** Mark attendance using device ID
**Permissions:** Device authentication required
**Status:** ✅ **Unchanged** - Frontend compatibility maintained

### 3. Basic Class & Subject Lists
```
GET /api/class_list/
GET /api/subject_list/<int:classlevel>/
GET /api/get_student_by_class/<int:classlevel>
GET /api/get_attendance_detail_by_id/<int:id>/
```
**Purpose:** Basic class and student information
**Permissions:** Varies by endpoint
**Status:** ✅ **Unchanged** - Frontend compatibility maintained

---

## 🆕 **New Enhanced Features (Student-Centric)**

### 1. **Enhanced Student Self-Attendance** (New)
```
POST /api/mark_attendance_with_status/
```
**Purpose:** Students can mark their attendance with specific status (present/late)
**Permissions:** Students only
**Features:**
- Mark attendance as "present" or "late"
- Update existing attendance status for the day
- Automatic date handling (today's date)
- Duplicate prevention

**Request Example:**
```json
{
    "status": "late"
}
```

**Response Example:**
```json
{
    "message": "Attendance marked as late",
    "date": "2024-01-15",
    "status": "late"
}
```

### 2. **Class Attendance Overview** (New)
```
GET /api/student_attendance/<int:classlevel>/
```
**Purpose:** Teachers/Admins can view comprehensive attendance data for all students in a class
**Permissions:** Teachers and Admins only
**Features:**
- Individual student attendance statistics
- Present/Absent/Late counts
- Attendance percentages
- Recent attendance history

**Request Example:**
```
GET /api/student_attendance/1/
```

**Response Example:**
```json
{
    "message": "Attendance data retrieved successfully",
    "class_level": 10,
    "data": [
        {
            "student_id": 1,
            "student_name": "John Doe",
            "total_days": 30,
            "present_days": 28,
            "absent_days": 1,
            "late_days": 1,
            "attendance_percentage": 93.33,
            "recent_attendance": [...]
        }
    ]
}
```

### 3. **Attendance Statistics & Analytics** (New)
```
GET /api/attendance_statistics/
GET /api/attendance_statistics/<int:classlevel_id>/
```
**Purpose:** Get comprehensive attendance statistics and analytics
**Permissions:** Teachers and Admins only
**Features:**
- Overall or class-specific statistics
- Date range filtering (default: last 30 days)
- Daily breakdown of attendance
- Attendance rates and trends

**Request Examples:**
```
GET /api/attendance_statistics/          # Overall statistics
GET /api/attendance_statistics/1/        # Class-specific statistics
```

**Response Example:**
```json
{
    "message": "Attendance statistics retrieved successfully",
    "data": {
        "class_level": 10,
        "total_students": 25,
        "date_range": {"start": "2023-12-15", "end": "2024-01-15"},
        "total_records": 750,
        "present_count": 680,
        "absent_count": 45,
        "late_count": 25,
        "attendance_rate": 90.67,
        "daily_breakdown": [...]
    }
}
```

### 4. **Individual Student Reports** (New)
```
GET /api/student_attendance_report/<int:student_id>/
```
**Purpose:** Detailed attendance report for individual students
**Permissions:** 
- Students: Can view their own report
- Teachers/Admins: Can view any student's report
**Features:**
- Comprehensive attendance statistics
- Monthly breakdown
- Recent attendance history
- Student and class information

**Request Example:**
```
GET /api/student_attendance_report/1/
```

**Response Example:**
```json
{
    "message": "Student attendance report retrieved successfully",
    "data": {
        "student": {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com"
        },
        "class": {"id": 1, "level": 10},
        "statistics": {
            "total_days": 30,
            "present_days": 28,
            "absent_days": 1,
            "late_days": 1,
            "attendance_percentage": 93.33
        },
        "monthly_breakdown": [...],
        "recent_attendance": [...]
    }
}
```

---

## 🔐 **Permission Matrix (Student-Centric)**

| Feature | Student | Teacher | Admin |
|---------|---------|---------|-------|
| **Mark Own Attendance** | ✅ | ❌ | ❌ |
| **Mark Attendance with Status** | ✅ | ❌ | ❌ |
| **View Own Attendance** | ✅ | ✅ | ✅ |
| **View Class Attendance** | ❌ | ✅ | ✅ |
| **View Statistics** | ❌ | ✅ | ✅ |
| **View Student Reports** | Own Only | ✅ | ✅ |

---

## 📊 **Attendance Status Types**

The system supports three attendance statuses:
- **`present`** - Student attended class on time
- **`late`** - Student attended but was late
- **`absent`** - Student did not attend class (automatically tracked)

**Note:** Students can only mark themselves as "present" or "late". "Absent" status is automatically inferred when no attendance is marked for a day.

---

## 🚀 **Usage Scenarios (Student-Centric)**

### Scenario 1: Student Marking Daily Attendance
1. Student logs in and calls `POST /api/mark_attendance/` to mark attendance
2. Student can update status using `POST /api/mark_attendance_with_status/` if needed
3. System automatically prevents duplicate attendance for the same day

### Scenario 2: Student Checking Performance
1. Student calls `GET /api/student_attendance_report/1/` (their own ID)
2. Student views attendance percentage and history
3. Student identifies areas for improvement

### Scenario 3: Teacher Monitoring Class
1. Teacher calls `GET /api/student_attendance/1/` to see class attendance overview
2. Teacher calls `GET /api/attendance_statistics/1/` for class statistics
3. Teacher identifies students with attendance issues

### Scenario 4: Admin Reviewing Overall Performance
1. Admin calls `GET /api/attendance_statistics/` for overall view
2. Admin analyzes trends across all classes
3. Admin makes data-driven decisions

---

## 🔧 **Error Handling**

All endpoints include comprehensive error handling:
- **400 Bad Request**: Invalid input data or duplicate attendance
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server-side issues

---

## 📈 **Key Features**

- **Student Empowerment**: Students take responsibility for their own attendance
- **Real-time Updates**: Immediate feedback when marking attendance
- **Status Flexibility**: Students can mark as present or late
- **Duplicate Prevention**: Automatic checking for existing attendance
- **Comprehensive Reporting**: Teachers and admins get full visibility
- **Performance Analytics**: Data-driven insights for improvement

---

## 🔮 **Future Enhancements**

The student-centric system is designed to support:
- **Mobile App Integration**: Easy attendance marking on mobile devices
- **Push Notifications**: Reminders for students to mark attendance
- **Parent Portal**: Parents can view their child's attendance
- **Integration**: Connect with other school systems

---

## 📝 **Migration Notes**

- **No Database Changes**: All existing data remains intact
- **No Schema Changes**: Existing models unchanged
- **Backward Compatible**: All existing APIs work exactly as before
- **Student-Centric Design**: New features empower students to manage their attendance

---

## 🧪 **Testing**

Test the new endpoints with:
```bash
# Test enhanced student attendance
curl -X POST -H "Authorization: Token YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"status": "late"}' \
     http://localhost:8000/api/mark_attendance_with_status/

# Test class attendance overview (teacher/admin)
curl -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8000/api/student_attendance/1/
```

---

## 📞 **Support**

For questions about the student-centric attendance system:
- Check existing documentation for unchanged APIs
- Refer to this document for new features
- Test endpoints in development environment first
- Contact development team for technical support

---

## 🎯 **System Philosophy**

This attendance system follows the principle of **student empowerment** where:
- Students are responsible for their own attendance
- Teachers and admins provide oversight and support
- The system facilitates self-discipline and accountability
- Data transparency helps identify areas for improvement 