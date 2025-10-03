from rest_framework import serializers
from .models import Utilisateur
from django.contrib.auth.password_validation import validate_password

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
        style={'input_type': 'password'}
    )

    class Meta:
        model = Utilisateur
        fields = ["username", "email", "password", "type_compte"]

    def create(self, validated_data):
        # Création sécurisée de l'utilisateur
        user = Utilisateur(
            username=validated_data['username'],
            email=validated_data['email'],
            type_compte=validated_data.get('type_compte', 'CLIENT')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
