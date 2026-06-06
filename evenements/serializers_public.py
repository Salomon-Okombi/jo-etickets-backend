# Last edited by you@example.com @ 05/06/26 19:27.
#analytics/serializers_public.py
from rest_framework import serializers
from .models import Evenement


def build_image_url(request, obj) -> str | None:
    """
    Retourne l'URL de l'image :
    - absolue si request est disponible
    - relative sinon
    - None si pas d'image
    """
    if not getattr(obj, "image", None):
        return None

    # obj.image.url existe quand une image est réellement stockée
    try:
        url = obj.image.url
    except Exception:
        return None

    if request:
        return request.build_absolute_uri(url)

    return url


# ============================================================
# LISTE PUBLIQUE DES ÉVÉNEMENTS (CARDS / LISTING)
# ============================================================

class EvenementListSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Evenement
        fields = [
            "id",
            "nom_evenement",
            "discipline",
            "lieu",
            "date_debut",
            "date_fin",
            "description_courte",
            "image_url",
            "prix_base",
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")
        return build_image_url(request, obj)


# ============================================================
# DÉTAIL PUBLIC D’UN ÉVÉNEMENT
# ============================================================

class EvenementDetailSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Evenement
        fields = [
            "id",
            "nom_evenement",
            "discipline",
            "lieu",
            "date_debut",
            "date_fin",
            "description_longue",
            "image_url",
            "prix_base",
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")
        return build_image_url(request, obj)