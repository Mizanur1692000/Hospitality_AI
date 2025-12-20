"""
Recipe Analysis Functions
Contains the core business logic for recipe management analysis.
"""

from backend.consulting_services.kpi.kpi_utils import format_business_report


def calculate_recipe_costing_analysis(ingredient_cost, portion_cost, recipe_price, total_cost, portion_size=1.0, servings=1.0, target_margin=70.0, labor_cost=0.0):
    """Calculate comprehensive recipe costing analysis with business report."""
    # Calculate key metrics
    total_recipe_cost = ingredient_cost + labor_cost
    cost_per_portion = total_recipe_cost / servings if servings > 0 else total_recipe_cost
    profit_margin = ((recipe_price - cost_per_portion) / recipe_price * 100) if recipe_price > 0 else 0
    margin_difference = profit_margin - target_margin

    # Calculate cost efficiency
    ingredient_cost_percentage = (ingredient_cost / total_recipe_cost * 100) if total_recipe_cost > 0 else 0
    labor_cost_percentage = (labor_cost / total_recipe_cost * 100) if total_recipe_cost > 0 else 0

    # Performance assessment
    if profit_margin >= target_margin and ingredient_cost_percentage <= 60:
        rating = "Excellent"
    elif profit_margin >= target_margin * 0.9 and ingredient_cost_percentage <= 70:
        rating = "Good"
    elif profit_margin >= target_margin * 0.8 and ingredient_cost_percentage <= 80:
        rating = "Acceptable"
    else:
        rating = "Needs Improvement"

    # Metrics dictionary
    metrics = {
        "ingredient_cost": ingredient_cost,
        "portion_cost": portion_cost,
        "recipe_price": recipe_price,
        "total_cost": total_cost,
        "portion_size": portion_size,
        "servings": servings,
        "total_recipe_cost": total_recipe_cost,
        "cost_per_portion": cost_per_portion,
        "profit_margin": profit_margin,
        "margin_difference": margin_difference,
        "ingredient_cost_percentage": ingredient_cost_percentage,
        "labor_cost_percentage": labor_cost_percentage
    }

    # Performance dictionary
    performance = {
        "rating": rating,
        "margin_status": "Optimal" if profit_margin >= target_margin else "Low" if profit_margin >= target_margin * 0.8 else "Critical",
        "cost_efficiency": "High" if ingredient_cost_percentage <= 60 else "Medium" if ingredient_cost_percentage <= 70 else "Low"
    }

    # Generate recommendations
    recommendations = []

    if profit_margin < target_margin:
        recommendations.append("Review recipe pricing to achieve target profit margins")
        recommendations.append("Analyze ingredient costs and portion sizes")

    if ingredient_cost_percentage > 70:
        recommendations.append("Negotiate better supplier pricing for ingredients")
        recommendations.append("Review portion sizes to optimize cost structure")

    if labor_cost_percentage > 30:
        recommendations.append("Optimize preparation processes to reduce labor costs")
        recommendations.append("Consider batch preparation for efficiency")

    if cost_per_portion > recipe_price * 0.4:
        recommendations.append("Review recipe formulation for cost optimization")
        recommendations.append("Consider ingredient substitutions")

    if not recommendations:
        recommendations.append("Maintain current recipe costing strategy")
        recommendations.append("Continue monitoring cost trends and margins")

    # Industry benchmarks
    benchmarks = {
        "target_margin": target_margin,
        "optimal_ingredient_cost": "50-60%",
        "optimal_labor_cost": "20-30%"
    }

    # Additional insights
    additional_data = {
        "cost_optimization": {
            "potential_savings": f"${max(0, (target_margin - profit_margin) * recipe_price / 100):.2f}",
            "cost_per_serving": f"${cost_per_portion:.2f}",
            "margin_improvement": f"{max(0, target_margin - profit_margin):.1f}%"
        },
        "performance_insights": {
            "cost_trend": "Optimized" if profit_margin >= target_margin else "Needs Review",
            "efficiency_rating": "High" if ingredient_cost_percentage <= 60 else "Medium" if ingredient_cost_percentage <= 70 else "Low",
            "next_review": "30 days"
        }
    }

    # Generate business report
    business_report_result = format_business_report(
        "Recipe Costing Analysis",
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


def calculate_ingredient_optimization_analysis(current_cost, supplier_cost, waste_percentage, quality_score, usage_volume=0.0, supplier_count=1.0, consistency_score=8.0, storage_cost=0.0):
    """Calculate comprehensive ingredient optimization analysis with business report."""
    # Calculate key metrics
    cost_savings = current_cost - supplier_cost if supplier_cost > 0 else 0
    savings_percentage = (cost_savings / current_cost * 100) if current_cost > 0 else 0
    total_cost = current_cost + storage_cost
    optimization_score = (quality_score + consistency_score) / 2

    # Calculate efficiency metrics
    waste_cost = (waste_percentage / 100) * current_cost
    effective_cost = current_cost - waste_cost
    cost_per_unit = effective_cost / usage_volume if usage_volume > 0 else effective_cost

    # Performance assessment
    if savings_percentage >= 15 and optimization_score >= 8 and waste_percentage <= 5:
        rating = "Excellent"
    elif savings_percentage >= 10 and optimization_score >= 7 and waste_percentage <= 10:
        rating = "Good"
    elif savings_percentage >= 5 and optimization_score >= 6 and waste_percentage <= 15:
        rating = "Acceptable"
    else:
        rating = "Needs Improvement"

    # Metrics dictionary
    metrics = {
        "current_cost": current_cost,
        "supplier_cost": supplier_cost,
        "waste_percentage": waste_percentage,
        "quality_score": quality_score,
        "usage_volume": usage_volume,
        "supplier_count": supplier_count,
        "consistency_score": consistency_score,
        "storage_cost": storage_cost,
        "cost_savings": cost_savings,
        "savings_percentage": savings_percentage,
        "total_cost": total_cost,
        "optimization_score": optimization_score,
        "waste_cost": waste_cost,
        "effective_cost": effective_cost,
        "cost_per_unit": cost_per_unit
    }

    # Performance dictionary
    performance = {
        "rating": rating,
        "cost_status": "Optimized" if savings_percentage >= 15 else "Good" if savings_percentage >= 10 else "Needs Review",
        "quality_status": "High" if optimization_score >= 8 else "Medium" if optimization_score >= 7 else "Low"
    }

    # Generate recommendations
    recommendations = []

    if savings_percentage < 10:
        recommendations.append("Explore alternative suppliers for better pricing")
        recommendations.append("Negotiate volume discounts with current suppliers")

    if waste_percentage > 10:
        recommendations.append("Implement better inventory management to reduce waste")
        recommendations.append("Review storage conditions and shelf life")

    if optimization_score < 7:
        recommendations.append("Improve quality control processes")
        recommendations.append("Standardize supplier selection criteria")

    if storage_cost > current_cost * 0.1:
        recommendations.append("Optimize storage and inventory management")
        recommendations.append("Consider just-in-time ordering")

    if supplier_count < 2:
        recommendations.append("Diversify supplier base to reduce risk")
        recommendations.append("Establish backup supplier relationships")

    if not recommendations:
        recommendations.append("Maintain current ingredient optimization strategy")
        recommendations.append("Continue monitoring supplier performance")

    # Industry benchmarks
    benchmarks = {
        "target_savings": "10-15%",
        "optimal_waste": "≤5%",
        "quality_threshold": "≥8.0"
    }

    # Additional insights
    additional_data = {
        "supplier_optimization": {
            "monthly_savings": f"${cost_savings * 30:.2f}",
            "annual_savings": f"${cost_savings * 365:.2f}",
            "roi_timeline": "Immediate"
        },
        "performance_insights": {
            "optimization_trend": "Improving" if savings_percentage >= 10 else "Stable" if savings_percentage >= 5 else "Declining",
            "quality_trend": "High" if optimization_score >= 8 else "Medium" if optimization_score >= 7 else "Low",
            "next_review": "30 days"
        }
    }

    # Generate business report
    business_report_result = format_business_report(
        "Ingredient Optimization Analysis",
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


def calculate_recipe_scaling_analysis(current_batch, target_batch, yield_percentage, consistency_score, base_recipe_cost=0.0, scaling_factor=1.0, quality_threshold=85.0, efficiency_score=8.0):
    """Calculate comprehensive recipe scaling analysis with business report."""
    # Calculate key metrics
    batch_difference = target_batch - current_batch
    scaling_ratio = target_batch / current_batch if current_batch > 0 else 1.0
    scaled_cost = base_recipe_cost * scaling_ratio
    cost_efficiency = (yield_percentage / 100) * (efficiency_score / 10)

    # Calculate scaling metrics
    yield_efficiency = yield_percentage / 100
    consistency_rating = consistency_score / 10
    scaling_score = (yield_efficiency + consistency_rating + (efficiency_score / 10)) / 3

    # Performance assessment
    if scaling_score >= 0.8 and yield_percentage >= 90 and consistency_score >= 8:
        rating = "Excellent"
    elif scaling_score >= 0.7 and yield_percentage >= 85 and consistency_score >= 7:
        rating = "Good"
    elif scaling_score >= 0.6 and yield_percentage >= 80 and consistency_score >= 6:
        rating = "Acceptable"
    else:
        rating = "Needs Improvement"

    # Metrics dictionary
    metrics = {
        "current_batch": current_batch,
        "target_batch": target_batch,
        "yield_percentage": yield_percentage,
        "consistency_score": consistency_score,
        "base_recipe_cost": base_recipe_cost,
        "scaling_factor": scaling_factor,
        "quality_threshold": quality_threshold,
        "efficiency_score": efficiency_score,
        "batch_difference": batch_difference,
        "scaling_ratio": scaling_ratio,
        "scaled_cost": scaled_cost,
        "cost_efficiency": cost_efficiency,
        "yield_efficiency": yield_efficiency,
        "consistency_rating": consistency_rating,
        "scaling_score": scaling_score
    }

    # Performance dictionary
    performance = {
        "rating": rating,
        "scaling_status": "Optimal" if scaling_score >= 0.8 else "Good" if scaling_score >= 0.7 else "Needs Work",
        "yield_status": "High" if yield_percentage >= 90 else "Medium" if yield_percentage >= 85 else "Low"
    }

    # Generate recommendations
    recommendations = []

    if yield_percentage < 85:
        recommendations.append("Review recipe scaling ratios for better yield")
        recommendations.append("Optimize preparation techniques for consistency")

    if consistency_score < 7:
        recommendations.append("Standardize measurement and preparation processes")
        recommendations.append("Implement quality control checkpoints")

    if scaling_score < 0.7:
        recommendations.append("Test recipe scaling in smaller increments")
        recommendations.append("Document scaling adjustments for consistency")

    if cost_efficiency < 0.7:
        recommendations.append("Optimize batch sizes for cost efficiency")
        recommendations.append("Review ingredient ratios for scaling")

    if batch_difference > current_batch * 0.5:
        recommendations.append("Consider gradual scaling to maintain quality")
        recommendations.append("Test scaled recipes before full implementation")

    if not recommendations:
        recommendations.append("Maintain current recipe scaling strategy")
        recommendations.append("Continue monitoring scaling performance")

    # Industry benchmarks
    benchmarks = {
        "optimal_yield": "≥90%",
        "consistency_threshold": "≥8.0",
        "scaling_efficiency": "≥0.8"
    }

    # Additional insights
    additional_data = {
        "scaling_optimization": {
            "cost_per_unit": f"${scaled_cost / target_batch:.2f}",
            "efficiency_gain": f"{(scaling_score - 0.6) * 100:.1f}%",
            "quality_maintenance": "High" if consistency_score >= 8 else "Medium" if consistency_score >= 7 else "Low"
        },
        "performance_insights": {
            "scaling_trend": "Improving" if scaling_score >= 0.8 else "Stable" if scaling_score >= 0.7 else "Declining",
            "yield_trend": "High" if yield_percentage >= 90 else "Medium" if yield_percentage >= 85 else "Low",
            "next_review": "30 days"
        }
    }

    # Generate business report
    business_report_result = format_business_report(
        "Recipe Scaling Analysis",
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
