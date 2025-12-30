"""
Script de diagnostic pour vérifier les utilisateurs et leur capacité à se connecter
"""
from app.database import SessionLocal
from app import models
from app.security import verify_password

def diagnose_users():
    """Diagnostique les problèmes potentiels avec les utilisateurs"""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("DIAGNOSTIC DES UTILISATEURS")
        print("=" * 60)
        
        # Récupérer tous les utilisateurs
        users = db.query(models.User).all()
        
        if not users:
            print("\n❌ Aucun utilisateur trouvé dans la base de données")
            return
        
        print(f"\n📊 Nombre total d'utilisateurs: {len(users)}\n")
        
        problems = []
        ok_users = []
        
        for user in users:
            issues = []
            
            # Vérifier le statut
            if not user.actif:
                issues.append(f"❌ Utilisateur inactif (actif=False)")
            else:
                issues.append(f"✅ Utilisateur actif (actif=True)")
            
            # Vérifier le rôle
            if not user.role_id:
                issues.append("❌ Aucun rôle assigné")
            else:
                role = db.query(models.Role).filter(models.Role.id == user.role_id).first()
                if not role:
                    issues.append(f"❌ Rôle ID {user.role_id} n'existe pas")
                else:
                    issues.append(f"✅ Rôle: {role.name}")
            
            # Vérifier le mot de passe hash
            if not user.password_hash:
                issues.append("❌ Aucun hash de mot de passe")
            elif not user.password_hash.startswith('$2'):
                issues.append(f"❌ Format de hash invalide (ne commence pas par $2): {user.password_hash[:20]}...")
            else:
                issues.append("✅ Hash de mot de passe valide")
            
            # Vérifier le username
            if not user.username:
                issues.append("❌ Username vide")
            else:
                issues.append(f"✅ Username: {user.username}")
            
            print(f"\n👤 Utilisateur: {user.full_name} ({user.username})")
            print(f"   Email: {user.email}")
            for issue in issues:
                print(f"   {issue}")
            
            # Compter les problèmes
            problem_count = sum(1 for i in issues if i.startswith("❌"))
            if problem_count > 0:
                problems.append({
                    "user": user,
                    "issues": [i for i in issues if i.startswith("❌")]
                })
            else:
                ok_users.append(user)
        
        # Résumé
        print("\n" + "=" * 60)
        print("RÉSUMÉ")
        print("=" * 60)
        print(f"✅ Utilisateurs OK: {len(ok_users)}")
        print(f"❌ Utilisateurs avec problèmes: {len(problems)}")
        
        if problems:
            print("\n⚠️  UTILISATEURS AVEC PROBLÈMES:")
            for p in problems:
                print(f"\n   - {p['user'].username} ({p['user'].full_name})")
                for issue in p['issues']:
                    print(f"     {issue}")
        
        # Vérifier les rôles disponibles
        print("\n" + "=" * 60)
        print("RÔLES DISPONIBLES")
        print("=" * 60)
        roles = db.query(models.Role).all()
        if not roles:
            print("❌ Aucun rôle trouvé dans la base de données")
            print("   → Lancez init_db.py pour créer les rôles")
        else:
            for role in roles:
                user_count = db.query(models.User).filter(models.User.role_id == role.id).count()
                print(f"   - {role.name}: {user_count} utilisateur(s)")
        
        print("\n" + "=" * 60)
        print("RECOMMANDATIONS")
        print("=" * 60)
        
        if problems:
            print("\n1. Corrigez les problèmes listés ci-dessus")
            print("2. Pour les utilisateurs sans rôle, assignez un rôle valide")
            print("3. Pour les utilisateurs avec statut invalide, mettez à jour le statut à 'actif'")
            print("4. Pour les utilisateurs avec hash invalide, réinitialisez leur mot de passe")
        else:
            print("\n✅ Tous les utilisateurs semblent correctement configurés")
            print("   Si vous avez toujours des problèmes de connexion:")
            print("   1. Vérifiez que le backend est bien démarré")
            print("   2. Vérifiez les logs du backend pour plus de détails")
            print("   3. Testez avec un utilisateur admin (username: admin, password: admin123)")
        
    finally:
        db.close()

if __name__ == "__main__":
    diagnose_users()

