from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer

from .database import Base

class Submission(Base):
    __tablename__ = 'submission'

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, index=True, nullable=False)
    student_name = Column(String, nullable=False)
    assignment_id = Column(Integer, index=True, nullable=False)
    filename = Column(String, nullable=False)
    file_id = Column(Integer, unique=True, nullable=False, index=True)
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)