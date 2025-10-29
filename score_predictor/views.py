# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from keras.models import load_model
import pandas as pd
import numpy as np
from rest_framework import status 
from drf_yasg.utils import swagger_auto_schema
from .serializers import StudentScoreInputSerializer, StudentScoreOutputSerializer
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # path to /SMS-Project/
MODEL_PATH = os.path.join(BASE_DIR, "score_predictor", "models", "student_score_model.h5")

nn_model = load_model(MODEL_PATH, compile=False)

features = ['Gender', 'Study_Hours_per_Week', 'Attendance_Rate', 'Past_Exam_Scores',
            'Parental_Education_Level', 'Internet_Access_at_Home', 'Extracurricular_Activities',
            'Internal_Marks', 'Assignment_Submission_Rate', 'Internal_Assessment_Marks']



@swagger_auto_schema(
    method='post',
    request_body=StudentScoreInputSerializer,
    responses={
        status.HTTP_200_OK: StudentScoreOutputSerializer
    }
)
@api_view(['POST'])
def score_prediction(request):
    """
    Predict final exam scores from request data.
    Accepts either a single JSON object or a list of JSON objects.
    """
    try:
        data = request.data

        # Handle single dict (one record) or list (multiple records)
        if isinstance(data, dict):
            X_new = pd.DataFrame([data])
        elif isinstance(data, list):
            X_new = pd.DataFrame(data)
        else:
            return Response({"error": "Invalid JSON format. Must be an object or list of objects."}, status=400)

        # Ensure all required features exist
        missing = [f for f in features if f not in X_new.columns]
        if missing:
            return Response({"error": f"Missing features: {missing}"}, status=400)

        # Keep only required features (ignore extras)
        X_new = X_new[features]

        # Predict
        predicted_marks = nn_model.predict(X_new, verbose=0).flatten().tolist()

        # Return response
        return Response({
            "message": "Prediction successful",
            "predicted_final_exam_scores": predicted_marks
        })

    except Exception as e:
        return Response({
            "message": "Error during prediction",
            "error": str(e)
        }, status=500)



# the data format is 

# {
#     "Gender": 1,
#     "Study_Hours_per_Week": 0.6,
#     "Attendance_Rate": 0.75,
#     "Past_Exam_Scores": 0.7,
#     "Parental_Education_Level": 2,
#     "Internet_Access_at_Home": 1,
#     "Extracurricular_Activities": 0,
#     "Internal_Marks": 0.65,
#     "Assignment_Submission_Rate": 0.6,
#     "Internal_Assessment_Marks": 0.7
# }
