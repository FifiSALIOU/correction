from typing import List
from uuid import UUID
import secrets
import string
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..security import get_current_user, require_role, get_password_hash

router = APIRouter()


class TechnicianWithWorkload(schemas.UserRead):
    """Schéma étendu pour inclure la charge de travail"""
    assigned_tickets_count: int = 0
    in_progress_tickets_count: int = 0

    class Config:
        from_attributes = True


@router.get("/technicians", response_model=List[schemas.UserRead])
def list_technicians(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_role("Secrétaire DSI", "Adjoint DSI", "DSI", "Admin")
    ),
):
    """Liste tous les techniciens avec leur charge de travail pour l'assignation de tickets"""
    technician_role = db.query(models.Role).filter(models.Role.name == "Technicien").first()
    if not technician_role:
        return []
    
    technicians = (
        db.query(models.User)
        .filter(
            models.User.role_id == technician_role.id,
            models.User.actif == True
        )
        .all()
    )
    
    # Ajouter la charge de travail pour chaque technicien
    result = []
    for tech in technicians:
        assigned_count = (
            db.query(models.Ticket)
            .filter(
                models.Ticket.technician_id == tech.id,
                models.Ticket.status.in_([
                    models.TicketStatus.ASSIGNE_TECHNICIEN,
                    models.TicketStatus.EN_COURS
                ])
            )
            .count()
        )
        in_progress_count = (
            db.query(models.Ticket)
            .filter(
                models.Ticket.technician_id == tech.id,
                models.Ticket.status == models.TicketStatus.EN_COURS
            )
            .count()
        )
        
        tech_dict = {
            "id": tech.id,
            "full_name": tech.full_name,
            "email": tech.email,
            "agency": tech.agency,
            "phone": tech.phone,
            "role": {
                "id": tech.role.id,
                "name": tech.role.name,
                "description": tech.role.description,
            },
            "actif": tech.actif,
            "specialization": tech.specialization,
            "assigned_tickets_count": assigned_count,
            "in_progress_tickets_count": in_progress_count,
        }
        result.append(tech_dict)
    
    return result


