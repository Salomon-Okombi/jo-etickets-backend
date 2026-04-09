from rest_framework import serializers
from django.conf import settings
from .models import Evenement


class EvenementListSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Evenement
        fields = [
            "id",
            "nom_evenement",
            "discipline",
            "date_evenement",
            "lieu",
            "description_courte",
            "image_url",
        ]

    def get_image_url(self, obj):
        if not obj.image:
            return None
        return f"{settings.MEDIA_URL}{obj.image.name}"


class EvenementDetailSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Evenement
        fields = [
            "id",
            "nom_evenement",
            "discipline",
            "date_evenement",
            "lieu",
            "description_longue",
            "image_url",
        ]

    def get_image_url(self, obj):
        if not obj.image:
            return None
        return f"{settings.MEDIA_URL}{obj.image.name}"