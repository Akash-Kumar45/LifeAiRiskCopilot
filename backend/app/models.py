from typing import Optional, List
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship


class AIModelBase(SQLModel):
    name: str
    version: str
    status: Optional[str] = "draft"
    description: Optional[str] = None
    repo_link: Optional[str] = None


class AIModel(AIModelBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    control_mappings: List["ControlMapping"] = Relationship(back_populates="model")


class ControlMapping(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    model_id: Optional[int] = Field(default=None, foreign_key="aimodel.id")
    osfi_control_id: str
    rationale: Optional[str] = None
    status: Optional[str] = "proposed"
    model: Optional[AIModel] = Relationship(back_populates="control_mappings")
    evidences: List["Evidence"] = Relationship(back_populates="control_mapping")


class Evidence(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    control_mapping_id: Optional[int] = Field(default=None, foreign_key="controlmapping.id")
    file_hash: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    content_summary: Optional[str] = None
    control_mapping: Optional[ControlMapping] = Relationship(back_populates="evidences")
