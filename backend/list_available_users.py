"""
Script pour lister les utilisateurs disponibles dans la base de données
Utile pour trouver les credentials à utiliser pour les tests
"""
from app.database import SessionLocal
from app import models

def list_users():
    """Liste tous les utilisateurs avec leurs credentials"""
    db = SessionLocal()
    try:
        users = db.query(models.User).all()
        
        if not users:
            print("Aucun utilisateur trouve dans la base de donnees")
            return
        
        print("=" * 70)
        print("UTILISATEURS DISPONIBLES")
        print("=" * 70)
        print(f"\nTotal: {len(users)} utilisateur(s)\n")
        
        for user in users:
            role_name = user.role.name if user.role else "N/A"
            actif_status = "Actif" if user.actif else "Inactif"
            
            print(f"Username: {user.username}")
            print(f"  Nom: {user.full_name}")
            print(f"  Email: {user.email}")
            print(f"  Role: {role_name}")
            print(f"  Statut: {actif_status}")
            print(f"  Agence: {user.agency or 'N/A'}")
            print()
        
        print("=" * 70)
        print("CREDENTIALS PAR DEFAUT (si crees par init_db.py):")
        print("  - admin / admin123 (Admin)")
        print("\nCREDENTIALS DE TEST (si crees par create_test_users.py):")
        print("  - user1 / user123 (Utilisateur)")
        print("  - tech1 / tech123 (Technicien)")
        print("  - secretary1 / secretary123 (Secretaire DSI)")
        print("  - adjoint1 / adjoint123 (Adjoint DSI)")
        print("  - dsi1 / dsi123 (DSI)")
        print("=" * 70)
        
    except Exception as e:
        print(f"[ERREUR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    list_users()

