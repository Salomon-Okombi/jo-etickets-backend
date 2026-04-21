from django.db import migrations


def forwards(apps, schema_editor):
    CategorieOffre = apps.get_model("offres", "CategorieOffre")
    Offre = apps.get_model("offres", "Offre")

    defaults = [
        ("SOLO", "Solo", 1, 1),
        ("DUO", "Duo", 2, 2),
        ("FAMILIALE", "Familiale", 4, 3),
    ]

    code_to_cat = {}
    for code, nom, nb, ordre in defaults:
        cat, _ = CategorieOffre.objects.get_or_create(
            code=code,
            defaults={
                "nom": nom,
                "nb_personnes": nb,
                "ordre_affichage": ordre,
                "active": True,
                "description": f"Offre {nom.lower()}",
                "cas_usage": "",
            },
        )
        code_to_cat[code] = cat

    # Si ton ancienne Offre avait type_offre en base, on mappe dessus.
    # Sinon, on met SOLO par défaut.
    for offre in Offre.objects.all():
        # Tente de lire type_offre si le champ existe encore dans ta DB
        code = getattr(offre, "type_offre", None) or "SOLO"
        cat = code_to_cat.get(code, code_to_cat["SOLO"])
        offre.categorie_id = cat.id
        offre.save(update_fields=["categorie"])


def backwards(apps, schema_editor):
    # Pas de rollback propre ici (optionnel)
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("offres", "000X_categorieoffre_and_fk"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
        # Ensuite, on rend la FK obligatoire via une migration Django auto
        # Tu peux faire : python manage.py makemigrations offres
    ]