from typing import Any, Dict, List

import requests
from fastapi import UploadFile

from .config import settings


class FileStorageClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def submit_file(
            self,
            student_id: str,
            student_name: str,
            assignment_id: str,
            file: UploadFile,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/files/submit"

        file_bytes = file.file.read()
        files = {
            "file": (file.filename, file_bytes, file.content_type or "application/octet-stream"),
        }
        data = {
            "student_id": student_id,
            "student_name": student_name,
            "assignment_id": assignment_id,
        }

        response = requests.post(url, data=data, files=files, timeout=10)
        response.raise_for_status()
        return response.json()


class FileAnalysisClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def analyze_submission(
            self,
            submission_id: int,
            assignment_id: str,
            student_id: str,
            file_download_url: str,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/internal/analyze"
        payload = {
            "submission_id": submission_id,
            "assignment_id": assignment_id,
            "student_id": student_id,
            "file_download_url": file_download_url,
        }
        response = requests.post(url, json=payload, timeout=20)
        response.raise_for_status()
        return response.json()

    def get_reports_by_assignment(self, assignment_id: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/reports/assignment/{assignment_id}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()


file_storage_client = FileStorageClient(settings.FILE_SERVICE_URL)
file_analysis_client = FileAnalysisClient(settings.ANALYSIS_SERVICE_URL)
