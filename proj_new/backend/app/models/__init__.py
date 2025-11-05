"""
Models Package - Import all models
"""
from app.models.user import User, UserRole
from app.models.shelter import Shelter
from app.models.animal import Animal, AnimalImage, Species, Sex, AnimalStatus
from app.models.application import Application, ApplicationType, ApplicationStatus
from app.models.medical_record import MedicalRecord, RecordType
from app.models.others import Notification, Job, JobType, JobStatus, Attachment, AuditLog
from app.models.pending_registration import PendingRegistration

__all__ = [
    'User',
    'UserRole',
    'Shelter',
    'Animal',
    'AnimalImage',
    'Species',
    'Sex',
    'AnimalStatus',
    'Application',
    'ApplicationType',
    'ApplicationStatus',
    'MedicalRecord',
    'RecordType',
    'Notification',
    'Job',
    'JobType',
    'JobStatus',
    'Attachment',
    'AuditLog',
    'PendingRegistration',
]
