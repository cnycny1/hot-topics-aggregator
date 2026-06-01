from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from data.database import get_db
from data.repository import HotTopicRepository, AuditLogRepository

router = APIRouter()


def get_operator(user_agent: Optional[str] = Header(None)) -> str:
    """获取操作者信息"""
    return user_agent or "anonymous"


@router.get("/hot-topics")
async def get_hot_topics(
    platform: Optional[str] = Query(None, description="平台筛选: weibo/douyin"),
    date: Optional[str] = Query(None, description="日期筛选: YYYY-MM-DD"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    repo = HotTopicRepository(db)

    filter_date = None
    if date:
        try:
            filter_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误，请使用YYYY-MM-DD")

    topics, total = repo.get_by_platform_and_date(
        platform=platform,
        date=filter_date,
        page=page,
        page_size=page_size
    )

    return {
        "items": [topic.to_dict() for topic in topics],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get("/hot-topics/deleted")
async def get_deleted_hot_topics(
    platform: Optional[str] = Query(None, description="平台筛选: weibo/douyin"),
    start_date: Optional[str] = Query(None, description="开始日期: YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期: YYYY-MM-DD"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    repo = HotTopicRepository(db)

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

    topics, total = repo.get_deleted(
        platform=platform,
        start_date=filter_start,
        end_date=filter_end,
        page=page,
        page_size=page_size
    )

    return {
        "items": [topic.to_dict() for topic in topics],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get("/hot-topics/{topic_id}")
async def get_hot_topic(
    topic_id: int,
    db: Session = Depends(get_db)
):
    repo = HotTopicRepository(db)
    topic = repo.get_by_id(topic_id)

    if not topic:
        raise HTTPException(status_code=404, detail="热点不存在")

    return topic.to_dict()


@router.get("/hot-topics/search")
async def search_hot_topics(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    repo = HotTopicRepository(db)
    topics, total = repo.search(keyword, page, page_size)

    return {
        "items": [topic.to_dict() for topic in topics],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.delete("/hot-topics/{topic_id}")
async def delete_hot_topic(
    topic_id: int,
    operator: str = Depends(get_operator),
    db: Session = Depends(get_db)
):
    repo = HotTopicRepository(db)
    topic = repo.soft_delete(topic_id, operator)
    
    if not topic:
        raise HTTPException(status_code=404, detail="热点不存在或已被删除")
    
    return {"message": "删除成功", "deleted_id": topic_id}


@router.post("/hot-topics/{topic_id}/restore")
async def restore_hot_topic(
    topic_id: int,
    operator: str = Depends(get_operator),
    db: Session = Depends(get_db)
):
    repo = HotTopicRepository(db)
    topic = repo.restore(topic_id, operator)
    
    if not topic:
        raise HTTPException(status_code=404, detail="热点不存在或未被删除")
    
    return {"message": "恢复成功", "restored_id": topic_id}


@router.post("/hot-topics/batch-delete")
async def batch_delete_hot_topics(
    data: dict,
    operator: str = Depends(get_operator),
    db: Session = Depends(get_db)
):
    """批量删除热点"""
    ids = data.get("ids", [])
    if not ids:
        raise HTTPException(status_code=400, detail="请选择要删除的热点")
    
    repo = HotTopicRepository(db)
    deleted_count = repo.batch_soft_delete(ids, operator)
    
    return {"message": f"成功删除 {deleted_count} 条热点", "deleted_count": deleted_count}


@router.post("/hot-topics/batch-restore")
async def batch_restore_hot_topics(
    data: dict,
    operator: str = Depends(get_operator),
    db: Session = Depends(get_db)
):
    """批量恢复热点"""
    ids = data.get("ids", [])
    if not ids:
        raise HTTPException(status_code=400, detail="请选择要恢复的热点")
    
    repo = HotTopicRepository(db)
    restored_count = repo.batch_restore(ids, operator)
    
    return {"message": f"成功恢复 {restored_count} 条热点", "restored_count": restored_count}


@router.post("/hot-topics/batch-purge")
async def batch_purge_hot_topics(
    data: dict,
    operator: str = Depends(get_operator),
    db: Session = Depends(get_db)
):
    """批量永久删除（清空）选中的已删除热点"""
    ids = data.get("ids", [])
    if not ids:
        raise HTTPException(status_code=400, detail="请选择要清空的热点")
    
    repo = HotTopicRepository(db)
    purged_count = repo.batch_purge(ids, operator)
    
    return {"message": f"成功永久删除 {purged_count} 条热点", "purged_count": purged_count}


@router.post("/hot-topics/purge-all")
async def purge_all_deleted_hot_topics(
    operator: str = Depends(get_operator),
    db: Session = Depends(get_db)
):
    """清空所有已删除的热点"""
    repo = HotTopicRepository(db)
    purged_count = repo.purge_all_deleted(operator)
    
    return {"message": f"成功永久删除 {purged_count} 条热点", "purged_count": purged_count}