#!/usr/bin/env python
"""简单测试脚本"""

try:
    import sys
    print("Python version:", sys.version)
    
    # 测试基础导入
    from data.database import init_db, get_db
    print("[OK] database module imported")
    
    from data.models import HotTopic, CrawlLog
    print("[OK] models module imported")
    
    from crawler.crawlers import WeiboCrawler, DouyinCrawler
    print("[OK] crawlers module imported")
    
    print("\nAll imports successful!")
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)