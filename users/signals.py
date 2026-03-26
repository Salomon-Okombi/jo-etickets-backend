# users/signals.py
from django.dispatch import receiver
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.utils import timezone
from .models import Utilisateur, HistoriqueConnexion


@receiver(user_logged_in)
def handle_user_logged_in(sender, request, user, **kwargs):
    """
    Connexion réussie :
    - met à jour last_login
    - reset le compteur de tentatives
    - enregistre l'historique
    """
    user.last_login = timezone.now()
    user.tentatives_connexion = 0
    user.save(update_fields=["last_login", "tentatives_connexion"])

    ip = request.META.get("REMOTE_ADDR")
    agent = request.META.get("HTTP_USER_AGENT", "")

    HistoriqueConnexion.objects.create(
        utilisateur=user,
        adresse_ip=ip,
        user_agent=agent,
        statut_connexion="SUCCES",
        type_action="CONNEXION",
    )


@receiver(user_logged_out)
def handle_user_logged_out(sender, request, user, **kwargs):
    """
    Déconnexion
    """
    if not user or not isinstance(user, Utilisateur):
        return

    ip = request.META.get("REMOTE_ADDR")
    agent = request.META.get("HTTP_USER_AGENT", "")

    HistoriqueConnexion.objects.create(
        utilisateur=user,
        adresse_ip=ip,
        user_agent=agent,
        statut_connexion="SUCCES",
        type_action="DECONNEXION",
    )


@receiver(user_login_failed)
def handle_user_login_failed(sender, credentials, request, **kwargs):
    """
    Tentative échouée
    """
    username = credentials.get("username")
    user = None

    try:
        user = Utilisateur.objects.get(username=username)
        user.tentatives_connexion += 1
        user.save(update_fields=["tentatives_connexion"])
    except Utilisateur.DoesNotExist:
        pass

    ip = request.META.get("REMOTE_ADDR")
    agent = request.META.get("HTTP_USER_AGENT", "")

    HistoriqueConnexion.objects.create(
        utilisateur=user,
        adresse_ip=ip,
        user_agent=agent,
        statut_connexion="ECHEC",
        type_action="TENTATIVE",
    )