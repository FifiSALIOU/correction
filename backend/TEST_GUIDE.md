# Guide de Test - Migration type_code → ticket_type_id

## ✅ Tests Automatiques

Les tests automatiques ont été exécutés avec succès. Pour les relancer :

```bash
python test_migration.py
```

## 🧪 Tests Manuels

### 1. Test de l'API Backend

#### Test 1.1 : Récupérer toutes les catégories

**URL :** `GET http://localhost:8000/ticket-config/categories`

**Headers :**
```
Authorization: Bearer VOTRE_TOKEN
```

**Résultat attendu :**
- Toutes les catégories doivent être retournées
- Chaque catégorie doit avoir un champ `type_code` (materiel ou applicatif)
- Les catégories doivent avoir un `id`, `name`, `description`, `is_active`

**Exemple de réponse :**
```json
[
  {
    "id": "uuid-here",
    "name": "Ordinateur portable",
    "description": null,
    "type_code": "materiel",
    "is_active": true
  },
  {
    "id": "uuid-here",
    "name": "Système d'exploitation",
    "description": null,
    "type_code": "applicatif",
    "is_active": true
  }
]
```

#### Test 1.2 : Filtrer par type_code

**URL :** `GET http://localhost:8000/ticket-config/categories?type_code=materiel`

**Résultat attendu :**
- Seules les catégories de type "materiel" doivent être retournées
- Devrait retourner 10 catégories

**URL :** `GET http://localhost:8000/ticket-config/categories?type_code=applicatif`

**Résultat attendu :**
- Seules les catégories de type "applicatif" doivent être retournées
- Devrait retourner 10 catégories

#### Test 1.3 : Vérifier les types de tickets

**URL :** `GET http://localhost:8000/ticket-config/types`

**Résultat attendu :**
- Doit retourner les types "materiel" et "applicatif"
- Chaque type doit avoir `id`, `code`, `label`, `is_active`

### 2. Test du Frontend

#### Test 2.1 : Créer un nouveau ticket

1. Connectez-vous au frontend
2. Cliquez sur "Nouveau ticket"
3. Sélectionnez le type "Matériel"
4. **Vérifiez :** La liste déroulante des catégories doit afficher uniquement les catégories matériel (Ordinateur portable, Imprimante, Scanner, etc.)
5. Sélectionnez le type "Applicatif"
6. **Vérifiez :** La liste déroulante des catégories doit afficher uniquement les catégories applicatif (Système d'exploitation, Logiciel bureautique, etc.)

#### Test 2.2 : Modifier un ticket existant

1. Ouvrez un ticket existant
2. Modifiez le type
3. **Vérifiez :** Les catégories disponibles changent selon le type sélectionné

### 3. Test de la Base de Données

#### Test 3.1 : Vérifier directement dans PostgreSQL

Connectez-vous à votre base de données PostgreSQL et exécutez :

```sql
-- Vérifier que toutes les catégories ont un ticket_type_id
SELECT 
    tc.name,
    tc.ticket_type_id,
    tt.code as type_code,
    tt.label as type_label
FROM ticket_categories tc
JOIN ticket_types tt ON tc.ticket_type_id = tt.id
ORDER BY tt.code, tc.name;
```

**Résultat attendu :**
- Toutes les catégories doivent avoir un `ticket_type_id` non NULL
- Le `type_code` doit correspondre (materiel ou applicatif)

#### Test 3.2 : Vérifier qu'il n'y a pas de valeurs NULL

```sql
SELECT COUNT(*) 
FROM ticket_categories 
WHERE ticket_type_id IS NULL;
```

**Résultat attendu :** `0`

#### Test 3.3 : Vérifier la contrainte de clé étrangère

```sql
-- Cette requête doit échouer si la contrainte fonctionne
INSERT INTO ticket_categories (name, ticket_type_id, is_active)
VALUES ('Test', '00000000-0000-0000-0000-000000000000', true);
```

**Résultat attendu :** Erreur de violation de contrainte de clé étrangère

## ✅ Checklist de Validation

- [ ] Tests automatiques passent (`python test_migration.py`)
- [ ] API retourne toutes les catégories avec `type_code`
- [ ] API filtre correctement par `type_code`
- [ ] Frontend affiche les catégories selon le type sélectionné
- [ ] Aucune erreur dans la console du navigateur
- [ ] Aucune erreur dans les logs du backend
- [ ] Base de données : toutes les catégories ont un `ticket_type_id` valide
- [ ] Base de données : contrainte de clé étrangère fonctionne

## 🚨 Problèmes Potentiels

### Problème : L'API ne retourne pas `type_code`

**Solution :** Vérifiez que l'endpoint charge bien la relation `ticket_type` avec `joinedload`

### Problème : Le frontend ne filtre pas les catégories

**Solution :** Vérifiez que le frontend utilise bien `c.type_code === type` pour filtrer

### Problème : Erreur de contrainte de clé étrangère

**Solution :** Vérifiez que tous les `ticket_type_id` pointent vers des IDs valides dans `ticket_types`

## 📝 Après Validation

Une fois tous les tests passés, vous pouvez supprimer l'ancienne colonne `type_code` :

```bash
python add_ticket_type_id_column.py drop
```

**⚠️ ATTENTION :** Ne supprimez la colonne que si vous êtes sûr que tout fonctionne !

