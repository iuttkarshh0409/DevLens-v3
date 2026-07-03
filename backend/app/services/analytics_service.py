import csv
import io
import math
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.models.analytics import (
    AuditHistoryRecord,
    RepositoryHealthRecord,
    RepositoryHealthView,
    TimeSeries,
    TrendPoint
)

class BaseAnalyticsStore(ABC):
    @abstractmethod
    def save_audit_record(self, record: AuditHistoryRecord) -> None:
        pass

    @abstractmethod
    def get_audit_records(self, repository_id: Optional[str] = None, installation_id: Optional[int] = None) -> List[AuditHistoryRecord]:
        pass

    @abstractmethod
    def delete_records_older_than(self, timestamp: datetime) -> int:
        pass

    @abstractmethod
    def delete_excess_records(self, repository_id: str, limit: int) -> int:
        pass

    @abstractmethod
    def save_health_record(self, record: RepositoryHealthRecord) -> None:
        pass

    @abstractmethod
    def get_health_records(self, installation_id: int) -> List[RepositoryHealthRecord]:
        pass


class InMemoryAnalyticsStore(BaseAnalyticsStore):
    def __init__(self):
        self.audit_records: List[AuditHistoryRecord] = []
        self.health_records: Dict[str, RepositoryHealthRecord] = {}

    def save_audit_record(self, record: AuditHistoryRecord) -> None:
        # Prevent double inserts
        self.audit_records = [r for r in self.audit_records if r.audit_id != record.audit_id]
        self.audit_records.append(record)
        # Sort chronologically
        self.audit_records.sort(key=lambda r: r.timestamp)

    def get_audit_records(self, repository_id: Optional[str] = None, installation_id: Optional[int] = None) -> List[AuditHistoryRecord]:
        records = self.audit_records
        if repository_id:
            records = [r for r in records if r.repository_id == repository_id]
        if installation_id:
            records = [r for r in records if r.installation_id == installation_id]
        return records

    def delete_records_older_than(self, timestamp: datetime) -> int:
        before_count = len(self.audit_records)
        self.audit_records = [r for r in self.audit_records if r.timestamp >= timestamp]
        return before_count - len(self.audit_records)

    def delete_excess_records(self, repository_id: str, limit: int) -> int:
        repo_records = [r for r in self.audit_records if r.repository_id == repository_id]
        if len(repo_records) <= limit:
            return 0
        
        # Identify the boundary timestamp
        repo_records.sort(key=lambda r: r.timestamp, reverse=True)
        keep_ids = {r.audit_id for r in repo_records[:limit]}
        
        before_count = len(self.audit_records)
        self.audit_records = [
            r for r in self.audit_records 
            if r.repository_id != repository_id or r.audit_id in keep_ids
        ]
        return before_count - len(self.audit_records)

    def save_health_record(self, record: RepositoryHealthRecord) -> None:
        self.health_records[record.repository_id] = record

    def get_health_records(self, installation_id: int) -> List[RepositoryHealthRecord]:
        # Filter installation matching (mocking using prefix check or simple mapping)
        return list(self.health_records.values())


class SQLAnalyticsStore(InMemoryAnalyticsStore):
    """Subclasses InMemoryAnalyticsStore to fulfill base interface for SQL databases."""
    pass


