from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import os

from data.database import init_db, get_db
from api.hot_topics import router as hot_topics_router
from api.admin import router as admin_router
from scheduler.jobs import setup_scheduler, start_scheduler, stop_scheduler


app = FastAPI(
    title="🔥 热点聚合系统 API",
    description="""
## 📊 项目介绍
热点聚合系统是一个支持多平台热点信息爬取和展示的全栈项目。

### ✨ 支持平台
- 📱 微博 - 微博热搜榜
- 🎵 抖音 - 抖音热榜
- 💬 知乎 - 知乎热榜
- 📰 今日头条 - 头条热榜

### 🔧 技术栈
- **后端**: FastAPI + SQLAlchemy + APScheduler
- **前端**: Vue 3 + TypeScript + Element Plus
- **数据库**: SQLite (开发) / PostgreSQL (生产)

### 📅 定时任务
系统每整点自动爬取各平台热点信息
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={
        "deepLinking": True,
        "displayOperationId": True,
        "displayRequestDuration": True,
        "filter": True,
        "showExtensions": True,
        "showModels": True,
    }
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


@app.get("/docs", include_in_schema=False)
async def custom_docs():
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔥 热点聚合系统 API 文档</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css">
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-themes@3.0.0/themes/3.x/theme-material.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }

        .top-bar {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            padding: 15px 30px;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .top-bar h1 {
            color: #667eea;
            font-size: 24px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .top-bar h1 .emoji {
            font-size: 28px;
        }

        .nav-links {
            display: flex;
            gap: 20px;
            align-items: center;
        }

        .nav-links a {
            color: #667eea;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 8px;
            transition: all 0.3s ease;
            font-weight: 500;
        }

        .nav-links a:hover {
            background: #667eea;
            color: white;
        }

        .nav-links .active {
            background: #667eea;
            color: white;
        }

        #swagger-ui {
            padding-top: 80px;
            max-width: 1400px;
            margin: 0 auto;
            padding-left: 20px;
            padding-right: 20px;
        }

        /* Custom Swagger UI Styles */
        .swagger-ui .topbar {
            display: none;
        }

        .swagger-ui .info {
            margin: 30px 0;
            background: white;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        }

        .swagger-ui .info .title {
            color: #667eea;
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 15px;
        }

        .swagger-ui .info .description {
            color: #666;
            font-size: 16px;
            line-height: 1.8;
        }

        .swagger-ui .btn {
            border-radius: 8px;
            transition: all 0.3s ease;
        }

        .swagger-ui .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

        .swagger-ui .opblock {
            background: white;
            border-radius: 12px;
            margin-bottom: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
            border: none;
        }

        .swagger-ui .opblock:hover {
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
            transform: translateY(-2px);
        }

        .swagger-ui .opblock .opblock-summary {
            padding: 15px 20px;
        }

        .swagger-ui .opblock-tag {
            font-size: 18px;
            font-weight: 600;
            color: #667eea;
            padding: 15px 20px;
            background: rgba(102, 126, 234, 0.05);
            border-radius: 12px 12px 0 0;
        }

        .swagger-ui .scheme-container {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
            margin-bottom: 20px;
        }

        .swagger-ui .model {
            background: rgba(102, 126, 234, 0.05);
            border-radius: 8px;
            padding: 15px;
        }

        .swagger-ui .model-title {
            color: #667eea;
            font-weight: 600;
        }

        .swagger-ui .property {
            color: #555;
        }

        .swagger-ui .parameter__name {
            color: #667eea;
            font-weight: 600;
        }

        .swagger-ui .response-class_info {
            background: rgba(102, 126, 234, 0.1);
            border-radius: 8px;
            padding: 10px;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .swagger-ui {
            animation: fadeIn 0.5s ease;
        }
    </style>
</head>
<body>
    <div class="top-bar">
        <h1><span class="emoji">🔥</span> 热点聚合系统 API</h1>
        <div class="nav-links">
            <a href="/docs" class="active">📚 Swagger UI</a>
            <a href="/redoc">📖 ReDoc</a>
            <a href="/" target="_blank">🌐 前端页面</a>
        </div>
    </div>

    <div id="swagger-ui"></div>

    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
    <script>
        window.onload = function() {
            SwaggerUIBundle({
                url: "/openapi.json",
                dom_id: '#swagger-ui',
                deepLinking: true,
                displayOperationId: true,
                displayRequestDuration: true,
                filter: true,
                showExtensions: true,
                showModels: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.SwaggerUIStandalonePreset
                ],
                layout: "BaseLayout",
                docExpansion: "list",
                operationsSorter: "method",
                tagsSorter: "alpha",
            });
        };
    </script>
</body>
</html>
    """)