from django.db import models

class StatistiquesVente(models.Model):
    offre = models.OneToOneField('offres.Offre', on_delete=models.CASCADE, related_name='statistiques')
    nombre_ventes = models.IntegerField(default=0)
    chiffre_affaires = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    date_derniere_maj = models.DateTimeField(auto_now=True)
    moyenne_ventes_jour = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    pic_ventes_heure = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'statistiques_vente'

    def __str__(self):
        return f"Stats Offre {self.offre_id} - ventes:{self.nombre_ventes}"
