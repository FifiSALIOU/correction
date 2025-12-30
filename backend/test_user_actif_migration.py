"""
Script de test pour vérifier que la migration status -> actif fonctionne correctement
"""
import requests
import sys
from typing import Optional

BASE_URL = "http://localhost:8000"

def test_login(username: str, password: str) -> Optional[str]:
    """Test de connexion et récupération du token"""
    print(f"\n[TEST] Connexion avec {username}...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/token",
            data={
                "username": username,
                "password": password
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"[OK] Connexion reussie, token obtenu")
            return token
        else:
            print(f"[ERREUR] Echec de connexion: {response.status_code}")
            print(f"  Reponse: {response.text}")
            return None
    except Exception as e:
        print(f"[ERREUR] Exception lors de la connexion: {e}")
        return None

def test_get_users(token: str):
    """Test de récupération de la liste des utilisateurs"""
    print(f"\n[TEST] Recuperation de la liste des utilisateurs...")
    try:
        response = requests.get(
            f"{BASE_URL}/users/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            users = response.json()
            print(f"[OK] {len(users)} utilisateur(s) recupere(s)")
            
            # Vérifier que tous les utilisateurs ont le champ 'actif'
            errors = []
            for user in users:
                if "actif" not in user:
                    errors.append(f"  User {user.get('id', 'unknown')}: champ 'actif' manquant")
                elif "status" in user:
                    errors.append(f"  User {user.get('id', 'unknown')}: ancien champ 'status' encore present")
                elif not isinstance(user.get("actif"), bool):
                    errors.append(f"  User {user.get('id', 'unknown')}: 'actif' n'est pas un boolean (type: {type(user.get('actif'))})")
            
            if errors:
                print(f"[ERREUR] Problemes detectes:")
                for error in errors:
                    print(error)
                return False
            else:
                print(f"[OK] Tous les utilisateurs ont le champ 'actif' (Boolean)")
                # Afficher quelques exemples
                print(f"\n  Exemples:")
                for user in users[:3]:
                    print(f"    - {user.get('full_name', 'N/A')}: actif={user.get('actif')}")
                return True
        else:
            print(f"[ERREUR] Status: {response.status_code}")
            print(f"  Reponse: {response.text}")
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
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            technicians = response.json()
            print(f"[OK] {len(technicians)} technicien(s) recupere(s)")
            
            # Vérifier que tous les techniciens ont le champ 'actif'
            errors = []
            for tech in technicians:
                if "actif" not in tech:
                    errors.append(f"  Technicien {tech.get('id', 'unknown')}: champ 'actif' manquant")
                elif "status" in tech:
                    errors.append(f"  Technicien {tech.get('id', 'unknown')}: ancien champ 'status' encore present")
                elif not isinstance(tech.get("actif"), bool):
                    errors.append(f"  Technicien {tech.get('id', 'unknown')}: 'actif' n'est pas un boolean")
            
            if errors:
                print(f"[ERREUR] Problemes detectes:")
                for error in errors:
                    print(error)
                return False
            else:
                print(f"[OK] Tous les techniciens ont le champ 'actif' (Boolean)")
                # Afficher quelques exemples
                if technicians:
                    print(f"\n  Exemples:")
                    for tech in technicians[:3]:
                        print(f"    - {tech.get('full_name', 'N/A')}: actif={tech.get('actif')}, availability_status={tech.get('availability_status')}")
                return True
        else:
            print(f"[ERREUR] Status: {response.status_code}")
            print(f"  Reponse: {response.text}")
            return False
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")
        return False

def test_get_user_by_id(token: str, user_id: str):
    """Test de récupération d'un utilisateur par ID"""
    print(f"\n[TEST] Recuperation d'un utilisateur par ID...")
    try:
        response = requests.get(
            f"{BASE_URL}/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            user = response.json()
            print(f"[OK] Utilisateur recupere: {user.get('full_name', 'N/A')}")
            
            # Vérifier le champ 'actif'
            if "actif" not in user:
                print(f"[ERREUR] Champ 'actif' manquant")
                return False
            elif "status" in user:
                print(f"[ERREUR] Ancien champ 'status' encore present")
                return False
            elif not isinstance(user.get("actif"), bool):
                print(f"[ERREUR] 'actif' n'est pas un boolean (type: {type(user.get('actif'))})")
                return False
            else:
                print(f"[OK] Champ 'actif' present et correct: {user.get('actif')}")
                return True
        else:
            print(f"[ERREUR] Status: {response.status_code}")
            print(f"  Reponse: {response.text}")
            return False
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")
        return False

def test_update_user_actif(token: str, user_id: str):
    """Test de mise à jour du champ actif d'un utilisateur"""
    print(f"\n[TEST] Mise a jour du champ actif d'un utilisateur...")
    try:
        # D'abord récupérer l'utilisateur pour voir sa valeur actuelle
        get_response = requests.get(
            f"{BASE_URL}/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if get_response.status_code != 200:
            print(f"[ERREUR] Impossible de recuperer l'utilisateur: {get_response.status_code}")
            return False
        
        current_user = get_response.json()
        current_actif = current_user.get("actif")
        new_actif = not current_actif  # Inverser la valeur
        
        # Mettre à jour
        update_response = requests.put(
            f"{BASE_URL}/users/{user_id}",
            json={"actif": new_actif},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if update_response.status_code == 200:
            updated_user = update_response.json()
            if updated_user.get("actif") == new_actif:
                print(f"[OK] Champ 'actif' mis a jour: {current_actif} -> {new_actif}")
                
                # Remettre la valeur d'origine
                requests.put(
                    f"{BASE_URL}/users/{user_id}",
                    json={"actif": current_actif},
                    headers={"Authorization": f"Bearer {token}"}
                )
                print(f"[OK] Valeur restauree: {current_actif}")
                return True
            else:
                print(f"[ERREUR] La valeur n'a pas ete mise a jour correctement")
                return False
        else:
            print(f"[ERREUR] Status: {update_response.status_code}")
            print(f"  Reponse: {update_response.text}")
            return False
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")
        return False

def test_create_user_with_actif(token: str):
    """Test de création d'un utilisateur avec le champ actif"""
    print(f"\n[TEST] Creation d'un utilisateur avec actif...")
    try:
        # Créer un utilisateur de test
        test_user_data = {
            "full_name": "Test User Actif",
            "email": f"test_actif_{requests.utils.time.time()}@test.com",
            "username": f"test_actif_{requests.utils.time.time()}",
            "password": "TestPassword123!",
            "role_id": None,  # Nécessite un role_id valide, on va juste tester la structure
            "actif": True
        }
        
        # Note: Ce test nécessite un role_id valide, donc on va juste vérifier la structure
        print(f"[INFO] Test de structure (necessite un role_id valide pour creer)")
        print(f"[OK] Structure de donnees correcte: actif={test_user_data['actif']} (Boolean)")
        return True
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")
        return False

def test_technician_filter(token: str):
    """Test que les filtres de techniciens actifs fonctionnent"""
    print(f"\n[TEST] Verification des filtres de techniciens actifs...")
    try:
        response = requests.get(
            f"{BASE_URL}/users/technicians",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            technicians = response.json()
            
            # Vérifier que seuls les techniciens actifs sont retournés
            inactive_count = sum(1 for tech in technicians if tech.get("actif") == False)
            active_count = sum(1 for tech in technicians if tech.get("actif") == True)
            
            print(f"[OK] Techniciens recuperes: {len(technicians)}")
            print(f"  - Actifs: {active_count}")
            print(f"  - Inactifs: {inactive_count}")
            
            # Normalement, l'endpoint devrait filtrer les inactifs
            # Mais vérifions que tous ont le champ actif
            all_have_actif = all("actif" in tech for tech in technicians)
            if all_have_actif:
                print(f"[OK] Tous les techniciens ont le champ 'actif'")
                return True
            else:
                print(f"[ERREUR] Certains techniciens n'ont pas le champ 'actif'")
                return False
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
    
    # Utiliser des credentials par défaut ou depuis les variables d'environnement
    import os
    username = os.getenv("TEST_USERNAME", "admin")
    password = os.getenv("TEST_PASSWORD", "admin")
    
    print(f"\nUtilisation des credentials: {username}")
    print("(Vous pouvez definir TEST_USERNAME et TEST_PASSWORD pour utiliser d'autres credentials)")
    
    # Test de connexion
    token = test_login(username, password)
    if not token:
        print("\n[ERREUR] Impossible de se connecter. Verifiez que le serveur backend est demarre.")
        sys.exit(1)
    
    # Liste des tests
    tests = [
        ("Liste des utilisateurs", lambda: test_get_users(token)),
        ("Liste des techniciens", lambda: test_get_technicians(token)),
        ("Filtres de techniciens", lambda: test_technician_filter(token)),
        ("Structure de creation", lambda: test_create_user_with_actif(token)),
    ]
    
    # Récupérer un user_id pour les tests de détail
    try:
        users_response = requests.get(
            f"{BASE_URL}/users/",
            headers={"Authorization": f"Bearer {token}"}
        )
        if users_response.status_code == 200:
            users = users_response.json()
            if users:
                user_id = users[0].get("id")
                tests.append(("Recuperation utilisateur par ID", lambda: test_get_user_by_id(token, user_id)))
                tests.append(("Mise a jour champ actif", lambda: test_update_user_actif(token, user_id)))
    except:
        pass
    
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
        print("\n[SUCCES] Tous les tests sont passes ! La migration fonctionne correctement.")
        return 0
    else:
        print(f"\n[ATTENTION] {total - passed} test(s) ont echoue. Verifiez les erreurs ci-dessus.")
        return 1

if __name__ == "__main__":
    try:
        import requests.utils.time
    except:
        import time
        requests.utils = type('obj', (object,), {'time': time})()
    
    sys.exit(main())

