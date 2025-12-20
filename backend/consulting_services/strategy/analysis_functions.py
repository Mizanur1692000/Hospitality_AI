"""
Strategic Analysis Functions
Contains the core business logic for strategic planning analysis.
"""

from backend.consulting_services.kpi.kpi_utils import format_business_report


def calculate_sales_forecasting_analysis(historical_sales, current_sales, growth_rate, seasonal_factor, forecast_periods=12.0, trend_strength=0.5, market_growth=5.0, confidence_level=85.0):
    """Calculate comprehensive sales forecasting analysis with business report."""
    # Calculate key metrics
    sales_growth = ((current_sales - historical_sales) / historical_sales * 100) if historical_sales > 0 else 0
    projected_sales = current_sales * (1 + growth_rate / 100) * seasonal_factor
    forecast_accuracy = min(100, confidence_level + (trend_strength * 10))

    # Calculate forecasting metrics
    trend_analysis = growth_rate * trend_strength
    market_alignment = min(100, (growth_rate / market_growth) * 100) if market_growth > 0 else 0
    seasonal_adjustment = abs(seasonal_factor - 1.0) * 100

    # Performance assessment
    if forecast_accuracy >= 90 and market_alignment >= 80 and sales_growth >= market_growth:
        rating = "Excellent"
    elif forecast_accuracy >= 80 and market_alignment >= 70 and sales_growth >= market_growth * 0.8:
        rating = "Good"
    elif forecast_accuracy >= 70 and market_alignment >= 60 and sales_growth >= market_growth * 0.6:
        rating = "Acceptable"
    else:
        rating = "Needs Improvement"

    # Metrics dictionary
    metrics = {
        "historical_sales": historical_sales,
        "current_sales": current_sales,
        "growth_rate": growth_rate,
        "seasonal_factor": seasonal_factor,
        "forecast_periods": forecast_periods,
        "trend_strength": trend_strength,
        "market_growth": market_growth,
        "confidence_level": confidence_level,
        "sales_growth": sales_growth,
        "projected_sales": projected_sales,
        "forecast_accuracy": forecast_accuracy,
        "trend_analysis": trend_analysis,
        "market_alignment": market_alignment,
        "seasonal_adjustment": seasonal_adjustment
    }

    # Performance dictionary
    performance = {
        "rating": rating,
        "forecast_status": "Accurate" if forecast_accuracy >= 85 else "Good" if forecast_accuracy >= 75 else "Needs Review",
        "growth_status": "Strong" if sales_growth >= market_growth else "Moderate" if sales_growth >= market_growth * 0.8 else "Weak"
    }

    # Generate recommendations
    recommendations = []

    if forecast_accuracy < 80:
        recommendations.append("Improve data collection and analysis methods")
        recommendations.append("Implement advanced forecasting techniques")

    if market_alignment < 70:
        recommendations.append("Align growth strategy with market trends")
        recommendations.append("Review competitive positioning")

    if seasonal_adjustment > 20:
        recommendations.append("Develop seasonal adjustment strategies")
        recommendations.append("Implement inventory management for seasonal variations")

    if sales_growth < market_growth * 0.8:
        recommendations.append("Focus on market penetration strategies")
        recommendations.append("Review pricing and marketing approaches")

    if trend_strength < 0.6:
        recommendations.append("Strengthen trend analysis capabilities")
        recommendations.append("Invest in predictive analytics tools")

    if not recommendations:
        recommendations.append("Maintain current forecasting strategy")
        recommendations.append("Continue monitoring market trends and performance")

    # Industry benchmarks
    benchmarks = {
        "target_accuracy": "≥85%",
        "market_growth_alignment": "≥80%",
        "seasonal_variance": "≤15%"
    }

    # Additional insights
    additional_data = {
        "forecasting_insights": {
            "next_quarter_projection": f"${projected_sales:,.2f}",
            "confidence_interval": f"±{100 - confidence_level:.0f}%",
            "trend_direction": "Positive" if growth_rate > 0 else "Negative"
        },
        "performance_insights": {
            "forecast_trend": "Improving" if forecast_accuracy >= 85 else "Stable" if forecast_accuracy >= 75 else "Declining",
            "market_position": "Leading" if market_alignment >= 90 else "Competitive" if market_alignment >= 70 else "Lagging",
            "next_review": "30 days"
        }
    }

    # Generate business report
    business_report_result = format_business_report(
        "Sales Forecasting Analysis",
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


def calculate_growth_strategy_analysis(market_size, market_share, competition_level, investment_budget, growth_potential=15.0, competitive_advantage=7.0, market_penetration=5.0, roi_target=20.0):
    """Calculate comprehensive growth strategy analysis with business report."""
    # Calculate key metrics
    market_opportunity = market_size * (100 - market_share) / 100
    competitive_position = (competitive_advantage / 10) * 100
    growth_score = (growth_potential + competitive_advantage + market_penetration) / 3

    # Calculate strategy metrics
    market_penetration_potential = min(100, (market_opportunity / market_size) * 100) if market_size > 0 else 0
    investment_efficiency = (roi_target / investment_budget * 100) if investment_budget > 0 else 0
    competitive_threat = max(0, 100 - (competition_level * 10))

    # Performance assessment
    if growth_score >= 8 and competitive_position >= 80 and market_penetration_potential >= 70:
        rating = "Excellent"
    elif growth_score >= 6 and competitive_position >= 70 and market_penetration_potential >= 50:
        rating = "Good"
    elif growth_score >= 4 and competitive_position >= 60 and market_penetration_potential >= 30:
        rating = "Acceptable"
    else:
        rating = "Needs Improvement"

    # Metrics dictionary
    metrics = {
        "market_size": market_size,
        "market_share": market_share,
        "competition_level": competition_level,
        "investment_budget": investment_budget,
        "growth_potential": growth_potential,
        "competitive_advantage": competitive_advantage,
        "market_penetration": market_penetration,
        "roi_target": roi_target,
        "market_opportunity": market_opportunity,
        "competitive_position": competitive_position,
        "growth_score": growth_score,
        "market_penetration_potential": market_penetration_potential,
        "investment_efficiency": investment_efficiency,
        "competitive_threat": competitive_threat
    }

    # Performance dictionary
    performance = {
        "rating": rating,
        "growth_status": "High" if growth_score >= 8 else "Medium" if growth_score >= 6 else "Low",
        "competitive_status": "Strong" if competitive_position >= 80 else "Moderate" if competitive_position >= 70 else "Weak"
    }

    # Generate recommendations
    recommendations = []

    if growth_score < 6:
        recommendations.append("Develop comprehensive growth strategy")
        recommendations.append("Identify new market opportunities")

    if competitive_position < 70:
        recommendations.append("Strengthen competitive advantages")
        recommendations.append("Invest in differentiation strategies")

    if market_penetration_potential < 50:
        recommendations.append("Focus on market expansion")
        recommendations.append("Develop new customer segments")

    if investment_efficiency < 15:
        recommendations.append("Optimize investment allocation")
        recommendations.append("Review ROI targets and expectations")

    if competitive_threat > 70:
        recommendations.append("Monitor competitive landscape closely")
        recommendations.append("Develop defensive strategies")

    if not recommendations:
        recommendations.append("Maintain current growth strategy")
        recommendations.append("Continue monitoring market opportunities")

    # Industry benchmarks
    benchmarks = {
        "target_growth_score": "≥8.0",
        "competitive_threshold": "≥80%",
        "market_penetration_goal": "≥70%"
    }

    # Additional insights
    additional_data = {
        "growth_opportunities": {
            "market_opportunity_value": f"${market_opportunity:,.2f}",
            "penetration_potential": f"{market_penetration_potential:.1f}%",
            "investment_roi": f"{roi_target:.1f}%"
        },
        "performance_insights": {
            "growth_trend": "Accelerating" if growth_score >= 8 else "Stable" if growth_score >= 6 else "Slowing",
            "competitive_trend": "Strengthening" if competitive_position >= 80 else "Stable" if competitive_position >= 70 else "Weakening",
            "next_review": "90 days"
        }
    }

    # Generate business report
    business_report_result = format_business_report(
        "Growth Strategy Analysis",
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


def calculate_operational_excellence_analysis(efficiency_score, process_time, quality_rating, customer_satisfaction, cost_per_unit=0.0, waste_percentage=0.0, employee_productivity=8.0, benchmark_score=85.0):
    """Calculate comprehensive operational excellence analysis with business report."""
    # Calculate key metrics
    operational_score = (efficiency_score + quality_rating + customer_satisfaction) / 3
    process_efficiency = (benchmark_score / process_time) if process_time > 0 else 0
    cost_efficiency = (100 - waste_percentage) * (efficiency_score / 10)

    # Calculate excellence metrics
    productivity_index = (employee_productivity / 10) * 100
    quality_index = (quality_rating / 10) * 100
    customer_index = (customer_satisfaction / 10) * 100
    excellence_score = (operational_score + productivity_index + quality_index + customer_index) / 4

    # Performance assessment
    if excellence_score >= 85 and process_efficiency >= 80 and cost_efficiency >= 75:
        rating = "Excellent"
    elif excellence_score >= 75 and process_efficiency >= 70 and cost_efficiency >= 65:
        rating = "Good"
    elif excellence_score >= 65 and process_efficiency >= 60 and cost_efficiency >= 55:
        rating = "Acceptable"
    else:
        rating = "Needs Improvement"

    # Metrics dictionary
    metrics = {
        "efficiency_score": efficiency_score,
        "process_time": process_time,
        "quality_rating": quality_rating,
        "customer_satisfaction": customer_satisfaction,
        "cost_per_unit": cost_per_unit,
        "waste_percentage": waste_percentage,
        "employee_productivity": employee_productivity,
        "benchmark_score": benchmark_score,
        "operational_score": operational_score,
        "process_efficiency": process_efficiency,
        "cost_efficiency": cost_efficiency,
        "productivity_index": productivity_index,
        "quality_index": quality_index,
        "customer_index": customer_index,
        "excellence_score": excellence_score
    }

    # Performance dictionary
    performance = {
        "rating": rating,
        "efficiency_status": "High" if efficiency_score >= 8 else "Medium" if efficiency_score >= 6 else "Low",
        "quality_status": "High" if quality_rating >= 8 else "Medium" if quality_rating >= 6 else "Low"
    }

    # Generate recommendations
    recommendations = []

    if excellence_score < 75:
        recommendations.append("Implement operational excellence framework")
        recommendations.append("Develop process improvement initiatives")

    if process_efficiency < 70:
        recommendations.append("Optimize process workflows")
        recommendations.append("Implement lean manufacturing principles")

    if cost_efficiency < 65:
        recommendations.append("Reduce waste and improve cost management")
        recommendations.append("Implement cost control measures")

    if productivity_index < 70:
        recommendations.append("Enhance employee training and development")
        recommendations.append("Implement productivity improvement programs")

    if quality_index < 80:
        recommendations.append("Strengthen quality control processes")
        recommendations.append("Implement quality management systems")

    if customer_index < 85:
        recommendations.append("Improve customer service processes")
        recommendations.append("Implement customer feedback systems")

    if not recommendations:
        recommendations.append("Maintain current operational excellence standards")
        recommendations.append("Continue monitoring performance metrics")

    # Industry benchmarks
    benchmarks = {
        "excellence_threshold": "≥85%",
        "process_efficiency_goal": "≥80%",
        "quality_standard": "≥90%"
    }

    # Additional insights
    additional_data = {
        "operational_insights": {
            "efficiency_gap": f"{benchmark_score - excellence_score:.1f} points",
            "improvement_potential": f"${cost_per_unit * (100 - cost_efficiency) / 100:.2f}",
            "productivity_trend": "Improving" if productivity_index >= 80 else "Stable" if productivity_index >= 70 else "Declining"
        },
        "performance_insights": {
            "excellence_trend": "Improving" if excellence_score >= 85 else "Stable" if excellence_score >= 75 else "Declining",
            "quality_trend": "High" if quality_index >= 90 else "Medium" if quality_index >= 80 else "Low",
            "next_review": "60 days"
        }
    }

    # Generate business report
    business_report_result = format_business_report(
        "Operational Excellence Analysis",
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
