from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Utilisateur

# =========================================================
# PROFIL UTILISATEUR (ME)
# =========================================================

class UtilisateurProfileSerializer(serializers.ModelSerializer):
    photo_profil_url = serializers.SerializerMethodField()

    class Meta:
        model = Utilisateur
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name", 
            "telephone",
            "photo_profil",
            "photo_profil_url",
            "role",
            "est_verifie",
            "date_creation",
        ]
        read_only_fields = [
            "id",
            "username",
            "email",
            "role",
            "est_verifie",
            "date_creation",
        ]

    def get_photo_profil_url(self, obj):
        request = self.context.get("request")
        if obj.photo_profil and request:
            return request.build_absolute_uri(obj.photo_profil.url)
        return None


# =========================================================
# INSCRIPTION PUBLIQUE
# =========================================================

class UtilisateurRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
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
        user.role = "UTILISATEUR"
        user.save()
        return user


# =========================================================
# ADMIN – READ
# =========================================================

class UtilisateurAdminReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "telephone",
            "role",
            "est_verifie",
            "est_bloque",
            "date_creation",
        ]


# =========================================================
# ADMIN – CREATE
# =========================================================

class AdminUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
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
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = Utilisateur(**validated_data)
        user.set_password(password)

        user.is_staff = user.role in ["ADMIN", "ORGANISATEUR"]
        user.is_superuser = user.role == "ADMIN"

        user.save()
        return user


# =========================================================
# ADMIN – UPDATE
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
            "username",
            "email",
            "password",
            "role",
            "est_verifie",
            "est_bloque",
        ]

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.is_staff = instance.role in ["ADMIN", "ORGANISATEUR"]
        instance.is_superuser = instance.role == "ADMIN"

        if password:
            validate_password(password, user=instance)
            instance.set_password(password)

        instance.save()
        return instance
