# 热点聚合系统

微博、抖音热点信息聚合爬取与展示系统

## 项目结构

```
hot-topics-aggregator/
├── backend/                 # 后端服务
│   ├── api/                 # API接口
│   ├── crawler/             # 爬虫模块
│   ├── data/                # 数据模型和仓库
│   ├── scheduler/           # 定时任务
│   ├── main.py              # FastAPI入口
│   └── requirements.txt     # Python依赖
│
└── frontend/                # 前端应用
    ├── src/
    │   ├── api/             # API客户端
    │   ├── components/      # Vue组件
    │   ├── stores/          # Pinia状态管理
    │   ├── views/           # 页面视图
    │   ├── types/           # TypeScript类型
    │   ├── App.vue          # 根组件
    │   ├── main.ts          # 入口文件
    │   └── router.ts        # 路由配置
    ├── package.json
    ├── vite.config.ts
    └── index.html
```

## 快速开始

### 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 前端启动

```bash
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

## 功能特性

### 用户功能
- 查看微博、抖音当日热点榜单
- 按平台筛选热点
- 按日期筛选历史热点
- 搜索热点关键词
- 响应式布局，支持移动端

### 管理功能
- 手动触发爬取任务
- 查看爬取日志
- 查看数据统计
- 清理历史数据

### 系统特性
- 每小时自动爬取最新热点
- SQLite数据库存储
- CORS跨域支持
- 深色模式切换

## API接口

| 接口 | 方法 | 说明 |
|------|------|------|
| /api/hot-topics | GET | 获取热点列表 |
| /api/hot-topics/{id} | GET | 获取单条热点 |
| /api/hot-topics/search | GET | 搜索热点 |
| /api/crawl/trigger | POST | 触发爬取 |
| /api/crawl/logs | GET | 获取爬取日志 |
| /api/stats | GET | 获取统计数据 |

## 技术栈

### 后端
- Python 3.10+
- FastAPI
- SQLAlchemy
- APScheduler
- httpx

### 前端
- Vue 3 + TypeScript
- Element Plus
- Pinia
- Vite
- Axios