# 🎟️ JO e-Tickets - Backend

Backend de l'application de réservation de e-tickets pour les Jeux Olympiques 2024 en France.  
Ce service expose une API REST sécurisée pour gérer les utilisateurs, les offres, les paniers, les achats et la validation des billets (QR Code).

---

## 🚀 Stack technique
- Python 3.11
- Django 5 + Django REST Framework
- MySQL (base relationnelle obligatoire)
- JWT Authentication
- Swagger (drf-yasg)
- Déploiement : Fly.io / Heroku

---

## ⚙️ Installation locale

### 1. Cloner le projet
```bash
git clone https://github.com/TON_USERNAME/jo-etickets-backend.git
cd jo-etickets-backend

## ⚙️ To run venv  use venv\Scripts\activate 
## ⚙️ To start the project : python manage.py runserver  

📄 Documentation du bug Django / MySQL et sa résolution
1. Contexte du problème

Tu travaillais sur un projet Django (JO-etickets) utilisant MySQL comme base de données.

Lors de l’exécution des migrations avec :

python manage.py migrate


tu as rencontré une erreur sur django_admin_log :

django.db.utils.OperationalError: (1005, "Can't create table `jo_etickets`.`django_admin_log` (errno: 150 'Foreign key constraint is incorrectly formed')")


Et, plus tôt, tu avais des erreurs de type :

NodeNotFoundError: Migration offres.0001_initial dependencies reference nonexistent parent node ('evenements', '0001_initial')

2. Analyse du problème

Tables existantes

Django essaie de créer une table (django_admin_log) qui existe déjà dans la base MySQL.

Cela peut arriver si :

Tu as réinitialisé la base après des migrations partielles.

Tu as changé le db_table d’un modèle et tenté de recréer la table.

Clés étrangères incorrectes

MySQL retourne errno: 150 lorsqu’une foreign key est mal formée.

Causes courantes :

Types de champs différents entre la table parent et enfant (ex. INT vs BIGINT).

Table parent inexistante ou table déjà supprimée.

Ordre des migrations incorrect : une table enfant est migrée avant sa table parent.

Migrations Django désynchronisées

Les migrations sont appliquées dans l’ordre, mais si une table existe déjà dans MySQL et que Django n’a pas de trace de migration, cela bloque tout.

C’est ce que tu as rencontré : Django essayait de recréer django_admin_log alors qu’elle existait déjà.

3. Méthode de résolution utilisée

Forcer Django à marquer les migrations comme appliquées

Commande utilisée :

python manage.py migrate admin --fake


⚡ Explication :

--fake → Django enregistre la migration comme appliquée dans sa table django_migrations sans toucher à la base.

Utile lorsque les tables existent déjà et que tu veux synchroniser l’état des migrations avec MySQL.

Appliquer ensuite les migrations restantes normalement

python manage.py migrate


Les autres apps (auth, contenttypes, evenements, offres, etc.) vont se migrer correctement car Django considère admin comme déjà appliqué.

4. Bonnes pratiques pour le futur

Toujours garder les migrations synchronisées

Si tu supprimes ou modifies des tables à la main dans MySQL, pense à utiliser --fake ou à recréer les migrations pour éviter les conflits.

Ne pas recréer les tables Django existantes

Si une table Django existe déjà et que tu veux repartir sur de nouvelles migrations :

Soit tu supprimes la table et recommences makemigrations/migrate.

Soit tu utilises --fake pour “mentir” à Django.

Ordre des migrations

Les dépendances (dependencies) doivent être correctes.

Toujours créer les migrations pour les apps parent avant les apps enfants.

Vérifie les dependencies dans les fichiers 0001_initial.py et supprime tout référence à une migration inexistante.

Gestion des foreign keys

Vérifie que les types de champs entre table parent et enfant correspondent.

Exemple : id du parent est INT AUTO_INCREMENT, la FK doit aussi être INT.

Backup

Avant de jouer avec --fake ou de supprimer des tables, fais toujours un backup MySQL pour éviter toute perte de données.

5. Résumé rapide
Problème	Cause	Solution
Can't create table django_admin_log	Table existe déjà ou FK mal formée	python manage.py migrate admin --fake
NodeNotFoundError	Migration enfant dépend d’une migration parent inexistante	Créer la migration parent (makemigrations evenements) avant
Foreign key incorrectly formed	Type de champ FK ne correspond pas au parent	Vérifier types et ordres de migration


## Open mysql : & "C:\Program Files\MariaDB 12.1\bin\mysql.exe" -u root -p