# Guide de Test : Migration status -> actif

Ce guide explique comment tester que la migration de `status` vers `actif` fonctionne correctement côté backend et frontend.

## Prérequis

1. **Backend démarré** : Le serveur FastAPI doit être en cours d'exécution
2. **Base de données migrée** : Les scripts de migration doivent avoir été exécutés
3. **Frontend démarré** (optionnel) : Pour tester l'interface utilisateur

## 1. Tests Backend (API)

### Démarrer le backend

```bash
cd backend
# Activer l'environnement virtuel si nécessaire
# source venv/bin/activate  # Sur Linux/Mac
# .\venv\Scripts\Activate.ps1  # Sur Windows PowerShell

# Démarrer le serveur
uvicorn app.main:app --reload
```

Le serveur devrait être accessible sur `http://localhost:8000`

### Exécuter les tests automatiques

```bash
# Dans un autre terminal
cd backend
python test_user_actif_quick.py
```

**Ou avec des credentials personnalisés :**
```bash
# Windows PowerShell
$env:TEST_USERNAME="votre_username"; $env:TEST_PASSWORD="votre_password"; python test_user_actif_quick.py

# Linux/Mac
TEST_USERNAME="votre_username" TEST_PASSWORD="votre_password" python test_user_actif_quick.py
```

### Tests manuels avec Swagger UI

1. Ouvrir `http://localhost:8000/docs` dans votre navigateur
2. Se connecter avec un compte admin/DSI
3. Tester les endpoints suivants :

#### Test 1 : Liste des utilisateurs
- **Endpoint** : `GET /users/`
- **Vérifications** :
  - ✅ Tous les utilisateurs ont le champ `actif` (Boolean)
  - ✅ Aucun utilisateur n'a l'ancien champ `status`
  - ✅ Les valeurs de `actif` sont `true` ou `false`

#### Test 2 : Liste des techniciens
- **Endpoint** : `GET /users/technicians`
- **Vérifications** :
  - ✅ Tous les techniciens ont le champ `actif` (Boolean)
  - ✅ Seuls les techniciens actifs sont retournés (filtre automatique)

#### Test 3 : Récupérer un utilisateur
- **Endpoint** : `GET /users/{user_id}`
- **Vérifications** :
  - ✅ Le champ `actif` est présent et de type Boolean
  - ✅ Pas de champ `status`

#### Test 4 : Mettre à jour un utilisateur
- **Endpoint** : `PUT /users/{user_id}`
- **Body** :
  ```json
  {
    "actif": false
  }
  ```
- **Vérifications** :
  - ✅ La mise à jour fonctionne
  - ✅ La réponse contient `actif: false`

### Tests avec curl

```bash
# 1. Se connecter et obtenir un token
TOKEN=$(curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin" | jq -r '.access_token')

# 2. Récupérer la liste des utilisateurs
curl -X GET "http://localhost:8000/users/" \
  -H "Authorization: Bearer $TOKEN" | jq '.[0] | {full_name, actif}'

# 3. Récupérer la liste des techniciens
curl -X GET "http://localhost:8000/users/technicians" \
  -H "Authorization: Bearer $TOKEN" | jq '.[0] | {full_name, actif, availability_status}'

# 4. Récupérer un utilisateur par ID
USER_ID=$(curl -X GET "http://localhost:8000/users/" \
  -H "Authorization: Bearer $TOKEN" | jq -r '.[0].id')

curl -X GET "http://localhost:8000/users/$USER_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '{full_name, actif}'
```

## 2. Tests Frontend

### Démarrer le frontend

```bash
cd frontend/ticket-frontend
npm install  # Si nécessaire
npm start
```

Le frontend devrait être accessible sur `http://localhost:3000`

### Tests à effectuer

#### Test 1 : Connexion
1. Se connecter avec un compte utilisateur
2. ✅ La connexion fonctionne normalement

#### Test 2 : Dashboard DSI (si vous êtes DSI)
1. Aller dans la section "Utilisateurs" ou "Techniciens"
2. ✅ Les utilisateurs/techniciens s'affichent correctement
3. ✅ Le statut "Actif/Inactif" s'affiche correctement
4. ✅ Les filtres par statut fonctionnent

#### Test 3 : Création d'utilisateur
1. Cliquer sur "Créer un utilisateur"
2. ✅ Le formulaire contient une checkbox "Actif" (pas de radio buttons)
3. ✅ Créer un utilisateur avec `actif = true`
4. ✅ Vérifier que l'utilisateur apparaît dans la liste avec `actif: true`

