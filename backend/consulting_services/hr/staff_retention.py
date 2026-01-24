"""
HR Staff Retention Analysis Task
Analyzes turnover rates and provides retention strategies with comprehensive business report.
"""

from backend.shared.utils.common import success_payload, error_payload, require, validate_positive_numbers


def run(params: dict, file_bytes: bytes | None = None) -> tuple[dict, int]:
    """
    Calculate staff retention analysis with comprehensive business report.

    Args:
        params: Dictionary containing turnover_rate and industry_average
        file_bytes: Optional file data (not used in this task)

    Returns:
        Tuple of (response_dict, status_code)
    """
    service, subtask = "hr", "staff_retention"

    try:
        # Validate required fields
        require(params, ["turnover_rate"])

        # Validate positive numbers
        validate_positive_numbers(params, ["turnover_rate"])

        # Extract and convert values
        turnover_rate = float(params["turnover_rate"])
        industry_average = float(params.get("industry_average", 70.0))

        # Validate turnover rate is reasonable (0-200%)
        if turnover_rate > 200:
            raise ValueError("Turnover rate cannot exceed 200%")

        # Calculate retention metrics
        retention_rate = 100 - turnover_rate
        vs_industry = turnover_rate - industry_average

        # Performance assessment
        if turnover_rate <= 30:
            performance = "Excellent"
            performance_color = "green"
        elif turnover_rate <= 50:
            performance = "Good"
            performance_color = "blue"
        elif turnover_rate <= 70:
            performance = "Acceptable"
            performance_color = "yellow"
        else:
            performance = "Needs Improvement"
            performance_color = "red"

        # Risk assessment
        if turnover_rate > industry_average + 20:
            risk_level = "High"
        elif turnover_rate > industry_average:
            risk_level = "Moderate"
        else:
            risk_level = "Low"

        # Calculate cost impact (estimated)
        # Average cost to replace an employee is 1.5x their annual salary
        # Assuming average restaurant worker makes $30,000 annually
        avg_annual_salary = 30000
        replacement_cost_per_employee = avg_annual_salary * 1.5
        estimated_annual_turnover_cost = (turnover_rate / 100) * 25 * replacement_cost_per_employee  # Assuming 25 employees

        # Generate recommendations
        recommendations = []
        if turnover_rate > industry_average:
            recommendations.append(f"Reduce turnover rate by {vs_industry:.1f}% to match industry average")
            recommendations.append("Implement stay interviews to understand exit reasons")
            recommendations.append("Launch peer recognition and reward programs")
            recommendations.append("Offer quarterly professional development workshops")
        else:
            recommendations.append("Maintain current retention strategies - performance is above industry average")
            recommendations.append("Continue investing in employee development programs")

        if turnover_rate > 50:
            recommendations.append("Conduct exit interviews to identify systemic issues")
            recommendations.append("Review compensation and benefits packages")
            recommendations.append("Improve onboarding and training processes")

        # Prepare data for business report
        metrics = {
            "turnover_rate": round(turnover_rate, 2),
            "retention_rate": round(retention_rate, 2),
            "industry_average": industry_average,
            "vs_industry": round(vs_industry, 2),
            "estimated_annual_cost": round(estimated_annual_turnover_cost, 2)
        }

        performance_data = {
            "rating": performance,
            "color": performance_color,
            "risk_level": risk_level
        }

        benchmarks = {
            "excellent_threshold": 30.0,
            "good_threshold": 50.0,
            "acceptable_threshold": 70.0,
            "industry_average": industry_average
        }

        additional_insights = {
            "replacement_cost_per_employee": replacement_cost_per_employee,
            "cost_savings_potential": round(estimated_annual_turnover_cost * 0.3, 2),  # 30% reduction potential
            "retention_strategy_priority": "High" if turnover_rate > 70 else "Medium" if turnover_rate > 50 else "Low",
            "employee_satisfaction_focus": "Critical" if turnover_rate > industry_average else "Maintain"
        }

        # Generate business report HTML
        business_report_html = f"""<section class="report"><header class="report__header"><h2>Staff Retention Analysis</h2><div class="report__meta">Generated: {__import__('datetime').datetime.now().strftime('%B %d, %Y')}</div><div class="badge badge--{performance.lower().replace(' ', '-')}">{performance}</div></header><article class="report__body"><p class="lead">This staff retention analysis reveals <strong>{performance.lower()}</strong> turnover metrics with <strong>{risk_level.lower()}</strong> risk level compared to industry standards.</p><h3>Key Performance Metrics</h3><ul><li>Turnover Rate: {turnover_rate:.1f}%</li><li>Retention Rate: {retention_rate:.1f}%</li><li>Industry Average: {industry_average:.1f}%</li><li>vs Industry: {vs_industry:+.1f}%</li><li>Estimated Annual Cost: ${estimated_annual_turnover_cost:,.0f}</li></ul><h3>Industry Benchmarks</h3><ul><li>Excellent Threshold: {benchmarks['excellent_threshold']:.1f}%</li><li>Good Threshold: {benchmarks['good_threshold']:.1f}%</li><li>Acceptable Threshold: {benchmarks['acceptable_threshold']:.1f}%</li><li>Industry Average: {benchmarks['industry_average']:.1f}%</li></ul><h3>Additional Insights</h3><ul><li>Risk Level: {risk_level}</li><li>Replacement Cost per Employee: ${replacement_cost_per_employee:,.0f}</li><li>Cost Savings Potential: ${additional_insights['cost_savings_potential']:,.0f}</li><li>Strategy Priority: {additional_insights['retention_strategy_priority']}</li></ul><h3>Strategic Recommendations</h3><ol>{''.join([f'<li>{rec}</li>' for rec in recommendations])}</ol></article></section>"""

        # Generate text business report
        business_report = f"""
RESTAURANT CONSULTING REPORT — STAFF RETENTION ANALYSIS
Generated: {__import__('datetime').datetime.now().strftime('%B %d, %Y')}

PERFORMANCE RATING: {performance.upper()}

This staff retention analysis reveals {performance.lower()} turnover metrics with {risk_level.lower()} risk level compared to industry standards.

KEY PERFORMANCE METRICS
• Turnover Rate: {turnover_rate:.1f}%
• Retention Rate: {retention_rate:.1f}%
• Industry Average: {industry_average:.1f}%
• vs Industry: {vs_industry:+.1f}%
• Estimated Annual Cost: ${estimated_annual_turnover_cost:,.0f}

INDUSTRY BENCHMARKS
• Excellent Threshold: {benchmarks['excellent_threshold']:.1f}%
• Good Threshold: {benchmarks['good_threshold']:.1f}%
• Acceptable Threshold: {benchmarks['acceptable_threshold']:.1f}%
• Industry Average: {benchmarks['industry_average']:.1f}%

ADDITIONAL INSIGHTS
• Risk Level: {risk_level}
• Replacement Cost per Employee: ${replacement_cost_per_employee:,.0f}
• Cost Savings Potential: ${additional_insights['cost_savings_potential']:,.0f}
• Strategy Priority: {additional_insights['retention_strategy_priority']}

STRATEGIC RECOMMENDATIONS
{chr(10).join([f'{i+1}. {rec}' for i, rec in enumerate(recommendations)])}

END OF REPORT
        """.strip()

        # Prepare response data
        data = {
            "turnover_rate": turnover_rate,
            "retention_rate": retention_rate,
            "industry_average": industry_average,
            "vs_industry": vs_industry,
            "performance_rating": performance,
            "risk_level": risk_level,
            "estimated_annual_cost": estimated_annual_turnover_cost,
            "business_report_html": business_report_html,
            "business_report": business_report
        }

        insights = recommendations

        return success_payload(service, subtask, params, data, insights), 200

    except ValueError as e:
        return error_payload(service, subtask, str(e))
    except Exception as e:
        return error_payload(service, subtask, f"Internal error: {str(e)}", 500)