@router.get("/technicians/{technician_id}/stats")
def get_technician_stats(
    technician_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_role("Secrétaire DSI", "Adjoint DSI", "DSI", "Admin")
    ),
):
    """Récupère les statistiques détaillées d'un technicien"""
    technician = db.query(models.User).filter(
        models.User.id == technician_id,
        models.User.role.has(models.Role.name == "Technicien")
    ).first()
    
    if not technician:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Technicien not found"
        )
    
    # Tickets résolus
    resolved_tickets = (
        db.query(models.Ticket)
        .filter(
            models.Ticket.technician_id == technician_id,
            models.Ticket.status == models.TicketStatus.RESOLU
        )
        .all()
    )
    
    # Tickets clôturés
    closed_tickets = (
        db.query(models.Ticket)
        .filter(
            models.Ticket.technician_id == technician_id,
            models.Ticket.status == models.TicketStatus.CLOTURE
        )
        .all()
    )
    
    # Calculer le temps moyen de résolution (en jours)
    total_resolution_time = 0
    resolved_count = 0
    for ticket in resolved_tickets + closed_tickets:
        if ticket.assigned_at and ticket.resolved_at:
            time_diff = (ticket.resolved_at - ticket.assigned_at).total_seconds() / 86400  # Convertir en jours
            total_resolution_time += time_diff
            resolved_count += 1
    
    avg_resolution_time = round(total_resolution_time / resolved_count, 1) if resolved_count > 0 else 0
    
    # Taux de réussite (tickets clôturés / tickets assignés)
    total_assigned = (
        db.query(models.Ticket)
        .filter(models.Ticket.technician_id == technician_id)
        .count()
    )
    
    success_rate = round((len(closed_tickets) / total_assigned * 100), 1) if total_assigned > 0 else 0
    
    # Tickets résolus ce mois
    first_day_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    resolved_this_month = (
        db.query(models.Ticket)
        .filter(
            models.Ticket.technician_id == technician_id,
            models.Ticket.status.in_([models.TicketStatus.RESOLU, models.TicketStatus.CLOTURE]),
            models.Ticket.resolved_at.isnot(None),
            models.Ticket.resolved_at >= first_day_of_month
        )
        .count()
    )
    
    # Compter les tickets en cours pour les statistiques
    in_progress_count = (
        db.query(models.Ticket)
        .filter(
            models.Ticket.technician_id == technician_id,
            models.Ticket.status == models.TicketStatus.EN_COURS
        )
        .count()
    )
    
    # Disponibilité basée uniquement sur actif (True/False)
    is_available = technician.actif
    
    # Calculer le temps de réponse moyen (temps entre assignation et première action du technicien)
    # Le temps de réponse = temps entre assigned_at et le moment où le ticket passe à "en_cours"
    total_response_time = 0
    response_count = 0
    
    for ticket in resolved_tickets + closed_tickets:
        if ticket.assigned_at:
            # Chercher dans l'historique le moment où le ticket est passé à "en_cours"
            first_en_cours_history = (
                db.query(models.TicketHistory)
                .filter(
                    models.TicketHistory.ticket_id == ticket.id,
                    models.TicketHistory.new_status == models.TicketStatus.EN_COURS
                )
                .order_by(models.TicketHistory.changed_at.asc())
                .first()
            )
            
            if first_en_cours_history:
                # Temps de réponse = temps entre assignation et première prise en charge
                time_diff = (first_en_cours_history.changed_at - ticket.assigned_at).total_seconds() / 60  # Convertir en minutes
                if time_diff >= 0:  # S'assurer que le temps est positif
                    total_response_time += time_diff
                    response_count += 1
            # Si pas d'historique "en_cours" mais que le ticket est résolu/clôturé,
            # on peut utiliser resolved_at comme approximation (mais moins précis)
            elif ticket.resolved_at and ticket.assigned_at:
                # Utiliser le temps jusqu'à la résolution comme approximation
                time_diff = (ticket.resolved_at - ticket.assigned_at).total_seconds() / 60
                if time_diff >= 0:
                    total_response_time += time_diff
                    response_count += 1
    
    avg_response_time_minutes = round(total_response_time / response_count, 0) if response_count > 0 else 0
    
    # Calculer la charge de travail (basée sur les tickets en cours, max 5)
    max_workload = 5
    current_workload = min(in_progress_count, max_workload)
    workload_ratio = f"{current_workload}/{max_workload}"
    
    # Tickets résolus aujourd'hui
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    resolved_today = (
        db.query(models.Ticket)
        .filter(
            models.Ticket.technician_id == technician_id,
            models.Ticket.status.in_([models.TicketStatus.RESOLU, models.TicketStatus.CLOTURE]),
            models.Ticket.resolved_at.isnot(None),
            models.Ticket.resolved_at >= today_start
        )
        .count()
    )
    
    return {
        "id": str(technician.id),
        "full_name": technician.full_name,
        "email": technician.email,
        "phone": technician.phone,
        "agency": technician.agency,
        "specialization": technician.specialization,
        "actif": technician.actif,
        "last_login_at": technician.last_login_at.isoformat() if technician.last_login_at else None,
        "assigned_tickets_count": total_assigned,
        "in_progress_tickets_count": in_progress_count,
        "resolved_tickets_count": len(resolved_tickets),
        "closed_tickets_count": len(closed_tickets),
        "resolved_this_month": resolved_this_month,
        "resolved_today": resolved_today,
        "avg_resolution_time_days": avg_resolution_time,
        "avg_response_time_minutes": avg_response_time_minutes,
        "success_rate": success_rate,
        # Disponibilité basée uniquement sur actif (True/False)
        "is_available": is_available,
        "workload_ratio": workload_ratio
    }


