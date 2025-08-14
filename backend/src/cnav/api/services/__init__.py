from cnav.database.connection import get_sync_session, init_sync_database

# Initialize database on module import
init_sync_database()

class DatabaseService:
    """Base class for database services with session management"""
    
    def get_db_session(self):
        """Get a database session using the connection manager"""
        return get_sync_session()

from .question_service import QuestionService
from .organization_service import OrganizationService
from .provision_service import ProvisionService
from .mapping_service import MappingService
from .self_assessment_answer_service import SelfAssessmentAnswerService

__all__ = [
    "QuestionService",
    "OrganizationService",
    "ProvisionService", 
    "MappingService",
    "SelfAssessmentAnswerService",
]