"""Dataset validation engine for FraudGraph fintech dataset."""

import sys
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np


@dataclass
class ValidationResult:
    """Stores dataset validation results and diagnostics."""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)


class DatasetValidator:
    """Validates raw synthetic fintech dataset integrity, constraints, and schemas."""

    ALLOWED_FRAUD_TYPES = {
        "shared_device",
        "shared_ip",
        "shared_payment",
        "coordinated_timing",
        "merchant_targeting",
        "geographic",
        "mixed",
    }

    ALLOWED_STATUSES = {"SUCCESS", "FAILED", "PENDING"}
    ALLOWED_PAYMENT_TYPES = {"UPI", "CREDIT_CARD", "DEBIT_CARD", "NET_BANKING", "WALLET"}

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            self.data_dir = Path(__file__).resolve().parent.parent.parent / "data" / "raw"
        else:
            self.data_dir = Path(data_dir)

    def load_datasets(self) -> Dict[str, pd.DataFrame]:
        """Loads all CSV tables from the raw dataset directory."""
        files = {
            "customers": "customers.csv",
            "transactions": "transactions.csv",
            "devices": "devices.csv",
            "ip_addresses": "ip_addresses.csv",
            "payment_methods": "payment_methods.csv",
            "merchants": "merchants.csv",
        }
        datasets = {}
        for name, filename in files.items():
            filepath = self.data_dir / filename
            if not filepath.exists():
                raise FileNotFoundError(f"Required dataset file not found: {filepath}")
            datasets[name] = pd.read_csv(filepath)
        return datasets

    def validate_all(self, datasets: Optional[Dict[str, pd.DataFrame]] = None) -> ValidationResult:
        """Runs full suite of integrity, schema, and relationship validation checks."""
        result = ValidationResult()

        try:
            if datasets is None:
                datasets = self.load_datasets()
        except Exception as e:
            result.add_error(f"Failed to load dataset files: {str(e)}")
            return result

        self._validate_customers(datasets.get("customers"), result)
        self._validate_devices(datasets.get("devices"), result)
        self._validate_ips(datasets.get("ip_addresses"), result)
        self._validate_payment_methods(datasets.get("payment_methods"), result)
        self._validate_merchants(datasets.get("merchants"), result)
        self._validate_transactions(datasets, result)

        return result

    def _validate_customers(self, df: Optional[pd.DataFrame], result: ValidationResult) -> None:
        if df is None or df.empty:
            result.add_error("Customers dataset is missing or empty.")
            return

        expected_cols = {
            "customer_id",
            "customer_age",
            "customer_segment",
            "account_age_days",
            "country",
            "city",
            "account_created_at",
        }
        missing_cols = expected_cols - set(df.columns)
        if missing_cols:
            result.add_error(f"Customers table missing columns: {missing_cols}")

        if len(df) < 2000:
            result.add_error(f"Customer count ({len(df)}) is less than required minimum of 2000.")

        if df["customer_id"].duplicated().any():
            dups = df[df["customer_id"].duplicated()]["customer_id"].tolist()[:5]
            result.add_error(f"Duplicate customer_id found: {dups}")

        if df["customer_id"].isnull().any():
            result.add_error("Null customer_id found in customers table.")

        if (df["customer_age"] < 18).any() or (df["customer_age"] > 100).any():
            result.add_error("Customer age contains invalid values outside [18, 100].")

        if (df["account_age_days"] < 0).any():
            result.add_error("Negative account_age_days found in customers table.")

        # Check account_created_at format
        try:
            pd.to_datetime(df["account_created_at"])
        except Exception as e:
            result.add_error(f"Invalid datetime format in customers.account_created_at: {str(e)}")

        result.stats["customer_count"] = len(df)

    def _validate_devices(self, df: Optional[pd.DataFrame], result: ValidationResult) -> None:
        if df is None or df.empty:
            result.add_error("Devices dataset is missing or empty.")
            return

        expected_cols = {"device_id", "device_type", "os", "device_age_days"}
        missing_cols = expected_cols - set(df.columns)
        if missing_cols:
            result.add_error(f"Devices table missing columns: {missing_cols}")

        if len(df) < 500:
            result.add_error(f"Device count ({len(df)}) is less than required minimum of 500.")

        if df["device_id"].duplicated().any():
            result.add_error("Duplicate device_id found in devices table.")

        if df.isnull().any().any():
            null_cols = df.columns[df.isnull().any()].tolist()
            result.add_error(f"Unexpected null values in devices table: {null_cols}")

        if (df["device_age_days"] < 0).any():
            result.add_error("Negative device_age_days found in devices table.")

        result.stats["device_count"] = len(df)

    def _validate_ips(self, df: Optional[pd.DataFrame], result: ValidationResult) -> None:
        if df is None or df.empty:
            result.add_error("IP addresses dataset is missing or empty.")
            return

        expected_cols = {"ip_id", "ip_type", "country", "city"}
        missing_cols = expected_cols - set(df.columns)
        if missing_cols:
            result.add_error(f"IP addresses table missing columns: {missing_cols}")

        if len(df) < 1000:
            result.add_error(f"IP address count ({len(df)}) is less than required minimum of 1000.")

        if df["ip_id"].duplicated().any():
            result.add_error("Duplicate ip_id found in ip_addresses table.")

        if df.isnull().any().any():
            null_cols = df.columns[df.isnull().any()].tolist()
            result.add_error(f"Unexpected null values in ip_addresses table: {null_cols}")

        result.stats["ip_count"] = len(df)

    def _validate_payment_methods(self, df: Optional[pd.DataFrame], result: ValidationResult) -> None:
        if df is None or df.empty:
            result.add_error("Payment methods dataset is missing or empty.")
            return

        expected_cols = {"payment_method_id", "payment_type", "issuer_category"}
        missing_cols = expected_cols - set(df.columns)
        if missing_cols:
            result.add_error(f"Payment methods table missing columns: {missing_cols}")

        if len(df) < 500:
            result.add_error(f"Payment method count ({len(df)}) is less than required minimum of 500.")

        if df["payment_method_id"].duplicated().any():
            result.add_error("Duplicate payment_method_id found in payment_methods table.")

        if df.isnull().any().any():
            null_cols = df.columns[df.isnull().any()].tolist()
            result.add_error(f"Unexpected null values in payment_methods table: {null_cols}")

        result.stats["payment_method_count"] = len(df)

    def _validate_merchants(self, df: Optional[pd.DataFrame], result: ValidationResult) -> None:
        if df is None or df.empty:
            result.add_error("Merchants dataset is missing or empty.")
            return

        expected_cols = {"merchant_id", "merchant_category", "merchant_size", "city"}
        missing_cols = expected_cols - set(df.columns)
        if missing_cols:
            result.add_error(f"Merchants table missing columns: {missing_cols}")

        if len(df) < 100:
            result.add_error(f"Merchant count ({len(df)}) is less than required minimum of 100.")

        if df["merchant_id"].duplicated().any():
            result.add_error("Duplicate merchant_id found in merchants table.")

        if df.isnull().any().any():
            null_cols = df.columns[df.isnull().any()].tolist()
            result.add_error(f"Unexpected null values in merchants table: {null_cols}")

        result.stats["merchant_count"] = len(df)

    def _validate_transactions(self, datasets: Dict[str, pd.DataFrame], result: ValidationResult) -> None:
        txns = datasets.get("transactions")
        if txns is None or txns.empty:
            result.add_error("Transactions dataset is missing or empty.")
            return

        expected_cols = {
            "transaction_id",
            "customer_id",
            "merchant_id",
            "device_id",
            "ip_id",
            "payment_method_id",
            "timestamp",
            "amount",
            "currency",
            "transaction_status",
            "payment_type",
            "city",
            "is_fraud",
            "fraud_ring_id",
            "fraud_type",
        }
        missing_cols = expected_cols - set(txns.columns)
        if missing_cols:
            result.add_error(f"Transactions table missing columns: {missing_cols}")

        if len(txns) < 10000:
            result.add_error(f"Transaction count ({len(txns)}) is less than required minimum of 10000.")

        if txns["transaction_id"].duplicated().any():
            result.add_error("Duplicate transaction_id found in transactions table.")

        # Amount validation
        if not pd.api.types.is_numeric_dtype(txns["amount"]):
            result.add_error("Transaction amount column is not numeric.")
        elif (txns["amount"] <= 0).any():
            result.add_error("Non-positive transaction amounts found.")

        # Currency validation
        if not (txns["currency"] == "INR").all():
            invalid_curr = txns[txns["currency"] != "INR"]["currency"].unique()
            result.add_error(f"Unexpected currency found: {invalid_curr}")

        # Status validation
        invalid_statuses = set(txns["transaction_status"].unique()) - self.ALLOWED_STATUSES
        if invalid_statuses:
            result.add_error(f"Invalid transaction statuses found: {invalid_statuses}")

        # Foreign key integrity
        cust_df = datasets.get("customers")
        if cust_df is not None:
            invalid_custs = set(txns["customer_id"]) - set(cust_df["customer_id"])
            if invalid_custs:
                result.add_error(f"Foreign key violation: transactions contain unknown customer_ids ({len(invalid_custs)} invalid).")

        merch_df = datasets.get("merchants")
        if merch_df is not None:
            invalid_merchs = set(txns["merchant_id"]) - set(merch_df["merchant_id"])
            if invalid_merchs:
                result.add_error(f"Foreign key violation: transactions contain unknown merchant_ids ({len(invalid_merchs)} invalid).")

        dev_df = datasets.get("devices")
        if dev_df is not None:
            invalid_devs = set(txns["device_id"]) - set(dev_df["device_id"])
            if invalid_devs:
                result.add_error(f"Foreign key violation: transactions contain unknown device_ids ({len(invalid_devs)} invalid).")

        ip_df = datasets.get("ip_addresses")
        if ip_df is not None:
            invalid_ips = set(txns["ip_id"]) - set(ip_df["ip_id"])
            if invalid_ips:
                result.add_error(f"Foreign key violation: transactions contain unknown ip_ids ({len(invalid_ips)} invalid).")

        pm_df = datasets.get("payment_methods")
        if pm_df is not None:
            invalid_pms = set(txns["payment_method_id"]) - set(pm_df["payment_method_id"])
            if invalid_pms:
                result.add_error(f"Foreign key violation: transactions contain unknown payment_method_ids ({len(invalid_pms)} invalid).")

        # Timestamp validation & chronological logic
        try:
            tx_times = pd.to_datetime(txns["timestamp"])
            if cust_df is not None:
                cust_created = cust_df.set_index("customer_id")["account_created_at"]
                cust_created_dt = pd.to_datetime(cust_created)
                merged_tx_cust = txns[["transaction_id", "customer_id", "timestamp"]].copy()
                merged_tx_cust["account_created_at"] = merged_tx_cust["customer_id"].map(cust_created_dt)
                merged_tx_cust["tx_dt"] = pd.to_datetime(merged_tx_cust["timestamp"])
                
                # Transaction cannot happen before account creation
                time_violations = merged_tx_cust[merged_tx_cust["tx_dt"] < merged_tx_cust["account_created_at"]]
                if not time_violations.empty:
                    result.add_error(
                        f"Chronological violation: {len(time_violations)} transactions occurred before customer account creation timestamp."
                    )
        except Exception as e:
            result.add_error(f"Error validating transaction timestamps: {str(e)}")

        # Ground truth labels validation
        if not set(txns["is_fraud"].unique()).issubset({0, 1}):
            result.add_error("is_fraud contains values other than 0 and 1.")

        fraud_txns = txns[txns["is_fraud"] == 1]
        legit_txns = txns[txns["is_fraud"] == 0]

        if fraud_txns.empty:
            result.add_error("No fraud transactions found in dataset.")

        # Ensure legit txns have empty/null fraud_ring_id and fraud_type
        legit_ring_ids = legit_txns["fraud_ring_id"].fillna("").astype(str).str.strip()
        if (legit_ring_ids != "").any():
            result.add_error("Legitimate transactions (is_fraud=0) have non-empty fraud_ring_id.")

        legit_fraud_types = legit_txns["fraud_type"].fillna("").astype(str).str.strip()
        if (legit_fraud_types != "").any():
            result.add_error("Legitimate transactions (is_fraud=0) have non-empty fraud_type.")

        # Ensure fraud txns have valid fraud_type and non-empty fraud_ring_id
        invalid_fraud_types = set(fraud_txns["fraud_type"].dropna().unique()) - self.ALLOWED_FRAUD_TYPES
        if invalid_fraud_types:
            result.add_error(f"Invalid fraud_type labels found: {invalid_fraud_types}")

        empty_fraud_rings = fraud_txns[fraud_txns["fraud_ring_id"].fillna("").astype(str).str.strip() == ""]
        if not empty_fraud_rings.empty:
            result.add_error(f"{len(empty_fraud_rings)} fraud transactions have missing fraud_ring_id.")

        # Ring statistics
        unique_rings = fraud_txns["fraud_ring_id"].dropna().unique()
        if len(unique_rings) < 5 or len(unique_rings) > 10:
            result.add_error(f"Expected 5-10 fraud rings, found {len(unique_rings)}.")

        # Verify each ring has multiple customers
        for ring_id in unique_rings:
            ring_custs = fraud_txns[fraud_txns["fraud_ring_id"] == ring_id]["customer_id"].unique()
            if len(ring_custs) < 2:
                result.add_error(f"Fraud ring {ring_id} contains only {len(ring_custs)} customer(s); rings must connect multiple accounts.")

        result.stats["transaction_count"] = len(txns)
        result.stats["fraud_transaction_count"] = len(fraud_txns)
        result.stats["fraud_rate_pct"] = round(len(fraud_txns) / len(txns) * 100, 2)
        result.stats["total_volume_inr"] = round(txns["amount"].sum(), 2)
        result.stats["fraud_volume_inr"] = round(fraud_txns["amount"].sum(), 2)
        result.stats["fraud_ring_count"] = len(unique_rings)
        result.stats["fraud_types"] = list(fraud_txns["fraud_type"].unique())


def main():
    """CLI execution entrypoint for data validation."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    validator = DatasetValidator()
    print("Running FraudGraph dataset validation...")
    res = validator.validate_all()

    print("\n" + "=" * 40)
    print("VALIDATION REPORT")
    print("=" * 40)
    print(f"Status: {'PASSED [VALID]' if res.is_valid else 'FAILED [INVALID]'}")
    
    if res.stats:
        print("\n--- Summary Statistics ---")
        for k, v in res.stats.items():
            print(f"  {k}: {v}")

    if res.warnings:
        print("\n--- Warnings ---")
        for w in res.warnings:
            print(f"  [WARN] {w}")

    if res.errors:
        print("\n--- Validation Errors ---")
        for e in res.errors:
            print(f"  [ERROR] {e}")
        print("=" * 40)
        sys.exit(1)
    else:
        print("\nAll dataset integrity and relationship checks passed successfully!")
        print("=" * 40)


if __name__ == "__main__":
    import sys
    main()
