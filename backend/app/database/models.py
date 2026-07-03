from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Index
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class AuditHistoryModel(Base):
    __tablename__ = "audit_history"
    
    audit_id = Column(String, primary_key=True)
    repository_id = Column(String, nullable=False)
    repo_name = Column(String, nullable=False)
    installation_id = Column(Integer, nullable=False)
    score = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    scoring_version = Column(String, nullable=False)
    devlens_version = Column(String, nullable=False)
    commit_sha = Column(String, nullable=False)
    branch = Column(String, nullable=False)
    audit_duration_ms = Column(Integer, nullable=False)
    trigger_type = Column(String, nullable=False)
    warnings_count = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    evidence = Column(JSON, nullable=False)

    __table_args__ = (
        Index("idx_installation_timestamp", "installation_id", "timestamp"),
        Index("idx_repository_timestamp", "repository_id", "timestamp"),
    )


class RepositoryHealthModel(Base):
    __tablename__ = "repository_health"
    
    repository_id = Column(String, primary_key=True)
    repo_name = Column(String, nullable=False)
    health_score = Column(Float, nullable=False)
    last_audit = Column(DateTime, nullable=False)
    trend = Column(String, nullable=False)
    risk_level = Column(String, nullable=False)
    critical_findings = Column(Integer, nullable=False)
    documentation_score = Column(Float, nullable=False)
    security_score = Column(Float, nullable=False)
    testing_score = Column(Float, nullable=False)
