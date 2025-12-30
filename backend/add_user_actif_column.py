"""
Script pour ajouter la colonne actif à la table users
et supprimer l'ancienne colonne status après migration
"""
from sqlalchemy import text
from app.database import engine, SessionLocal

def add_actif_column():
    """Ajoute la colonne actif à users"""
    try:
        print("Ajout de la colonne actif...")
        print("-" * 50)
        
        with engine.begin() as conn:
            # Vérifier si la colonne existe déjà
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name = 'actif'
            """))
            
            if result.fetchone():
                print("[OK] La colonne actif existe deja")
            else:
                # Ajouter la colonne actif (nullable d'abord pour permettre la migration)
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN actif BOOLEAN DEFAULT true
                """))
                print("[OK] Colonne actif ajoutee (nullable avec default true)")
        
        print("\n" + "-" * 50)
        print("[OK] Colonne actif creee avec succes !")
        print("\nProchaine etape: Executez migrate_user_status_to_actif.py pour migrer les donnees")
        
    except Exception as e:
        print(f"\n[ERREUR] {e}")
        import traceback
        traceback.print_exc()

def drop_status_column():
    """Supprime l'ancienne colonne status après migration"""
    try:
        print("Suppression de l'ancienne colonne status...")
        print("-" * 50)
        
        with engine.begin() as conn:
            # Vérifier si la colonne existe
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name = 'status'
            """))
            
            if not result.fetchone():
                print("[OK] La colonne status n'existe plus")
                return
            
            # Supprimer la colonne
            conn.execute(text("""
                ALTER TABLE users 
                DROP COLUMN status
            """))
            print("[OK] Colonne status supprimee")
        
        print("\n" + "-" * 50)
        print("[OK] Nettoyage termine avec succes !")
        
    except Exception as e:
        print(f"\n[ERREUR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "add":
            add_actif_column()
        elif action == "drop":
            drop_status_column()
        else:
            print("Usage:")
            print("  python add_user_actif_column.py add  - Ajoute la colonne actif")
            print("  python add_user_actif_column.py drop - Supprime l'ancienne colonne status")
    else:
        # Par défaut, ajouter la colonne
        add_actif_column()

