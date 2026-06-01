from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import asyncio

from crawler.crawlers import get_crawler, CRAWLERS
from data.repository import HotTopicRepository, CrawlLogRepository
from logger import get_logger

logger = get_logger(__name__)

scheduler = AsyncIOScheduler()


async def crawl_platform(platform: str, db: Session):
    log_repo = CrawlLogRepository(db)
    topic_repo = HotTopicRepository(db)
    
    crawl_start_time = datetime.utcnow()
    today_start = crawl_start_time.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    logger.info(f"开始爬取 {platform}，爬取时间: {crawl_start_time.isoformat()}，目标日期范围: {today_start.isoformat()} 至 {today_end.isoformat()}")

    log = log_repo.create(platform=platform, status="running")

    crawler = get_crawler(platform)
    if not crawler:
        error_msg = f"Unknown platform: {platform}"
        logger.error(error_msg)
        log_repo.update(log.id, "failed", 0, error_msg)
        return

    try:
        topics, error = await crawler.crawl()

        if error:
            logger.error(f"{platform} 爬取失败: {error}")
            log_repo.update(log.id, "failed", 0, error)
        else:
            if topics:
                # 校验数据时效性
                valid_topics = []
                for topic in topics:
                    topic_crawl_time = topic.get('crawl_time')
                    if topic_crawl_time:
                        if isinstance(topic_crawl_time, str):
                            topic_crawl_time = datetime.fromisoformat(topic_crawl_time.replace('Z', '+00:00'))
                        
                        # 确保爬取时间是当日
                        if today_start <= topic_crawl_time < today_end:
                            valid_topics.append(topic)
                        else:
                            logger.warning(f"{platform} 数据时效性校验失败: {topic.get('title')}，爬取时间: {topic_crawl_time.isoformat()}")
                
                if valid_topics:
                    count = topic_repo.bulk_create(valid_topics)
                    crawl_end_time = datetime.utcnow()
                    duration = (crawl_end_time - crawl_start_time).total_seconds()
                    logger.info(f"{platform} 成功爬取 {count} 条当日有效数据，耗时 {duration:.2f}秒，原始数据 {len(topics)} 条")
                    log_repo.update(log.id, "success", count)
                else:
                    logger.warning(f"{platform} 爬取成功但无当日有效数据，原始数据 {len(topics)} 条")
                    log_repo.update(log.id, "success", 0)
            else:
                logger.warning(f"{platform} 爬取成功但无数据")
                log_repo.update(log.id, "success", 0)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"{platform} 爬取异常: {error_msg}")
        log_repo.update(log.id, "failed", 0, error_msg)


async def crawl_all(db: Session):
    for platform in CRAWLERS.keys():
        await crawl_platform(platform, db)


def setup_scheduler(get_db):
    def job_wrapper():
        db = next(get_db())
        asyncio.create_task(crawl_all(db))

    scheduler.add_job(
        job_wrapper,
        CronTrigger(hour="*"),
        id="crawl_hot_topics",
        name="爬取全平台热点",
        replace_existing=True
    )

    logger.info("定时任务已设置：每整点爬取全平台热点")

    return scheduler


def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        logger.info("定时任务调度器已启动")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("定时任务调度器已停止")