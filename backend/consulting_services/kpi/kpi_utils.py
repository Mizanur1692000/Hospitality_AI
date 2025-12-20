"""
Performance Management Module
Handles KPI tracking, analytics, and performance reporting
"""

from typing import Any, Dict

import pandas as pd
from datetime import datetime
from backend.shared.utils.business_report import format_comprehensive_analysis


def format_business_report(analysis_type, metrics, performance, recommendations, benchmarks=None, additional_data=None):
    current_date = datetime.now().strftime("%B %d, %Y")

    rating = performance['rating']
    tone = (
        "excellent" if rating == "Excellent"
        else "good" if rating == "Good"
        else "acceptable" if rating == "Acceptable"
        else "concerning"
    )
    comp = (
        "exceed" if rating in ["Excellent", "Good"]
        else "meet" if rating == "Acceptable"
        else "fall below"
    )

    # Text (keep for file export)
    exec_summary_text = (
        f"PERFORMANCE RATING: {rating.upper()}\n\n"
        f"This {analysis_type.lower()} reveals {tone} performance metrics that {comp} industry standards."
    )
    key_metrics_lines = []
    for k, v in metrics.items():
        label = k.replace('_', ' ').title()
        key_lower = k.lower()
        if isinstance(v, float):
            if 'percent' in key_lower or '%' in k:
                key_metrics_lines.append(f"{label}: {v:.1f}%")
            elif any(w in key_lower for w in ['cost', 'sales', 'revenue', 'profit', 'savings', 'price']):
                key_metrics_lines.append(f"{label}: ${v:,.2f}")
            else:
                key_metrics_lines.append(f"{label}: {v:.2f}")
        else:
            key_metrics_lines.append(f"{label}: {v:,}")

    bench_lines = []
    if benchmarks:
        for k, v in benchmarks.items():
            if isinstance(v, (int, float)):
                bench_lines.append(f"{k.replace('_', ' ').title()}: {v:.1f}%")
            else:
                bench_lines.append(f"{k.replace('_', ' ').title()}: {v}")

    rec_lines = [f"{i}. {r}" for i, r in enumerate(recommendations, 1)]

    add_lines = []
    if additional_data:
        for k, v in additional_data.items():
            if isinstance(v, dict):
                add_lines.append(f"{k.replace('_',' ').title()}:")
                for sk, sv in v.items():
                    add_lines.append(f"  {sk.replace('_',' ').title()}: {sv}")
            else:
                add_lines.append(f"{k.replace('_',' ').title()}: {v}")

    # Add bullets back for text version
    key_metrics_text = ["• " + line for line in key_metrics_lines]
    bench_text = ["• " + line for line in bench_lines] if bench_lines else []
    add_text = []
    for line in add_lines:
        if line.startswith("  "):  # Indented sub-item
            add_text.append("  • " + line.strip())
        else:
            add_text.append("• " + line)
    
    business_report_text = (
        f"RESTAURANT CONSULTING REPORT — {analysis_type.upper()}\n"
        f"Generated: {current_date}\n\n"
        f"{exec_summary_text}\n\n"
        "KEY PERFORMANCE METRICS\n"
        + "\n".join(key_metrics_text) + ("\n\nINDUSTRY BENCHMARKS\n" + "\n".join(bench_text) if bench_text else "")
        + ("\n\nADDITIONAL INSIGHTS\n" + "\n".join(add_text) if add_text else "")
        + "\n\nSTRATEGIC RECOMMENDATIONS\n"
        + "\n".join(rec_lines)
        + "\n\nEND OF REPORT"
    ).strip()

    # HTML (for on-screen display)
    def li_items(lines):  # helper for <ul>
        return "".join(f"<li>{line}</li>" for line in lines)

    # Normalize badge class name
    badge_class = rating.lower().replace(' ', '-').replace('_', '-')
    
    business_report_html = f"""
<section class="report">
  <header class="report__header">
    <h2>{analysis_type}</h2>
    <div class="report__meta">Generated: {current_date}</div>
    <div class="badge badge--{badge_class}">{rating}</div>
  </header>

  <article class="report__body">
    <p class="lead">This {analysis_type.lower()} reveals <strong>{tone}</strong> performance metrics that <strong>{comp}</strong> industry standards.</p>

    <h3>Key Performance Metrics</h3>
    <ul>{li_items(key_metrics_lines)}</ul>

    {f"<h3>Industry Benchmarks</h3><ul>{li_items(bench_lines)}</ul>" if bench_lines else ""}

    {f"<h3>Additional Insights</h3><ul>{li_items(add_lines)}</ul>" if add_lines else ""}

    <h3>Strategic Recommendations</h3>
    <ol>{''.join(f'<li>{r}</li>' for r in recommendations)}</ol>
  </article>
</section>
""".strip()

    return {
        "status": "success",
        "analysis_type": analysis_type,
        "report_date": current_date,
        "performance_rating": rating,
        "performance_color": performance.get('color', 'blue'),
        "business_report": business_report_text,          # keep for downloads
        "business_report_html": business_report_html,     # render this in UI
        "executive_summary": exec_summary_text,
        "key_metrics": metrics,
        "benchmarks": benchmarks or {},
        "recommendations": recommendations,
        "additional_insights": additional_data or {},
    }


