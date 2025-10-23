from account.models import CustomUser, StudentClassEnrollment
from assignment.models import Assignment, AssignmentSubmission 
from attendance.models import Attendance 
from marksheet.models import ClassParticipation, Marksheet
from django.db.models import Sum, Avg


def get_present_days():
    return 180

def get_attendance_detail(id):
    class_enrollment = StudentClassEnrollment.objects.filter(student_id=id, is_current=True).order_by("-id").first()
    total_attendance = Attendance.objects.filter(student_id=id, classlevel=class_enrollment.class_level).count()
    total_pressent_days = get_present_days()
    attendance = total_attendance / total_pressent_days
    return attendance 


def get_total_assignment_marks(student_id):
    # Get the current class enrollment
    class_enrollment = StudentClassEnrollment.objects.filter(
        student_id=student_id,
        is_current=True
    ).order_by("-id").first()
    
    if not class_enrollment:
        return 0  # No current enrollment
    total_assignment = Assignment.objects.filter(
        classlevel=class_enrollment.class_level
    ).count()
    
    if total_assignment == 0:
        return 
    # Submitted assignments for this student
    submitted_assignments = AssignmentSubmission.objects.filter(
        assignment__classlevel=class_enrollment.class_level,
        student_id=student_id
    )
    
    # Total marks of all submitted assignments
    total_marks = submitted_assignments.aggregate(total=Sum('marks'))['total'] or 0

    avg_mark = total_marks/total_assignment
    return avg_mark/10


def get_class_participation(student_id):
    class_enrollment = StudentClassEnrollment.objects.filter(
        student_id=student_id,
        is_current=True
    ).order_by("-id").first()
    
    if not class_enrollment:
        return 0  
    
    class_participations = ClassParticipation.objects.filter(student_id=student_id, classlevel=class_enrollment.class_level)
    avg_mark = class_participations.aggregate(avg=Avg('mark'))['avg'] or 0
    return avg_mark



def get_gender(student_id):
    student = CustomUser.objects.get(id=student_id)
    
    try:
        if student.gender == "male":
            return 0 
        
        elif student.gender == "female":
            return 1 
    
    except:
        return None 
    
    
    
def get_eca(id):
    return 1 

def get_internet_access(id):
    return 1 


def get_parent_education_level(id):
    return 1 


def get_internal_marks(id):
    attendance = get_attendance_detail(id) * 5
    assignment = get_total_assignment_marks(id) * 10 
    class_participation = get_class_participation(id)
    total = float(attendance) + float(assignment) + float(class_participation)

    return total / 20 



def get_past_mark(id):
    class_enrollment = StudentClassEnrollment.objects.filter(
        student_id=id,
        is_current=True
    ).order_by("-id").first()
    
    past_marks = Marksheet.objects.filter(student_id=id).exclude(classlevel=class_enrollment.class_level)
    
    if not past_marks.exists():
        return 0
    total_fraction = 0 
    count = past_marks.count()
    
    for mark in past_marks:
        
        if mark.full_marks > 0 :
            total_fraction += mark.marks / mark.full_marks 
    return total_fraction / count



def get_study_hour_per_week(id):
    assignment = get_total_assignment_marks(id)
    internal_mark = get_internal_marks(id)
    attendance = get_attendance_detail(id)
    
    return (float(assignment)+float(internal_mark)+float(attendance)) /3 


def get_internal_assesment_marks(id):
    class_enrollment = StudentClassEnrollment.objects.filter(
        student_id=id,
        is_current=True
    ).order_by("-id").first()
    
    current_marks = Marksheet.objects.filter(student_id=id, classlevel=class_enrollment.class_level)
    
    if not current_marks.exists():
        return 0
    
    total_fraction = 0 
    count = current_marks.count()
    
    for mark in current_marks:
        
        if mark.full_marks > 0 :
            total_fraction += mark.marks / mark.full_marks 
    return total_fraction / count
        
    
    
    
    


    
    
    
    

    
    
    
    