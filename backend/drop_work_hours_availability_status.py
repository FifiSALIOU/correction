"""
Script pour supprimer les colonnes work_hours et availability_status de la table users
"""
from sqlalchemy import text
from app.database import engine, SessionLocal

def drop_columns():
    """Supprime les colonnes work_hours et availability_status"""
    try:
        print("Suppression des colonnes work_hours et availability_status...")
        print("-" * 70)
        
        with engine.begin() as conn:
            # Vérifier si les colonnes existent
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name IN ('work_hours', 'availability_status')
            """))
            
            existing_columns = [row[0] for row in result]
            
            if not existing_columns:
                print("[OK] Les colonnes work_hours et availability_status n'existent plus")
                return
            
            # Supprimer work_hours si elle existe
            if 'work_hours' in existing_columns:
                conn.execute(text("ALTER TABLE users DROP COLUMN work_hours"))
                print("[OK] Colonne work_hours supprimee")
            else:
                print("[INFO] Colonne work_hours n'existe pas")
            
            # Supprimer availability_status si elle existe
            if 'availability_status' in existing_columns:
                conn.execute(text("ALTER TABLE users DROP COLUMN availability_status"))
                print("[OK] Colonne availability_status supprimee")
            else:
                print("[INFO] Colonne availability_status n'existe pas")
        
        print("\n" + "-" * 70)
        print("[OK] Nettoyage termine avec succes !")
        
    except Exception as e:
        print(f"\n[ERREUR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    drop_columns()