def calculate_labor_cost_analysis(total_sales, labor_cost, hours_worked, target_labor_percent=30.0):
    """
    Comprehensive Labor Cost Analysis with industry benchmarks and recommendations

    Args:
        total_sales (float): Total sales revenue
        labor_cost (float): Total labor costs
        hours_worked (float): Total hours worked
        target_labor_percent (float): Target labor percentage (default 30%)

    Returns:
        dict: Labor cost analysis with recommendations
    """
    # Input validation
    if not all(isinstance(x, (int, float)) and x > 0 for x in [total_sales, labor_cost, hours_worked]):
        return {"status": "error", "message": "All inputs must be positive numbers"}

    # Calculate key metrics
    labor_percent = (labor_cost / total_sales) * 100
    sales_per_labor_hour = total_sales / hours_worked
    cost_per_labor_hour = labor_cost / hours_worked

    # Industry benchmarks
    excellent_labor_percent = 25.0
    good_labor_percent = 30.0
    acceptable_labor_percent = 35.0

    # Performance assessment
    if labor_percent <= excellent_labor_percent:
        performance = "Excellent"
        performance_color = "green"
    elif labor_percent <= good_labor_percent:
        performance = "Good"
        performance_color = "blue"
    elif labor_percent <= acceptable_labor_percent:
        performance = "Acceptable"
        performance_color = "yellow"
    else:
        performance = "Needs Improvement"
        performance_color = "red"

    # Calculate potential savings
    target_labor_cost = (target_labor_percent / 100) * total_sales
    potential_savings = labor_cost - target_labor_cost

    # Generate recommendations
    recommendations = []
    if labor_percent > target_labor_percent:
        recommendations.append(f"Reduce labor costs by ${potential_savings:,.2f} to reach {target_labor_percent}% target")
        recommendations.append("Consider optimizing staff scheduling during slow periods")
        recommendations.append("Review overtime policies and cross-training opportunities")
    else:
        recommendations.append("Labor costs are within target range - maintain current efficiency")
        recommendations.append("Consider investing in staff training to improve productivity")

    if sales_per_labor_hour < 50:
        recommendations.append("Sales per labor hour is low - focus on upselling and efficiency")
    elif sales_per_labor_hour > 100:
        recommendations.append("Excellent sales per labor hour - consider expanding during peak times")

    # Prepare data for business report
    metrics = {
        "labor_percent": round(labor_percent, 2),
        "sales_per_labor_hour": round(sales_per_labor_hour, 2),
        "cost_per_labor_hour": round(cost_per_labor_hour, 2),
        "total_labor_cost": labor_cost,
        "total_sales": total_sales,
        "hours_worked": hours_worked
    }

    performance_data = {
        "rating": performance,
        "color": performance_color,
        "vs_target": round(labor_percent - target_labor_percent, 2)
    }

    benchmarks = {
        "excellent_threshold": excellent_labor_percent,
        "good_threshold": good_labor_percent,
        "acceptable_threshold": acceptable_labor_percent,
        "target_percent": target_labor_percent
    }

    additional_insights = {
        "potential_savings": round(potential_savings, 2),
        "efficiency_rating": "High" if sales_per_labor_hour > 80 else "Medium" if sales_per_labor_hour > 50 else "Low",
        "cost_control": "Excellent" if labor_percent <= 25 else "Good" if labor_percent <= 30 else "Needs Improvement"
    }

    return format_business_report(
        analysis_type="Labor Cost Analysis",
        metrics=metrics,
        performance=performance_data,
        recommendations=recommendations,
        benchmarks=benchmarks,
        additional_data=additional_insights
    )


def calculate_prime_cost_analysis(total_sales, labor_cost, food_cost, target_prime_percent=60.0):
    """
    Comprehensive Prime Cost Analysis (Labor + Food costs)

    Args:
        total_sales (float): Total sales revenue
        labor_cost (float): Total labor costs
        food_cost (float): Total food costs
        target_prime_percent (float): Target prime cost percentage (default 60%)

    Returns:
        dict: Prime cost analysis with recommendations
    """
    # Input validation
    if not all(isinstance(x, (int, float)) and x > 0 for x in [total_sales, labor_cost, food_cost]):
        return {"status": "error", "message": "All inputs must be positive numbers"}

    # Calculate key metrics
    prime_cost = labor_cost + food_cost
    prime_percent = (prime_cost / total_sales) * 100
    labor_percent = (labor_cost / total_sales) * 100
    food_percent = (food_cost / total_sales) * 100

    # Industry benchmarks
    excellent_prime_percent = 55.0
    good_prime_percent = 60.0
    acceptable_prime_percent = 65.0

    # Performance assessment
    if prime_percent <= excellent_prime_percent:
        performance = "Excellent"
        performance_color = "green"
    elif prime_percent <= good_prime_percent:
        performance = "Good"
        performance_color = "blue"
    elif prime_percent <= acceptable_prime_percent:
        performance = "Acceptable"
        performance_color = "yellow"
    else:
        performance = "Needs Improvement"
        performance_color = "red"

    # Calculate potential savings
    target_prime_cost = (target_prime_percent / 100) * total_sales
    potential_savings = prime_cost - target_prime_cost

    # Cost breakdown analysis
    cost_breakdown = {
        "labor_portion": round((labor_cost / prime_cost) * 100, 1),
        "food_portion": round((food_cost / prime_cost) * 100, 1)
    }

    # Generate recommendations
    recommendations = []
    if prime_percent > target_prime_percent:
        recommendations.append(f"Reduce prime costs by ${potential_savings:,.2f} to reach {target_prime_percent}% target")

        if labor_percent > 30:
            recommendations.append("Focus on labor cost optimization - consider scheduling improvements")
        if food_percent > 30:
            recommendations.append("Focus on food cost control - review portion sizes and waste")
    else:
        recommendations.append("Prime costs are within target range - maintain current efficiency")

    if cost_breakdown["labor_portion"] > 60:
        recommendations.append("Labor costs dominate - focus on labor efficiency and scheduling")
    elif cost_breakdown["food_portion"] > 60:
        recommendations.append("Food costs dominate - focus on menu engineering and portion control")

    # Prepare data for business report
    metrics = {
        "prime_cost": round(prime_cost, 2),
        "prime_percent": round(prime_percent, 2),
        "labor_percent": round(labor_percent, 2),
        "food_percent": round(food_percent, 2),
        "total_sales": total_sales
    }

    performance_data = {
        "rating": performance,
        "color": performance_color,
        "vs_target": round(prime_percent - target_prime_percent, 2)
    }

    benchmarks = {
        "excellent_threshold": excellent_prime_percent,
        "good_threshold": good_prime_percent,
        "acceptable_threshold": acceptable_prime_percent,
        "target_percent": target_prime_percent
    }

    additional_insights = {
        "potential_savings": round(potential_savings, 2),
        "cost_breakdown": cost_breakdown,
        "cost_control_rating": "Excellent" if prime_percent <= 55 else "Good" if prime_percent <= 60 else "Needs Improvement",
        "primary_cost_driver": (
            "Labor" if cost_breakdown["labor_portion"] > 60
            else "Food" if cost_breakdown["food_portion"] > 60
            else "Balanced"
        )
    }

    return format_business_report(
        analysis_type="Prime Cost Analysis",
        metrics=metrics,
        performance=performance_data,
        recommendations=recommendations,
        benchmarks=benchmarks,
        additional_data=additional_insights
    )


