from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import asyncio
from datetime import datetime

from data.database import get_db
from data.repository import CrawlLogRepository, HotTopicRepository, AuditLogRepository
from scheduler.jobs import crawl_platform

router = APIRouter()

VALID_PLATFORMS = ["weibo", "douyin", "zhihu", "toutiao"]


@router.post("/crawl/trigger")
async def trigger_crawl(
    platform: Optional[str] = None,
    force: bool = False,
    db: Session = Depends(get_db)
):
    if platform and platform not in VALID_PLATFORMS:
        raise HTTPException(
            status_code=400,
            detail=f"平台必须是 {', '.join(VALID_PLATFORMS)} 之一"
        )

    topic_repo = HotTopicRepository(db)

    if platform:
        if not force and topic_repo.has_today_data(platform):
            return {
                "message": f"{platform} 今日已爬取过数据，如需强制爬取请添加 ?force=true",
                "platform": platform,
                "status": "skipped"
            }
        asyncio.create_task(crawl_platform(platform, db))
        return {"message": f"已触发 {platform} 爬取任务", "platform": platform, "status": "started"}
    else:
        skipped = []
        started = []

        for p in VALID_PLATFORMS:
            if not force and topic_repo.has_today_data(p):
                skipped.append(p)
            else:
                asyncio.create_task(crawl_platform(p, db))
                started.append(p)

        message = []
        if started:
            message.append(f"已触发 {', '.join(started)} 爬取任务")
        if skipped:
            message.append(f"{', '.join(skipped)} 今日已爬取过（如需强制爬取请添加 ?force=true）")

        return {"message": "；".join(message), "started": started, "skipped": skipped}


@router.get("/platforms")
async def get_platforms():
    platforms = [
        {"id": "weibo", "name": "微博", "icon": "sina"},
        {"id": "douyin", "name": "抖音", "icon": "video"},
        {"id": "zhihu", "name": "知乎", "icon": "question"},
        {"id": "toutiao", "name": "今日头条", "icon": "document"},
    ]
    return {"platforms": platforms}


@router.get("/crawl/logs")
async def get_crawl_logs(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    repo = CrawlLogRepository(db)
    logs = repo.get_recent_logs(limit)
    return {"items": [log.to_dict() for log in logs]}


@router.get("/audit-logs")
async def get_audit_logs(
    action: Optional[str] = Query(None, description="操作类型: DELETE/RESTORE"),
    start_date: Optional[str] = Query(None, description="开始日期: YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期: YYYY-MM-DD"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    repo = AuditLogRepository(db)
    
    filter_start = None
    filter_end = None
    
    if start_date:
        try:
            filter_start = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="开始日期格式错误，请使用YYYY-MM-DD")
    
    if end_date:
        try:
            filter_end = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="结束日期格式错误，请使用YYYY-MM-DD")
    
    logs, total = repo.get_all(
        action=action,
        start_date=filter_start,
        end_date=filter_end,
        page=page,
        page_size=page_size
    )
    
    return {
        "items": [log.to_dict() for log in logs],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    repo = CrawlLogRepository(db)
    stats = repo.get_stats()
    return stats


@router.delete("/cleanup")
async def cleanup_old_data(
    days: int = 7,
    db: Session = Depends(get_db)
):
    repo = HotTopicRepository(db)
    count = repo.delete_old_data(days)
    return {"message": f"已删除 {days} 天前的数据", "deleted_count": count}