"""
Script pour lister tous les utilisateurs créés
"""
from app.database import SessionLocal
from app import models

def list_users():
    db = SessionLocal()
    try:
        users = db.query(models.User).all()
        
        print("\n" + "="*60)
        print("UTILISATEURS CREES DANS LA BASE DE DONNEES")
        print("="*60 + "\n")
        
        for i, user in enumerate(users, 1):
            role_name = user.role.name if user.role else "N/A"
            agency = user.agency or "N/A"
            print(f"{i}. Username: {user.username}")
            print(f"   Nom complet: {user.full_name}")
            print(f"   Email: {user.email}")
            print(f"   Role: {role_name}")
            print(f"   Agence: {agency}")
            print(f"   Actif: {user.actif}")
            print()
        
        print("="*60)
        print("\nRESUME DES COMPTES DE TEST:")
        print("-" * 60)
        print("  - user1 / user123 (Utilisateur)")
        print("  - tech1 / tech123 (Technicien)")
        print("  - tech2 / tech123 (Technicien)")
        print("  - secretary1 / secretary123 (Secretaire DSI)")
        print("  - adjoint1 / adjoint123 (Adjoint DSI)")
        print("  - dsi1 / dsi123 (DSI)")
        print("  - admin / admin123 (Admin)")
        print()
        
    except Exception as e:
        print(f"ERREUR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    list_users()

