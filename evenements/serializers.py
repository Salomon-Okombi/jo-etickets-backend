# evenements/serializers.py
from rest_framework import serializers
from .models import Evenement

class EvenementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evenement
        fields = "__all__"
        read_only_fields = ["date_creation"]
