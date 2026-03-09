from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Utilisateur


class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = ["id", "username", "email", "type_compte", "statut", "date_creation"]
        read_only_fields = ["id", "date_creation"]


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

        # ✅ si tu veux que type_compte=ADMIN soit un vrai admin Django
        if user.type_compte == "ADMIN":
            user.is_staff = True

        user.save()
        return user


# =========================
# ✅ SERIALIZERS ADMIN CRUD
# =========================

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

        # ✅ map type_compte -> is_staff
        if user.type_compte == "ADMIN":
            user.is_staff = True
        else:
            user.is_staff = False

        user.save()
        return user


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """
    Update admin : on autorise la modification de username/email/type_compte/statut
    + changement mdp optionnel via champ password.
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

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # ✅ map type_compte -> is_staff
        if getattr(instance, "type_compte", None) == "ADMIN":
            instance.is_staff = True
        else:
            instance.is_staff = False

        if password:
            validate_password(password, user=instance)
            instance.set_password(password)

        instance.save()
        return instance