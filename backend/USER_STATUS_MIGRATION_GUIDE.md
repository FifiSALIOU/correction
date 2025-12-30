# Guide de Migration : status -> actif (Boolean)

Ce guide explique comment migrer la colonne `status` (String) vers `actif` (Boolean) dans la table `users`.

## Étapes de migration

### 1. Ajouter la colonne `actif`

Exécutez le script pour ajouter la nouvelle colonne :

```bash
cd backend
python add_user_actif_column.py add
```

Cette commande :
- Ajoute la colonne `actif` (BOOLEAN) avec une valeur par défaut `true`
- La colonne est nullable temporairement pour permettre la migration des données

### 2. Migrer les données

Exécutez le script de migration des données :

```bash
python migrate_user_status_to_actif.py
```

Cette commande :
- Convertit les valeurs `status` existantes en valeurs `actif` :
  - `"actif"` ou `"active"` → `true`
  - Toute autre valeur → `false`
- Rend la colonne `actif` NOT NULL après migration

### 3. Supprimer l'ancienne colonne (optionnel)

Une fois que vous avez vérifié que tout fonctionne correctement, vous pouvez supprimer l'ancienne colonne :

```bash
python add_user_actif_column.py drop
```

## Vérification

Après la migration, vérifiez que :

1. Tous les utilisateurs ont une valeur `actif` (true ou false)
2. Les utilisateurs précédemment "actif" ou "active" ont maintenant `actif = true`
3. Les autres utilisateurs ont `actif = false`
4. L'API fonctionne correctement avec le nouveau champ `actif`

## Notes importantes

- **Sauvegarde** : Faites une sauvegarde de votre base de données avant d'exécuter la migration
- **Test** : Testez l'application après chaque étape pour vous assurer que tout fonctionne
- **Rollback** : Si vous devez annuler, vous pouvez restaurer la sauvegarde et réexécuter les migrations SQLAlchemy

## Changements dans le code

### Backend
- `models.py` : `status = Column(String(20))` → `actif = Column(Boolean, default=True)`
- `schemas.py` : `status: Optional[str]` → `actif: Optional[bool]`
- Tous les filtres `User.status == "actif"` → `User.actif == True`
- `security.py` : Vérification `user.status.lower() not in ["actif", "active"]` → `not user.actif`

### Frontend
- Interface `Technician` : `status?: string` → `actif?: boolean`
- Les formulaires utilisent maintenant des checkboxes au lieu de radio buttons
- Les filtres utilisent `user.actif === true` au lieu de `user.status === "actif"`

## Support

Si vous rencontrez des problèmes lors de la migration, vérifiez :
1. Les logs d'erreur dans la console
2. L'état de la base de données (colonnes existantes)
3. Que tous les scripts ont été exécutés dans l'ordre

