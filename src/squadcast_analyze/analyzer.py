from __future__ import annotations
import pandas as pd
from typing import Optional, List, Dict, Any


def to_dataframe(records: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert a list of JSON records into a pandas DataFrame.
    """
    if not records:
        return pd.DataFrame()
    return pd.json_normalize(records)


def best_match_column(df: pd.DataFrame, wanted: str) -> Optional[str]:
    """
    Try to find the column name that best matches the requested field.
    """
    if wanted in df.columns:
        return wanted

    candidates = [c for c in df.columns if c.endswith(wanted) or wanted in c]
    return candidates[0] if candidates else None


def top_counts(df: pd.DataFrame, group_by: str, top: int) -> pd.DataFrame:
    """
    Group the DataFrame by the chosen field and return Top-N counts.
    """
    col = best_match_column(df, group_by)
    if not col:
        cols = ", ".join(df.columns[:50])  # preview
        raise ValueError(f"Field '{group_by}' not found. Columns sample: {cols}")

    out = df.groupby(col, dropna=False).size().reset_index(name="count")
    out = out.sort_values("count", ascending=False).head(top)
    return out
