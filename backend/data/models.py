from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from datetime import datetime
from .database import Base


class HotTopic(Base):
    __tablename__ = "hot_topics"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(20), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    hot_value = Column(Float, nullable=False, index=True)
    rank = Column(Integer, nullable=False)
    url = Column(String(1000), nullable=True)
    summary = Column(Text, nullable=True)
    crawl_time = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 逻辑删除字段
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(String(100), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "platform": self.platform,
            "title": self.title,
            "hot_value": self.hot_value,
            "rank": self.rank,
            "url": self.url,
            "summary": self.summary,
            "crawl_time": self.crawl_time.isoformat() if self.crawl_time else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
            "deleted_by": self.deleted_by,
        }


class CrawlLog(Base):
    __tablename__ = "crawl_logs"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)
    count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "platform": self.platform,
            "status": self.status,
            "count": self.count,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
        }


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(50), nullable=False, index=True)  # DELETE, RESTORE
    entity_type = Column(String(50), nullable=False)  # HotTopic
    entity_id = Column(Integer, nullable=False, index=True)
    operator = Column(String(100), nullable=False)
    operation_time = Column(DateTime, default=datetime.utcnow, index=True)
    details = Column(Text, nullable=True)
    
    # 旧值快照（JSON格式存储）
    old_value = Column(Text, nullable=True)
    # 新值快照（JSON格式存储）
    new_value = Column(Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "operator": self.operator,
            "operation_time": self.operation_time.isoformat() if self.operation_time else None,
            "details": self.details,
            "old_value": self.old_value,
            "new_value": self.new_value,
        }