#!/usr/bin/env python3
"""
Generate Product Mix Analysis CSV for Investor Presentation
Exports menu engineering matrix data to a formatted CSV file.
"""

import csv
import os
import sys
from datetime import datetime
from backend.consulting_services.menu.product_mix import run

def generate_csv():
    """Generate product mix analysis CSV for investor presentation."""
    
    # Run the product mix analysis
    print("Running product mix analysis...")
    params = {}
    response, status_code = run(params, None)
    
    if status_code != 200:
        print(f"Error: {response.get('error', 'Unknown error')}")
        sys.exit(1)
    
    data = response.get('data', {})
    matrix = data.get('menu_engineering_matrix', {})
    
    # Collect all items from all quadrants
    all_items = []
    
    for quadrant_name, items in matrix.items():
        for item in items:
            item_with_quadrant = item.copy()
            item_with_quadrant['quadrant'] = quadrant_name.upper()
            all_items.append(item_with_quadrant)
    
    if not all_items:
        print("No items found in analysis.")
        sys.exit(1)
    
    # Sort by total profit (descending) for investor presentation
    all_items.sort(key=lambda x: x.get('total_profit', 0), reverse=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"product_mix_analysis_{timestamp}.csv"
    
    # Define CSV columns for investor presentation
    columns = [
        'Menu Item',
        'Category',
        'Price',
        'Units Sold',
        'Revenue',
        'Profit',
        'Contribution Margin %',
        'Food Cost %',
        'Quadrant',
        'Popularity Score',
        'Profitability Score'
    ]
    
    # Write CSV file
    print(f"Writing {len(all_items)} items to {filename}...")
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        
        for item in all_items:
            # Format financial values for readability
            row = {
                'Menu Item': item.get('menu_name', ''),
                'Category': item.get('category', ''),
                'Price': f"${item.get('menu_price', 0):.2f}",
                'Units Sold': int(item.get('total_units_sold', 0)),
                'Revenue': f"${item.get('total_revenue', 0):.2f}",
                'Profit': f"${item.get('total_profit', 0):.2f}",
                'Contribution Margin %': f"{item.get('contribution_margin', 0):.2f}%",
                'Food Cost %': f"{item.get('food_cost_percent', 0):.2f}%",
                'Quadrant': item.get('quadrant', ''),
                'Popularity Score': item.get('popularity_score', 0),
                'Profitability Score': item.get('profitability_score', 0)
            }
            writer.writerow(row)
    
    # Generate summary statistics
    total_items = len(all_items)
    total_revenue = sum(item.get('total_revenue', 0) for item in all_items)
    total_profit = sum(item.get('total_profit', 0) for item in all_items)
    
    quadrant_counts = {}
    for item in all_items:
        quadrant = item.get('quadrant', 'UNKNOWN')
        quadrant_counts[quadrant] = quadrant_counts.get(quadrant, 0) + 1
    
    print("\n" + "="*60)
    print("PRODUCT MIX ANALYSIS SUMMARY")
    print("="*60)
    print(f"Total Menu Items: {total_items}")
    print(f"Total Revenue: ${total_revenue:,.2f}")
    print(f"Total Profit: ${total_profit:,.2f}")
    print(f"\nQuadrant Distribution:")
    for quadrant, count in sorted(quadrant_counts.items()):
        percentage = (count / total_items) * 100
        print(f"  {quadrant}: {count} items ({percentage:.1f}%)")
    print(f"\nCSV file saved: {filename}")
    print("="*60)
    
    return filename

if __name__ == "__main__":
    try:
        generate_csv()
    except Exception as e:
        print(f"Error generating CSV: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

