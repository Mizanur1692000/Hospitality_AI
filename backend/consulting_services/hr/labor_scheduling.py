"""
HR Labor Scheduling Analysis Task
Analyzes scheduling efficiency and provides optimization strategies with comprehensive business report.
"""

from backend.shared.utils.common import success_payload, error_payload, require, validate_positive_numbers


def run(params: dict, file_bytes: bytes | None = None) -> tuple[dict, int]:
    """
    Calculate labor scheduling analysis with comprehensive business report.

    Args:
        params: Dictionary containing total_sales, labor_hours, hourly_rate, and optional peak_hours
        file_bytes: Optional file data (not used in this task)

    Returns:
        Tuple of (response_dict, status_code)
    """
    service, subtask = "hr", "labor_scheduling"

    try:
        # Validate required fields
        require(params, ["total_sales", "hourly_rate"])

        # Handle both labor_hours and hours_worked
        labor_hours = params.get("labor_hours") or params.get("hours_worked")
        if not labor_hours:
            return error_payload(service, subtask, "Missing required field: labor_hours or hours_worked")

        # Validate positive numbers
        validate_positive_numbers(params, ["total_sales", "hourly_rate"])
        validate_positive_numbers({"labor_hours": labor_hours}, ["labor_hours"])

        # Extract and convert values
        total_sales = float(params["total_sales"])
        labor_hours = float(labor_hours)
        hourly_rate = float(params["hourly_rate"])
        peak_hours = float(params.get("peak_hours", labor_hours * 0.3))  # Assume 30% peak hours if not provided

        # Calculate scheduling metrics
        total_labor_cost = labor_hours * hourly_rate
        sales_per_hour = total_sales / labor_hours
        labor_percent = (total_labor_cost / total_sales) * 100
        cost_per_hour = total_labor_cost / labor_hours

        # Peak efficiency analysis
        peak_efficiency = (peak_hours / labor_hours) * 100
        off_peak_hours = labor_hours - peak_hours

        # Performance assessment
        if labor_percent <= 25:
            performance = "Excellent"
            performance_color = "green"
        elif labor_percent <= 30:
            performance = "Good"
            performance_color = "blue"
        elif labor_percent <= 35:
            performance = "Acceptable"
            performance_color = "yellow"
        else:
            performance = "Needs Improvement"
            performance_color = "red"

        # Scheduling efficiency assessment
        if peak_efficiency >= 40:
            scheduling_efficiency = "High"
        elif peak_efficiency >= 25:
            scheduling_efficiency = "Medium"
        else:
            scheduling_efficiency = "Low"

        # Calculate potential savings
        target_labor_percent = 30.0
        target_labor_cost = (target_labor_percent / 100) * total_sales
        potential_savings = total_labor_cost - target_labor_cost

        # Generate recommendations
        recommendations = []
        if labor_percent > target_labor_percent:
            recommendations.append(f"Reduce labor costs by ${potential_savings:,.2f} to reach {target_labor_percent}% target")
            recommendations.append("Optimize scheduling during slow periods to reduce off-peak hours")
            recommendations.append("Implement cross-training to improve flexibility and reduce overtime")

        if peak_efficiency < 30:
            recommendations.append("Increase staffing during peak hours to improve service quality")
            recommendations.append("Analyze customer traffic patterns to better align staffing")
        else:
            recommendations.append("Maintain current peak hour staffing levels")

        if sales_per_hour < 50:
            recommendations.append("Focus on increasing sales per hour through upselling and efficiency")
            recommendations.append("Consider reducing labor hours during consistently slow periods")
        elif sales_per_hour > 100:
            recommendations.append("Excellent sales per hour - consider expanding during peak times")

        recommendations.append("Implement shift bidding system to improve employee satisfaction")
        recommendations.append("Use predictive scheduling based on historical sales data")

        # Prepare data for business report
        metrics = {
            "total_sales": total_sales,
            "labor_hours": labor_hours,
            "hourly_rate": hourly_rate,
            "total_labor_cost": total_labor_cost,
            "sales_per_hour": round(sales_per_hour, 2),
            "labor_percent": round(labor_percent, 2),
            "cost_per_hour": round(cost_per_hour, 2),
            "peak_hours": peak_hours,
            "off_peak_hours": off_peak_hours
        }

        performance_data = {
            "rating": performance,
            "color": performance_color,
            "scheduling_efficiency": scheduling_efficiency
        }

        benchmarks = {
            "excellent_labor_percent": 25.0,
            "good_labor_percent": 30.0,
            "acceptable_labor_percent": 35.0,
            "target_labor_percent": target_labor_percent,
            "optimal_peak_percent": 40.0
        }

        additional_insights = {
            "peak_efficiency_percent": round(peak_efficiency, 1),
            "potential_savings": round(potential_savings, 2),
            "scheduling_optimization_priority": "High" if labor_percent > 35 else "Medium" if labor_percent > 30 else "Low",
            "overtime_risk": "High" if peak_hours > labor_hours * 0.5 else "Medium" if peak_hours > labor_hours * 0.3 else "Low"
        }

        # Generate business report HTML
        business_report_html = f"""
<section class="report">
  <header class="report__header">
    <h2>Labor Scheduling Analysis</h2>
    <div class="report__meta">Generated: {__import__('datetime').datetime.now().strftime('%B %d, %Y')}</div>
    <div class="badge badge--{performance.lower().replace(' ', '-')}">{performance}</div>
  </header>

  <article class="report__body">
    <p class="lead">This labor scheduling analysis reveals <strong>{performance.lower()}</strong> scheduling efficiency with <strong>{scheduling_efficiency.lower()}</strong> peak hour optimization.</p>

    <h3>Key Performance Metrics</h3>
    <ul>
      <li>• Total Sales: ${total_sales:,.2f}</li>
      <li>• Labor Hours: {labor_hours:.1f}</li>
      <li>• Hourly Rate: ${hourly_rate:.2f}</li>
      <li>• Total Labor Cost: ${total_labor_cost:,.2f}</li>
      <li>• Sales per Hour: ${sales_per_hour:.2f}</li>
      <li>• Labor Percent: {labor_percent:.1f}%</li>
      <li>• Peak Hours: {peak_hours:.1f}</li>
      <li>• Off-Peak Hours: {off_peak_hours:.1f}</li>
    </ul>

    <h3>Industry Benchmarks</h3>
    <ul>
      <li>• Excellent Labor %: {benchmarks['excellent_labor_percent']:.1f}%</li>
      <li>• Good Labor %: {benchmarks['good_labor_percent']:.1f}%</li>
      <li>• Acceptable Labor %: {benchmarks['acceptable_labor_percent']:.1f}%</li>
      <li>• Target Labor %: {benchmarks['target_labor_percent']:.1f}%</li>
      <li>• Optimal Peak %: {benchmarks['optimal_peak_percent']:.1f}%</li>
    </ul>

    <h3>Additional Insights</h3>
    <ul>
      <li>• Peak Efficiency: {additional_insights['peak_efficiency_percent']:.1f}%</li>
      <li>• Scheduling Efficiency: {scheduling_efficiency}</li>
      <li>• Potential Savings: ${additional_insights['potential_savings']:,.2f}</li>
      <li>• Optimization Priority: {additional_insights['scheduling_optimization_priority']}</li>
      <li>• Overtime Risk: {additional_insights['overtime_risk']}</li>
    </ul>

    <h3>Strategic Recommendations</h3>
    <ol>
      {''.join([f'<li>{rec}</li>' for rec in recommendations])}
    </ol>
  </article>
</section>
        """.strip()

        # Generate text business report
        business_report = f"""
RESTAURANT CONSULTING REPORT — LABOR SCHEDULING ANALYSIS
Generated: {__import__('datetime').datetime.now().strftime('%B %d, %Y')}

PERFORMANCE RATING: {performance.upper()}

This labor scheduling analysis reveals {performance.lower()} scheduling efficiency with {scheduling_efficiency.lower()} peak hour optimization.

KEY PERFORMANCE METRICS
• Total Sales: ${total_sales:,.2f}
• Labor Hours: {labor_hours:.1f}
• Hourly Rate: ${hourly_rate:.2f}
• Total Labor Cost: ${total_labor_cost:,.2f}
• Sales per Hour: ${sales_per_hour:.2f}
• Labor Percent: {labor_percent:.1f}%
• Peak Hours: {peak_hours:.1f}
• Off-Peak Hours: {off_peak_hours:.1f}

INDUSTRY BENCHMARKS
• Excellent Labor %: {benchmarks['excellent_labor_percent']:.1f}%
• Good Labor %: {benchmarks['good_labor_percent']:.1f}%
• Acceptable Labor %: {benchmarks['acceptable_labor_percent']:.1f}%
• Target Labor %: {benchmarks['target_labor_percent']:.1f}%
• Optimal Peak %: {benchmarks['optimal_peak_percent']:.1f}%

ADDITIONAL INSIGHTS
• Peak Efficiency: {additional_insights['peak_efficiency_percent']:.1f}%
• Scheduling Efficiency: {scheduling_efficiency}
• Potential Savings: ${additional_insights['potential_savings']:,.2f}
• Optimization Priority: {additional_insights['scheduling_optimization_priority']}
• Overtime Risk: {additional_insights['overtime_risk']}

STRATEGIC RECOMMENDATIONS
{chr(10).join([f'{i+1}. {rec}' for i, rec in enumerate(recommendations)])}

END OF REPORT
        """.strip()

        # Prepare response data
        data = {
            "total_sales": total_sales,
            "labor_hours": labor_hours,
            "hourly_rate": hourly_rate,
            "total_labor_cost": total_labor_cost,
            "sales_per_hour": sales_per_hour,
            "labor_percent": labor_percent,
            "peak_hours": peak_hours,
            "off_peak_hours": off_peak_hours,
            "performance_rating": performance,
            "scheduling_efficiency": scheduling_efficiency,
            "potential_savings": potential_savings,
            "business_report_html": business_report_html,
            "business_report": business_report
        }

        insights = recommendations

        return success_payload(service, subtask, params, data, insights), 200

    except ValueError as e:
        return error_payload(service, subtask, str(e))
    except Exception as e:
        return error_payload(service, subtask, f"Internal error: {str(e)}", 500)
