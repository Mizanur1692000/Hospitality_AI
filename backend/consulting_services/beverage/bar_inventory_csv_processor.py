"""
Beverage: Bar Inventory CSV Processor
Parses uploaded CSV to run bar inventory analysis and return a business report.
Required columns: current_stock, reorder_point, monthly_usage, inventory_value
Optional columns: lead_time_days, safety_stock, item_cost, target_turnover
"""
from typing import Any, Dict, List
import pandas as pd

from backend.consulting_services.kpi.kpi_utils import calculate_inventory_analysis


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
        if l in ("current_stock", "current stock", "on_hand", "on hand"):
            mapping[col] = "current_stock"
        elif l in ("reorder_point", "reorder point", "rop"):
            mapping[col] = "reorder_point"
        elif l in ("monthly_usage", "monthly usage", "usage_per_month", "usage per month"):
            mapping[col] = "monthly_usage"
        elif l in ("inventory_value", "inventory value", "stock_value", "stock value"):
            mapping[col] = "inventory_value"
        elif l in ("lead_time_days", "lead time days", "lead_time", "lead time"):
            mapping[col] = "lead_time_days"
        elif l in ("safety_stock", "safety stock"):
            mapping[col] = "safety_stock"
        elif l in ("item_cost", "item cost", "unit_cost", "unit cost"):
            mapping[col] = "item_cost"
        elif l in ("target_turnover", "target turnover"):
            mapping[col] = "target_turnover"
    return mapping


essential_cols = ["current_stock", "reorder_point", "monthly_usage", "inventory_value"]


def process_bar_inventory_csv_data(csv_file) -> Dict[str, Any]:
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
                "help": "CSV must include: current_stock, reorder_point, monthly_usage, inventory_value. Optional: lead_time_days, safety_stock, item_cost, target_turnover"
            }

        # Clean numeric
        numeric_cols = essential_cols + ["lead_time_days", "safety_stock", "item_cost", "target_turnover"]
        for c in numeric_cols:
            if c in df.columns:
                df[c] = df[c].apply(_clean_numeric)

        # Take first row as aggregate
        row = df.iloc[0]
        result = calculate_inventory_analysis(
            current_stock=float(row.get("current_stock", 0.0)),
            reorder_point=float(row.get("reorder_point", 0.0)),
            monthly_usage=float(row.get("monthly_usage", 0.0)),
            inventory_value=float(row.get("inventory_value", 0.0)),
            lead_time_days=float(row.get("lead_time_days", 7.0)) if "lead_time_days" in df.columns else 7.0,
            safety_stock=float(row.get("safety_stock", 0.0)) if "safety_stock" in df.columns else 0.0,
            item_cost=float(row.get("item_cost", 0.0)) if "item_cost" in df.columns else 0.0,
            target_turnover=float(row.get("target_turnover", 12.0)) if "target_turnover" in df.columns else 12.0,
        )

        return {
            "status": "success",
            "analysis_type": "bar_inventory_analysis",
            **result,
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": f"CSV processing error: {str(e)}",
            "traceback": traceback.format_exc() if hasattr(traceback, "format_exc") else None,
        }
