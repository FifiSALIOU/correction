"""
Script pour créer des utilisateurs de test
"""
from app.database import SessionLocal
from app import models
from app.security import get_password_hash

def create_test_users():
    db = SessionLocal()
    try:
        # Récupérer les rôles
        user_role = db.query(models.Role).filter(models.Role.name == "Utilisateur").first()
        tech_role = db.query(models.Role).filter(models.Role.name == "Technicien").first()
        secretary_role = db.query(models.Role).filter(models.Role.name == "Secrétaire DSI").first()
        adjoint_role = db.query(models.Role).filter(models.Role.name == "Adjoint DSI").first()
        dsi_role = db.query(models.Role).filter(models.Role.name == "DSI").first()
        
        if not user_role or not tech_role or not secretary_role or not adjoint_role or not dsi_role:
            print("ERREUR: Les roles n'existent pas. Lancez d'abord init_db.py")
            return
        
        # Créer un utilisateur simple
        existing_user = db.query(models.User).filter(models.User.username == "user1").first()
        if not existing_user:
            user1 = models.User(
                full_name="Jean Dupont",
                email="jean.dupont@example.com",
                username="user1",
                password_hash=get_password_hash("user123"),
                role_id=user_role.id,
                agency="Agence Paris",
                actif=True
            )
            db.add(user1)
            print("OK - Utilisateur cree: user1 (password: user123)")
        
        # Créer un technicien matériel
        existing_tech1 = db.query(models.User).filter(models.User.username == "tech1").first()
        if not existing_tech1:
            tech1 = models.User(
                full_name="Pierre Martin",
                email="pierre.martin@example.com",
                username="tech1",
                password_hash=get_password_hash("tech123"),
                role_id=tech_role.id,
                agency="Agence IT",
                actif=True,
                specialization="materiel"
            )
            db.add(tech1)
            print("OK - Technicien cree: tech1 (password: tech123, specialisation: materiel)")
        elif not existing_tech1.specialization:
            # Mettre à jour la spécialisation si elle n'existe pas
            existing_tech1.specialization = "materiel"
            print("OK - Specialisation mise a jour pour tech1: materiel")
        
        # Créer un technicien applicatif
        existing_tech2 = db.query(models.User).filter(models.User.username == "tech2").first()
        if not existing_tech2:
            tech2 = models.User(
                full_name="Marie Dubois",
                email="marie.dubois@example.com",
                username="tech2",
                password_hash=get_password_hash("tech123"),
                role_id=tech_role.id,
                agency="Agence IT",
                actif=True,
                specialization="applicatif"
            )
            db.add(tech2)
            print("OK - Technicien cree: tech2 (password: tech123, specialisation: applicatif)")
        elif not existing_tech2.specialization:
            # Mettre à jour la spécialisation si elle n'existe pas
            existing_tech2.specialization = "applicatif"
            print("OK - Specialisation mise a jour pour tech2: applicatif")
        
        # Créer une secrétaire DSI
        existing_sec = db.query(models.User).filter(models.User.username == "secretary1").first()
        if not existing_sec:
            secretary1 = models.User(
                full_name="Sophie Bernard",
                email="sophie.bernard@example.com",
                username="secretary1",
                password_hash=get_password_hash("secretary123"),
                role_id=secretary_role.id,
                agency="Agence IT",
                actif=True
            )
            db.add(secretary1)
            print("OK - Secretaire DSI creee: secretary1 (password: secretary123)")
        
        # Créer un Adjoint DSI
        existing_adjoint = db.query(models.User).filter(models.User.username == "adjoint1").first()
        if not existing_adjoint:
            adjoint1 = models.User(
                full_name="Thomas Leroy",
                email="thomas.leroy@example.com",
                username="adjoint1",
                password_hash=get_password_hash("adjoint123"),
                role_id=adjoint_role.id,
                agency="Agence IT",
                actif=True
            )
            db.add(adjoint1)
            print("OK - Adjoint DSI cree: adjoint1 (password: adjoint123)")
        
        # Créer un DSI
        existing_dsi = db.query(models.User).filter(models.User.username == "dsi1").first()
        if not existing_dsi:
            dsi1 = models.User(
                full_name="Michel Durand",
                email="michel.durand@example.com",
                username="dsi1",
                password_hash=get_password_hash("dsi123"),
                role_id=dsi_role.id,
                agency="Agence IT",
                actif=True
            )
            db.add(dsi1)
            print("OK - DSI cree: dsi1 (password: dsi123)")
        
        db.commit()
        print("\nUtilisateurs de test crees avec succes !")
        print("\nComptes disponibles:")
        print("  - user1 / user123 (Utilisateur)")
        print("  - tech1 / tech123 (Technicien)")
        print("  - tech2 / tech123 (Technicien)")
        print("  - secretary1 / secretary123 (Secretaire DSI)")
        print("  - adjoint1 / adjoint123 (Adjoint DSI)")
        print("  - dsi1 / dsi123 (DSI)")
        print("  - admin / admin123 (Admin)")
        
    except Exception as e:
        db.rollback()
        print(f"ERREUR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_users()

