from django.db import models

class Evenement(models.Model):
    STATUTS = [
        ('A_VENIR', 'À venir'),
        ('EN_COURS', 'En cours'),
        ('TERMINE', 'Terminé'),
    ]

    nom = models.CharField(max_length=200)
    discipline_sportive = models.CharField(max_length=100)
    date_evenement = models.DateField()
    lieu_evenement = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='A_VENIR')
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'evenement'
        ordering = ['date_evenement']

    def __str__(self):
        return f"{self.nom} - {self.date_evenement}"
