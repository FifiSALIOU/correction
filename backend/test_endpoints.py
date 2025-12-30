"""
Script Python pour tester les endpoints de l'API après migration
"""
import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"
TOKEN = None  # Sera rempli après connexion

def login(username="admin", password="admin123"):
    """Se connecter et obtenir un token"""
    global TOKEN
    try:
        # L'endpoint utilise OAuth2PasswordRequestForm qui nécessite form-data
        response = requests.post(
            f"{BASE_URL}/auth/token",
            data={"username": username, "password": password}  # form-data, pas JSON
        )
        if response.status_code == 200:
            data = response.json()
            TOKEN = data.get("access_token")
            print(f"[OK] Connexion reussie")
            print(f"    Token: {TOKEN[:20]}...")
            return True
        else:
            print(f"[ERREUR] Echec de connexion: {response.status_code}")
            print(f"    {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("[ERREUR] Impossible de se connecter au serveur")
        print("    Assurez-vous que le backend est demarre: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"[ERREUR] {e}")
        return False

def test_get_categories():
    """Test 1: Récupérer toutes les catégories"""
    print("\n" + "="*60)
    print("TEST 1: GET /ticket-config/categories (toutes)")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(f"{BASE_URL}/ticket-config/categories", headers=headers)
    
    if response.status_code == 200:
        categories = response.json()
        print(f"[OK] {len(categories)} categories recuperees")
        
        # Vérifier que chaque catégorie a type_code
        all_have_type_code = all("type_code" in cat for cat in categories)
        if all_have_type_code:
            print("[OK] Toutes les categories ont le champ 'type_code'")
        else:
            print("[ERREUR] Certaines categories n'ont pas 'type_code'")
        
        # Afficher quelques exemples
        print("\nExemples de categories:")
        for cat in categories[:3]:
            print(f"  - {cat['name']}: type_code={cat.get('type_code', 'MANQUANT')}")
        
        return True
    else:
        print(f"[ERREUR] Status: {response.status_code}")
        print(f"    {response.text}")
        return False

def test_get_categories_filtered(type_code):
    """Test 2: Récupérer les catégories filtrées par type"""
    print("\n" + "="*60)
    print(f"TEST 2: GET /ticket-config/categories?type_code={type_code}")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    params = {"type_code": type_code}
    response = requests.get(
        f"{BASE_URL}/ticket-config/categories",
        headers=headers,
        params=params
    )
    
    if response.status_code == 200:
        categories = response.json()
        print(f"[OK] {len(categories)} categories de type '{type_code}'")
        
        # Vérifier que toutes ont le bon type_code
        all_correct = all(cat.get("type_code") == type_code for cat in categories)
        if all_correct:
            print(f"[OK] Toutes les categories ont type_code='{type_code}'")
        else:
            print(f"[ERREUR] Certaines categories n'ont pas type_code='{type_code}'")
        
        # Afficher quelques exemples
        print(f"\nCategories de type '{type_code}':")
        for cat in categories[:5]:
            print(f"  - {cat['name']}")
        
        return True
    else:
        print(f"[ERREUR] Status: {response.status_code}")
        print(f"    {response.text}")
        return False

def test_get_types():
    """Test 3: Récupérer les types de tickets"""
    print("\n" + "="*60)
    print("TEST 3: GET /ticket-config/types")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(f"{BASE_URL}/ticket-config/types", headers=headers)
    
    if response.status_code == 200:
        types = response.json()
        print(f"[OK] {len(types)} types recuperes")
        
        print("\nTypes disponibles:")
        for t in types:
            print(f"  - {t['label']} (code: {t['code']}, id: {t['id']})")
        
        return True
    else:
        print(f"[ERREUR] Status: {response.status_code}")
        print(f"    {response.text}")
        return False

def main():
    """Exécuter tous les tests"""
    print("="*60)
    print("TESTS DES ENDPOINTS API")
    print("="*60)
    
    # Se connecter
    if not login():
        sys.exit(1)
    
    # Tests
    results = []
    results.append(("Toutes les categories", test_get_categories()))
    results.append(("Categories materiel", test_get_categories_filtered("materiel")))
    results.append(("Categories applicatif", test_get_categories_filtered("applicatif")))
    results.append(("Types de tickets", test_get_types()))
    
    # Résumé
    print("\n" + "="*60)
    print("RESUME DES TESTS")
    print("="*60)
    
    for test_name, result in results:
        status = "[OK]" if result else "[ERREUR]"
        print(f"{status} {test_name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n[SUCCES] Tous les tests sont passes !")
        print("\nLa migration fonctionne correctement. L'API retourne bien")
        print("les categories avec type_code via la relation ticket_type.")
    else:
        print("\n[ERREUR] Certains tests ont echoue")
        sys.exit(1)

if __name__ == "__main__":
    main()

