from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean

from .database import Base


class Report(Base):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, index=True, nullable=False)
    assignment_id = Column(Integer, index=True, nullable=False)
    student_id = Column(Integer, index=True, nullable=False)
    content_hash = Column(String, index=True, nullable=False)
    is_plagiarism = Column(Boolean, default=False, nullable=False)
    plagiarism_source_submission_id = Column(Integer, nullable=True)
    wordcloud_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
