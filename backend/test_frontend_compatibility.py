"""
Test automatique de compatibilité frontend-backend pour la migration status -> actif
Simule les appels API que le frontend fait et vérifie la compatibilité
"""
import requests
import sys
import os
from typing import Optional, Dict, Any

BASE_URL = "http://localhost:8000"
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin123"

def test_login(username: str = DEFAULT_USERNAME, password: str = DEFAULT_PASSWORD) -> Optional[str]:
    """Test de connexion"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/token",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=5
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    except:
        return None

def test_auth_me(token: str) -> bool:
    """Test /auth/me - utilisé par le frontend pour récupérer les infos utilisateur"""
    print(f"\n[TEST] GET /auth/me (utilise par le frontend pour le role)")
    try:
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        
        if response.status_code == 200:
            user = response.json()
            print(f"[OK] Utilisateur recupere: {user.get('full_name', 'N/A')}")
            
            # Vérifier que le champ actif est présent (si exposé)
            if "actif" in user:
                if not isinstance(user.get("actif"), bool):
                    print(f"[ERREUR] 'actif' n'est pas un boolean dans /auth/me")
                    return False
                print(f"[OK] Champ 'actif' present: {user.get('actif')}")
            
            # Vérifier qu'il n'y a pas de champ status
            if "status" in user:
                print(f"[ATTENTION] Ancien champ 'status' encore present dans /auth/me")
            
            return True
        else:
            print(f"[ERREUR] Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")
        return False

def test_users_list(token: str) -> bool:
    """Test GET /users/ - utilisé par DSIDashboard"""
    print(f"\n[TEST] GET /users/ (utilise par DSIDashboard)")
    try:
        response = requests.get(
            f"{BASE_URL}/users/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        
        if response.status_code == 200:
            users = response.json()
            print(f"[OK] {len(users)} utilisateur(s) recupere(s)")
            
            if not users:
                print(f"[SKIP] Aucun utilisateur pour tester la structure")
                return True
            
            # Vérifier la structure attendue par le frontend
            user = users[0]
            required_fields = ["id", "full_name", "email", "role"]
            missing_fields = [f for f in required_fields if f not in user]
            
            if missing_fields:
                print(f"[ERREUR] Champs manquants: {missing_fields}")
                return False
            
            # Vérifier actif
            if "actif" not in user:
                print(f"[ERREUR] Champ 'actif' manquant")
                return False
            
            if not isinstance(user.get("actif"), bool):
                print(f"[ERREUR] 'actif' n'est pas un boolean")
                return False
            
            # Vérifier qu'il n'y a pas de status
            if "status" in user:
                print(f"[ATTENTION] Ancien champ 'status' encore present")
            
            print(f"[OK] Structure compatible avec le frontend")
            print(f"  Exemple: {user.get('full_name')} - actif={user.get('actif')}")
            return True
        else:
            print(f"[ERREUR] Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")
        return False

def test_technicians_list(token: str) -> bool:
    """Test GET /users/technicians - utilisé par DSIDashboard"""
    print(f"\n[TEST] GET /users/technicians (utilise par DSIDashboard)")
    try:
        response = requests.get(
            f"{BASE_URL}/users/technicians",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        
        if response.status_code == 200:
            technicians = response.json()
            print(f"[OK] {len(technicians)} technicien(s) recupere(s)")
            
            if not technicians:
                print(f"[SKIP] Aucun technicien pour tester la structure")
                return True
            
            # Vérifier la structure attendue par le frontend
            tech = technicians[0]
            required_fields = ["id", "full_name", "email"]
            missing_fields = [f for f in required_fields if f not in tech]
            
            if missing_fields:
                print(f"[ERREUR] Champs manquants: {missing_fields}")
                return False
            
            # Vérifier actif
            if "actif" not in tech:
                print(f"[ERREUR] Champ 'actif' manquant")
                return False
            
            if not isinstance(tech.get("actif"), bool):
                print(f"[ERREUR] 'actif' n'est pas un boolean")
                return False
            
            # Vérifier qu'il n'y a pas de status
            if "status" in tech:
                print(f"[ATTENTION] Ancien champ 'status' encore present")
            
            print(f"[OK] Structure compatible avec le frontend")
            print(f"  Exemple: {tech.get('full_name')} - actif={tech.get('actif')}, availability_status={tech.get('availability_status')}")
            return True
        else:
            print(f"[ERREUR] Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")
        return False

def test_user_by_id(token: str) -> bool:
    """Test GET /users/{id} - utilisé pour éditer un utilisateur"""
    print(f"\n[TEST] GET /users/{{id}} (utilise pour editer un utilisateur)")
    try:
        # D'abord récupérer un ID
        users_response = requests.get(
            f"{BASE_URL}/users/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        
        if users_response.status_code != 200 or not users_response.json():
            print(f"[SKIP] Aucun utilisateur disponible")
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
            
            # Vérifier actif
            if "actif" not in user:
                print(f"[ERREUR] Champ 'actif' manquant")
                return False
            
            if not isinstance(user.get("actif"), bool):
                print(f"[ERREUR] 'actif' n'est pas un boolean")
                return False
            
            if "status" in user:
                print(f"[ATTENTION] Ancien champ 'status' encore present")
            
            print(f"[OK] Structure compatible - actif={user.get('actif')}")
            return True
        else:
            print(f"[ERREUR] Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")
        return False

def test_update_user(token: str) -> bool:
    """Test PUT /users/{id} - utilisé pour mettre à jour un utilisateur"""
    print(f"\n[TEST] PUT /users/{{id}} (utilise pour mettre a jour actif)")
    try:
        # Récupérer un utilisateur
        users_response = requests.get(
            f"{BASE_URL}/users/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        
        if users_response.status_code != 200 or not users_response.json():
            print(f"[SKIP] Aucun utilisateur disponible")
            return True
        
        user = users_response.json()[0]
        user_id = user.get("id")
        current_actif = user.get("actif")
        
        # Tester la mise à jour avec actif
        update_data = {"actif": not current_actif}
        
        response = requests.put(
            f"{BASE_URL}/users/{user_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        
        if response.status_code == 200:
            updated_user = response.json()
            
            if updated_user.get("actif") != (not current_actif):
                print(f"[ERREUR] La mise a jour n'a pas fonctionne")
                # Restaurer
                requests.put(
                    f"{BASE_URL}/users/{user_id}",
                    json={"actif": current_actif},
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=5
                )
                return False
            
            print(f"[OK] Mise a jour reussie: actif={current_actif} -> {not current_actif}")
            
            # Restaurer la valeur d'origine
            requests.put(
                f"{BASE_URL}/users/{user_id}",
                json={"actif": current_actif},
                headers={"Authorization": f"Bearer {token}"},
                timeout=5
            )
            print(f"[OK] Valeur restauree: actif={current_actif}")
            
            return True
        else:
            print(f"[ERREUR] Status: {response.status_code}")
            print(f"  Reponse: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")
        return False

def test_technician_stats(token: str) -> bool:
    """Test GET /users/technicians/{id}/stats - utilisé par DSIDashboard"""
    print(f"\n[TEST] GET /users/technicians/{{id}}/stats (utilise par DSIDashboard)")
    try:
        # Récupérer un technicien
        techs_response = requests.get(
            f"{BASE_URL}/users/technicians",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        
        if techs_response.status_code != 200 or not techs_response.json():
            print(f"[SKIP] Aucun technicien disponible")
            return True
        
        tech_id = techs_response.json()[0].get("id")
        
        response = requests.get(
            f"{BASE_URL}/users/technicians/{tech_id}/stats",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        
        if response.status_code == 200:
            stats = response.json()
            print(f"[OK] Statistiques recuperees pour: {stats.get('full_name', 'N/A')}")
            
            # Vérifier que actif est présent
            if "actif" not in stats:
                print(f"[ERREUR] Champ 'actif' manquant dans les stats")
                return False
            
            if not isinstance(stats.get("actif"), bool):
                print(f"[ERREUR] 'actif' n'est pas un boolean dans les stats")
                return False
            
            if "status" in stats:
                print(f"[ATTENTION] Ancien champ 'status' encore present dans les stats")
            
            print(f"[OK] Structure compatible - actif={stats.get('actif')}")
            return True
        else:
            print(f"[ERREUR] Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")
        return False

def simulate_frontend_workflow(token: str) -> bool:
    """Simule un workflow complet du frontend"""
    print(f"\n[TEST] Simulation workflow frontend complet")
    try:
        # 1. Récupérer les utilisateurs (comme DSIDashboard)
        users_res = requests.get(
            f"{BASE_URL}/users/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        
        if users_res.status_code != 200:
            print(f"[ERREUR] Impossible de recuperer les utilisateurs")
            return False
        
        users = users_res.json()
        print(f"  [OK] {len(users)} utilisateur(s) recupere(s)")
        
        # 2. Récupérer les techniciens (comme DSIDashboard)
        techs_res = requests.get(
            f"{BASE_URL}/users/technicians",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        
        if techs_res.status_code != 200:
            print(f"[ERREUR] Impossible de recuperer les techniciens")
            return False
        
        techs = techs_res.json()
        print(f"  [OK] {len(techs)} technicien(s) recupere(s)")
        
        # 3. Vérifier que tous ont actif (Boolean)
        all_have_actif = True
        for user in users:
            if "actif" not in user or not isinstance(user.get("actif"), bool):
                print(f"  [ERREUR] User {user.get('full_name')} n'a pas actif (Boolean)")
                all_have_actif = False
        
        for tech in techs:
            if "actif" not in tech or not isinstance(tech.get("actif"), bool):
                print(f"  [ERREUR] Tech {tech.get('full_name')} n'a pas actif (Boolean)")
                all_have_actif = False
        
        if not all_have_actif:
            return False
        
        print(f"  [OK] Tous les utilisateurs et techniciens ont actif (Boolean)")
        print(f"  [OK] Workflow frontend compatible")
        return True
        
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")
        return False

def main():
    """Fonction principale"""
    print("=" * 70)
    print("TEST DE COMPATIBILITE FRONTEND-BACKEND")
    print("Migration: status -> actif (Boolean)")
    print("=" * 70)
    
    # Utiliser des credentials depuis les variables d'environnement ou par défaut
    username = os.getenv("TEST_USERNAME", DEFAULT_USERNAME)
    password = os.getenv("TEST_PASSWORD", DEFAULT_PASSWORD)
    
    print(f"\nCredentials: {username}")
    print(f"Backend URL: {BASE_URL}")
    
    # Connexion
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
        ("Auth /me", lambda: test_auth_me(token)),
        ("Liste utilisateurs", lambda: test_users_list(token)),
        ("Liste techniciens", lambda: test_technicians_list(token)),
        ("Utilisateur par ID", lambda: test_user_by_id(token)),
        ("Mise a jour utilisateur", lambda: test_update_user(token)),
        ("Stats technicien", lambda: test_technician_stats(token)),
        ("Workflow frontend complet", lambda: simulate_frontend_workflow(token)),
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
    print("\n" + "=" * 70)
    print("RESUME DES TESTS")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[OK]" if result else "[ERREUR]"
        print(f"{status} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests reussis")
    
    if passed == total:
        print("\n[SUCCES] Tous les tests sont passes !")
        print("Le backend est compatible avec le frontend pour la migration status -> actif.")
        print("\nLe frontend devrait fonctionner correctement avec ces endpoints.")
        return 0
    else:
        print(f"\n[ATTENTION] {total - passed} test(s) ont echoue.")
        print("Verifiez les erreurs ci-dessus avant de tester le frontend.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

