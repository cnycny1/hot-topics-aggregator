from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from data.database import init_db, get_db
from api.hot_topics import router as hot_topics_router
from api.admin import router as admin_router
from scheduler.jobs import setup_scheduler, start_scheduler, stop_scheduler


app = FastAPI(
    title="热点聚合系统 API",
    description="热点聚合系统是一个支持多平台热点信息爬取和展示的全栈项目。支持微博、抖音、知乎、今日头条四大平台。",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.on_event("startup")
async def startup_event():
    init_db()
    setup_scheduler(get_db)
    start_scheduler()


@app.on_event("shutdown")
async def shutdown_event():
    stop_scheduler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hot_topics_router, prefix="/api", tags=["热点查询"])
app.include_router(admin_router, prefix="/api", tags=["系统管理"])


@app.get("/")
async def root():
    return {"message": "热点聚合系统 API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}