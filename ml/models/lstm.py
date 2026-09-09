"""
ml/models/lstm.py
PyTorch LSTM model for multi-horizon temporal irrigation forecasting.
Dual-head architecture:
  - Head 1: Binary classification (irrigation_required)
  - Head 2: Volume regression (irrigation_volume_liters)
"""
import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, mean_absolute_error,
    mean_squared_error, r2_score
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from ml import config as cfg

logger = logging.getLogger(__name__)


class IrrigationLSTMNet(nn.Module):
    """
    PyTorch LSTM neural network with shared recurrent backbone
    and dual specialized output prediction heads.
    """

    def __init__(
        self,
        input_dim: int = len(cfg.LSTM_FEATURE_COLS),
        hidden_dim: int = cfg.LSTM_HIDDEN_SIZE,
        num_layers: int = cfg.LSTM_NUM_LAYERS,
        dropout: float = cfg.LSTM_DROPOUT,
    ):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )

        self.fc_shared = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
        )

        # Classification Head (Irrigation Required)
        self.classifier_head = nn.Linear(32, 1)

        # Volume Regression Head (Liters)
        self.regressor_head = nn.Sequential(
            nn.Linear(32, 1),
            nn.ReLU(),  # Volume cannot be negative
        )

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        x: [batch_size, seq_len, input_dim]
        returns: (classification_logits, regression_volume)
        """
        lstm_out, _ = self.lstm(x)
        # Use final time step hidden state
        last_hidden = lstm_out[:, -1, :]
        shared_rep = self.fc_shared(last_hidden)

        logits = self.classifier_head(shared_rep).squeeze(-1)
        volume = self.regressor_head(shared_rep).squeeze(-1)
        return logits, volume


class LSTMIrrigationModel:
    """
    High-level wrapper for training, evaluating, and serving the PyTorch LSTM model.
    """

    def __init__(
        self,
        seq_len: int = cfg.LSTM_SEQUENCE_LENGTH,
        feature_cols: Optional[List[str]] = None,
        hidden_dim: int = cfg.LSTM_HIDDEN_SIZE,
        num_layers: int = cfg.LSTM_NUM_LAYERS,
        lr: float = cfg.LSTM_LEARNING_RATE,
        batch_size: int = cfg.LSTM_BATCH_SIZE,
        max_epochs: int = cfg.LSTM_MAX_EPOCHS,
        patience: int = cfg.LSTM_EARLY_STOP_PATIENCE,
    ):
        self.name = "lstm"
        self.version = "1.0.0"
        self.seq_len = seq_len
        self.feature_cols = feature_cols or list(cfg.LSTM_FEATURE_COLS)
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.lr = lr
        self.batch_size = batch_size
        self.max_epochs = max_epochs
        self.patience = patience

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.scaler = StandardScaler()
        self.is_fitted = False

        self.net = IrrigationLSTMNet(
            input_dim=len(self.feature_cols),
            hidden_dim=hidden_dim,
            num_layers=num_layers,
        ).to(self.device)

    def create_sequences(
        self,
        df: pd.DataFrame,
        is_training: bool = True,
    ) -> Tuple[np.ndarray, Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Convert time-ordered DataFrame into sliding window sequences.
        Returns:
            X_seq: [N, seq_len, num_features]
            y_cls: [N]
            y_vol: [N]
        """
        missing = [c for c in self.feature_cols if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required LSTM feature columns: {missing}")

        data_vals = df[self.feature_cols].copy()
        # Handle scaling
        if is_training:
            scaled_data = self.scaler.fit_transform(data_vals)
        else:
            scaled_data = self.scaler.transform(data_vals)

        X_list: List[np.ndarray] = []
        y_cls_list: List[int] = []
        y_vol_list: List[float] = []

        cls_arr = df["irrigation_required"].values if "irrigation_required" in df.columns else None
        vol_arr = df["irrigation_volume_liters"].values if "irrigation_volume_liters" in df.columns else None

        for i in range(len(df) - self.seq_len + 1):
            X_list.append(scaled_data[i : i + self.seq_len])
            if cls_arr is not None:
                y_cls_list.append(cls_arr[i + self.seq_len - 1])
                y_vol_list.append(vol_arr[i + self.seq_len - 1] if vol_arr is not None else 0.0)

        X_seq = np.array(X_list, dtype=np.float32)
        y_cls = np.array(y_cls_list, dtype=np.float32) if len(y_cls_list) > 0 else None
        y_vol = np.array(y_vol_list, dtype=np.float32) if len(y_vol_list) > 0 else None

        return X_seq, y_cls, y_vol

    def fit(self, train_df: pd.DataFrame, val_df: Optional[pd.DataFrame] = None) -> "LSTMIrrigationModel":
        """Train the LSTM model using early stopping on validation loss."""
        logger.info(f"Preparing LSTM sequences (seq_len={self.seq_len})...")
        X_train, y_train_cls, y_train_vol = self.create_sequences(train_df, is_training=True)

        if len(X_train) == 0:
            raise ValueError("Insufficient data to build LSTM training sequences.")

        train_ds = TensorDataset(
            torch.tensor(X_train),
            torch.tensor(y_train_cls, dtype=torch.float32),
            torch.tensor(y_train_vol, dtype=torch.float32),
        )
        train_loader = DataLoader(train_ds, batch_size=self.batch_size, shuffle=True)

        val_loader = None
        if val_df is not None and len(val_df) >= self.seq_len:
            X_val, y_val_cls, y_val_vol = self.create_sequences(val_df, is_training=False)
            if len(X_val) > 0:
                val_ds = TensorDataset(
                    torch.tensor(X_val),
                    torch.tensor(y_val_cls, dtype=torch.float32),
                    torch.tensor(y_val_vol, dtype=torch.float32),
                )
                val_loader = DataLoader(val_ds, batch_size=self.batch_size, shuffle=False)

        optimizer = torch.optim.Adam(self.net.parameters(), lr=self.lr)
        cls_criterion = nn.BCEWithLogitsLoss()
        vol_criterion = nn.MSELoss()

        best_val_loss = float("inf")
        patience_counter = 0
        best_state = None

        logger.info(f"Training LSTM on {self.device} for up to {self.max_epochs} epochs...")
        self.net.train()

        for epoch in range(1, self.max_epochs + 1):
            epoch_loss = 0.0
            for batch_x, batch_cls, batch_vol in train_loader:
                batch_x = batch_x.to(self.device)
                batch_cls = batch_cls.to(self.device)
                batch_vol = batch_vol.to(self.device)

                optimizer.zero_grad()
                logits, vols = self.net(batch_x)

                loss_cls = cls_criterion(logits, batch_cls)
                loss_vol = vol_criterion(vols, batch_vol)
                # Weighted multi-task loss
                loss = loss_cls + 0.0001 * loss_vol

                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()

            avg_train_loss = epoch_loss / len(train_loader)

            # Validation step
            if val_loader:
                self.net.eval()
                val_loss = 0.0
                with torch.no_grad():
                    for vx, vcls, vvol in val_loader:
                        vx, vcls, vvol = vx.to(self.device), vcls.to(self.device), vvol.to(self.device)
                        l, v = self.net(vx)
                        v_loss = cls_criterion(l, v) + 0.0001 * vol_criterion(v, vvol)
                        val_loss += v_loss.item()
                avg_val_loss = val_loss / len(val_loader)
                self.net.train()

                if avg_val_loss < best_val_loss:
                    best_val_loss = avg_val_loss
                    best_state = {k: v.cpu().clone() for k, v in self.net.state_dict().items()}
                    patience_counter = 0
                else:
                    patience_counter += 1
                    if patience_counter >= self.patience:
                        logger.info(f"Early stopping triggered at epoch {epoch}")
                        break

        if best_state is not None:
            self.net.load_state_dict(best_state)

        self.is_fitted = True
        logger.info("LSTM training completed.")
        return self

    def predict(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate predictions for DataFrame.
        Returns:
            (pred_cls, pred_vol, confidence)
        """
        if not self.is_fitted:
            raise RuntimeError("LSTM model is not fitted.")

        X_seq, _, _ = self.create_sequences(df, is_training=False)
        if len(X_seq) == 0:
            return np.array([]), np.array([]), np.array([])

        self.net.eval()
        with torch.no_grad():
            x_tensor = torch.tensor(X_seq, dtype=torch.float32).to(self.device)
            logits, vols = self.net(x_tensor)
            probs = torch.sigmoid(logits).cpu().numpy()
            vols = vols.cpu().numpy()

        pred_cls = (probs >= 0.5).astype(int)
        pred_vol = np.where(pred_cls == 1, np.maximum(cfg.MIN_IRRIGATION_VOLUME_LITERS, vols), 0.0)
        confidence = np.maximum(probs, 1.0 - probs)

        return pred_cls, np.round(pred_vol, 1), np.round(confidence, 3)

    def evaluate(self, test_df: pd.DataFrame) -> Dict[str, Any]:
        """Evaluate LSTM predictions against ground truth labels."""
        X_test, y_test_cls, y_test_vol = self.create_sequences(test_df, is_training=False)
        if len(X_test) == 0:
            return {"model": self.name, "error": "Insufficient data"}

        self.net.eval()
        with torch.no_grad():
            x_tensor = torch.tensor(X_test, dtype=torch.float32).to(self.device)
            logits, vols = self.net(x_tensor)
            probs = torch.sigmoid(logits).cpu().numpy()
            pred_vols = vols.cpu().numpy()

        pred_cls = (probs >= 0.5).astype(int)
        pred_vols = np.where(pred_cls == 1, np.maximum(cfg.MIN_IRRIGATION_VOLUME_LITERS, pred_vols), 0.0)

        metrics: Dict[str, Any] = {
            "model": self.name,
            "accuracy": round(accuracy_score(y_test_cls, pred_cls), 4),
            "precision": round(precision_score(y_test_cls, pred_cls, zero_division=0), 4),
            "recall": round(recall_score(y_test_cls, pred_cls, zero_division=0), 4),
            "f1": round(f1_score(y_test_cls, pred_cls, zero_division=0), 4),
        }

        try:
            metrics["roc_auc"] = round(roc_auc_score(y_test_cls, probs), 4)
        except Exception:
            metrics["roc_auc"] = None

        if y_test_vol is not None:
            mask = y_test_cls == 1
            if np.sum(mask) > 0:
                v_true = y_test_vol[mask]
                v_pred = pred_vols[mask]
                metrics["volume_mae"] = round(mean_absolute_error(v_true, v_pred), 2)
                metrics["volume_rmse"] = round(float(np.sqrt(mean_squared_error(v_true, v_pred))), 2)

        logger.info(f"LSTM evaluation: {metrics}")
        return metrics

    def save(self, output_dir: Path) -> Path:
        """Save PyTorch weights and scaler."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        model_path = output_dir / f"{self.name}_v{self.version}.pt"
        torch.save({
            "net_state": self.net.state_dict(),
            "scaler": self.scaler,
            "feature_cols": self.feature_cols,
            "seq_len": self.seq_len,
            "hidden_dim": self.hidden_dim,
            "num_layers": self.num_layers,
            "version": self.version,
        }, model_path)
        logger.info(f"LSTM model saved to {model_path}")
        return model_path

    @classmethod
    def load(cls, model_path: Path) -> "LSTMIrrigationModel":
        try:
            checkpoint = torch.load(model_path, map_location="cpu", weights_only=False)
        except TypeError:
            checkpoint = torch.load(model_path, map_location="cpu")
        instance = cls(
            seq_len=checkpoint.get("seq_len", cfg.LSTM_SEQUENCE_LENGTH),
            feature_cols=checkpoint.get("feature_cols", cfg.LSTM_FEATURE_COLS),
            hidden_dim=checkpoint.get("hidden_dim", cfg.LSTM_HIDDEN_SIZE),
            num_layers=checkpoint.get("num_layers", cfg.LSTM_NUM_LAYERS),
        )
        instance.net.load_state_dict(checkpoint["net_state"])
        instance.scaler = checkpoint["scaler"]
        instance.version = checkpoint.get("version", "1.0.0")
        instance.is_fitted = True
        return instance
