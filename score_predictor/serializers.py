from rest_framework import serializers 



class StudentScoreInputSerializer(serializers.Serializer):
    Gender = serializers.IntegerField()
    Study_Hours_per_Week = serializers.FloatField()
    Attendance_Rate = serializers.FloatField()
    Past_Exam_Scores = serializers.FloatField()
    Parental_Education_Level = serializers.IntegerField()
    Internet_Access_at_Home = serializers.IntegerField()
    Extracurricular_Activities = serializers.IntegerField()
    Internal_Marks = serializers.FloatField()
    Assignment_Submission_Rate = serializers.FloatField()
    Internal_Assessment_Marks = serializers.FloatField()
    
    
class StudentScoreOutputSerializer(serializers.Serializer):
    message = serializers.CharField()
    predicted_final_scores = serializers.ListField(
        child = serializers.FloatField()
    )