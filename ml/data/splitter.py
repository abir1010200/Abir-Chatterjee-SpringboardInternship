"""
ml/data/splitter.py
Time-aware chronological train/val/test split.
CRITICAL: Do NOT use random shuffling — it would cause temporal leakage.

Split strategy: chronological (sorted by timestamp)
  70% training | 15% validation | 15% test

This ensures the model is evaluated on the most recent data,
mimicking real deployment where the model predicts future events.
"""
from typing import Tuple
import pandas as pd
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from ml import config as cfg


def chronological_split(
    df: pd.DataFrame,
    train_ratio: float = cfg.TRAIN_RATIO,
    val_ratio: float = cfg.VAL_RATIO,
    timestamp_col: str = "timestamp",
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split DataFrame chronologically. Returns (train, val, test).
    No data from the future leaks into training.
    """
    df = df.copy()
    if timestamp_col in df.columns:
        df = df.sort_values(timestamp_col).reset_index(drop=True)

    n = len(df)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)

    train = df.iloc[:n_train].copy()
    val = df.iloc[n_train: n_train + n_val].copy()
    test = df.iloc[n_train + n_val:].copy()

    return train, val, test


def get_split_summary(train: pd.DataFrame, val: pd.DataFrame, test: pd.DataFrame,
                      timestamp_col: str = "timestamp") -> dict:
    """Return a human-readable split summary dict."""
    summary = {
        "train_rows": len(train),
        "val_rows": len(val),
        "test_rows": len(test),
        "total_rows": len(train) + len(val) + len(test),
    }
    for name, df in [("train", train), ("val", val), ("test", test)]:
        if timestamp_col in df.columns and len(df) > 0:
            summary[f"{name}_start"] = str(df[timestamp_col].iloc[0])
            summary[f"{name}_end"] = str(df[timestamp_col].iloc[-1])
    return summary
