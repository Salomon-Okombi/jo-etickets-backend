from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("offres", "0001_initial"),
        # adapte si ton dernier fichier n'est pas 0001_initial
    ]

    operations = [
        migrations.CreateModel(
            name="CategorieOffre",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=50, unique=True)),
                ("nom", models.CharField(max_length=120)),
                ("description", models.TextField(blank=True, null=True)),
                ("nb_personnes", models.PositiveIntegerField(default=1)),
                ("cas_usage", models.TextField(blank=True, null=True)),
                ("ordre_affichage", models.PositiveIntegerField(default=0)),
                ("active", models.BooleanField(default=True)),
                ("date_creation", models.DateTimeField(auto_now_add=True)),
                ("date_modification", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "categorie_offre",
                "ordering": ["ordre_affichage", "nom"],
            },
        ),
        migrations.AddField(
            model_name="offre",
            name="categorie",
            field=models.ForeignKey(
                to="offres.categorieoffre",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="offres",
                null=True,
            ),
        ),
    ]