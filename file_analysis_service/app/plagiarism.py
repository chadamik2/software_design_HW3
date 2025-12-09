from typing import Optional, Tuple
from sqlalchemy.orm import Session

from .models import Report


def check_plagiarism(
        db: Session,
        assignment_id: str,
        student_id: str,
        content_hash: str,
) -> Tuple[bool, Optional[int]]:
    reports = (db.query(Report).filter(Report.assignment_id == assignment_id, Report.content_hash == content_hash)
               .order_by(Report.created_at.asc())
               .all()
               )
    other_students_reports = [r for r in reports if r.student_id != student_id]

    if other_students_reports:
        source = other_students_reports[0]
        return True, source.submission_id
    return False, None
