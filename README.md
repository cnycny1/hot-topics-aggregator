# 热点聚合系统

🔥 微博、抖音、知乎、今日头条热点信息聚合爬取与展示系统

## 项目简介

这是一个功能强大的热点信息聚合系统，支持多平台热点信息的自动爬取、存储、展示和管理。

### ✨ 核心功能

- 📱 **多平台支持**: 微博、抖音、知乎、今日头条四大平台
- ⏰ **定时爬取**: 每小时自动爬取最新热点信息
- 🔄 **逻辑删除**: 支持删除和恢复，数据不丢失
- 📊 **批量操作**: 批量删除、批量恢复、批量清空
- 🔍 **搜索功能**: 支持关键词搜索热点
- 📝 **审计日志**: 记录所有操作，便于追溯
- 🌐 **响应式设计**: 适配各种设备

## 🛠️ 技术栈

### 后端
- Python 3.9+
- FastAPI - 高性能Web框架
- SQLAlchemy - ORM工具
- APScheduler - 定时任务
- SQLite - 开发数据库

### 前端
- Vue 3 + TypeScript
- Element Plus - UI组件库
- Pinia - 状态管理
- Vite - 构建工具
- Axios - HTTP客户端

## 🚀 快速开始

### 环境要求

- Python 3.9+
- Node.js 16+
- npm 或 yarn

### 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 访问应用

- 前端页面: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 📁 项目结构

```
hot-topics-aggregator/
├── backend/                    # 后端服务
│   ├── api/                   # API接口
│   ├── crawler/               # 爬虫模块
│   ├── data/                  # 数据层
│   ├── scheduler/             # 定时任务
│   └── main.py               # FastAPI入口
│
└── frontend/                   # 前端应用
    └── src/                   # 源代码
```

## 📡 API接口

### 热点查询

| 接口 | 方法 | 说明 |
|------|------|------|
| GET /api/hot-topics | 获取热点列表 | 支持平台、日期筛选 |
| GET /api/hot-topics/{id} | 获取单条热点 | 获取指定热点详情 |
| GET /api/hot-topics/search | 搜索热点 | 关键词搜索 |
| GET /api/hot-topics/deleted | 获取已删除热点 | 回收站功能 |

### 热点操作

| 接口 | 方法 | 说明 |
|------|------|------|
| DELETE /api/hot-topics/{id} | 删除热点 | 逻辑删除 |
| POST /api/hot-topics/{id}/restore | 恢复热点 | 从回收站恢复 |
| POST /api/hot-topics/batch-delete | 批量删除 | 批量逻辑删除 |
| POST /api/hot-topics/batch-restore | 批量恢复 | 批量恢复 |

### 系统管理

| 接口 | 方法 | 说明 |
|------|------|------|
| POST /api/crawl/trigger | 触发爬取 | 手动爬取指定平台 |
| GET /api/crawl/logs | 获取爬取日志 | 查看爬取历史 |
| GET /api/audit-logs | 获取审计日志 | 查看操作记录 |
| GET /api/stats | 获取统计数据 | 系统统计 |

## 🔐 安全特性

- ✅ 逻辑删除机制 - 数据可恢复
- ✅ 审计日志 - 所有操作可追溯
- ✅ 操作确认 - 危险操作需要确认

## 📄 许可证

本项目采用 MIT 许可证