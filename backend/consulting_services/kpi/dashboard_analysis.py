"""
KPI Dashboard Analysis Functions
Contains the core business logic for KPI dashboard analysis.
"""

from backend.consulting_services.kpi.kpi_utils import format_business_report


def calculate_comprehensive_analysis(total_sales, labor_cost, food_cost, prime_cost, hours_worked=0.0, hourly_rate=0.0, previous_sales=0.0, target_margin=70.0):
    """Calculate comprehensive analysis with multi-metric analysis and industry benchmarking."""
    # Calculate key metrics
    total_costs = labor_cost + food_cost
    prime_cost_percentage = (total_costs / total_sales * 100) if total_sales > 0 else 0
    labor_percentage = (labor_cost / total_sales * 100) if total_sales > 0 else 0
    food_percentage = (food_cost / total_sales * 100) if total_sales > 0 else 0

    # Calculate efficiency metrics
    sales_per_hour = total_sales / hours_worked if hours_worked > 0 else 0
    labor_efficiency = (total_sales / labor_cost) if labor_cost > 0 else 0
    cost_efficiency = (total_sales / total_costs) if total_costs > 0 else 0

    # Calculate growth metrics
    sales_growth = ((total_sales - previous_sales) / previous_sales * 100) if previous_sales > 0 else 0
    performance_score = (target_margin - prime_cost_percentage) / target_margin * 100 if target_margin > 0 else 0

    # Performance assessment
    if prime_cost_percentage <= 60 and performance_score >= 80 and sales_growth >= 10:
        rating = "Excellent"
    elif prime_cost_percentage <= 65 and performance_score >= 70 and sales_growth >= 5:
        rating = "Good"
    elif prime_cost_percentage <= 70 and performance_score >= 60 and sales_growth >= 0:
        rating = "Acceptable"
    else:
        rating = "Needs Improvement"

    # Metrics dictionary
    metrics = {
        "total_sales": total_sales,
        "labor_cost": labor_cost,
        "food_cost": food_cost,
        "prime_cost": prime_cost,
        "hours_worked": hours_worked,
        "hourly_rate": hourly_rate,
        "previous_sales": previous_sales,
        "target_margin": target_margin,
        "total_costs": total_costs,
        "prime_cost_percentage": prime_cost_percentage,
        "labor_percentage": labor_percentage,
        "food_percentage": food_percentage,
        "sales_per_hour": sales_per_hour,
        "labor_efficiency": labor_efficiency,
        "cost_efficiency": cost_efficiency,
        "sales_growth": sales_growth,
        "performance_score": performance_score
    }

    # Performance dictionary
    performance = {
        "rating": rating,
        "cost_status": "Optimal" if prime_cost_percentage <= 60 else "Good" if prime_cost_percentage <= 65 else "Needs Review",
        "efficiency_status": "High" if performance_score >= 80 else "Medium" if performance_score >= 70 else "Low"
    }

    # Generate recommendations
    recommendations = []

    if prime_cost_percentage > 65:
        recommendations.append("Optimize prime cost structure to improve profitability")
        recommendations.append("Review labor and food cost management strategies")

    if labor_percentage > 35:
        recommendations.append("Improve labor efficiency and scheduling")
        recommendations.append("Consider automation and process optimization")

    if food_percentage > 35:
        recommendations.append("Optimize food cost through better purchasing and portion control")
        recommendations.append("Review menu pricing and ingredient costs")

    if sales_per_hour < 100:
        recommendations.append("Increase sales velocity through better marketing and service")
        recommendations.append("Optimize operational efficiency")

    if sales_growth < 5:
        recommendations.append("Develop growth strategies to increase revenue")
        recommendations.append("Focus on customer acquisition and retention")

    if performance_score < 70:
        recommendations.append("Implement performance improvement initiatives")
        recommendations.append("Set specific targets and track progress regularly")

    if not recommendations:
        recommendations.append("Maintain current performance levels")
        recommendations.append("Continue monitoring key performance indicators")

    # Industry benchmarks
    benchmarks = {
        "optimal_prime_cost": "≤60%",
        "target_labor_cost": "≤30%",
        "target_food_cost": "≤30%",
        "sales_growth_target": "≥10%"
    }

    # Additional insights
    additional_data = {
        "comprehensive_insights": {
            "overall_score": f"{performance_score:.1f}/100",
            "cost_optimization_potential": f"${total_costs * 0.1:.2f}",
            "efficiency_rating": "High" if performance_score >= 80 else "Medium" if performance_score >= 70 else "Low"
        },
        "performance_insights": {
            "trend_direction": "Improving" if sales_growth >= 10 else "Stable" if sales_growth >= 5 else "Declining",
            "benchmark_comparison": "Above Industry" if performance_score >= 80 else "Industry Average" if performance_score >= 70 else "Below Industry",
            "next_review": "30 days"
        }
    }

    # Generate business report
    business_report_result = format_business_report(
        "Comprehensive Analysis",
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


def calculate_performance_optimization(current_performance, target_performance, optimization_potential, efficiency_score, baseline_metrics=0.0, improvement_rate=10.0, goal_timeframe=90.0, progress_tracking=8.0):
    """Calculate performance optimization with actionable recommendations and goal setting."""
    # Calculate key metrics
    performance_gap = target_performance - current_performance
    optimization_score = (optimization_potential / 100) * (efficiency_score / 10)
    improvement_potential = (performance_gap / current_performance * 100) if current_performance > 0 else 0

    # Calculate optimization metrics
    goal_achievement_rate = (current_performance / target_performance * 100) if target_performance > 0 else 0
    efficiency_rating = (efficiency_score / 10) * 100
    progress_score = (progress_tracking / 10) * 100
    overall_optimization_score = (optimization_score + efficiency_rating + progress_score) / 3

    # Performance assessment
    if overall_optimization_score >= 85 and goal_achievement_rate >= 90 and improvement_potential >= 15:
        rating = "Excellent"
    elif overall_optimization_score >= 75 and goal_achievement_rate >= 80 and improvement_potential >= 10:
        rating = "Good"
    elif overall_optimization_score >= 65 and goal_achievement_rate >= 70 and improvement_potential >= 5:
        rating = "Acceptable"
    else:
        rating = "Needs Improvement"

    # Metrics dictionary
    metrics = {
        "current_performance": current_performance,
        "target_performance": target_performance,
        "optimization_potential": optimization_potential,
        "efficiency_score": efficiency_score,
        "baseline_metrics": baseline_metrics,
        "improvement_rate": improvement_rate,
        "goal_timeframe": goal_timeframe,
        "progress_tracking": progress_tracking,
        "performance_gap": performance_gap,
        "optimization_score": optimization_score,
        "improvement_potential": improvement_potential,
        "goal_achievement_rate": goal_achievement_rate,
        "efficiency_rating": efficiency_rating,
        "progress_score": progress_score,
        "overall_optimization_score": overall_optimization_score
    }

    # Performance dictionary
    performance = {
        "rating": rating,
        "optimization_status": "High" if overall_optimization_score >= 85 else "Medium" if overall_optimization_score >= 75 else "Low",
        "goal_status": "On Track" if goal_achievement_rate >= 90 else "Behind" if goal_achievement_rate >= 70 else "At Risk"
    }

    # Generate recommendations
    recommendations = []

    if overall_optimization_score < 75:
        recommendations.append("Implement comprehensive performance optimization strategy")
        recommendations.append("Focus on efficiency improvements and process optimization")

    if goal_achievement_rate < 80:
        recommendations.append("Review and adjust performance goals")
        recommendations.append("Implement targeted improvement initiatives")

    if improvement_potential < 10:
        recommendations.append("Identify new optimization opportunities")
        recommendations.append("Explore innovative approaches to performance enhancement")

    if efficiency_rating < 70:
        recommendations.append("Improve operational efficiency through better processes")
        recommendations.append("Invest in training and development programs")

    if progress_tracking < 7:
        recommendations.append("Implement robust progress tracking systems")
        recommendations.append("Establish regular performance review cycles")

    if performance_gap > current_performance * 0.2:
        recommendations.append("Develop action plan to close performance gap")
        recommendations.append("Set intermediate milestones for goal achievement")

    if not recommendations:
        recommendations.append("Maintain current optimization strategies")
        recommendations.append("Continue monitoring performance improvements")

    # Industry benchmarks
    benchmarks = {
        "target_optimization_score": "≥85%",
        "goal_achievement_threshold": "≥90%",
        "improvement_potential_target": "≥15%"
    }

    # Additional insights
    additional_data = {
        "optimization_insights": {
            "improvement_timeline": f"{goal_timeframe:.0f} days",
            "potential_gain": f"{improvement_potential:.1f}%",
            "optimization_priority": "High" if overall_optimization_score < 75 else "Medium" if overall_optimization_score < 85 else "Low"
        },
        "performance_insights": {
            "optimization_trend": "Improving" if overall_optimization_score >= 85 else "Stable" if overall_optimization_score >= 75 else "Declining",
            "goal_progress": "On Track" if goal_achievement_rate >= 90 else "Behind" if goal_achievement_rate >= 70 else "At Risk",
            "next_review": "30 days"
        }
    }

    # Generate business report
    business_report_result = format_business_report(
        "Performance Optimization Analysis",
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
