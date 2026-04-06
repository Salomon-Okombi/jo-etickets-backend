# evenements/serializers.py
from rest_framework import serializers
from .models import Evenement


class EvenementListSerializer(serializers.ModelSerializer):
    """
    Serializer PUBLIC — liste (boutique)
    """
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
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class EvenementDetailSerializer(serializers.ModelSerializer):
    """
    Serializer PUBLIC — détail
    """
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
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class EvenementAdminSerializer(serializers.ModelSerializer):
    """
    Serializer ADMIN — création / édition (avec upload image)
    """
    class Meta:
        model = Evenement
        fields = [
            "id",
            "nom_evenement",
            "discipline",
            "date_evenement",
            "lieu",
            "description_courte",
            "description_longue",
            "image",
            "statut",
        ]