def calculate_sales_performance_analysis(total_sales, labor_cost, food_cost, hours_worked, previous_sales=None):
    """
    Comprehensive Sales Performance Analysis

    Args:
        total_sales (float): Current period sales revenue
        labor_cost (float): Total labor costs
        food_cost (float): Total food costs
        hours_worked (float): Total hours worked
        previous_sales (float, optional): Previous period sales for comparison

    Returns:
        dict: Sales performance analysis with insights
    """
    # Input validation
    if not all(isinstance(x, (int, float)) and x > 0 for x in [total_sales, labor_cost, food_cost, hours_worked]):
        return {"status": "error", "message": "All inputs must be positive numbers"}

    # Calculate key metrics
    sales_per_labor_hour = total_sales / hours_worked
    labor_percent = (labor_cost / total_sales) * 100
    food_percent = (food_cost / total_sales) * 100
    prime_percent = labor_percent + food_percent

    # Performance benchmarks
    excellent_sales_per_hour = 80.0
    good_sales_per_hour = 60.0
    acceptable_sales_per_hour = 40.0

    # Sales performance assessment
    if sales_per_labor_hour >= excellent_sales_per_hour:
        sales_performance = "Excellent"
        sales_color = "green"
    elif sales_per_labor_hour >= good_sales_per_hour:
        sales_performance = "Good"
        sales_color = "blue"
    elif sales_per_labor_hour >= acceptable_sales_per_hour:
        sales_performance = "Acceptable"
        sales_color = "yellow"
    else:
        sales_performance = "Needs Improvement"
        sales_color = "red"

    # Calculate growth metrics if previous sales provided
    growth_analysis = {}
    if previous_sales and previous_sales > 0:
        sales_growth = ((total_sales - previous_sales) / previous_sales) * 100
        growth_analysis = {
            "sales_growth_percent": round(sales_growth, 2),
            "sales_growth_amount": round(total_sales - previous_sales, 2),
            "growth_trend": "Positive" if sales_growth > 0 else "Negative"
        }

    # Revenue efficiency analysis
    revenue_efficiency = {
        "sales_per_labor_hour": round(sales_per_labor_hour, 2),
        "labor_efficiency": round(labor_percent, 2),
        "food_efficiency": round(food_percent, 2),
        "prime_efficiency": round(prime_percent, 2)
    }

    # Generate recommendations
    recommendations = []

    if sales_per_labor_hour < acceptable_sales_per_hour:
        recommendations.append("Sales per labor hour is low - focus on increasing revenue or reducing labor hours")
        recommendations.append("Consider staff training to improve service speed and upselling")
    elif sales_per_labor_hour >= excellent_sales_per_hour:
        recommendations.append("Excellent sales performance - consider expanding during peak hours")
        recommendations.append("Maintain current efficiency while exploring growth opportunities")

    if labor_percent > 35:
        recommendations.append("High labor percentage - optimize scheduling and reduce overtime")
    if food_percent > 35:
        recommendations.append("High food cost percentage - review menu pricing and portion control")

    if previous_sales and previous_sales > 0:
        if growth_analysis["sales_growth_percent"] < 0:
            recommendations.append("Sales declining - analyze market trends and customer feedback")
        elif growth_analysis["sales_growth_percent"] > 10:
            recommendations.append("Strong growth - consider capacity planning and staff expansion")

    # Prepare data for business report
    metrics = {
        "total_sales": total_sales,
        "sales_per_labor_hour": round(sales_per_labor_hour, 2),
        "labor_percent": round(labor_percent, 2),
        "food_percent": round(food_percent, 2),
        "prime_percent": round(prime_percent, 2),
        "hours_worked": hours_worked
    }

    performance_data = {
        "rating": sales_performance,
        "color": sales_color
    }

    benchmarks = {
        "excellent_threshold": excellent_sales_per_hour,
        "good_threshold": good_sales_per_hour,
        "acceptable_threshold": acceptable_sales_per_hour
    }

    additional_insights = {
        "revenue_efficiency": revenue_efficiency,
        "growth_analysis": growth_analysis,
        "performance_trend": (
            "Growing" if growth_analysis and growth_analysis.get("sales_growth_percent", 0) > 0
            else "Declining" if growth_analysis and growth_analysis.get("sales_growth_percent", 0) < 0
            else "Stable"
        ),
        "efficiency_rating": "High" if sales_per_labor_hour > 80 else "Medium" if sales_per_labor_hour > 50 else "Low"
    }

    return format_business_report(
        analysis_type="Sales Performance Analysis",
        metrics=metrics,
        performance=performance_data,
        recommendations=recommendations,
        benchmarks=benchmarks,
        additional_data=additional_insights
    )


