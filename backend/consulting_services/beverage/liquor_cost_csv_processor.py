"""
Beverage: Liquor Cost CSV Processor
Parses uploaded CSV to run liquor cost analysis and return a business report.
Required columns: expected_oz, actual_oz, liquor_cost, total_sales
Optional columns: bottle_cost, bottle_size_oz, target_cost_percentage
"""
from typing import Any, Dict, List
import pandas as pd

from backend.consulting_services.kpi.kpi_utils import calculate_liquor_cost_analysis


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
        if l in ("expected_oz", "expected oz", "expected_usage_oz", "expected usage oz"):
            mapping[col] = "expected_oz"
        elif l in ("actual_oz", "actual oz", "actual_usage_oz", "actual usage oz"):
            mapping[col] = "actual_oz"
        elif "liquor_cost" in l or "beverage_cost" in l or l in ("bar_cost", "alcohol_cost", "drink_cost"):
            mapping[col] = "liquor_cost"
        elif l in ("total_sales", "sales", "revenue", "total sales"):
            mapping[col] = "total_sales"
        elif l in ("bottle_cost", "bottle cost", "cost_per_bottle", "cost per bottle"):
            mapping[col] = "bottle_cost"
        elif l in ("bottle_size_oz", "bottle size oz", "bottle_size", "bottle size"):
            mapping[col] = "bottle_size_oz"
        elif l in ("target_cost_percentage", "target cost percentage", "target_liquor_pct", "target liquor pct"):
            mapping[col] = "target_cost_percentage"
    return mapping


def process_liquor_cost_csv_data(csv_file) -> Dict[str, Any]:
    try:
        df = pd.read_csv(csv_file)
        actual_cols = [c.strip() for c in df.columns]
        df.columns = actual_cols
        mapping = _map_columns(actual_cols)
        df = df.rename(columns=mapping)

        required = ["expected_oz", "actual_oz", "liquor_cost", "total_sales"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            return {
                "status": "error",
                "message": f"Missing required columns: {', '.join(missing)}",
                "your_columns": actual_cols,
                "help": "CSV must include: expected_oz, actual_oz, liquor_cost, total_sales. Optional: bottle_cost, bottle_size_oz, target_cost_percentage"
            }

        # Clean numeric fields
        for c in ["expected_oz", "actual_oz", "liquor_cost", "total_sales", "bottle_cost", "bottle_size_oz", "target_cost_percentage"]:
            if c in df.columns:
                df[c] = df[c].apply(_clean_numeric)

        # Drop invalid rows
        df = df.dropna(subset=["expected_oz", "actual_oz"]).copy()
        df = df[(df["total_sales"] > 0) & (df["liquor_cost"] >= 0)]
        if len(df) == 0:
            return {"status": "error", "message": "No valid data rows found after cleaning"}

        # Use first row as aggregate inputs
        row = df.iloc[0]
        result = calculate_liquor_cost_analysis(
            expected_oz=float(row.get("expected_oz", 0.0)),
            actual_oz=float(row.get("actual_oz", 0.0)),
            liquor_cost=float(row.get("liquor_cost", 0.0)),
            total_sales=float(row.get("total_sales", 0.0)),
            bottle_cost=float(row.get("bottle_cost", 0.0)) if "bottle_cost" in df.columns else 0.0,
            bottle_size_oz=float(row.get("bottle_size_oz", 25.0)) if "bottle_size_oz" in df.columns else 25.0,
            target_cost_percentage=float(row.get("target_cost_percentage", 20.0)) if "target_cost_percentage" in df.columns else 20.0,
        )

        return {
            "status": "success",
            "analysis_type": "liquor_cost_analysis",
            **result,
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": f"CSV processing error: {str(e)}",
            "traceback": traceback.format_exc() if hasattr(traceback, "format_exc") else None,
        }
