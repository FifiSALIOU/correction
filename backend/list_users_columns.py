"""
Script pour lister les colonnes de la table users
"""
from sqlalchemy import text
from app.database import engine, SessionLocal

def list_users_columns():
    """Liste toutes les colonnes de la table users"""
    try:
        print("=" * 70)
        print("COLONNES DE LA TABLE users")
        print("=" * 70)
        
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length
                FROM information_schema.columns
                WHERE table_name = 'users'
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            
            if not columns:
                print("Aucune colonne trouvee")
                return
            
            print(f"\nTotal: {len(columns)} colonne(s)\n")
            
            for col in columns:
                col_name = col[0]
                data_type = col[1]
                is_nullable = col[2]
                default = col[3]
                max_length = col[4]
                
                # Formater le type
                type_str = data_type
                if max_length:
                    type_str = f"{data_type}({max_length})"
                
                # Formater nullable
                nullable_str = "NULL" if is_nullable == "YES" else "NOT NULL"
                
                # Formater default
                default_str = f" DEFAULT {default}" if default else ""
                
                print(f"  - {col_name}")
                print(f"    Type: {type_str}")
                print(f"    Nullable: {nullable_str}")
                if default:
                    print(f"    Default: {default}")
                print()
        
        print("=" * 70)
        
        # Vérifier spécifiquement actif et status
        print("\nVerification specifique:")
        with engine.connect() as conn:
            # Vérifier actif
            result_actif = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'actif'
            """))
            has_actif = result_actif.fetchone() is not None
            
            # Vérifier status
            result_status = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'status'
            """))
            has_status = result_status.fetchone() is not None
            
            if has_actif:
                print("  [OK] Colonne 'actif' existe")
            else:
                print("  [ERREUR] Colonne 'actif' n'existe pas")
            
            if has_status:
                print("  [ATTENTION] Colonne 'status' existe encore")
            else:
                print("  [OK] Colonne 'status' n'existe plus (supprimee)")
        
        print("=" * 70)
        
    except Exception as e:
        print(f"[ERREUR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    list_users_columns()

