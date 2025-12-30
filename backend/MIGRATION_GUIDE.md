# Guide de Migration : type_code → ticket_type_id

Ce guide explique comment migrer la table `ticket_categories` de `type_code` (String) vers `ticket_type_id` (ForeignKey).

## Étapes de migration

### Étape 1 : Ajouter la nouvelle colonne

Exécutez le script pour ajouter la colonne `ticket_type_id` :

```bash
python add_ticket_type_id_column.py add
```

Ou simplement :
```bash
python add_ticket_type_id_column.py
```

Cette commande :
- Ajoute la colonne `ticket_type_id` (nullable d'abord)
- Ajoute la contrainte de clé étrangère vers `ticket_types`

### Étape 2 : Migrer les données existantes

Si vous avez des catégories existantes avec `type_code`, exécutez :

```bash
python migrate_ticket_categories.py
```

Ce script :
- Convertit tous les `type_code` existants en `ticket_type_id`
- Mappe "materiel" → ID du type matériel
- Mappe "applicatif" → ID du type applicatif

### Étape 3 : Rendre la colonne NOT NULL

Une fois toutes les données migrées, rendez la colonne obligatoire :

```bash
python add_ticket_type_id_column.py not-null
```

### Étape 4 : Supprimer l'ancienne colonne (optionnel)

Après avoir vérifié que tout fonctionne, supprimez l'ancienne colonne :

```bash
python add_ticket_type_id_column.py drop
```

## Ordre d'exécution complet

```bash
# 1. Ajouter la colonne
python add_ticket_type_id_column.py add

# 2. Migrer les données (si vous avez des données existantes)
python migrate_ticket_categories.py

# 3. Rendre NOT NULL
python add_ticket_type_id_column.py not-null

# 4. Supprimer l'ancienne colonne (après vérification)
python add_ticket_type_id_column.py drop
```

## Si vous partez d'une base vide

Si vous initialisez une nouvelle base de données, exécutez simplement :

```bash
python init_db.py
```

Le script `init_db.py` a été modifié pour utiliser directement `ticket_type_id`, donc aucune migration n'est nécessaire.

## Vérification

Pour vérifier que la migration a réussi :

```python
from app.database import SessionLocal
from app import models

db = SessionLocal()
categories = db.query(models.TicketCategory).all()
for cat in categories:
    print(f"{cat.name}: ticket_type_id={cat.ticket_type_id}, type_code={cat.ticket_type.code if cat.ticket_type else 'N/A'}")
```

