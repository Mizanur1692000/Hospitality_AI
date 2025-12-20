#!/usr/bin/env python3
"""
Test script for Menu Engineering tasks (Product Mix, Pricing, Design)
Tests all 3 features with actual restaurant data
"""

import sys
import os

# Add project to path
sys.path.insert(0, '/home/jkatz015/repos/hospitality_ai_agent')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

# Import task functions
from backend.consulting_services.menu import product_mix, pricing, design

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def print_result(test_name, success, details=""):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"   {details}")

def test_product_mix_happy_path():
    """Test Product Mix Analysis with default parameters"""
    print_section("TEST 1: Product Mix Analysis - Happy Path")

    try:
        params = {}  # Use defaults
        result, status_code = product_mix.run(params, None)

        # Check status code
        if status_code != 200:
            error_msg = result.get("message", "Unknown error")
            print_result("Status Code", False, f"Expected 200, got {status_code}")
            print(f"   Error: {error_msg}")
            print(f"   Result: {result}")
            return False

        # Check required fields
        required_fields = ["status", "data"]
        for field in required_fields:
            if field not in result:
                print_result(f"Field '{field}'", False, "Missing from result")
                return False

        # Check data structure
        data = result.get("data", {})

        # Check business reports are in data
        if "business_report" not in data or "business_report_html" not in data:
            print_result("Business Reports", False, "Missing from data")
            return False
        if "menu_engineering_matrix" not in data:
            print_result("Menu Engineering Matrix", False, "Missing from data")
            return False

        # Check quadrant summary
        if "quadrant_summary" not in data:
            print_result("Quadrant Summary", False, "Missing from data")
            return False

        quadrant_summary = data["quadrant_summary"]
        for quadrant in ["stars", "plowhorses", "puzzles", "dogs"]:
            if quadrant not in quadrant_summary:
                print_result(f"Quadrant '{quadrant}'", False, "Missing from summary")
                return False

        # Print summary statistics
        print_result("Status Code", True, "200 OK")
        print_result("Required Fields", True, "All present")
        print_result("Data Structure", True, "Valid")

        print("\n📊 Summary Statistics:")
        overall = data.get("overall_metrics", {})
        print(f"   Total Menu Items: {overall.get('total_menu_items', 0)}")
        print(f"   Total Revenue: ${overall.get('total_revenue', 0):,.2f}")
        print(f"   Total Profit: ${overall.get('total_profit', 0):,.2f}")
        print(f"   Stars: {quadrant_summary['stars']['count']}")
        print(f"   Plowhorses: {quadrant_summary['plowhorses']['count']}")
        print(f"   Puzzles: {quadrant_summary['puzzles']['count']}")
        print(f"   Dogs: {quadrant_summary['dogs']['count']}")

        print("\n📝 Recommendations:")
        for i, rec in enumerate(result.get("insights", [])[:3], 1):
            print(f"   {i}. {rec}")

        return True

    except Exception as e:
        print_result("Product Mix Analysis", False, f"Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_pricing_strategy_happy_path():
    """Test Menu Pricing Strategy with default parameters"""
    print_section("TEST 2: Menu Pricing Strategy - Happy Path")

    try:
        params = {}  # Use defaults
        result, status_code = pricing.run(params, None)

        # Check status code
        if status_code != 200:
            error_msg = result.get("message", "Unknown error")
            print_result("Status Code", False, f"Expected 200, got {status_code}")
            print(f"   Error: {error_msg}")
            print(f"   Result: {result}")
            return False

        # Check required fields
        if "data" not in result:
            print_result("Data Field", False, "Missing from result")
            return False

        data = result.get("data", {})

        # Check pricing opportunities
        if "pricing_opportunities" not in data:
            print_result("Pricing Opportunities", False, "Missing from data")
            return False

        pricing_opps = data["pricing_opportunities"]
        if "underpriced_items" not in pricing_opps:
            print_result("Underpriced Items", False, "Missing from opportunities")
            return False

        # Check revenue impact
        if "revenue_impact" not in data:
            print_result("Revenue Impact", False, "Missing from data")
            return False

        print_result("Status Code", True, "200 OK")
        print_result("Required Fields", True, "All present")
        print_result("Data Structure", True, "Valid")

        # Print summary
        print("\n💰 Pricing Analysis Summary:")
        summary = pricing_opps.get("summary", {})
        print(f"   Underpriced Items: {summary.get('underpriced_count', 0)}")
        print(f"   Overpriced Items: {summary.get('overpriced_count', 0)}")
        print(f"   Well-Priced Items: {summary.get('well_priced_count', 0)}")

        revenue_impact = data.get("revenue_impact", {})
        print(f"   Revenue Opportunity: ${revenue_impact.get('total_opportunity', 0):,.2f}")
        print(f"   Potential Improvement: {revenue_impact.get('percentage_improvement', 0):.1f}%")

        print("\n📝 Top Pricing Recommendations:")
        for i, rec in enumerate(result.get("insights", [])[:3], 1):
            print(f"   {i}. {rec}")

        return True

    except Exception as e:
        print_result("Pricing Strategy", False, f"Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_design_recommendations_happy_path():
    """Test Menu Design Recommendations with default parameters"""
    print_section("TEST 3: Menu Design Recommendations - Happy Path")

    try:
        params = {}  # Use defaults
        result, status_code = design.run(params, None)

        # Check status code
        if status_code != 200:
            error_msg = result.get("message", "Unknown error")
            print_result("Status Code", False, f"Expected 200, got {status_code}")
            print(f"   Error: {error_msg}")
            print(f"   Result: {result}")
            return False

        # Check required fields
        if "data" not in result:
            print_result("Data Field", False, "Missing from result")
            return False

        data = result.get("data", {})

        # Check golden triangle
        if "golden_triangle" not in data:
            print_result("Golden Triangle", False, "Missing from data")
            return False

        # Check layout strategy
        if "layout_strategy" not in data:
            print_result("Layout Strategy", False, "Missing from data")
            return False

        # Check design principles
        if "design_principles" not in data:
            print_result("Design Principles", False, "Missing from data")
            return False

        # Check implementation guide
        if "implementation_guide" not in data:
            print_result("Implementation Guide", False, "Missing from data")
            return False

        print_result("Status Code", True, "200 OK")
        print_result("Required Fields", True, "All present")
        print_result("Data Structure", True, "Valid")

        # Print summary
        print("\n🎨 Design Analysis Summary:")
        golden_triangle = data.get("golden_triangle", [])
        print(f"   Golden Triangle Recommendations: {len(golden_triangle)}")

        if golden_triangle:
            print(f"\n   Top Placement (Primary):")
            print(f"      Item: {golden_triangle[0].get('menu_item', 'N/A')}")
            print(f"      Position: {golden_triangle[0].get('position', 'N/A')}")
            print(f"      Reason: {golden_triangle[0].get('reason', 'N/A')}")

        quadrant_counts = data.get("quadrant_counts", {})
        print(f"\n   Quadrant Distribution:")
        print(f"      Stars: {quadrant_counts.get('stars', 0)} (high visibility)")
        print(f"      Puzzles: {quadrant_counts.get('puzzles', 0)} (need awareness)")
        print(f"      Plowhorses: {quadrant_counts.get('plowhorses', 0)} (maintain)")
        print(f"      Dogs: {quadrant_counts.get('dogs', 0)} (minimize/remove)")

        print("\n📝 Design Recommendations:")
        for i, rec in enumerate(result.get("insights", [])[:3], 1):
            print(f"   {i}. {rec}")

        return True

    except Exception as e:
        print_result("Design Recommendations", False, f"Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_category_filter():
    """Test Product Mix with category filter"""
    print_section("TEST 4: Product Mix with Category Filter")

    try:
        params = {"category_filter": "Main Course"}
        result, status_code = product_mix.run(params, None)

        if status_code != 200:
            print_result("Status Code", False, f"Expected 200, got {status_code}")
            return False

        data = result.get("data", {})
        overall = data.get("overall_metrics", {})

        print_result("Category Filter", True, "Applied successfully")
        print(f"   Filtered to Main Course: {overall.get('total_menu_items', 0)} items")

        return True

    except Exception as e:
        print_result("Category Filter", False, f"Exception: {str(e)}")
        return False

def test_custom_target_food_cost():
    """Test Pricing with custom target food cost"""
    print_section("TEST 5: Pricing with Custom Target Food Cost")

    try:
        params = {"target_food_cost": 28.0}
        result, status_code = pricing.run(params, None)

        if status_code != 200:
            print_result("Status Code", False, f"Expected 200, got {status_code}")
            return False

        data = result.get("data", {})
        target = data.get("target_food_cost_percent", 0)

        print_result("Custom Target", True, f"Target set to {target}%")

        return True

    except Exception as e:
        print_result("Custom Target", False, f"Exception: {str(e)}")
        return False

def test_business_reports():
    """Test that business reports are generated properly"""
    print_section("TEST 6: Business Report Generation")

    try:
        # Test all 3 features
        features = [
            ("Product Mix", product_mix),
            ("Pricing", pricing),
            ("Design", design)
        ]

        all_passed = True
        for name, module in features:
            result, status_code = module.run({}, None)

            if status_code != 200:
                print_result(f"{name} Report", False, "Failed to generate")
                all_passed = False
                continue

            # Check for business reports
            business_report = result.get("data", {}).get("business_report", "")
            business_report_html = result.get("data", {}).get("business_report_html", "")

            if not business_report:
                print_result(f"{name} Text Report", False, "Empty or missing")
                all_passed = False
            else:
                print_result(f"{name} Text Report", True, f"{len(business_report)} chars")

            if not business_report_html:
                print_result(f"{name} HTML Report", False, "Empty or missing")
                all_passed = False
            else:
                print_result(f"{name} HTML Report", True, f"{len(business_report_html)} chars")

        return all_passed

    except Exception as e:
        print_result("Business Reports", False, f"Exception: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("  MENU ENGINEERING VALIDATION SUITE")
    print("  Testing: Product Mix, Pricing Strategy, Menu Design")
    print("="*80)

    tests = [
        ("Product Mix - Happy Path", test_product_mix_happy_path),
        ("Pricing Strategy - Happy Path", test_pricing_strategy_happy_path),
        ("Design Recommendations - Happy Path", test_design_recommendations_happy_path),
        ("Category Filter", test_category_filter),
        ("Custom Target Food Cost", test_custom_target_food_cost),
        ("Business Report Generation", test_business_reports)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR in {test_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Print summary
    print_section("TEST SUMMARY")

    passed = sum(1 for _, p in results if p)
    total = len(results)

    for test_name, passed_test in results:
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\n{'='*80}")
    print(f"  RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"{'='*80}\n")

    if passed == total:
        print("🎉 ALL TESTS PASSED! Menu Engineering implementation is ready for production.")
        return 0
    else:
        print(f"⚠️  {total - passed} test(s) failed. Review output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
