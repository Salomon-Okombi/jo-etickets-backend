from django.contrib import admin
from .models import Evenement

'''
@admin.register(Evenement)
class EvenementAdmin(admin.ModelAdmin):
    list_display = ("nom", "discipline", "date_evenement", "lieu", "statut")
    list_filter = ("discipline", "statut")
    search_fields = ("nom", "discipline", "lieu")
'''