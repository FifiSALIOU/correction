# Guide de Test des Endpoints API

Ce guide vous montre plusieurs façons de tester les endpoints après la migration.

## Prérequis

1. **Démarrer le backend :**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Obtenir un token d'authentification** (nécessaire pour tous les endpoints)

## Méthode 1 : Script Python Automatique (Recommandé)

Le plus simple : utilisez le script de test automatique.

```bash
# Installer requests si nécessaire
pip install requests

# Exécuter les tests
python test_endpoints.py
```

Ce script va :
- Se connecter automatiquement
- Tester tous les endpoints
- Vérifier que `type_code` est présent dans les réponses
- Vérifier que le filtrage fonctionne

## Méthode 2 : Avec curl (Ligne de commande)

### Étape 1 : Se connecter et obtenir un token

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**Réponse attendue :**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Copiez le `access_token` pour les prochaines requêtes.**

### Étape 2 : Tester l'endpoint des catégories

Remplacez `VOTRE_TOKEN` par le token obtenu :

```bash
# Toutes les catégories
curl -X GET "http://localhost:8000/ticket-config/categories" \
  -H "Authorization: Bearer VOTRE_TOKEN"

# Catégories matériel uniquement
curl -X GET "http://localhost:8000/ticket-config/categories?type_code=materiel" \
  -H "Authorization: Bearer VOTRE_TOKEN"

# Catégories applicatif uniquement
curl -X GET "http://localhost:8000/ticket-config/categories?type_code=applicatif" \
  -H "Authorization: Bearer VOTRE_TOKEN"
```

### Étape 3 : Tester l'endpoint des types

```bash
curl -X GET "http://localhost:8000/ticket-config/types" \
  -H "Authorization: Bearer VOTRE_TOKEN"
```

## Méthode 3 : Avec le Navigateur (GET uniquement)

⚠️ **Note :** Cela ne fonctionne que si vous êtes déjà connecté via le frontend.

1. Ouvrez votre navigateur
2. Connectez-vous au frontend
3. Ouvrez la console développeur (F12)
4. Allez dans l'onglet "Network" (Réseau)
5. Créez un ticket ou rechargez la page
6. Cherchez les requêtes vers `/ticket-config/categories`
7. Cliquez dessus pour voir la réponse

## Méthode 4 : Avec Postman (Recommandé pour tests avancés)

### Configuration Postman

1. **Créer une requête POST pour se connecter :**
   - URL : `http://localhost:8000/auth/login`
   - Method : POST
   - Body (x-www-form-urlencoded) :
     - `username` : `admin`
     - `password` : `admin123`
   - Envoyer la requête
   - **Copier le `access_token` de la réponse**

2. **Créer une variable d'environnement :**
   - Cliquez sur "Environments" (Environnements)
   - Créez un nouvel environnement
   - Ajoutez une variable `token` avec la valeur du token

3. **Tester GET /ticket-config/categories :**
   - URL : `http://localhost:8000/ticket-config/categories`
   - Method : GET
   - Headers :
     - `Authorization` : `Bearer {{token}}`
   - Envoyer la requête

4. **Tester avec filtre :**
   - URL : `http://localhost:8000/ticket-config/categories?type_code=materiel`
   - Même configuration que ci-dessus

## Réponses Attendues

### GET /ticket-config/categories

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

**Points à vérifier :**
- ✅ Chaque catégorie a un champ `type_code`
- ✅ Le `type_code` est soit "materiel" soit "applicatif"
- ✅ Toutes les catégories sont retournées (20 au total)

### GET /ticket-config/categories?type_code=materiel

```json
[
  {
    "id": "uuid-here",
    "name": "Ordinateur portable",
    "type_code": "materiel",
    ...
  },
  {
    "id": "uuid-here",
    "name": "Imprimante",
    "type_code": "materiel",
    ...
  }
]
```

**Points à vérifier :**
- ✅ Seules les catégories avec `type_code="materiel"` sont retournées
- ✅ Devrait retourner 10 catégories

### GET /ticket-config/categories?type_code=applicatif

**Points à vérifier :**
- ✅ Seules les catégories avec `type_code="applicatif"` sont retournées
- ✅ Devrait retourner 10 catégories

## Checklist de Validation

- [ ] Le script `test_endpoints.py` passe tous les tests
- [ ] L'endpoint retourne toutes les catégories avec `type_code`
- [ ] Le filtre `?type_code=materiel` retourne uniquement les catégories matériel
- [ ] Le filtre `?type_code=applicatif` retourne uniquement les catégories applicatif
- [ ] Aucune erreur 500 (Internal Server Error)
- [ ] Les réponses JSON sont valides

## Dépannage

### Erreur 401 (Unauthorized)
- Vérifiez que vous avez bien inclus le header `Authorization: Bearer TOKEN`
- Vérifiez que le token n'a pas expiré (reconnectez-vous)

### Erreur 500 (Internal Server Error)
- Vérifiez les logs du backend
- Vérifiez que la migration a bien été effectuée
- Exécutez `python test_migration.py` pour vérifier la base de données

### Le champ `type_code` est manquant
- Vérifiez que l'endpoint charge bien la relation `ticket_type`
- Vérifiez les logs du backend pour voir les erreurs SQL

### Le filtre ne fonctionne pas
- Vérifiez que la jointure avec `ticket_types` est bien faite
- Vérifiez que les `ticket_type_id` sont bien remplis dans la base

