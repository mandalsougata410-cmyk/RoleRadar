from typing import List, Optional
try:
    from pydantic import BaseModel, Field
except ImportError:
    # Graceful fallback when running in vanilla python environment
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def dict(self):
            return self.__dict__
    def Field(default=None, description=""):
        return default

class UserIntentFilter(BaseModel):
    def __init__(self, role=None, skills=None, location=None, remote_only=None, min_stipend=None):
        self.role = role
        self.skills = skills or []
        self.location = location
        self.remote_only = remote_only
        self.min_stipend = min_stipend

class ChatRequest(BaseModel):
    user_id: str = "student_user_1"
    message: str = ""

class ChatResponse(BaseModel):
    reply: str = ""
    tools_called: List[str] = []
    matched_jobs: List[dict] = []
    user_profile: dict = {}

class InteractionRequest(BaseModel):
    user_id: str = ""
    job_id: int = 0
    action: str = "" # 'viewed', 'saved', 'dismissed', 'applied'