#### Test 4 : Modification d'utilisateur
1. Cliquer sur "Modifier" pour un utilisateur existant
2. ✅ Le formulaire affiche une checkbox "Actif" (pas de radio buttons)
3. ✅ Modifier le statut (actif/inactif)
4. ✅ Sauvegarder et vérifier que le changement est pris en compte

#### Test 5 : Liste des techniciens
1. Aller dans la section "Techniciens"
2. ✅ Les techniciens s'affichent avec leur statut `actif`
3. ✅ Les détails d'un technicien affichent correctement "Actif" ou "Inactif"

#### Test 6 : Filtres
1. Utiliser le filtre "Statut" dans la liste des utilisateurs
2. ✅ Le filtre "Actif" ne montre que les utilisateurs avec `actif: true`
3. ✅ Le filtre "Inactif" ne montre que les utilisateurs avec `actif: false`

### Vérifications dans la console du navigateur

Ouvrir la console développeur (F12) et vérifier :

1. **Requêtes API** :
   - ✅ Les réponses JSON contiennent `actif` (Boolean)
   - ✅ Aucune réponse ne contient l'ancien champ `status`

2. **Erreurs** :
   - ✅ Aucune erreur liée à `status` ou `actif`

## 3. Vérifications Base de Données

### Vérifier la structure de la table

```sql
-- Se connecter à PostgreSQL
psql -U tickets_user -d tickets_db

-- Vérifier les colonnes
\d users

-- Vérifier que la colonne actif existe
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'users' AND column_name IN ('status', 'actif');

-- Vérifier les données
SELECT id, full_name, actif FROM users LIMIT 5;

-- Vérifier qu'il n'y a pas de valeurs NULL
SELECT COUNT(*) FROM users WHERE actif IS NULL;
```

### Résultats attendus

- ✅ La colonne `actif` existe (type: boolean)
- ✅ La colonne `status` n'existe plus (ou existe encore temporairement)
- ✅ Tous les utilisateurs ont une valeur `actif` (true ou false)
- ✅ Aucun utilisateur n'a `actif IS NULL`

## 4. Checklist Complète

### Backend
- [ ] Le serveur démarre sans erreur
- [ ] Les endpoints `/users/` retournent `actif` (Boolean)
- [ ] Les endpoints `/users/technicians` retournent `actif` (Boolean)
- [ ] Les filtres de techniciens actifs fonctionnent
- [ ] La mise à jour de `actif` fonctionne
- [ ] L'authentification fonctionne (vérifie `actif`)

### Frontend
- [ ] La connexion fonctionne
- [ ] Les listes d'utilisateurs/techniciens s'affichent
- [ ] Les formulaires utilisent des checkboxes pour `actif`
- [ ] Les filtres par statut fonctionnent
- [ ] La création d'utilisateur fonctionne avec `actif`
- [ ] La modification d'utilisateur fonctionne avec `actif`
- [ ] Aucune erreur dans la console

### Base de Données
- [ ] La colonne `actif` existe (Boolean, NOT NULL)
- [ ] Tous les utilisateurs ont une valeur `actif`
- [ ] Les valeurs sont cohérentes (anciens "actif"/"active" → true)

## 5. Problèmes Courants

### Problème : "Champ 'actif' manquant"
**Solution** : Vérifiez que les scripts de migration ont été exécutés :
```bash
python add_user_actif_column.py add
python migrate_user_status_to_actif.py
```

### Problème : "Ancien champ 'status' encore présent"
**Solution** : C'est normal si vous n'avez pas encore supprimé l'ancienne colonne. Vous pouvez la supprimer après vérification :
```bash
python add_user_actif_column.py drop
```

### Problème : "TypeError: actif is not a boolean"
**Solution** : Vérifiez que le modèle SQLAlchemy a été mis à jour et redémarrez le serveur.

### Problème : Frontend affiche "undefined"
**Solution** : Vérifiez que l'API retourne bien `actif` et que le frontend utilise `user.actif` au lieu de `user.status`.

## 6. Support

Si vous rencontrez des problèmes :
1. Vérifiez les logs du backend
2. Vérifiez la console du navigateur (F12)
3. Vérifiez l'état de la base de données
4. Assurez-vous que tous les fichiers ont été modifiés correctement

