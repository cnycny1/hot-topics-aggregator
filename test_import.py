#!/usr/bin/env python
"""测试脚本 - 检查项目是否能正常启动"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("Checking project dependencies and syntax...")
print("=" * 60)

try:
    # 测试导入主要模块
    from backend.data.database import init_db, Base
    print("[OK] 数据库模块导入成功")
    
    from backend.data.models import HotTopic, CrawlLog
    print("[OK] 数据模型导入成功")
    
    from backend.crawler.crawlers import WeiboCrawler, DouyinCrawler
    print("[OK] 爬虫模块导入成功")
    
    print("\n[OK] All modules imported successfully!")
    print("\nYou can start the project with these commands:")
    print("  cd backend")
    print("  pip install -r requirements.txt")
    print("  uvicorn main:app --reload --port 8000")
    
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)