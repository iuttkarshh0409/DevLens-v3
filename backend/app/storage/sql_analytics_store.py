from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

# Local imports
from app.models.analytics import (
    AuditHistoryRecord,
    RepositoryHealthRecord,
    EvidenceSummary
)
from app.database.models import AuditHistoryModel, RepositoryHealthModel
from app.services.analytics_service import BaseAnalyticsStore

class SQLAnalyticsStore(BaseAnalyticsStore):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def save_audit_record(self, record: AuditHistoryRecord) -> None:
        async with self.session_factory() as session:
            async with session.begin():
                existing = await session.get(AuditHistoryModel, record.audit_id)
                evidence_dict = record.evidence.dict()
                
                if existing:
                    existing.repository_id = record.repository_id
                    existing.repo_name = record.repo_name
                    existing.installation_id = record.installation_id
                    existing.score = record.score
                    existing.status = record.status
                    existing.scoring_version = record.scoring_version
                    existing.devlens_version = record.devlens_version
                    existing.commit_sha = record.commit_sha
                    existing.branch = record.branch
                    existing.audit_duration_ms = record.audit_duration_ms
                    existing.trigger_type = record.trigger_type
                    existing.warnings_count = record.warnings_count
                    existing.timestamp = record.timestamp
                    existing.evidence = evidence_dict
                else:
                    db_record = AuditHistoryModel(
                        audit_id=record.audit_id,
                        repository_id=record.repository_id,
                        repo_name=record.repo_name,
                        installation_id=record.installation_id,
                        score=record.score,
                        status=record.status,
                        scoring_version=record.scoring_version,
                        devlens_version=record.devlens_version,
                        commit_sha=record.commit_sha,
                        branch=record.branch,
                        audit_duration_ms=record.audit_duration_ms,
                        trigger_type=record.trigger_type,
                        warnings_count=record.warnings_count,
                        timestamp=record.timestamp,
                        evidence=evidence_dict
                    )
                    session.add(db_record)

    async def get_audit_records(self, repository_id: Optional[str] = None, installation_id: Optional[int] = None) -> List[AuditHistoryRecord]:
        async with self.session_factory() as session:
            stmt = select(AuditHistoryModel)
            if repository_id:
                stmt = stmt.where(AuditHistoryModel.repository_id == repository_id)
            if installation_id:
                stmt = stmt.where(AuditHistoryModel.installation_id == installation_id)
            stmt = stmt.order_by(AuditHistoryModel.timestamp)
            
            result = await session.execute(stmt)
            db_records = result.scalars().all()
            
            return [
                AuditHistoryRecord(
                    audit_id=r.audit_id,
                    repository_id=r.repository_id,
                    repo_name=r.repo_name,
                    installation_id=r.installation_id,
                    score=r.score,
                    status=r.status,
                    scoring_version=r.scoring_version,
                    devlens_version=r.devlens_version,
                    commit_sha=r.commit_sha,
                    branch=r.branch,
                    audit_duration_ms=r.audit_duration_ms,
                    trigger_type=r.trigger_type,
                    warnings_count=r.warnings_count,
                    timestamp=r.timestamp,
                    evidence=EvidenceSummary(**r.evidence)
                )
                for r in db_records
            ]

    async def delete_records_older_than(self, timestamp: datetime) -> int:
        async with self.session_factory() as session:
            async with session.begin():
                stmt = delete(AuditHistoryModel).where(AuditHistoryModel.timestamp < timestamp)
                result = await session.execute(stmt)
                return result.rowcount

    async def delete_excess_records(self, repository_id: str, limit: int) -> int:
        async with self.session_factory() as session:
            async with session.begin():
                stmt = (
                    select(AuditHistoryModel)
                    .where(AuditHistoryModel.repository_id == repository_id)
                    .order_by(desc(AuditHistoryModel.timestamp))
                )
                result = await session.execute(stmt)
                records = result.scalars().all()
                
                if len(records) <= limit:
                    return 0
                    
                delete_ids = [r.audit_id for r in records[limit:]]
                
                del_stmt = delete(AuditHistoryModel).where(AuditHistoryModel.audit_id.in_(delete_ids))
                del_result = await session.execute(del_stmt)
                return del_result.rowcount

    async def save_health_record(self, record: RepositoryHealthRecord) -> None:
        async with self.session_factory() as session:
            async with session.begin():
                existing = await session.get(RepositoryHealthModel, record.repository_id)
                if existing:
                    existing.repo_name = record.repo_name
                    existing.health_score = record.health_score
                    existing.last_audit = record.last_audit
                    existing.trend = record.trend
                    existing.risk_level = record.risk_level
                    existing.critical_findings = record.critical_findings
                    existing.documentation_score = record.documentation_score
                    existing.security_score = record.security_score
                    existing.testing_score = record.testing_score
                else:
                    db_health = RepositoryHealthModel(
                        repository_id=record.repository_id,
                        repo_name=record.repo_name,
                        health_score=record.health_score,
                        last_audit=record.last_audit,
                        trend=record.trend,
                        risk_level=record.risk_level,
                        critical_findings=record.critical_findings,
                        documentation_score=record.documentation_score,
                        security_score=record.security_score,
                        testing_score=record.testing_score
                    )
                    session.add(db_health)

    async def get_health_records(self, installation_id: int) -> List[RepositoryHealthRecord]:
        async with self.session_factory() as session:
            stmt = select(RepositoryHealthModel)
            result = await session.execute(stmt)
            db_records = result.scalars().all()
            
            return [
                RepositoryHealthRecord(
                    repository_id=r.repository_id,
                    repo_name=r.repo_name,
                    health_score=r.health_score,
                    last_audit=r.last_audit,
                    trend=r.trend,
                    risk_level=r.risk_level,
                    critical_findings=r.critical_findings,
                    documentation_score=r.documentation_score,
                    security_score=r.security_score,
                    testing_score=r.testing_score
                )
                for r in db_records
            ]
