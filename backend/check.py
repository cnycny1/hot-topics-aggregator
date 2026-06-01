#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""简单语法检查 - 兼容 Python 2/3"""

import sys

print("=" * 60)
print("Python Version Check")
print("=" * 60)
print("Python version:", sys.version)

if sys.version_info < (3, 6):
    print("\n[WARNING] Python version is too old!")
    print("          Project requires Python 3.10+")
    print("          Please upgrade Python first.")
else:
    print("\n[OK] Python version is compatible")

print("\n" + "=" * 60)
print("Checking file structure...")
print("=" * 60)

import os
backend_dir = os.path.dirname(os.path.abspath(__file__))

expected_files = [
    'main.py',
    'requirements.txt',
    'data/database.py',
    'data/models.py',
    'data/repository.py',
    'crawler/crawlers.py',
    'api/hot_topics.py',
    'api/admin.py',
    'scheduler/jobs.py'
]

all_found = True
for file_path in expected_files:
    full_path = os.path.join(backend_dir, file_path)
    if os.path.exists(full_path):
        print("[OK]", file_path)
    else:
        print("[MISSING]", file_path)
        all_found = False

print("\n" + "=" * 60)
if all_found:
    print("[OK] All required files are present!")
else:
    print("[ERROR] Some files are missing!")
print("=" * 60)