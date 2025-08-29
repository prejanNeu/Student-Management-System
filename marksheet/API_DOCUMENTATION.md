# Student Management System API Documentation

## Overview
This API provides comprehensive functionality for managing student marks in a role-based system with three user roles: Admin, Teacher, and Student.

## Authentication
All APIs require authentication. Include the authentication token in the request header:
```
Authorization: Token <your_auth_token>
```

## User Roles and Permissions

### Admin
- Can perform all operations (CRUD) on marks
- Can view all students' marks
- Can manage exam types
- Can view performance statistics

### Teacher
- Can perform all operations (CRUD) on marks
- Can view all students' marks
- Can manage exam types
- Can view performance statistics

### Student
- Can only view their own marks
- Cannot modify any marks
- Cannot access performance statistics

## API Endpoints

### 1. Exam Type Management

#### Get All Exam Types
```
GET /api/exam-types/
```
**Permissions:** All authenticated users
**Response:** List of all exam types

#### Add New Exam Type
```
POST /api/exam-types/add/
```
**Permissions:** Admin and Teacher only
**Request Body:**
```json
{
    "name": "Mid Term"
}
```

### 2. Marks Management

#### Add Marks
```
POST /api/marks/add/
```
**Permissions:** Admin and Teacher only
**Request Body (Single Mark):**
```json
{
    "student_id": 1,
    "subject_id": 1,
    "classlevel_id": 1,
    "examtype_id": 1,
    "full_marks": 100.00,
    "marks": 85.50
}
```

**Request Body (Bulk Marks):**
```json
[
    {
        "student_id": 1,
        "subject_id": 1,
        "classlevel_id": 1,
        "examtype_id": 1,
        "full_marks": 100.00,
        "marks": 85.50
    },
    {
        "student_id": 2,
        "subject_id": 1,
        "classlevel_id": 1,
        "examtype_id": 1,
        "full_marks": 100.00,
        "marks": 92.00
    }
]
```

#### Update Marks
```
PUT /api/marks/update/{mark_id}/
```
**Permissions:** Admin and Teacher only
**Request Body:**
```json
{
    "marks": 90.00
}
```

#### Delete Marks
```
DELETE /api/marks/delete/{mark_id}/
```
**Permissions:** Admin and Teacher only

#### Get Mark Details
```
GET /api/marks/{mark_id}/
```
**Permissions:** 
- Admin/Teacher: Can view any mark
- Student: Can only view their own marks

#### Get All Marks
```
GET /api/marks/
```
**Permissions:** All authenticated users
**Query Parameters:**
- `student_id`: Filter by student (Admin/Teacher only)
- `subject_id`: Filter by subject
- `examtype_id`: Filter by exam type

**Example:**
```
GET /api/marks/?subject_id=1&examtype_id=1
```

#### Get Marks by Class Level
```
GET /api/marks/class/{classlevel}/
```
**Permissions:** All authenticated users
- Admin/Teacher: Can view all marks in the class
- Student: Can only view their own marks in the class

### 3. Performance Statistics

#### Get Student Performance Statistics
```
GET /api/performance/{student_id}/
```
**Permissions:** Admin and Teacher only
**Response:**
```json
{
    "message": "Performance statistics retrieved successfully",
    "data": {
        "student_id": 1,
        "total_subjects": 5,
        "total_exams": 15,
        "average_percentage": 78.5,
        "subject_wise_stats": [
            {
                "subject__name": "Mathematics",
                "avg_marks": 85.0,
                "max_marks": 95.0,
                "min_marks": 75.0,
                "exam_count": 3
            }
        ]
    }
}
```

## Response Format

All API responses follow this standard format:

### Success Response
```json
{
    "message": "Operation completed successfully",
    "data": {...},
    "count": 5
}
```

### Error Response
```json
{
    "message": "Error description",
    "errors": {...}
}
```

## HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Validation error or invalid data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Data Validation

The API includes the following validations:
- Marks cannot exceed full marks
- Marks cannot be negative
- Full marks cannot be negative
- Required fields must be provided
- Student, subject, class level, and exam type must exist

## Example Usage Scenarios

### Scenario 1: Teacher Adding Marks for a Class
1. Teacher logs in and gets authentication token
2. Teacher calls `POST /api/marks/add/` with bulk marks data
3. System validates data and creates marks records
4. Teacher receives confirmation with created data

### Scenario 2: Student Viewing Their Marks
1. Student logs in and gets authentication token
2. Student calls `GET /api/marks/` to view their marks
3. System filters marks to show only student's own marks
4. Student receives their marks with subject details

### Scenario 3: Admin Updating Marks
1. Admin logs in and gets authentication token
2. Admin calls `PUT /api/marks/update/{mark_id}/` with new marks
3. System validates and updates the marks
4. Admin receives confirmation with updated data

## Error Handling

The API provides detailed error messages for:
- Validation errors
- Permission denied errors
- Resource not found errors
- Server errors

All errors include descriptive messages to help developers understand and resolve issues.

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing rate limiting for production use.

## Security Considerations

- All endpoints require authentication
- Role-based access control is enforced
- Students can only access their own data
- Input validation prevents malicious data
- SQL injection protection through Django ORM 