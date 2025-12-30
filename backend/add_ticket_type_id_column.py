"""
Script pour ajouter la colonne ticket_type_id à la table ticket_categories
et supprimer l'ancienne colonne type_code après migration
"""
from sqlalchemy import text
from app.database import engine, SessionLocal
from app import models

def add_ticket_type_id_column():
    """Ajoute la colonne ticket_type_id à ticket_categories"""
    db = SessionLocal()
    try:
        print("Ajout de la colonne ticket_type_id...")
        print("-" * 50)
        
        with engine.begin() as conn:
            # Vérifier si la colonne existe déjà
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'ticket_categories' 
                AND column_name = 'ticket_type_id'
            """))
            
            if result.fetchone():
                print("[OK] La colonne ticket_type_id existe deja")
            else:
                # Ajouter la colonne ticket_type_id (nullable d'abord pour permettre la migration)
                conn.execute(text("""
                    ALTER TABLE ticket_categories 
                    ADD COLUMN ticket_type_id UUID
                """))
                print("[OK] Colonne ticket_type_id ajoutee (nullable)")
                
                # Ajouter la contrainte de clé étrangère
                conn.execute(text("""
                    ALTER TABLE ticket_categories 
                    ADD CONSTRAINT fk_ticket_categories_ticket_type 
                    FOREIGN KEY (ticket_type_id) 
                    REFERENCES ticket_types(id)
                """))
                print("[OK] Contrainte de cle etrangere ajoutee")
                
                # Rendre la colonne NOT NULL après migration des données
                # (on le fera après avoir migré les données)
        
        print("\n" + "-" * 50)
        print("[OK] Colonne ticket_type_id creee avec succes !")
        print("\nProchaine etape: Executez migrate_ticket_categories.py pour migrer les donnees")
        
    except Exception as e:
        print(f"\n[ERREUR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def make_ticket_type_id_not_null():
    """Rend la colonne ticket_type_id NOT NULL après migration des données"""
    try:
        print("Rendre ticket_type_id NOT NULL...")
        print("-" * 50)
        
        with engine.begin() as conn:
            # Vérifier qu'il n'y a pas de valeurs NULL
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM ticket_categories 
                WHERE ticket_type_id IS NULL
            """))
            null_count = result.scalar()
            
            if null_count > 0:
                print(f"[ATTENTION] {null_count} categorie(s) ont encore ticket_type_id NULL")
                print("  Veuillez d'abord executer migrate_ticket_categories.py")
                return
            
            # Rendre la colonne NOT NULL
            conn.execute(text("""
                ALTER TABLE ticket_categories 
                ALTER COLUMN ticket_type_id SET NOT NULL
            """))
            print("[OK] Colonne ticket_type_id est maintenant NOT NULL")
        
        print("\n" + "-" * 50)
        print("[OK] Migration terminee avec succes !")
        
    except Exception as e:
        print(f"\n[ERREUR] {e}")
        import traceback
        traceback.print_exc()

def drop_type_code_column():
    """Supprime l'ancienne colonne type_code après migration"""
    try:
        print("Suppression de l'ancienne colonne type_code...")
        print("-" * 50)
        
        with engine.begin() as conn:
            # Vérifier si la colonne existe
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'ticket_categories' 
                AND column_name = 'type_code'
            """))
            
            if not result.fetchone():
                print("[OK] La colonne type_code n'existe plus")
                return
            
            # Supprimer la colonne
            conn.execute(text("""
                ALTER TABLE ticket_categories 
                DROP COLUMN type_code
            """))
            print("[OK] Colonne type_code supprimee")
        
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
            add_ticket_type_id_column()
        elif action == "not-null":
            make_ticket_type_id_not_null()
        elif action == "drop":
            drop_type_code_column()
        else:
            print("Usage:")
            print("  python add_ticket_type_id_column.py add      - Ajoute la colonne ticket_type_id")
            print("  python add_ticket_type_id_column.py not-null - Rend ticket_type_id NOT NULL")
            print("  python add_ticket_type_id_column.py drop    - Supprime l'ancienne colonne type_code")
    else:
        # Par défaut, ajouter la colonne
        add_ticket_type_id_column()

