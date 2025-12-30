"""
Script pour lister les emails des DSI, Secrétaires DSI et Adjoints DSI
"""
from app.database import SessionLocal
from app import models

def list_dsi_emails():
    db = SessionLocal()
    try:
        # Récupérer les rôles
        dsi_role = db.query(models.Role).filter(models.Role.name == "DSI").first()
        secretary_role = db.query(models.Role).filter(models.Role.name == "Secrétaire DSI").first()
        adjoint_role = db.query(models.Role).filter(models.Role.name == "Adjoint DSI").first()
        
        print("=" * 60)
        print("LISTE DES EMAILS - DSI, SECRÉTAIRES ET ADJOINTS")
        print("=" * 60)
        print()
        
        # DSI
        if dsi_role:
            dsi_users = db.query(models.User).filter(
                models.User.role_id == dsi_role.id,
                models.User.actif == True
            ).all()
            
            print(f"DSI ({len(dsi_users)} utilisateur(s)):")
            if dsi_users:
                for user in dsi_users:
                    print(f"   • {user.full_name}")
                    print(f"     Email: {user.email}")
                    print(f"     Username: {user.username}")
                    print()
            else:
                print("   Aucun DSI actif trouvé")
                print()
        else:
            print("⚠️  Rôle DSI non trouvé")
            print()
        
        # Secrétaires DSI
        if secretary_role:
            secretary_users = db.query(models.User).filter(
                models.User.role_id == secretary_role.id,
                models.User.actif == True
            ).all()
            
            print(f"SECRETAIRES DSI ({len(secretary_users)} utilisateur(s)):")
            if secretary_users:
                for user in secretary_users:
                    print(f"   • {user.full_name}")
                    print(f"     Email: {user.email}")
                    print(f"     Username: {user.username}")
                    print()
            else:
                print("   Aucun Secrétaire DSI actif trouvé")
                print()
        else:
            print("⚠️  Rôle Secrétaire DSI non trouvé")
            print()
        
        # Adjoints DSI
        if adjoint_role:
            adjoint_users = db.query(models.User).filter(
                models.User.role_id == adjoint_role.id,
                models.User.actif == True
            ).all()
            
            print(f"ADJOINTS DSI ({len(adjoint_users)} utilisateur(s)):")
            if adjoint_users:
                for user in adjoint_users:
                    print(f"   • {user.full_name}")
                    print(f"     Email: {user.email}")
                    print(f"     Username: {user.username}")
                    print()
            else:
                print("   Aucun Adjoint DSI actif trouvé")
                print()
        else:
            print("⚠️  Rôle Adjoint DSI non trouvé")
            print()
        
        # Résumé
        print("=" * 60)
        total = 0
        if dsi_role:
            total += len(db.query(models.User).filter(models.User.role_id == dsi_role.id, models.User.status == "actif").all())
        if secretary_role:
            total += len(db.query(models.User).filter(models.User.role_id == secretary_role.id, models.User.status == "actif").all())
        if adjoint_role:
            total += len(db.query(models.User).filter(models.User.role_id == adjoint_role.id, models.User.status == "actif").all())
        print(f"TOTAL: {total} utilisateur(s) recevront des emails lors de la création d'un ticket")
        print("=" * 60)
        
    except Exception as e:
        print(f"ERREUR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    list_dsi_emails()