def calculate_kpi_summary(total_sales, labor_cost, food_cost, hours_worked):
    """
    Calculate comprehensive KPI summary with input validation

    Args:
        total_sales (float): Total sales revenue
        labor_cost (float): Total labor costs
        food_cost (float): Total food costs
        hours_worked (float): Total hours worked

    Returns:
        dict: KPI calculations or error response
    """
    # Input validation
    inputs = {"total_sales": total_sales, "labor_cost": labor_cost, "food_cost": food_cost, "hours_worked": hours_worked}

    # Check for None values
    for name, value in inputs.items():
        if value is None:
            return {"status": "error", "message": f"{name} cannot be null"}

    # Check for numeric types
    for name, value in inputs.items():
        if not isinstance(value, (int, float)):
            return {"status": "error", "message": f"{name} must be a number, got {type(value).__name__}"}

    # Check for negative values
    for name, value in inputs.items():
        if value < 0:
            return {"status": "error", "message": f"{name} cannot be negative"}

    # Check for zero values where division occurs
    if total_sales == 0:
        return {"status": "error", "message": "total_sales cannot be zero"}

    if hours_worked == 0:
        return {"status": "error", "message": "hours_worked cannot be zero"}

    # Perform calculations
    prime_cost = labor_cost + food_cost
    labor_percent = (labor_cost / total_sales) * 100
    food_percent = (food_cost / total_sales) * 100
    prime_percent = (prime_cost / total_sales) * 100
    sales_per_labor_hour = total_sales / hours_worked

    # Industry benchmarks for comparison
    industry_benchmarks = {
        "labor_percent": {"excellent": 25, "good": 30, "needs_improvement": 35},
        "food_percent": {"excellent": 28, "good": 32, "needs_improvement": 38},
        "prime_percent": {"excellent": 55, "good": 60, "needs_improvement": 65},
    }

    # Performance assessment
    def assess_performance(value, benchmarks):
        if value <= benchmarks["excellent"]:
            return "excellent", "🟢"
        elif value <= benchmarks["good"]:
            return "good", "🟡"
        else:
            return "needs_improvement", "🔴"

    labor_assessment, labor_icon = assess_performance(labor_percent, industry_benchmarks["labor_percent"])
    food_assessment, food_icon = assess_performance(food_percent, industry_benchmarks["food_percent"])
    prime_assessment, prime_icon = assess_performance(prime_percent, industry_benchmarks["prime_percent"])

    # Generate recommendations
    recommendations = []
    if labor_percent > 30:
        recommendations.append("Consider optimizing staff scheduling to reduce labor costs")
    if food_percent > 32:
        recommendations.append("Review menu pricing and food cost controls")
    if prime_percent > 60:
        recommendations.append("Focus on both labor and food cost optimization")
    if sales_per_labor_hour < 50:
        recommendations.append("Improve staff productivity and sales training")

    if not recommendations:
        recommendations.append("Great job! Your KPIs are within industry standards")

    # Generate business report using the new formatter
    kpi_data = {
        "labor_percent": {
            "title": "Labor Cost Percentage",
            "calculation": "(Labor Cost / Total Sales) × 100",
            "example": f"(${labor_cost:,.2f} / ${total_sales:,.2f}) × 100 = {labor_percent:.1f}%",
            "interpretation": f"Your labor cost percentage of {labor_percent:.1f}% is {labor_assessment} compared to industry standards of 25-30%.",
            "recommendations": [rec for rec in recommendations if "labor" in rec.lower() or "staff" in rec.lower() or "scheduling" in rec.lower()]
        },
        "food_percent": {
            "title": "Food Cost Percentage",
            "calculation": "(Food Cost / Total Sales) × 100",
            "example": f"(${food_cost:,.2f} / ${total_sales:,.2f}) × 100 = {food_percent:.1f}%",
            "interpretation": f"Your food cost percentage of {food_percent:.1f}% is {food_assessment} compared to industry standards of 28-32%.",
            "recommendations": [rec for rec in recommendations if "food" in rec.lower() or "menu" in rec.lower() or "pricing" in rec.lower()]
        },
        "prime_percent": {
            "title": "Prime Cost Percentage",
            "calculation": "((Labor Cost + Food Cost) / Total Sales) × 100",
            "example": f"(${prime_cost:,.2f} / ${total_sales:,.2f}) × 100 = {prime_percent:.1f}%",
            "interpretation": f"Your prime cost percentage of {prime_percent:.1f}% is {prime_assessment} compared to industry standards of 55-60%.",
            "recommendations": [rec for rec in recommendations if "prime" in rec.lower() or "cost" in rec.lower()]
        },
        "sales_per_labor_hour": {
            "title": "Sales per Labor Hour",
            "calculation": "Total Sales / Labor Hours",
            "example": f"${total_sales:,.2f} / {hours_worked:.0f} hours = ${sales_per_labor_hour:.2f} per hour",
            "interpretation": f"Your sales per labor hour of ${sales_per_labor_hour:.2f} is {'excellent' if sales_per_labor_hour > 50 else 'good' if sales_per_labor_hour > 40 else 'needs improvement'} compared to industry standards of $50+/hour.",
            "recommendations": [rec for rec in recommendations if "productivity" in rec.lower() or "sales" in rec.lower() or "training" in rec.lower()]
        }
    }

    business_report = format_comprehensive_analysis('kpi', kpi_data)

    return {
        "status": "success",
        "summary": {
            "total_sales": f"${total_sales:,.2f}",
            "prime_cost": f"${prime_cost:,.2f}",
            "prime_percent": f"{prime_percent:.1f}%",
        },
        "kpis": {
            "labor_percent": {
                "value": round(labor_percent, 2),
                "assessment": labor_assessment,
                "icon": labor_icon,
                "benchmark": "25-30%",
            },
            "food_percent": {
                "value": round(food_percent, 2),
                "assessment": food_assessment,
                "icon": food_icon,
                "benchmark": "28-32%",
            },
            "prime_percent": {
                "value": round(prime_percent, 2),
                "assessment": prime_assessment,
                "icon": prime_icon,
                "benchmark": "55-60%",
            },
            "sales_per_labor_hour": {
                "value": round(sales_per_labor_hour, 2),
                "assessment": (
                    "excellent" if sales_per_labor_hour > 50 else "good" if sales_per_labor_hour > 40 else "needs_improvement"
                ),
                "icon": "🟢" if sales_per_labor_hour > 50 else "🟡" if sales_per_labor_hour > 40 else "🔴",
                "benchmark": "$50+/hour",
            },
        },
        "recommendations": recommendations,
        "industry_benchmarks": industry_benchmarks,
        "business_report": business_report
    }