class TrendEngine:
    @staticmethod
    def calculate_trends(records: List[AuditHistoryRecord], interval: str, aggregation: str) -> TimeSeries:
        if not records:
            return TimeSeries(interval=interval, aggregation=aggregation, points=[])

        # Group records by interval date key
        groups: Dict[str, List[AuditHistoryRecord]] = {}
        for r in records:
            if interval == "hourly":
                date_key = r.timestamp.strftime("%Y-%m-%d %H:00")
            elif interval == "daily":
                date_key = r.timestamp.strftime("%Y-%m-%d")
            elif interval == "weekly":
                # Align to Monday of that week
                monday = r.timestamp - timedelta(days=r.timestamp.weekday())
                date_key = monday.strftime("%Y-%m-%d")
            else:  # monthly
                date_key = r.timestamp.strftime("%Y-%m-01")
            
            if date_key not in groups:
                groups[date_key] = []
            groups[date_key].append(r)

        points: List[TrendPoint] = []
        date_keys = sorted(groups.keys())

        # Rolling history container for rolling average calculation
        rolling_values: List[float] = []

        for date_str in date_keys:
            group_records = groups[date_str]
            scores = [r.score for r in group_records]
            pass_count = sum(1 for r in group_records if r.status == "success")
            fail_count = sum(1 for r in group_records if r.status == "failure")
            
            if interval == "hourly":
                timestamp = datetime.strptime(date_str, "%Y-%m-%d %H:00")
            else:
                timestamp = datetime.strptime(date_str, "%Y-%m-%d")

            # Basic aggregation calculations
            val = 0.0
            if aggregation == "average":
                val = sum(scores) / len(scores) if scores else 0.0
            elif aggregation == "sum":
                val = sum(scores)
            elif aggregation == "max":
                val = max(scores) if scores else 0.0
            elif aggregation == "median":
                sorted_scores = sorted(scores)
                n = len(sorted_scores)
                if n == 0:
                    val = 0.0
                elif n % 2 == 1:
                    val = sorted_scores[n // 2]
                else:
                    val = (sorted_scores[n // 2 - 1] + sorted_scores[n // 2]) / 2.0
            elif aggregation == "percentile":
                # 90th percentile implementation
                sorted_scores = sorted(scores)
                if sorted_scores:
                    idx = max(0, min(len(sorted_scores) - 1, int(len(sorted_scores) * 0.9)))
                    val = sorted_scores[idx]
                else:
                    val = 0.0
            elif aggregation == "rolling_average":
                # Computes standard simple average updated with historical rolling scores
                avg = sum(scores) / len(scores) if scores else 0.0
                rolling_values.append(avg)
                if len(rolling_values) > 5:  # Keep window size 5
                    rolling_values.pop(0)
                val = sum(rolling_values) / len(rolling_values)
            
            points.append(TrendPoint(
                timestamp=timestamp,
                value=round(val, 2),
                pass_count=pass_count,
                fail_count=fail_count
            ))

        return TimeSeries(interval=interval, aggregation=aggregation, points=points)


class ExportService:
    @staticmethod
    def generate_json_export(records: List[AuditHistoryRecord], installation_id: int, range_str: str) -> Dict[str, Any]:
        data = []
        for r in records:
            data.append({
                "audit_id": r.audit_id,
                "repository_id": r.repository_id,
                "repo_name": r.repo_name,
                "score": r.score,
                "status": r.status,
                "scoring_version": r.scoring_version,
                "devlens_version": r.devlens_version,
                "commit_sha": r.commit_sha,
                "branch": r.branch,
                "trigger_type": r.trigger_type,
                "warnings_count": r.warnings_count,
                "timestamp": r.timestamp.isoformat()
            })
        
        return {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "installation_id": installation_id,
            "range": range_str,
            "record_count": len(records),
            "data": data
        }

    @staticmethod
    def generate_csv_export(records: List[AuditHistoryRecord]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers matching schema requirements
        writer.writerow([
            "Audit ID", "Repository ID", "Repo Name", "Score", "Status", 
            "Scoring Version", "DevLens Version", "Commit SHA", "Branch", 
            "Trigger Type", "Warnings Count", "Timestamp"
        ])
        
        for r in records:
            writer.writerow([
                r.audit_id, r.repository_id, r.repo_name, r.score, r.status,
                r.scoring_version, r.devlens_version, r.commit_sha, r.branch,
                r.trigger_type, r.warnings_count, r.timestamp.isoformat()
            ])
            
        return output.getvalue()


class AnalyticsService:
    def __init__(self, store: BaseAnalyticsStore, retention_days: int = 180, retention_count: Optional[int] = None):
        self.store = store
        self.retention_days = retention_days
        self.retention_count = retention_count

    def process_audit_completion(self, record: AuditHistoryRecord) -> None:
        """Processes audit records and runs automatic retention expiries."""
        self.store.save_audit_record(record)
        
        # Enforce configurable retention policy
        if self.retention_days > 0:
            cutoff = datetime.utcnow() - timedelta(days=self.retention_days)
            self.store.delete_records_older_than(cutoff)
        
        if self.retention_count and self.retention_count > 0:
            self.store.delete_excess_records(record.repository_id, self.retention_count)
            
        # Re-calculate repository health summary
        self.update_repository_health(record.repository_id, record.installation_id)

    def update_repository_health(self, repository_id: str, installation_id: int) -> None:
        records = self.store.get_audit_records(repository_id=repository_id)
        if not records:
            return
            
        # Sort newest first
        records.sort(key=lambda r: r.timestamp, reverse=True)
        latest = records[0]
        
        # Determine score trend
        trend = "stable"
        if len(records) > 1:
            prev = records[1]
            if latest.score > prev.score:
                trend = "up"
            elif latest.score < prev.score:
                trend = "down"

        # Determine risk level
        risk_level = "low"
        if latest.score < 5.0 or latest.evidence.security_findings > 5:
            risk_level = "high"
        elif latest.score < 7.0 or latest.evidence.security_findings > 2:
            risk_level = "medium"

        # Map scores
        health = RepositoryHealthRecord(
            repository_id=repository_id,
            repo_name=latest.repo_name,
            health_score=latest.score,
            last_audit=latest.timestamp,
            trend=trend,
            risk_level=risk_level,
            critical_findings=latest.evidence.security_findings,
            documentation_score=latest.evidence.documentation_findings,
            security_score=latest.evidence.security_findings,
            testing_score=latest.evidence.testing_findings
        )
        self.store.save_health_record(health)

    def execute_nightly_rebuild(self, installation_id: int) -> None:
        """Idempotent nightly full rebuild that reconciles repository summaries and structures."""
        records = self.store.get_audit_records(installation_id=installation_id)
        repo_ids = {r.repository_id for r in records}
        for repo_id in repo_ids:
            self.update_repository_health(repo_id, installation_id)

    def get_dashboard_widgets(self, installation_id: int) -> Dict[str, Any]:
        """Assembles dashboard widget DTO structures."""
        healths = self.store.get_health_records(installation_id)
        
        # Widget 1: Score Distribution counts
        dist = {"high_quality": 0, "medium_quality": 0, "low_quality": 0}
        for h in healths:
            if h.health_score >= 8.5:
                dist["high_quality"] += 1
            elif h.health_score >= 6.5:
                dist["medium_quality"] += 1
            else:
                dist["low_quality"] += 1

        # Widget 2: Risk Repositories listings
        high_risk = [
            {"repo_name": h.repo_name, "score": h.health_score, "risk": h.risk_level}
            for h in healths if h.risk_level == "high"
        ]

        return {
            "score_distribution": dist,
            "highest_risk_repositories": high_risk,
            "total_repositories_monitored": len(healths)
        }
