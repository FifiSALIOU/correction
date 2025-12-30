# Test Rapide : Migration status -> actif

## Test Backend (1 minute)

### 1. Démarrer le backend
```bash
cd backend
uvicorn app.main:app --reload
```

### 2. Dans un autre terminal, exécuter le test
```bash
cd backend
python test_user_actif_quick.py
```

**Résultat attendu** : Tous les tests passent ✅

## Test Frontend (2 minutes)

### 1. Démarrer le frontend
```bash
cd frontend/ticket-frontend
npm start
```

### 2. Tests rapides
1. Se connecter
2. Aller dans "Utilisateurs" ou "Techniciens"
3. Vérifier que les statuts s'affichent correctement
4. Essayer de créer/modifier un utilisateur
5. Vérifier que la checkbox "Actif" fonctionne

## Vérification Rapide Base de Données

```sql
-- Vérifier que la colonne actif existe
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users' AND column_name = 'actif';

-- Vérifier quelques utilisateurs
SELECT full_name, actif FROM users LIMIT 5;
```

**Résultat attendu** :
- Colonne `actif` existe (type: boolean)
- Tous les utilisateurs ont `actif = true` ou `actif = false`

