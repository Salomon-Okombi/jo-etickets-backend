from django.contrib import admin
from .models import Evenement

@admin.register(Evenement)
class EvenementAdmin(admin.ModelAdmin):
    list_display = ('nom', 'discipline_sportive', 'date_evenement', 'lieu_evenement', 'statut', 'date_creation')
    list_filter = ('statut', 'discipline_sportive', 'date_evenement')
    search_fields = ('nom', 'discipline_sportive', 'lieu_evenement')
    ordering = ('date_evenement',)
    date_hierarchy = 'date_evenement'
