from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime, timedelta
from typing import Optional, List
import json
from . import models


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        action: str,
        entity_type: str,
        entity_id: int,
        operator: str,
        details: Optional[str] = None,
        old_value: Optional[dict] = None,
        new_value: Optional[dict] = None
    ) -> models.AuditLog:
        audit_log = models.AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            operator=operator,
            details=details,
            old_value=json.dumps(old_value, ensure_ascii=False) if old_value else None,
            new_value=json.dumps(new_value, ensure_ascii=False) if new_value else None
        )
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        return audit_log

    def get_by_entity(
        self,
        entity_type: str,
        entity_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[models.AuditLog], int]:
        query = self.db.query(models.AuditLog).filter(
            and_(
                models.AuditLog.entity_type == entity_type,
                models.AuditLog.entity_id == entity_id
            )
        )
        total = query.count()
        logs = query.order_by(desc(models.AuditLog.operation_time)) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()
        return logs, total

    def get_all(
        self,
        action: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[models.AuditLog], int]:
        query = self.db.query(models.AuditLog)
        
        if action:
            query = query.filter(models.AuditLog.action == action)
        if start_time:
            query = query.filter(models.AuditLog.operation_time >= start_time)
        if end_time:
            query = query.filter(models.AuditLog.operation_time <= end_time)
        
        total = query.count()
        logs = query.order_by(desc(models.AuditLog.operation_time)) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()
        return logs, total