def process_kpi_csv_data(csv_file) -> Dict[str, Any]:
    """
    Process uploaded CSV file for comprehensive KPI analysis

    Expected CSV columns: date, sales, labor_cost, food_cost, labor_hours
    """
    try:
        df = pd.read_csv(csv_file)

        # Flexible column mapping
        column_mapping = {
            "sales": ["sales", "revenue", "total_sales", "daily_sales"],
            "labor_cost": ["labor_cost", "labor", "wages", "payroll"],
            "food_cost": ["food_cost", "cogs", "cost_of_goods", "food"],
            "labor_hours": ["labor_hours", "hours", "hours_worked", "staff_hours"],
        }

        # Find matching columns
        mapped_columns = {}
        for target, variations in column_mapping.items():
            for col in df.columns:
                if any(var.lower() in col.lower() for var in variations):
                    mapped_columns[target] = col
                    break

        # Check for required columns
        missing_columns = [col for col in column_mapping.keys() if col not in mapped_columns]
        if missing_columns:
            return {
                "status": "error",
                "message": f"Missing required columns: {', '.join(missing_columns)}",
                "found_columns": list(df.columns),
                "help": "Please ensure your CSV has columns for: sales, labor_cost, food_cost, labor_hours",
            }

        # Clean and process data
        df_clean = df.copy()
        for target, source_col in mapped_columns.items():
            df_clean[target] = pd.to_numeric(df_clean[source_col], errors="coerce").fillna(0)

        # Calculate daily KPIs
        daily_kpis = []
        for _, row in df_clean.iterrows():
            if row["sales"] > 0:  # Only process days with sales
                daily_kpi = calculate_kpi_summary(row["sales"], row["labor_cost"], row["food_cost"], row["labor_hours"])
                if daily_kpi.get("status") == "success":
                    daily_kpis.append(
                        {
                            "date": row.get("date", "Unknown"),
                            "sales": row["sales"],
                            "labor_percent": daily_kpi["kpis"]["labor_percent"]["value"],
                            "food_percent": daily_kpi["kpis"]["food_percent"]["value"],
                            "prime_percent": daily_kpi["kpis"]["prime_percent"]["value"],
                            "sales_per_hour": daily_kpi["kpis"]["sales_per_labor_hour"]["value"],
                        }
                    )

        if not daily_kpis:
            return {
                "status": "error",
                "message": "No valid data found in CSV",
                "help": "Please ensure your CSV has positive sales values",
            }

        # Calculate averages and trends
        avg_labor_percent = sum(kpi["labor_percent"] for kpi in daily_kpis) / len(daily_kpis)
        avg_food_percent = sum(kpi["food_percent"] for kpi in daily_kpis) / len(daily_kpis)
        avg_prime_percent = sum(kpi["prime_percent"] for kpi in daily_kpis) / len(daily_kpis)
        avg_sales_per_hour = sum(kpi["sales_per_hour"] for kpi in daily_kpis) / len(daily_kpis)
        total_sales = sum(kpi["sales"] for kpi in daily_kpis)

        # Calculate trends (comparing first half vs second half)
        mid_point = len(daily_kpis) // 2
        first_half_avg = sum(kpi["prime_percent"] for kpi in daily_kpis[:mid_point]) / mid_point
        second_half_avg = sum(kpi["prime_percent"] for kpi in daily_kpis[mid_point:]) / (len(daily_kpis) - mid_point)
        trend = (
            "improving" if second_half_avg < first_half_avg else "declining" if second_half_avg > first_half_avg else "stable"
        )

        return {
            "status": "success",
            "file_info": csv_file.name,
            "period_analyzed": f"{len(daily_kpis)} days",
            "summary": {
                "total_sales": f"${total_sales:,.2f}",
                "avg_labor_percent": f"{avg_labor_percent:.1f}%",
                "avg_food_percent": f"{avg_food_percent:.1f}%",
                "avg_prime_percent": f"{avg_prime_percent:.1f}%",
                "avg_sales_per_hour": f"${avg_sales_per_hour:.2f}",
                "trend": trend,
            },
            "daily_kpis": daily_kpis[:30],  # Show last 30 days
            "recommendations": generate_kpi_recommendations(
                avg_labor_percent, avg_food_percent, avg_prime_percent, avg_sales_per_hour
            ),
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"CSV processing error: {str(e)}",
            "help": "Please ensure your CSV has columns: date, sales, labor_cost, food_cost, labor_hours",
        }


