#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/home/jkatz015/repos/hospitality_ai_agent')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from backend.consulting_services.menu import product_mix

try:
    params = {"category_filter": "Entree"}
    result, status_code = product_mix.run(params, None)
    print(f"Status: {status_code}")
    if status_code != 200:
        print(f"Error: {result.get('error', 'Unknown error')}")
        print(f"Full result: {result}")
    else:
        print("Success!")
        print(f"Items: {result['data']['overall_metrics']['total_menu_items']}")
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
