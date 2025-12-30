import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    permissions = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    agency = Column(String(100), nullable=True)  # Agence au lieu de département
    phone = Column(String(30), nullable=True)
    profile_photo_url = Column(String(255), nullable=True)
    actif = Column(Boolean, default=True)
    specialization = Column(String(50), nullable=True)  # Spécialisation : "materiel" ou "applicatif"
    max_tickets_capacity = Column(Integer, nullable=True)  # Capacité max de tickets simultanés
    notes = Column(Text, nullable=True)  # Notes optionnelles
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)

    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    role = relationship("Role", back_populates="users")

    created_tickets = relationship(
        "Ticket", back_populates="creator", foreign_keys="Ticket.creator_id"
    )
    assigned_tickets = relationship(
        "Ticket", back_populates="technician", foreign_keys="Ticket.technician_id"
    )


from enum import Enum as PyEnum


class TicketType(str, PyEnum):
    MATERIEL = "materiel"
    APPLICATIF = "applicatif"


class TicketPriority(str, PyEnum):
    FAIBLE = "faible"
    MOYENNE = "moyenne"
    HAUTE = "haute"
    CRITIQUE = "critique"


class TicketStatus(str, PyEnum):
    EN_ATTENTE_ANALYSE = "en_attente_analyse"
    ASSIGNE_TECHNICIEN = "assigne_technicien"
    EN_COURS = "en_cours"
    RESOLU = "resolu"
    REJETE = "rejete"
    CLOTURE = "cloture"


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    number = Column(Integer, autoincrement=True, unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    type = Column(Enum(TicketType), nullable=False)
    priority = Column(Enum(TicketPriority), nullable=False, default=TicketPriority.MOYENNE)
    status = Column(Enum(TicketStatus), nullable=False, default=TicketStatus.EN_ATTENTE_ANALYSE)
    category = Column(String(100), nullable=True)  # Catégorie du ticket (ex: Réseau, Logiciel, Matériel, etc.)

    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    technician_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    secretary_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    user_agency = Column(String(100), nullable=True)  # Agence de l'utilisateur créateur

    created_at = Column(DateTime, default=datetime.utcnow)
    assigned_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    auto_closed_at = Column(DateTime, nullable=True)  # Date de clôture automatique (si applicable)

    attachments = Column(JSONB, nullable=True)
    feedback_score = Column(Integer, nullable=True)
    feedback_comment = Column(Text, nullable=True)

    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_tickets")
    technician = relationship("User", foreign_keys=[technician_id], back_populates="assigned_tickets")

    comments = relationship("Comment", back_populates="ticket", cascade="all, delete-orphan")
    history = relationship("TicketHistory", back_populates="ticket", cascade="all, delete-orphan")


class CommentType(str, PyEnum):
    TECHNIQUE = "technique"
    UTILISATEUR = "utilisateur"
    SYSTEME = "systeme"


class Comment(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    type = Column(Enum(CommentType), nullable=False, default=CommentType.TECHNIQUE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    attachments = Column(JSONB, nullable=True)

    ticket = relationship("Ticket", back_populates="comments")
    user = relationship("User")


class TicketHistory(Base):
    __tablename__ = "ticket_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False)
    old_status = Column(Enum(TicketStatus), nullable=True)
    new_status = Column(Enum(TicketStatus), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reason = Column(Text, nullable=True)
    changed_at = Column(DateTime, default=datetime.utcnow)

    ticket = relationship("Ticket", back_populates="history")
    user = relationship("User")


class TicketTypeModel(Base):
    """
    Table de configuration pour les types de tickets.
    Elle permet de gérer les types dans la base sans impacter la logique existante basée sur l'enum TicketType.
    """
    __tablename__ = "ticket_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False)  # ex: "materiel", "applicatif"
    label = Column(String(100), nullable=False)  # ex: "Matériel", "Applicatif"
    is_active = Column(Boolean, default=True)


class TicketCategory(Base):
    """
    Table de configuration pour les catégories de tickets.
    Les tickets continuent de stocker le nom de la catégorie en texte libre via Ticket.category,
    mais cette table permet de centraliser et d'étendre facilement la liste des catégories.
    """
    __tablename__ = "ticket_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    ticket_type_id = Column(UUID(as_uuid=True), ForeignKey("ticket_types.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relation vers TicketTypeModel
    ticket_type = relationship("TicketTypeModel", backref="categories")


class NotificationType(str, PyEnum):
    # Notifications utilisateur
    TICKET_CREE = "ticket_créé"
    TICKET_ASSIGNE = "ticket_assigné"
    COMMENTAIRE = "commentaire"
    TICKET_RESOLU = "ticket_résolu"
    DEMANDE_VALIDATION = "demande_validation"
    TICKET_CLOTURE = "ticket_clôturé"
    RAPPEL = "rappel"
    TICKET_EN_COURS = "ticket_en_cours"
    TICKET_REJETE = "ticket_rejeté"
    PRIORITE_MODIFIEE = "priorité_modifiée"
    TECHNICIEN_CHANGE = "technicien_change"
    TICKET_REOUVERT = "ticket_réouvert"
    CLOTURE_AUTOMATIQUE = "clôture_automatique"
    RAPPEL_VALIDATION_1 = "rappel_validation_1"
    RAPPEL_VALIDATION_2 = "rappel_validation_2"
    RAPPEL_VALIDATION_3 = "rappel_validation_3"
    ESCALADE_USER = "escalade_user"
    
    # Notifications secrétaire/adjoint
    NOUVEAU_TICKET = "nouveau_ticket"
    TICKET_EN_ATTENTE = "ticket_en_attente"
    TECHNICIEN_INDISPONIBLE = "technicien_indisponible"
    ESCALADE = "escalade"
    SATISFACTION = "satisfaction"
    
    # Notifications technicien
    ASSIGNATION = "assignation"
    REASSIGNATION = "reassignation"
    REJET_RESOLUTION = "rejet_résolution"
    DEMANDE_INFO = "demande_info"
    
    # Notifications DSI
    RAPPORT_PERFORMANCE = "rapport_performance"
    PROBLEME_RECURRENT = "problème_récurrent"
    SATISFACTION_FAIBLE = "satisfaction_faible"
    
    # Notifications générales
    RESOLUTION = "resolution"
    CLOTURE = "cloture"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=True)
    message = Column(Text, nullable=False)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    report_type = Column(String(50), nullable=False)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    data = Column(JSONB, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)


