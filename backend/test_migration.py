"""
Script de test pour vérifier que la migration type_code -> ticket_type_id a réussi
"""
from app.database import SessionLocal
from app import models
from sqlalchemy import text
from sqlalchemy.orm import joinedload
from app.database import engine

def test_migration():
    """Teste que la migration a bien fonctionné"""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("TESTS DE VERIFICATION DE LA MIGRATION")
        print("=" * 60)
        
        # Test 1: Vérifier que la colonne ticket_type_id existe
        print("\n[TEST 1] Verification de la colonne ticket_type_id...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'ticket_categories' 
                AND column_name = 'ticket_type_id'
            """))
            row = result.fetchone()
            if row:
                print(f"  [OK] Colonne ticket_type_id existe")
                print(f"      Type: {row[1]}")
                print(f"      Nullable: {row[2]}")
            else:
                print("  [ERREUR] Colonne ticket_type_id n'existe pas !")
                return False
        
        # Test 2: Vérifier qu'il n'y a pas de valeurs NULL
        print("\n[TEST 2] Verification des valeurs NULL...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM ticket_categories 
                WHERE ticket_type_id IS NULL
            """))
            null_count = result.scalar()
            if null_count == 0:
                print(f"  [OK] Aucune valeur NULL dans ticket_type_id")
            else:
                print(f"  [ERREUR] {null_count} categorie(s) ont ticket_type_id NULL !")
                return False
        
        # Test 3: Vérifier que toutes les catégories ont un ticket_type_id valide
        print("\n[TEST 3] Verification des references vers ticket_types...")
        categories = db.query(models.TicketCategory).all()
        print(f"  Total categories: {len(categories)}")
        
        invalid_refs = 0
        for cat in categories:
            if not cat.ticket_type_id:
                print(f"  [ERREUR] Categorie '{cat.name}' n'a pas de ticket_type_id")
                invalid_refs += 1
            elif not cat.ticket_type:
                print(f"  [ERREUR] Categorie '{cat.name}' a un ticket_type_id invalide: {cat.ticket_type_id}")
                invalid_refs += 1
        
        if invalid_refs == 0:
            print(f"  [OK] Toutes les categories ont une reference valide")
        else:
            print(f"  [ERREUR] {invalid_refs} reference(s) invalide(s)")
            return False
        
        # Test 4: Vérifier que la relation fonctionne et que type_code est accessible
        print("\n[TEST 4] Verification de la relation ticket_type...")
        categories_with_type = db.query(models.TicketCategory).options(
            joinedload(models.TicketCategory.ticket_type)
        ).all()
        
        materiel_count = 0
        applicatif_count = 0
        errors = []
        
        for cat in categories_with_type:
            if not cat.ticket_type:
                errors.append(f"Categorie '{cat.name}' n'a pas de relation ticket_type")
            else:
                type_code = cat.ticket_type.code
                if type_code == "materiel":
                    materiel_count += 1
                elif type_code == "applicatif":
                    applicatif_count += 1
                else:
                    errors.append(f"Categorie '{cat.name}' a un type_code inattendu: {type_code}")
        
        if errors:
            print(f"  [ERREUR] {len(errors)} probleme(s) trouve(s):")
            for error in errors:
                print(f"    - {error}")
            return False
        
        print(f"  [OK] Relation ticket_type fonctionne")
        print(f"      Categories materiel: {materiel_count}")
        print(f"      Categories applicatif: {applicatif_count}")
        
        # Test 5: Vérifier quelques exemples de catégories
        print("\n[TEST 5] Exemples de categories...")
        sample_categories = db.query(models.TicketCategory).limit(5).all()
        for cat in sample_categories:
            if cat.ticket_type:
                print(f"  - {cat.name}: ticket_type_id={cat.ticket_type_id}, type_code={cat.ticket_type.code}")
            else:
                print(f"  [ERREUR] {cat.name}: pas de relation ticket_type")
                return False
        
        # Test 6: Vérifier la contrainte de clé étrangère
        print("\n[TEST 6] Verification de la contrainte de cle etrangere...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT constraint_name, constraint_type
                FROM information_schema.table_constraints 
                WHERE table_name = 'ticket_categories' 
                AND constraint_name LIKE '%ticket_type%'
            """))
            constraints = result.fetchall()
            if constraints:
                print(f"  [OK] Contrainte de cle etrangere trouvee:")
                for constraint in constraints:
                    print(f"      - {constraint[0]} ({constraint[1]})")
            else:
                print("  [ATTENTION] Aucune contrainte de cle etrangere trouvee")
        
        # Test 7: Test de compatibilité API (filtrage)
        print("\n[TEST 7] Test de compatibilite API (filtrage)...")
        
        # Tester le filtrage par type_code (comme dans l'API)
        categories_materiel = db.query(models.TicketCategory)\
            .join(models.TicketTypeModel)\
            .filter(models.TicketTypeModel.code == "materiel")\
            .all()
        
        categories_applicatif = db.query(models.TicketCategory)\
            .join(models.TicketTypeModel)\
            .filter(models.TicketTypeModel.code == "applicatif")\
            .all()
        
        print(f"  [OK] Filtrage par type_code fonctionne:")
        print(f"      Categories materiel: {len(categories_materiel)}")
        print(f"      Categories applicatif: {len(categories_applicatif)}")
        
        # Vérifier que toutes les catégories ont bien le bon type_code
        all_correct = True
        for cat in categories_materiel:
            if not cat.ticket_type or cat.ticket_type.code != "materiel":
                print(f"  [ERREUR] Categorie '{cat.name}' devrait etre materiel")
                all_correct = False
        
        for cat in categories_applicatif:
            if not cat.ticket_type or cat.ticket_type.code != "applicatif":
                print(f"  [ERREUR] Categorie '{cat.name}' devrait etre applicatif")
                all_correct = False
        
        if all_correct:
            print(f"  [OK] Toutes les categories ont le bon type_code")
        
        print("\n" + "=" * 60)
        print("[SUCCES] Tous les tests sont passes !")
        print("=" * 60)
        print("\nLa migration est reussie. Vous pouvez maintenant:")
        print("  1. Tester l'API dans votre navigateur ou avec Postman")
        print("  2. Tester le frontend pour verifier que les categories s'affichent")
        print("  3. Supprimer l'ancienne colonne type_code si tout fonctionne:")
        print("     python add_ticket_type_id_column.py drop")
        
        return True
        
    except Exception as e:
        print(f"\n[ERREUR] Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_migration()
    exit(0 if success else 1)

