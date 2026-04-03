fieldsets = UserAdmin.fieldsets + (
    ("Informations supplémentaires", {
        "fields": (
            "role",
            "telephone",
            "photo_profil",
            "est_verifie",
            "est_bloque",
            "tentatives_connexion",
            "derniere_connexion_ip",
        )
    }),
    ("Droits d'administration", {
        "fields": (
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )
    }),
)