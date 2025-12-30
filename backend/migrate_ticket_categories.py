"""
Script de migration : remplace type_code par ticket_type_id dans ticket_categories
Ce script convertit les catégories existantes qui utilisent type_code (String) 
vers ticket_type_id (ForeignKey vers ticket_types)
"""
from sqlalchemy import text
from app.database import engine, SessionLocal
from app import models

def migrate_ticket_categories():
    """Migre les catégories de tickets de type_code vers ticket_type_id"""
    db = SessionLocal()
    try:
        print("Début de la migration ticket_categories...")
        print("-" * 50)
        
        # Vérifier si la colonne type_code existe encore
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'ticket_categories' 
                AND column_name IN ('type_code', 'ticket_type_id')
            """))
            columns = [row[0] for row in result]
            
            if 'ticket_type_id' in columns:
                print("[OK] La colonne ticket_type_id existe deja")
            else:
                print("[ERREUR] La colonne ticket_type_id n'existe pas")
                print("  Veuillez d'abord executer: python add_ticket_type_id_column.py add")
                return
            
            if 'type_code' not in columns:
                print("[OK] La colonne type_code n'existe plus (deja migree)")
                print("Migration terminee - aucune action necessaire")
                return
        
        # Récupérer les types de tickets
        materiel_type = db.query(models.TicketTypeModel).filter(models.TicketTypeModel.code == "materiel").first()
        applicatif_type = db.query(models.TicketTypeModel).filter(models.TicketTypeModel.code == "applicatif").first()
        
        if not materiel_type:
            print("✗ ERREUR: Le type 'materiel' n'existe pas dans ticket_types")
            return
        if not applicatif_type:
            print("✗ ERREUR: Le type 'applicatif' n'existe pas dans ticket_types")
            return
        
        print(f"[OK] Types trouves:")
        print(f"  - materiel: {materiel_type.id}")
        print(f"  - applicatif: {applicatif_type.id}")
        
        # Récupérer les catégories qui ont encore type_code mais pas ticket_type_id
        with engine.connect() as conn:
            # Vérifier les catégories à migrer
            result = conn.execute(text("""
                SELECT id, name, type_code 
                FROM ticket_categories 
                WHERE type_code IS NOT NULL 
                AND (ticket_type_id IS NULL OR ticket_type_id = '00000000-0000-0000-0000-000000000000'::uuid)
            """))
            categories_to_migrate = result.fetchall()
            
            if not categories_to_migrate:
                print("[OK] Aucune categorie a migrer")
            else:
                print(f"\n{len(categories_to_migrate)} categorie(s) a migrer:")
                
                for cat_id, cat_name, type_code in categories_to_migrate:
                    # Déterminer l'ID du type
                    if type_code == "materiel":
                        type_id = materiel_type.id
                    elif type_code == "applicatif":
                        type_id = applicatif_type.id
                    else:
                        print(f"  [ATTENTION] Categorie '{cat_name}' a un type_code inconnu: {type_code}")
                        print(f"     Assignation par defaut a 'materiel'")
                        type_id = materiel_type.id
                    
                    # Mettre à jour la catégorie
                    conn.execute(
                        text("""
                            UPDATE ticket_categories 
                            SET ticket_type_id = :type_id 
                            WHERE id = :cat_id
                        """),
                        {"type_id": str(type_id), "cat_id": str(cat_id)}
                    )
                    print(f"  [OK] '{cat_name}' ({type_code}) -> ticket_type_id: {type_id}")
                
                conn.commit()
                print(f"\n[OK] {len(categories_to_migrate)} categorie(s) migree(s) avec succes")
        
        # Optionnel: Supprimer la colonne type_code après migration
        # Décommentez les lignes suivantes si vous voulez supprimer type_code
        # print("\nSuppression de la colonne type_code...")
        # with engine.connect() as conn:
        #     conn.execute(text("ALTER TABLE ticket_categories DROP COLUMN IF EXISTS type_code"))
        #     conn.commit()
        # print("✓ Colonne type_code supprimée")
        
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
    migrate_ticket_categories()