def generate_kpi_recommendations(labor_percent, food_percent, prime_percent, sales_per_hour):
    """Generate actionable recommendations based on KPI analysis"""
    recommendations = []

    if labor_percent > 30:
        recommendations.append(
            {
                "category": "Labor Optimization",
                "priority": "High",
                "action": "Review staff scheduling and reduce overtime",
                "impact": f"Could save ${(labor_percent - 30) * 1000:.0f} per $10k in sales",
            }
        )

    if food_percent > 32:
        recommendations.append(
            {
                "category": "Food Cost Control",
                "priority": "High",
                "action": "Audit portion sizes and supplier pricing",
                "impact": f"Could save ${(food_percent - 32) * 1000:.0f} per $10k in sales",
            }
        )

    if sales_per_hour < 50:
        recommendations.append(
            {
                "category": "Sales Performance",
                "priority": "Medium",
                "action": "Improve staff training and upselling techniques",
                "impact": "Could increase revenue by 15-20%",
            }
        )

    if prime_percent > 60:
        recommendations.append(
            {
                "category": "Overall Efficiency",
                "priority": "Critical",
                "action": "Focus on both labor and food cost optimization",
                "impact": "Essential for profitability",
            }
        )

    if not recommendations:
        recommendations.append(
            {
                "category": "Performance",
                "priority": "Maintain",
                "action": "Keep up the excellent work!",
                "impact": "Your KPIs are within industry standards",
            }
        )

    return recommendations


def calculate_liquor_cost_analysis(expected_oz, actual_oz, liquor_cost, total_sales, bottle_cost=0.0, bottle_size_oz=25.0, target_cost_percentage=20.0):
    """
    Calculate comprehensive liquor cost analysis with business report.

    Args:
        expected_oz: Expected liquor usage in ounces
        actual_oz: Actual liquor usage in ounces
        liquor_cost: Total liquor cost
        total_sales: Total sales revenue
        bottle_cost: Cost per bottle
        bottle_size_oz: Bottle size in ounces
        target_cost_percentage: Target liquor cost percentage

    Returns:
        Dictionary with analysis results and business report
    """
    # Calculate key metrics
    variance_oz = actual_oz - expected_oz
    variance_percent = (variance_oz / expected_oz * 100) if expected_oz > 0 else 0

    cost_per_oz = (liquor_cost / actual_oz) if actual_oz > 0 else 0
    liquor_cost_percentage = (liquor_cost / total_sales * 100) if total_sales > 0 else 0

    # Calculate theoretical usage and waste
    theoretical_cost = expected_oz * cost_per_oz
    waste_cost = liquor_cost - theoretical_cost
    waste_percentage = (waste_cost / liquor_cost * 100) if liquor_cost > 0 else 0

    # Performance assessment
    if abs(variance_percent) <= 5 and liquor_cost_percentage <= target_cost_percentage:
        rating = "Excellent"
    elif abs(variance_percent) <= 10 and liquor_cost_percentage <= target_cost_percentage + 2:
        rating = "Good"
    elif abs(variance_percent) <= 15 and liquor_cost_percentage <= target_cost_percentage + 5:
        rating = "Acceptable"
    else:
        rating = "Needs Improvement"

    # Metrics dictionary
    metrics = {
        "expected_oz": expected_oz,
        "actual_oz": actual_oz,
        "variance_oz": variance_oz,
        "variance_percent": variance_percent,
        "liquor_cost": liquor_cost,
        "cost_per_oz": cost_per_oz,
        "liquor_cost_percentage": liquor_cost_percentage,
        "waste_cost": waste_cost,
        "waste_percentage": waste_percentage
    }

    # Performance dictionary
    performance = {
        "rating": rating,
        "variance_status": "Within Target" if abs(variance_percent) <= 5 else "Needs Attention" if abs(variance_percent) <= 10 else "Critical",
        "cost_status": "Optimal" if liquor_cost_percentage <= target_cost_percentage else "High" if liquor_cost_percentage <= target_cost_percentage + 2 else "Critical"
    }

    # Generate recommendations
    recommendations = []

    if abs(variance_percent) > 10:
        recommendations.append("Implement daily liquor inventory tracking to reduce variance")
        recommendations.append("Train staff on proper pouring techniques and portion control")

    if liquor_cost_percentage > target_cost_percentage:
        recommendations.append(f"Review supplier pricing - target cost percentage is {target_cost_percentage}%")
        recommendations.append("Consider negotiating bulk purchase discounts")

    if waste_percentage > 5:
        recommendations.append("Investigate waste sources - implement waste tracking system")
        recommendations.append("Review storage and handling procedures")

    if variance_percent < -10:
        recommendations.append("Check for potential theft or unauthorized usage")
        recommendations.append("Verify inventory counting procedures")

    if not recommendations:
        recommendations.append("Maintain current liquor cost management practices")
        recommendations.append("Continue monitoring variance trends")

    # Industry benchmarks
    benchmarks = {
        "target_cost_percentage": target_cost_percentage,
        "acceptable_variance": "±5%",
        "industry_average_cost_percentage": "18-22%"
    }

    # Additional insights
    additional_data = {
        "cost_efficiency": {
            "theoretical_cost": f"${theoretical_cost:.2f}",
            "actual_cost": f"${liquor_cost:.2f}",
            "efficiency_ratio": f"{(theoretical_cost/liquor_cost*100):.1f}%" if liquor_cost > 0 else "N/A"
        },
        "waste_analysis": {
            "waste_cost": f"${waste_cost:.2f}",
            "waste_percentage": f"{waste_percentage:.1f}%",
            "monthly_waste_impact": f"${waste_cost * 30:.2f}"
        }
    }

    # Generate business report
    business_report_result = format_business_report(
        "Liquor Cost Analysis",
        metrics,
        performance,
        recommendations,
        benchmarks,
        additional_data
    )

    business_report_html = business_report_result.get("business_report_html", "")
    business_report = business_report_result.get("business_report", "")

    return {
        "metrics": metrics,
        "performance": performance,
        "recommendations": recommendations,
        "industry_benchmarks": benchmarks,
        "business_report_html": business_report_html,
        "business_report": business_report
    }


