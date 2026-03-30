from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Utilisateur

# =========================================================
# UTILISATEUR (READ / PROFILE)
# =========================================================

class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = [
            "id",
            "username",
            "email",
            "role",
            "est_verifie",
            "date_creation",
        ]
        read_only_fields = ["id", "date_creation"]


# =========================================================
# INSCRIPTION PUBLIQUE
# =========================================================

class UtilisateurRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )

    class Meta:
        model = Utilisateur
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        user = Utilisateur.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )

        # rôle par défaut
        user.role = "UTILISATEUR"
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
        style={"input_type": "password"},
    )

    class Meta:
        model = Utilisateur
        fields = [
            "id",
            "username",
            "email",
            "password",
            "role",
            "est_verifie",
            "date_creation",
        ]
        read_only_fields = ["id", "date_creation"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = Utilisateur(**validated_data)
        user.set_password(password)

        # mapping rôle → permissions Django
        user.is_staff = user.role in ["ADMIN", "ORGANISATEUR"]
        user.is_superuser = user.role == "ADMIN"

        user.save()
        return user


# =========================================================
# ADMIN CRUD – UPDATE
# =========================================================

class AdminUserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = Utilisateur
        fields = [
            "id",
            "username",
            "email",
            "password",
            "role",
            "est_verifie",
            "est_bloque",
        ]
        read_only_fields = ["id"]

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # mapping rôle → permissions Django
        instance.is_staff = instance.role in ["ADMIN", "ORGANISATEUR"]
        instance.is_superuser = instance.role == "ADMIN"

        if password:
            validate_password(password, user=instance)
            instance.set_password(password)

        instance.save()
        return instance