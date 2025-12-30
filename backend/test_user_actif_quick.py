"""
Script de test rapide et non-interactif pour vérifier la migration status -> actif
"""
import requests
import sys
import os
from typing import Optional

BASE_URL = "http://localhost:8000"

# Credentials par défaut (à modifier si nécessaire)
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin123"  # Mot de passe par défaut dans init_db.py

def test_login(username: str = DEFAULT_USERNAME, password: str = DEFAULT_PASSWORD) -> Optional[str]:
    """Test de connexion et récupération du token"""
    print(f"\n[TEST] Connexion avec {username}...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/token",
            data={
                "username": username,
                "password": password
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=5
        )
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"[OK] Connexion reussie")
            return token
        else:
            print(f"[ERREUR] Echec de connexion: {response.status_code}")
            if response.status_code == 401:
                print(f"  -> Credentials incorrects. Utilisez TEST_USERNAME et TEST_PASSWORD")
            return None
    except requests.exceptions.ConnectionError:
        print(f"[ERREUR] Impossible de se connecter au serveur")
        print(f"  -> Assurez-vous que le backend est demarre sur {BASE_URL}")
        return None
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")
        return None

def test_get_users(token: str):
    """Test de récupération de la liste des utilisateurs"""
    print(f"\n[TEST] Recuperation de la liste des utilisateurs...")
    try:
        response = requests.get(
            f"{BASE_URL}/users/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        
        if response.status_code == 200:
            users = response.json()
            print(f"[OK] {len(users)} utilisateur(s) recupere(s)")
            
            # Vérifier que tous les utilisateurs ont le champ 'actif'
            errors = []
            has_status = []
            for user in users:
                if "actif" not in user:
                    errors.append(f"  User {user.get('full_name', 'unknown')}: champ 'actif' manquant")
                if "status" in user:
                    has_status.append(f"  User {user.get('full_name', 'unknown')}: ancien champ 'status' encore present")
                if "actif" in user and not isinstance(user.get("actif"), bool):
                    errors.append(f"  User {user.get('full_name', 'unknown')}: 'actif' n'est pas un boolean (type: {type(user.get('actif'))})")
            
            if errors:
                print(f"[ERREUR] Problemes detectes:")
                for error in errors:
                    print(error)
                return False
            
            if has_status:
                print(f"[ATTENTION] Ancien champ 'status' encore present:")
                for msg in has_status:
                    print(msg)
            
            print(f"[OK] Tous les utilisateurs ont le champ 'actif' (Boolean)")
            # Afficher quelques exemples
            if users:
                print(f"\n  Exemples:")
                for user in users[:3]:
                    print(f"    - {user.get('full_name', 'N/A')}: actif={user.get('actif')}")
            return True
        else:
            print(f"[ERREUR] Status: {response.status_code}")
            print(f"  Reponse: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")
        return False

def test_get_technicians(token: str):
    """Test de récupération de la liste des techniciens"""
    print(f"\n[TEST] Recuperation de la liste des techniciens...")
    try:
        response = requests.get(
            f"{BASE_URL}/users/technicians",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        
        if response.status_code == 200:
            technicians = response.json()
            print(f"[OK] {len(technicians)} technicien(s) recupere(s)")
            
            # Vérifier que tous les techniciens ont le champ 'actif'
            errors = []
            has_status = []
            for tech in technicians:
                if "actif" not in tech:
                    errors.append(f"  Technicien {tech.get('full_name', 'unknown')}: champ 'actif' manquant")
                if "status" in tech:
                    has_status.append(f"  Technicien {tech.get('full_name', 'unknown')}: ancien champ 'status' encore present")
                if "actif" in tech and not isinstance(tech.get("actif"), bool):
                    errors.append(f"  Technicien {tech.get('full_name', 'unknown')}: 'actif' n'est pas un boolean")
            
            if errors:
                print(f"[ERREUR] Problemes detectes:")
                for error in errors:
                    print(error)
                return False
            
            if has_status:
                print(f"[ATTENTION] Ancien champ 'status' encore present:")
                for msg in has_status:
                    print(msg)
            
            print(f"[OK] Tous les techniciens ont le champ 'actif' (Boolean)")
            # Afficher quelques exemples
            if technicians:
                print(f"\n  Exemples:")
                for tech in technicians[:3]:
                    print(f"    - {tech.get('full_name', 'N/A')}: actif={tech.get('actif')}, availability_status={tech.get('availability_status')}")
            return True
        else:
            print(f"[ERREUR] Status: {response.status_code}")
            print(f"  Reponse: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")
        return False

def test_get_user_by_id(token: str):
    """Test de récupération d'un utilisateur par ID"""
    print(f"\n[TEST] Recuperation d'un utilisateur par ID...")
    try:
        # D'abord récupérer la liste pour avoir un ID
        users_response = requests.get(
            f"{BASE_URL}/users/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        
        if users_response.status_code != 200 or not users_response.json():
            print(f"[SKIP] Aucun utilisateur disponible pour ce test")
            return True
        
        user_id = users_response.json()[0].get("id")
        
        response = requests.get(
            f"{BASE_URL}/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        
        if response.status_code == 200:
            user = response.json()
            print(f"[OK] Utilisateur recupere: {user.get('full_name', 'N/A')}")
            
            # Vérifier le champ 'actif'
            if "actif" not in user:
                print(f"[ERREUR] Champ 'actif' manquant")
                return False
            if "status" in user:
                print(f"[ERREUR] Ancien champ 'status' encore present")
                return False
            if not isinstance(user.get("actif"), bool):
                print(f"[ERREUR] 'actif' n'est pas un boolean (type: {type(user.get('actif'))})")
                return False
            
            print(f"[OK] Champ 'actif' present et correct: {user.get('actif')}")
            return True
        else:
            print(f"[ERREUR] Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("=" * 60)
    print("TEST DE MIGRATION: status -> actif (Boolean)")
    print("=" * 60)
    
    # Utiliser des credentials depuis les variables d'environnement ou par défaut
    username = os.getenv("TEST_USERNAME", DEFAULT_USERNAME)
    password = os.getenv("TEST_PASSWORD", DEFAULT_PASSWORD)
    
    print(f"\nCredentials: {username}")
    print(f"Backend URL: {BASE_URL}")
    print(f"\n(Definissez TEST_USERNAME et TEST_PASSWORD pour utiliser d'autres credentials)")
    
    # Test de connexion
    token = test_login(username, password)
    if not token:
        print("\n[ERREUR] Impossible de se connecter.")
        print("\nVerifications:")
        print("  1. Le backend est-il demarre ? (uvicorn app.main:app --reload)")
        print("  2. Les credentials sont-ils corrects ?")
        print("  3. L'URL du backend est-elle correcte ?")
        sys.exit(1)
    
    # Liste des tests
    tests = [
        ("Liste des utilisateurs", lambda: test_get_users(token)),
        ("Liste des techniciens", lambda: test_get_technicians(token)),
        ("Recuperation utilisateur par ID", lambda: test_get_user_by_id(token)),
    ]
    
    # Exécuter les tests
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[ERREUR] Test '{test_name}' a echoue avec exception: {e}")
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "=" * 60)
    print("RESUME DES TESTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[OK]" if result else "[ERREUR]"
        print(f"{status} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests reussis")
    
    if passed == total:
        print("\n[SUCCES] Tous les tests sont passes !")
        print("La migration status -> actif fonctionne correctement.")
        return 0
    else:
        print(f"\n[ATTENTION] {total - passed} test(s) ont echoue.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

