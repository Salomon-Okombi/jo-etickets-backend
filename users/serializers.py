from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Utilisateur


# =========================================================
# UTILISATEUR (READ / PROFILE)
# =========================================================

class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = ["id", "username", "email", "type_compte", "statut", "date_creation"]
        read_only_fields = ["id", "date_creation"]


# =========================================================
# INSCRIPTION PUBLIQUE
# =========================================================

class UtilisateurRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"}
    )

    class Meta:
        model = Utilisateur
        fields = ["username", "email", "password", "type_compte"]

    def create(self, validated_data):
        user = Utilisateur(
            username=validated_data["username"],
            email=validated_data["email"],
            type_compte=validated_data.get("type_compte", "CLIENT"),
        )
        user.set_password(validated_data["password"])

        # si type_compte = ADMIN → accès admin Django
        if user.type_compte == "ADMIN":
            user.is_staff = True

        user.save()
        return user


# =========================================================
# ADMIN CRUD – CREATE
# =========================================================

class AdminUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"}
    )

    class Meta:
        model = Utilisateur
        fields = ["id", "username", "email", "password", "type_compte", "statut", "date_creation"]
        read_only_fields = ["id", "date_creation"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = Utilisateur(**validated_data)
        user.set_password(password)

        # map type_compte → is_staff
        user.is_staff = (user.type_compte == "ADMIN")

        user.save()
        return user


# =========================================================
# ADMIN CRUD – UPDATE
# =========================================================

class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """
    Admin : mise à jour des infos utilisateur
    + changement de mot de passe optionnel.
    """
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        style={"input_type": "password"}
    )

    class Meta:
        model = Utilisateur
        fields = ["id", "username", "email", "password", "type_compte", "statut", "date_creation"]
        read_only_fields = ["id", "date_creation"]

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        # Mise à jour des champs simples
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # map type_compte → is_staff
        instance.is_staff = (instance.type_compte == "ADMIN")

        # Mise à jour du mot de passe
        if password:
            validate_password(password, user=instance)
            instance.set_password(password)

        instance.save()
        return instance