class HotTopicRepository:
    def __init__(self, db: Session):
        self.db = db
        self.audit_repo = AuditLogRepository(db)

    def create(self, platform: str, title: str, hot_value: float, rank: int, url: str, crawl_time: datetime, summary: str = "") -> models.HotTopic:
        hot_topic = models.HotTopic(
            platform=platform,
            title=title,
            hot_value=hot_value,
            rank=rank,
            url=url,
            crawl_time=crawl_time,
            summary=summary
        )
        self.db.add(hot_topic)
        self.db.commit()
        self.db.refresh(hot_topic)
        return hot_topic

    def get_by_platform_and_title(self, platform: str, title: str, crawl_time: datetime) -> Optional[models.HotTopic]:
        """查找相同平台和标题的记录"""
        start_of_day = crawl_time.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        return self.db.query(models.HotTopic).filter(
            and_(
                models.HotTopic.platform == platform,
                models.HotTopic.title == title,
                models.HotTopic.crawl_time >= start_of_day,
                models.HotTopic.crawl_time < end_of_day
            )
        ).first()

    def exists_by_platform_and_title(self, platform: str, title: str, crawl_time: datetime) -> bool:
        """检查相同平台和标题的记录是否已在同一天存在"""
        return self.get_by_platform_and_title(platform, title, crawl_time) is not None

    def update_or_create(self, topic: dict) -> bool:
        """更新或创建热点记录，返回是否是新创建的"""
        existing = self.get_by_platform_and_title(
            topic['platform'],
            topic['title'],
            topic['crawl_time']
        )
        
        if existing:
            # 更新现有记录
            existing.hot_value = topic.get('hot_value', existing.hot_value)
            existing.rank = topic.get('rank', existing.rank)
            existing.url = topic.get('url', existing.url)
            existing.summary = topic.get('summary', existing.summary)
            existing.crawl_time = topic['crawl_time']  # 更新爬取时间
            self.db.commit()
            return False
        else:
            # 创建新记录
            hot_topic = models.HotTopic(**topic)
            self.db.add(hot_topic)
            self.db.commit()
            return True

    def bulk_create(self, topics: List[dict]) -> int:
        if not topics:
            return 0
            
        count = 0
        updated = 0
        
        # 按平台分组处理，提高效率
        from collections import defaultdict
        topics_by_platform = defaultdict(list)
        for topic in topics:
            topics_by_platform[topic['platform']].append(topic)
        
        # 对每个平台，先查询当天已存在的记录
        crawl_time = topics[0]['crawl_time']
        start_of_day = crawl_time.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        for platform, platform_topics in topics_by_platform.items():
            # 先查询该平台当天的所有记录
            existing_records = self.db.query(models.HotTopic).filter(
                and_(
                    models.HotTopic.platform == platform,
                    models.HotTopic.crawl_time >= start_of_day,
                    models.HotTopic.crawl_time < end_of_day
                )
            ).all()
            
            # 构建标题到记录的映射
            title_to_record = {record.title: record for record in existing_records}
            
            # 处理该平台的话题
            for topic in platform_topics:
                if topic['title'] in title_to_record:
                    # 更新现有记录
                    existing = title_to_record[topic['title']]
                    existing.hot_value = topic.get('hot_value', existing.hot_value)
                    existing.rank = topic.get('rank', existing.rank)
                    existing.url = topic.get('url', existing.url)
                    existing.summary = topic.get('summary', existing.summary)
                    existing.crawl_time = topic['crawl_time']
                    updated += 1
                else:
                    # 创建新记录
                    hot_topic = models.HotTopic(**topic)
                    self.db.add(hot_topic)
                    count += 1
        
        self.db.commit()
        
        if updated > 0 or count > 0:
            from logger import get_logger
            logger = get_logger(__name__)
            if updated > 0 and count > 0:
                logger.info(f"更新了 {updated} 条已存在的热点数据，新增 {count} 条")
            elif updated > 0:
                logger.info(f"更新了 {updated} 条已存在的热点数据")
            else:
                logger.info(f"新增了 {count} 条热点数据")
        
        return count

    def get_by_platform_and_date(
        self,
        platform: Optional[str] = None,
        date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
        include_deleted: bool = False
    ) -> tuple[List[models.HotTopic], int]:
        query = self.db.query(models.HotTopic)

        if platform:
            query = query.filter(models.HotTopic.platform == platform)

        if date:
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            query = query.filter(
                and_(
                    models.HotTopic.crawl_time >= start_of_day,
                    models.HotTopic.crawl_time < end_of_day
                )
            )
        
        if not include_deleted:
            query = query.filter(models.HotTopic.is_deleted == False)

        total = query.count()

        topics = query.order_by(desc(models.HotTopic.hot_value)) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()

        return topics, total

    def get_deleted(
        self,
        platform: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[models.HotTopic], int]:
        query = self.db.query(models.HotTopic).filter(models.HotTopic.is_deleted == True)

        if platform:
            query = query.filter(models.HotTopic.platform == platform)

        if start_date:
            query = query.filter(models.HotTopic.deleted_at >= start_date)
        if end_date:
            query = query.filter(models.HotTopic.deleted_at <= end_date)

        total = query.count()

        topics = query.order_by(desc(models.HotTopic.deleted_at)) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()

        return topics, total

    def soft_delete(self, id: int, operator: str = "system") -> Optional[models.HotTopic]:
        topic = self.get_by_id(id)
        if not topic:
            return None
        
        old_value = topic.to_dict()
        
        topic.is_deleted = True
        topic.deleted_at = datetime.utcnow()
        topic.deleted_by = operator
        
        self.db.commit()
        self.db.refresh(topic)
        
        # 记录审计日志
        new_value = topic.to_dict()
        self.audit_repo.create(
            action="DELETE",
            entity_type="HotTopic",
            entity_id=id,
            operator=operator,
            details=f"删除热点：{topic.title}",
            old_value=old_value,
            new_value=new_value
        )
        
        return topic

    def restore(self, id: int, operator: str = "system") -> Optional[models.HotTopic]:
        topic = self.db.query(models.HotTopic).filter(models.HotTopic.id == id).first()
        if not topic or not topic.is_deleted:
            return None
        
        old_value = topic.to_dict()
        
        topic.is_deleted = False
        deleted_at = topic.deleted_at
        topic.deleted_at = None
        topic.deleted_by = None
        
        self.db.commit()
        self.db.refresh(topic)
        
        # 记录审计日志
        new_value = topic.to_dict()
        self.audit_repo.create(
            action="RESTORE",
            entity_type="HotTopic",
            entity_id=id,
            operator=operator,
            details=f"恢复热点：{topic.title}（原删除时间：{deleted_at}）",
            old_value=old_value,
            new_value=new_value
        )
        
        return topic

    def batch_soft_delete(self, ids: List[int], operator: str = "system") -> int:
        """批量逻辑删除"""
        topics = self.db.query(models.HotTopic).filter(
            and_(
                models.HotTopic.id.in_(ids),
                models.HotTopic.is_deleted == False
            )
        ).all()
        
        count = 0
        for topic in topics:
            old_value = topic.to_dict()
            
            topic.is_deleted = True
            topic.deleted_at = datetime.utcnow()
            topic.deleted_by = operator
            
            # 记录审计日志
            new_value = topic.to_dict()
            self.audit_repo.create(
                action="DELETE",
                entity_type="HotTopic",
                entity_id=topic.id,
                operator=operator,
                details=f"批量删除热点：{topic.title}",
                old_value=old_value,
                new_value=new_value
            )
            count += 1
        
        self.db.commit()
        return count

    def batch_restore(self, ids: List[int], operator: str = "system") -> int:
        """批量恢复"""
        topics = self.db.query(models.HotTopic).filter(
            and_(
                models.HotTopic.id.in_(ids),
                models.HotTopic.is_deleted == True
            )
        ).all()
        
        count = 0
        for topic in topics:
            old_value = topic.to_dict()
            
            topic.is_deleted = False
            deleted_at = topic.deleted_at
            topic.deleted_at = None
            topic.deleted_by = None
            
            # 记录审计日志
            new_value = topic.to_dict()
            self.audit_repo.create(
                action="RESTORE",
                entity_type="HotTopic",
                entity_id=topic.id,
                operator=operator,
                details=f"批量恢复热点：{topic.title}（原删除时间：{deleted_at}）",
                old_value=old_value,
                new_value=new_value
            )
            count += 1
        
        self.db.commit()
        return count

    def batch_purge(self, ids: List[int], operator: str = "system") -> int:
        """批量物理删除（清空）"""
        topics = self.db.query(models.HotTopic).filter(
            and_(
                models.HotTopic.id.in_(ids),
                models.HotTopic.is_deleted == True
            )
        ).all()
        
        count = 0
        for topic in topics:
            # 记录审计日志
            old_value = topic.to_dict()
            self.audit_repo.create(
                action="PURGE",
                entity_type="HotTopic",
                entity_id=topic.id,
                operator=operator,
                details=f"永久删除热点：{topic.title}",
                old_value=old_value,
                new_value=None
            )
            self.db.delete(topic)
            count += 1
        
        self.db.commit()
        return count

    def purge_all_deleted(self, operator: str = "system") -> int:
        """清空所有已删除的热点"""
        topics = self.db.query(models.HotTopic).filter(
            models.HotTopic.is_deleted == True
        ).all()
        
        count = 0
        for topic in topics:
            # 记录审计日志
            old_value = topic.to_dict()
            self.audit_repo.create(
                action="PURGE",
                entity_type="HotTopic",
                entity_id=topic.id,
                operator=operator,
                details=f"永久删除热点：{topic.title}",
                old_value=old_value,
                new_value=None
            )
            self.db.delete(topic)
            count += 1
        
        self.db.commit()
        return count

    def get_by_id(self, topic_id: int) -> Optional[models.HotTopic]:
        return self.db.query(models.HotTopic).filter(models.HotTopic.id == topic_id).first()

    def search(self, keyword: str, page: int = 1, page_size: int = 20) -> tuple[List[models.HotTopic], int]:
        query = self.db.query(models.HotTopic).filter(
            models.HotTopic.title.like(f"%{keyword}%")
        )
        total = query.count()
        topics = query.order_by(desc(models.HotTopic.crawl_time)) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()
        return topics, total

    def delete_old_data(self, days: int = 7) -> int:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        count = self.db.query(models.HotTopic).filter(
            models.HotTopic.crawl_time < cutoff_date
        ).delete()
        self.db.commit()
        return count

    def delete_by_id(self, topic_id: int, operator: str = "system") -> bool:
        # 使用逻辑删除替代物理删除
        topic = self.soft_delete(topic_id, operator)
        return topic is not None

    def delete_by_platform(self, platform: str, operator: str = "system") -> int:
        # 逻辑删除指定平台的所有数据
        topics = self.db.query(models.HotTopic).filter(
            and_(
                models.HotTopic.platform == platform,
                models.HotTopic.is_deleted == False
            )
        ).all()
        
        count = 0
        for topic in topics:
            if self.soft_delete(topic.id, operator):
                count += 1
        return count

    def has_today_data(self, platform: str) -> bool:
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        count = self.db.query(models.HotTopic).filter(
            and_(
                models.HotTopic.platform == platform,
                models.HotTopic.crawl_time >= today_start,
                models.HotTopic.crawl_time < today_end,
                models.HotTopic.is_deleted == False
            )
        ).count()
        return count > 0


class CrawlLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, platform: str, status: str = "running") -> models.CrawlLog:
        log = models.CrawlLog(
            platform=platform,
            status=status,
            started_at=datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def update(self, log_id: int, status: str, count: int = 0, error_message: Optional[str] = None):
        log = self.db.query(models.CrawlLog).filter(models.CrawlLog.id == log_id).first()
        if log:
            log.status = status
            log.count = count
            log.error_message = error_message
            log.finished_at = datetime.utcnow()
            self.db.commit()

    def get_recent_logs(self, limit: int = 50) -> List[models.CrawlLog]:
        return self.db.query(models.CrawlLog) \
            .order_by(desc(models.CrawlLog.started_at)) \
            .limit(limit) \
            .all()

    def get_stats(self) -> dict:
        total_topics = self.db.query(models.HotTopic).filter(models.HotTopic.is_deleted == False).count()
        deleted_count = self.db.query(models.HotTopic).filter(models.HotTopic.is_deleted == True).count()
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_topics = self.db.query(models.HotTopic).filter(
            and_(
                models.HotTopic.crawl_time >= today,
                models.HotTopic.is_deleted == False
            )
        ).count()

        platform_counts = {}
        platforms = ["weibo", "douyin", "zhihu", "toutiao"]
        for platform in platforms:
            count = self.db.query(models.HotTopic).filter(
                and_(
                    models.HotTopic.platform == platform,
                    models.HotTopic.is_deleted == False
                )
            ).count()
            platform_counts[platform] = count

        recent_logs = self.db.query(models.CrawlLog).order_by(
            desc(models.CrawlLog.started_at)
        ).limit(10).all()

        return {
            "total_topics": total_topics,
            "deleted_count": deleted_count,
            "today_topics": today_topics,
            "platform_counts": platform_counts,
            "recent_logs": [log.to_dict() for log in recent_logs]
        }