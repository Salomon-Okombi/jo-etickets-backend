from django.contrib import admin
from .models import EBillet
from django.utils.html import format_html


@admin.register(EBillet)
class EBilletAdmin(admin.ModelAdmin):
    list_display = (
        "numero_billet",
        "utilisateur",
        "offre",
        "statut",
        "prix_paye",
        "date_achat",
        "date_utilisation",
        "afficher_qr_code",
    )
    list_filter = ("statut", "date_achat", "date_utilisation")
    search_fields = (
        "numero_billet",
        "utilisateur__username",
        "utilisateur__email",
        "offre__nom_offre",
    )
    ordering = ("-date_achat",)
    readonly_fields = (
        "numero_billet",
        "cle_achat",
        "cle_finale",
        "qr_code_image",
        "date_achat",
    )
    fieldsets = (
        ("Infos Billet", {
            "fields": ("numero_billet", "utilisateur", "offre", "prix_paye", "statut")
        }),
        ("Validation", {
            "fields": ("id_validateur", "date_utilisation", "lieu_utilisation")
        }),
        ("Sécurité", {
            "fields": ("cle_achat", "cle_finale", "qr_code_image")
        }),
    )

    def afficher_qr_code(self, obj):
        """Affichage mini QR code dans list_display"""
        if obj.qr_code:
            return format_html('<img src="data:image/png;base64,{}" width="50" height="50" />', obj.qr_code)
        return "—"
    afficher_qr_code.short_description = "QR Code"

    def qr_code_image(self, obj):
        """Affichage grand QR code dans le détail"""
        if obj.qr_code:
            return format_html('<img src="data:image/png;base64,{}" width="200" height="200" />', obj.qr_code)
        return "Pas de QR code"
    qr_code_image.short_description = "QR Code"
