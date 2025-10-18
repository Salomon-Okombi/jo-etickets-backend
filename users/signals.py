# users/signals.py
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.utils import timezone
from .models import Utilisateur, HistoriqueConnexion


@receiver(user_logged_in)
def handle_user_logged_in(sender, request, user, **kwargs):
    """
    ✅ Déclenché lorsqu'un utilisateur se connecte avec succès.
    - Met à jour la date de dernière connexion.
    - Enregistre une entrée dans l'historique des connexions.
    """
    user.derniere_connexion = timezone.now()
    user.tentatives_connexion = 0  # reset du compteur d’échecs
    user.save(update_fields=["derniere_connexion", "tentatives_connexion"])

    # Récupère des infos utiles
    ip = request.META.get('REMOTE_ADDR')
    agent = request.META.get('HTTP_USER_AGENT', '')

    HistoriqueConnexion.objects.create(
        utilisateur=user,
        adresse_ip=ip,
        user_agent=agent,
        statut_connexion='SUCCES',
        type_action='CONNEXION'
    )


@receiver(user_logged_out)
def handle_user_logged_out(sender, request, user, **kwargs):
    """
    ✅ Déclenché lors de la déconnexion.
    - Ajoute une entrée dans l’historique.
    """
    if user and isinstance(user, Utilisateur):
        ip = request.META.get('REMOTE_ADDR')
        agent = request.META.get('HTTP_USER_AGENT', '')

        HistoriqueConnexion.objects.create(
            utilisateur=user,
            adresse_ip=ip,
            user_agent=agent,
            statut_connexion='SUCCES',
            type_action='DECONNEXION'
        )


@receiver(user_login_failed)
def handle_user_login_failed(sender, credentials, request, **kwargs):
    """
    ⚠️ Déclenché lorsqu'une tentative de connexion échoue.
    - Incrémente le compteur d’échecs.
    - Enregistre l’échec dans l’historique.
    """
    username = credentials.get('username')

    try:
        user = Utilisateur.objects.get(username=username)
        user.tentatives_connexion += 1
        user.save(update_fields=["tentatives_connexion"])
    except Utilisateur.DoesNotExist:
        user = None  # utilisateur inexistant

    ip = request.META.get('REMOTE_ADDR')
    agent = request.META.get('HTTP_USER_AGENT', '')

    HistoriqueConnexion.objects.create(
        utilisateur=user if user else None,
        adresse_ip=ip,
        user_agent=agent,
        statut_connexion='ECHEC',
        type_action='TENTATIVE'
    )