@router.post("/", response_model=schemas.UserRead)
def create_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("DSI", "Admin")),
):
    """Créer un nouvel utilisateur (Admin uniquement)"""
    # Vérifier si l'email ou le username existe déjà
    existing = (
        db.query(models.User)
        .filter(
            (models.User.email == user_in.email)
            | (models.User.username == user_in.username)
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with same email or username already exists",
        )
    
    # Vérifier que le rôle existe
    role = db.query(models.Role).filter(models.Role.id == user_in.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    db_user = models.User(
        full_name=user_in.full_name,
        email=user_in.email,
        agency=user_in.agency,
        phone=user_in.phone,
        username=user_in.username,
        password_hash=get_password_hash(user_in.password),
        role_id=user_in.role_id,
        specialization=user_in.specialization,
        max_tickets_capacity=user_in.max_tickets_capacity,
        notes=user_in.notes,
        actif=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Charger le rôle pour la réponse
    db_user.role = role
    
    return db_user


@router.get("/", response_model=List[schemas.UserRead])
def list_all_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("DSI", "Admin")),
):
    """Liste tous les utilisateurs (Admin uniquement)"""
    users = db.query(models.User).all()
    
    result = []
    for user in users:
        user_dict = {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "agency": user.agency,
            "phone": user.phone,
            "role": {
                "id": user.role.id,
                "name": user.role.name,
                "description": user.role.description
            },
            "actif": user.actif,
            "specialization": user.specialization
        }
        result.append(user_dict)
    
    return result


@router.get("/{user_id}", response_model=schemas.UserRead)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("DSI", "Admin")),
):
    """Récupérer un utilisateur par son ID"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=schemas.UserRead)
def update_user(
    user_id: UUID,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("DSI", "Admin")),
):
    """Modifier un utilisateur"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Vérifier si l'email est déjà utilisé par un autre utilisateur
    if user_update.email and user_update.email != user.email:
        existing_user = db.query(models.User).filter(
            models.User.email == user_update.email,
            models.User.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
    
    # Mettre à jour les champs fournis
    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.agency is not None:
        user.agency = user_update.agency
    if user_update.phone is not None:
        user.phone = user_update.phone
    if user_update.actif is not None:
        user.actif = user_update.actif
    if user_update.specialization is not None:
        user.specialization = user_update.specialization
    if user_update.max_tickets_capacity is not None:
        user.max_tickets_capacity = user_update.max_tickets_capacity
    if user_update.notes is not None:
        user.notes = user_update.notes
    if user_update.role_id is not None:
        # Vérifier que le rôle existe
        role = db.query(models.Role).filter(models.Role.id == user_update.role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        user.role_id = user_update.role_id
    
    db.commit()
    db.refresh(user)
    
    # Charger le rôle pour la réponse
    user.role = db.query(models.Role).filter(models.Role.id == user.role_id).first()
    
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("DSI", "Admin")),
):
    """Supprimer un utilisateur"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Ne pas permettre la suppression de soi-même
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Vérifier si l'utilisateur a des tickets créés ou assignés
    created_tickets = db.query(models.Ticket).filter(models.Ticket.creator_id == user_id).count()
    assigned_tickets = db.query(models.Ticket).filter(models.Ticket.technician_id == user_id).count()
    
    if created_tickets > 0 or assigned_tickets > 0:
        # Au lieu de supprimer, désactiver l'utilisateur
        user.actif = False
        db.commit()
        return {"message": "User deactivated (has associated tickets)", "user_id": str(user_id)}
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully", "user_id": str(user_id)}


@router.post("/{user_id}/reset-password")
def reset_user_password(
    user_id: UUID,
    password_reset: schemas.PasswordReset,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("DSI", "Admin")),
):
    """Réinitialiser le mot de passe d'un utilisateur"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Générer un mot de passe aléatoire si non fourni
    if password_reset.new_password:
        new_password = password_reset.new_password
    else:
        # Générer un mot de passe aléatoire de 12 caractères
        alphabet = string.ascii_letters + string.digits
        new_password = ''.join(secrets.choice(alphabet) for i in range(12))
    
    # Hasher et sauvegarder le nouveau mot de passe
    user.password_hash = get_password_hash(new_password)
    db.commit()
    
    return {
        "message": "Password reset successfully",
        "user_id": str(user_id),
        "new_password": new_password  # Retourner le mot de passe pour l'affichage (à ne faire qu'en développement)
    }

