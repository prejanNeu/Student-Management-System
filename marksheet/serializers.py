from rest_framework import serializers 
from .models import Marksheet, ExamType



class ExamTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExamType
        fields = '__all__'

class MarksheetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Marksheet
        field = '__all__'


