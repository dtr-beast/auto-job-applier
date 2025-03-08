from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, SQLModel


class SubmittedJob(SQLModel, table=True):
    __tablename__ = "submitted_job"
    job_id: str = Field(primary_key=True)
    title: str
    company: str
    company_link: str
    work_location: str
    work_style: str
    description: str
    experience_required: Optional[int]
    skills: Optional[List[str]]
    hr_name: Optional[str]
    hr_link: Optional[str]
    resume: str
    reposted: bool
    date_listed: Optional[datetime]
    date_applied: Optional[datetime]
    job_link: str
    application_link: str
    questions_list: Optional[Set[str]]
    connect_request: Optional[str]
    is_mail_sent: bool = Field(default=False)