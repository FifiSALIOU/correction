"""
Script de migration : remplace status (String) par actif (Boolean) dans la table users
"""
from sqlalchemy import text
from app.database import engine, SessionLocal
from app import models

def migrate_user_status_to_actif():
    """Migre la colonne status vers actif dans la table users"""
    db = SessionLocal()
    try:
        print("Debut de la migration users: status -> actif")
        print("-" * 50)
        
        # Vérifier si la colonne actif existe déjà
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name IN ('status', 'actif')
            """))
            columns = [row[0] for row in result]
            
            if 'actif' in columns:
                print("[OK] La colonne actif existe deja")
            else:
                print("[ERREUR] La colonne actif n'existe pas")
                print("  Veuillez d'abord executer les migrations SQLAlchemy pour creer la colonne")
                return
            
            if 'status' not in columns:
                print("[OK] La colonne status n'existe plus (deja migree)")
                print("Migration terminee - aucune action necessaire")
                return
        
        # Migrer les données
        with engine.connect() as conn:
            # Vérifier les utilisateurs à migrer
            result = conn.execute(text("""
                SELECT id, status 
                FROM users 
                WHERE status IS NOT NULL 
                AND (actif IS NULL OR actif = false)
            """))
            users_to_migrate = result.fetchall()
            
            if not users_to_migrate:
                print("[OK] Aucun utilisateur a migrer")
            else:
                print(f"\n{len(users_to_migrate)} utilisateur(s) a migrer:")
                
                for user_id, user_status in users_to_migrate:
                    # Convertir status en boolean
                    # "actif" ou "active" -> True, tout le reste -> False
                    status_lower = (user_status or "").lower()
                    actif_value = status_lower in ["actif", "active"]
                    
                    # Mettre à jour l'utilisateur
                    conn.execute(
                        text("""
                            UPDATE users 
                            SET actif = :actif_value 
                            WHERE id = :user_id
                        """),
                        {"actif_value": actif_value, "user_id": str(user_id)}
                    )
                    print(f"  [OK] User {user_id}: status='{user_status}' -> actif={actif_value}")
                
                conn.commit()
                print(f"\n[OK] {len(users_to_migrate)} utilisateur(s) migre(s) avec succes")
        
        # Rendre la colonne NOT NULL après migration
        print("\nRendre la colonne actif NOT NULL...")
        with engine.connect() as conn:
            # Vérifier qu'il n'y a pas de valeurs NULL
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM users 
                WHERE actif IS NULL
            """))
            null_count = result.scalar()
            
            if null_count > 0:
                print(f"[ATTENTION] {null_count} utilisateur(s) ont encore actif NULL")
                print("  Attribution de True par defaut")
                conn.execute(text("""
                    UPDATE users 
                    SET actif = true 
                    WHERE actif IS NULL
                """))
                conn.commit()
            
            # Rendre la colonne NOT NULL
            conn.execute(text("""
                ALTER TABLE users 
                ALTER COLUMN actif SET NOT NULL
            """))
            conn.commit()
            print("[OK] Colonne actif est maintenant NOT NULL")
        
        print("\n" + "-" * 50)
        print("[OK] Migration terminee avec succes !")
        
    except Exception as e:
        print(f"\n[ERREUR] Erreur lors de la migration: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_user_status_to_actif()