def calculate_inventory_analysis(current_stock, reorder_point, monthly_usage, inventory_value, lead_time_days=7.0, safety_stock=0.0, item_cost=0.0, target_turnover=12.0):
    """
    Calculate comprehensive inventory analysis with business report.

    Args:
        current_stock: Current inventory level
        reorder_point: Reorder point level
        monthly_usage: Monthly usage rate
        inventory_value: Total inventory value
        lead_time_days: Lead time in days
        safety_stock: Safety stock level
        item_cost: Cost per item
        target_turnover: Target inventory turnover rate

    Returns:
        Dictionary with analysis results and business report
    """
    # Calculate key metrics
    days_of_stock = (current_stock / monthly_usage * 30) if monthly_usage > 0 else 0
    reorder_status = "Order Now" if current_stock <= reorder_point else "Adequate Stock"

    # Calculate optimal reorder point
    daily_usage = monthly_usage / 30
    optimal_reorder_point = (daily_usage * lead_time_days) + safety_stock

    # Calculate turnover rate
    annual_usage = monthly_usage * 12
    turnover_rate = (annual_usage / current_stock) if current_stock > 0 else 0

    # Calculate carrying cost
    carrying_cost_percentage = 25.0  # Industry standard
    annual_carrying_cost = inventory_value * (carrying_cost_percentage / 100)

    # Performance assessment
    if turnover_rate >= target_turnover and current_stock > reorder_point:
        rating = "Excellent"
    elif turnover_rate >= target_turnover * 0.8 and current_stock > reorder_point * 0.8:
        rating = "Good"
    elif turnover_rate >= target_turnover * 0.6 and current_stock > reorder_point * 0.6:
        rating = "Acceptable"
    else:
        rating = "Needs Improvement"

    # Metrics dictionary
    metrics = {
        "current_stock": current_stock,
        "reorder_point": reorder_point,
        "monthly_usage": monthly_usage,
        "inventory_value": inventory_value,
        "days_of_stock": days_of_stock,
        "turnover_rate": turnover_rate,
        "optimal_reorder_point": optimal_reorder_point,
        "carrying_cost": annual_carrying_cost
    }

    # Performance dictionary
    performance = {
        "rating": rating,
        "stock_status": reorder_status,
        "turnover_status": "Optimal" if turnover_rate >= target_turnover else "Low" if turnover_rate >= target_turnover * 0.8 else "Critical"
    }

    # Generate recommendations
    recommendations = []

    if current_stock <= reorder_point:
        recommendations.append("Place immediate reorder to avoid stockout")
        recommendations.append("Consider increasing safety stock levels")

    if turnover_rate < target_turnover * 0.8:
        recommendations.append("Review slow-moving inventory and consider promotions")
        recommendations.append("Optimize reorder quantities to reduce carrying costs")

    if days_of_stock > 45:
        recommendations.append("Reduce order quantities to improve cash flow")
        recommendations.append("Implement just-in-time inventory management")

    if abs(optimal_reorder_point - reorder_point) > reorder_point * 0.2:
        recommendations.append(f"Update reorder point to {optimal_reorder_point:.0f} units")
        recommendations.append("Review lead time assumptions with suppliers")

    if not recommendations:
        recommendations.append("Maintain current inventory management practices")
        recommendations.append("Continue monitoring turnover trends")

    # Industry benchmarks
    benchmarks = {
        "target_turnover": target_turnover,
        "optimal_days_of_stock": "15-30 days",
        "industry_carrying_cost": "20-30%"
    }

    # Additional insights
    additional_data = {
        "efficiency_metrics": {
            "stockout_risk": "Low" if current_stock > reorder_point * 1.5 else "Medium" if current_stock > reorder_point else "High",
            "cash_flow_impact": f"${inventory_value * 0.25:.2f} annual carrying cost",
            "reorder_frequency": f"{30/days_of_stock:.1f} times per month" if days_of_stock > 0 else "N/A"
        },
        "optimization_potential": {
            "potential_savings": f"${annual_carrying_cost * 0.2:.2f}",
            "improvement_area": "Turnover Rate" if turnover_rate < target_turnover else "Carrying Cost",
            "next_review_date": "30 days"
        }
    }

    # Generate business report
    business_report_result = format_business_report(
        "Bar Inventory Analysis",
        metrics,
        performance,
        recommendations,
        benchmarks,
        additional_data
    )

    business_report_html = business_report_result.get("business_report_html", "")
    business_report = business_report_result.get("business_report", "")

    return {
        "metrics": metrics,
        "performance": performance,
        "recommendations": recommendations,
        "industry_benchmarks": benchmarks,
        "business_report_html": business_report_html,
        "business_report": business_report
    }


