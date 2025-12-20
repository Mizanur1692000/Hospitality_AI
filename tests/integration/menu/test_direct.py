#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/home/jkatz015/repos/hospitality_ai_agent')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from backend.consulting_services.menu import product_mix

try:
    result, status_code = product_mix.run({}, None)
    print(f"Status: {status_code}")
    print(f"Result: {result}")
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
