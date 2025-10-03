from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Users / Auth
    path('api/utilisateurs/', include('users.urls')),

    # Événements
    path('api/evenements/', include('evenements.urls')),

    # Offres
    path('api/offres/', include('offres.urls')),

    # Paniers
    path('api/paniers/', include('paniers.urls')),

    # Commandes (app correcte : paiements)
    path('api/commandes/', include('paiements.urls')),

    # E-billets
    path('api/billets/', include('billets.urls')),

    # Statistiques
    path('api/statistiques/', include('analytics.urls')),
]