def calculate_pricing_analysis(drink_price, cost_per_drink, sales_volume, competitor_price, target_margin=75.0, market_position="premium", elasticity_factor=1.5):
    """
    Calculate comprehensive pricing analysis with business report.

    Args:
        drink_price: Current drink price
        cost_per_drink: Cost per drink
        sales_volume: Monthly sales volume
        competitor_price: Competitor's price
        target_margin: Target margin percentage
        market_position: Market position (premium, standard, value)
        elasticity_factor: Price elasticity factor

    Returns:
        Dictionary with analysis results and business report
    """
    # Calculate key metrics
    current_margin = ((drink_price - cost_per_drink) / drink_price * 100) if drink_price > 0 else 0
    margin_difference = current_margin - target_margin

    # Calculate optimal price
    optimal_price = cost_per_drink / (1 - target_margin / 100) if target_margin < 100 else cost_per_drink * 2

    # Calculate competitive position
    price_vs_competitor = ((drink_price - competitor_price) / competitor_price * 100) if competitor_price > 0 else 0

    # Calculate revenue impact
    current_revenue = drink_price * sales_volume
    optimal_revenue = optimal_price * sales_volume

    # Calculate elasticity impact
    price_change_percent = ((optimal_price - drink_price) / drink_price * 100) if drink_price > 0 else 0
    volume_change_percent = -price_change_percent * elasticity_factor
    new_volume = sales_volume * (1 + volume_change_percent / 100)
    elasticity_revenue = optimal_price * new_volume

    # Performance assessment
    if current_margin >= target_margin and abs(price_vs_competitor) <= 10:
        rating = "Excellent"
    elif current_margin >= target_margin * 0.9 and abs(price_vs_competitor) <= 20:
        rating = "Good"
    elif current_margin >= target_margin * 0.8 and abs(price_vs_competitor) <= 30:
        rating = "Acceptable"
    else:
        rating = "Needs Improvement"

    # Metrics dictionary
    metrics = {
        "drink_price": drink_price,
        "cost_per_drink": cost_per_drink,
        "current_margin": current_margin,
        "target_margin": target_margin,
        "margin_difference": margin_difference,
        "optimal_price": optimal_price,
        "competitor_price": competitor_price,
        "price_vs_competitor": price_vs_competitor,
        "sales_volume": sales_volume,
        "current_revenue": current_revenue,
        "optimal_revenue": optimal_revenue,
        "elasticity_revenue": elasticity_revenue
    }

    # Performance dictionary
    performance = {
        "rating": rating,
        "margin_status": "Optimal" if current_margin >= target_margin else "Low" if current_margin >= target_margin * 0.8 else "Critical",
        "competitive_status": "Competitive" if abs(price_vs_competitor) <= 10 else "Premium" if price_vs_competitor > 10 else "Value"
    }

    # Generate recommendations
    recommendations = []

    if current_margin < target_margin:
        recommendations.append(f"Consider price increase to ${optimal_price:.2f} to achieve target margin")
        recommendations.append("Review cost structure and supplier negotiations")

    if price_vs_competitor > 20:
        recommendations.append("Consider price reduction to remain competitive")
        recommendations.append("Focus on value proposition and quality differentiation")

    if price_vs_competitor < -20:
        recommendations.append("Opportunity to increase prices while maintaining competitive advantage")
        recommendations.append("Invest in marketing to justify premium positioning")

    if elasticity_revenue > current_revenue * 1.1:
        recommendations.append("Price optimization could increase revenue by 10%+")
        recommendations.append("Test price changes in small increments")

    if market_position == "premium" and price_vs_competitor < 0:
        recommendations.append("Align pricing with premium market positioning")
        recommendations.append("Enhance product presentation and service quality")

    if not recommendations:
        recommendations.append("Maintain current pricing strategy")
        recommendations.append("Continue monitoring competitive landscape")

    # Industry benchmarks
    benchmarks = {
        "target_margin": target_margin,
        "industry_margin_range": "70-80%",
        "competitive_tolerance": "±10%"
    }

    # Additional insights
    additional_data = {
        "pricing_strategy": {
            "market_position": market_position.title(),
            "elasticity_factor": elasticity_factor,
            "recommended_action": "Maintain" if rating == "Excellent" else "Optimize" if rating == "Good" else "Review"
        },
        "revenue_optimization": {
            "current_monthly_revenue": f"${current_revenue:,.2f}",
            "potential_increase": f"${max(optimal_revenue, elasticity_revenue) - current_revenue:,.2f}",
            "roi_timeline": "Immediate"
        }
    }

    # Generate business report
    business_report_result = format_business_report(
        "Beverage Pricing Analysis",
        metrics,
        performance,
        recommendations,
        benchmarks,
        additional_data
    )

    business_report_html = business_report_result.get("business_report_html", "")
    business_report = business_report_result.get("business_report", "")

    return {
        "metrics": metrics,
        "performance": performance,
        "recommendations": recommendations,
        "industry_benchmarks": benchmarks,
        "business_report_html": business_report_html,
        "business_report": business_report
    }
