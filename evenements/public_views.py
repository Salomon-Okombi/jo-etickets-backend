# evenements/public_views.py
from rest_framework import generics
from rest_framework.permissions import AllowAny

from evenements.models import Evenement
from evenements.serializers_public import PublicEvenementSerializer


class PublicEvenementListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PublicEvenementSerializer

    def get_queryset(self):
        return Evenement.objects.all().order_by("date_evenement")


class PublicEvenementDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = PublicEvenementSerializer
    lookup_field = "pk"

    def get_queryset(self):
        return Evenement.objects.all()