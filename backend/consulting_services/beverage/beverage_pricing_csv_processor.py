"""
Beverage: Pricing CSV Processor
Parses uploaded CSV to analyze beverage pricing and return a business report.
Required columns: drink_price, cost_per_drink, sales_volume, competitor_price
Optional columns: target_margin, market_position, elasticity_factor
"""
from typing import Any, Dict, List
import pandas as pd

from backend.consulting_services.kpi.kpi_utils import calculate_pricing_analysis


def _clean_numeric(value) -> float:
    if value is None:
        return 0.0
    try:
        if isinstance(value, float) and pd.isna(value):
            return 0.0
    except Exception:
        pass
    if isinstance(value, str):
        s = value.strip().replace("$", "").replace("%", "").replace(",", "")
        if s == "" or s.lower() == "nan":
            return 0.0
        try:
            return float(s)
        except ValueError:
            return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _map_columns(actual_columns: List[str]) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for col in actual_columns:
        l = col.lower().strip()
        if l in mapping:
            continue
        if l in ("drink_price", "price", "avg_drink_price", "average drink price"):
            mapping[col] = "drink_price"
        elif l in ("cost_per_drink", "cost per drink", "unit_cost", "unit cost"):
            mapping[col] = "cost_per_drink"
        elif l in ("sales_volume", "sales volume", "units_sold", "units sold"):
            mapping[col] = "sales_volume"
        elif l in ("competitor_price", "competitor price"):
            mapping[col] = "competitor_price"
        elif l in ("target_margin", "target margin", "target_margin_pct", "target margin %"):
            mapping[col] = "target_margin"
        elif l in ("market_position", "market position"):
            mapping[col] = "market_position"
        elif l in ("elasticity_factor", "elasticity factor"):
            mapping[col] = "elasticity_factor"
    return mapping


essential_cols = ["drink_price", "cost_per_drink", "sales_volume", "competitor_price"]


def process_beverage_pricing_csv_data(csv_file) -> Dict[str, Any]:
    try:
        df = pd.read_csv(csv_file)
        actual_cols = [c.strip() for c in df.columns]
        df.columns = actual_cols
        mapping = _map_columns(actual_cols)
        df = df.rename(columns=mapping)

        missing = [c for c in essential_cols if c not in df.columns]
        if missing:
            return {
                "status": "error",
                "message": f"Missing required columns: {', '.join(missing)}",
                "your_columns": actual_cols,
                "help": "CSV must include: drink_price, cost_per_drink, sales_volume, competitor_price. Optional: target_margin, market_position, elasticity_factor"
            }

        # Clean numeric
        numeric_cols = essential_cols + ["target_margin", "elasticity_factor"]
        for c in numeric_cols:
            if c in df.columns:
                df[c] = df[c].apply(_clean_numeric)

        # Use first row inputs
        row = df.iloc[0]
        result = calculate_pricing_analysis(
            drink_price=float(row.get("drink_price", 0.0)),
            cost_per_drink=float(row.get("cost_per_drink", 0.0)),
            sales_volume=float(row.get("sales_volume", 0.0)),
            competitor_price=float(row.get("competitor_price", 0.0)),
            target_margin=float(row.get("target_margin", 75.0)) if "target_margin" in df.columns else 75.0,
            market_position=str(row.get("market_position", "premium")) if "market_position" in df.columns else "premium",
            elasticity_factor=float(row.get("elasticity_factor", 1.5)) if "elasticity_factor" in df.columns else 1.5,
        )

        return {
            "status": "success",
            "analysis_type": "beverage_pricing_analysis",
            **result,
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": f"CSV processing error: {str(e)}",
            "traceback": traceback.format_exc() if hasattr(traceback, "format_exc") else None,
        }
