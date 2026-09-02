"""Unit and integration test suite for FraudGraph synthetic dataset and validator."""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from backend.config.settings import get_settings
from backend.utils.validator import DatasetValidator, ValidationResult
from data.generate_data import FintechDataGenerator


@pytest.fixture(scope="module")
def settings():
    return get_settings()


@pytest.fixture(scope="module")
def generated_data(settings):
    generator = FintechDataGenerator(seed=settings.random_seed)
    datasets = generator.generate_all(
        num_customers=settings.num_customers,
        num_transactions=settings.num_transactions,
        num_devices=settings.num_devices,
        num_ips=settings.num_ips,
        num_payment_methods=settings.num_payment_methods,
        num_merchants=settings.num_merchants,
    )
    return datasets


def test_dataset_sizes(generated_data, settings):
    """Verify that all generated datasets satisfy minimum size requirements."""
    assert len(generated_data["customers"]) >= 2000
    assert len(generated_data["transactions"]) >= 10000
    assert len(generated_data["devices"]) >= 500
    assert len(generated_data["ip_addresses"]) >= 1000
    assert len(generated_data["payment_methods"]) >= 500
    assert len(generated_data["merchants"]) >= 100


def test_unique_customer_ids(generated_data):
    """Verify all customer IDs are strictly unique."""
    cust_df = generated_data["customers"]
    assert cust_df["customer_id"].is_unique
    assert cust_df["customer_id"].isnull().sum() == 0


def test_unique_transaction_ids(generated_data):
    """Verify all transaction IDs are strictly unique."""
    txn_df = generated_data["transactions"]
    assert txn_df["transaction_id"].is_unique
    assert txn_df["transaction_id"].isnull().sum() == 0


def test_foreign_key_relationships(generated_data):
    """Verify referential integrity across all transactional foreign keys."""
    txns = generated_data["transactions"]
    customers = set(generated_data["customers"]["customer_id"])
    merchants = set(generated_data["merchants"]["merchant_id"])
    devices = set(generated_data["devices"]["device_id"])
    ips = set(generated_data["ip_addresses"]["ip_id"])
    pms = set(generated_data["payment_methods"]["payment_method_id"])

    # Check foreign keys
    assert set(txns["customer_id"]).issubset(customers)
    assert set(txns["merchant_id"]).issubset(merchants)
    assert set(txns["device_id"]).issubset(devices)
    assert set(txns["ip_id"]).issubset(ips)
    assert set(txns["payment_method_id"]).issubset(pms)


def test_no_invalid_amounts(generated_data):
    """Verify transaction amounts are strictly positive and properly numeric."""
    txns = generated_data["transactions"]
    assert pd.api.types.is_numeric_dtype(txns["amount"])
    assert (txns["amount"] > 0).all()
    assert txns["amount"].isnull().sum() == 0


def test_timestamps_chronological_integrity(generated_data):
    """Verify timestamps are valid ISO datetimes and occur after customer account creation."""
    txns = generated_data["transactions"]
    customers = generated_data["customers"].set_index("customer_id")

    txn_times = pd.to_datetime(txns["timestamp"])
    assert txn_times.isnull().sum() == 0

    merged = txns[["customer_id", "timestamp"]].copy()
    merged["account_created_at"] = merged["customer_id"].map(
        pd.to_datetime(customers["account_created_at"])
    )
    merged["txn_dt"] = pd.to_datetime(merged["timestamp"])

    # Every transaction must happen on or after account creation
    violations = merged[merged["txn_dt"] < merged["account_created_at"]]
    assert len(violations) == 0, f"Found {len(violations)} transactions before account creation."


def test_no_unexpected_null_values(generated_data):
    """Verify that primary attributes have no null values."""
    for table_name in ["customers", "devices", "ip_addresses", "payment_methods", "merchants"]:
        df = generated_data[table_name]
        assert df.isnull().sum().sum() == 0, f"Nulls found in {table_name}"

    # For transactions, everything except fraud fields (which can be empty strings) must be non-null
    txns = generated_data["transactions"]
    non_fraud_cols = [c for c in txns.columns if c not in ["fraud_ring_id", "fraud_type"]]
    assert txns[non_fraud_cols].isnull().sum().sum() == 0


def test_fraud_ring_labels_and_structure(generated_data):
    """Verify ground truth fraud labels, fraud types, and ring topologies."""
    txns = generated_data["transactions"]
    
    assert set(txns["is_fraud"].unique()) == {0, 1}
    
    fraud_txns = txns[txns["is_fraud"] == 1]
    legit_txns = txns[txns["is_fraud"] == 0]

    assert len(fraud_txns) > 0
    assert len(legit_txns) > len(fraud_txns)

    # Legitimate transactions must have empty fraud labels
    assert (legit_txns["fraud_ring_id"].fillna("") == "").all()
    assert (legit_txns["fraud_type"].fillna("") == "").all()

    # Fraud transactions must have valid fraud types
    valid_types = {
        "shared_device",
        "shared_ip",
        "shared_payment",
        "coordinated_timing",
        "merchant_targeting",
        "geographic",
        "mixed",
    }
    assert set(fraud_txns["fraud_type"].unique()).issubset(valid_types)

    # Number of rings must be between 5 and 10
    unique_rings = fraud_txns["fraud_ring_id"].dropna().unique()
    assert 5 <= len(unique_rings) <= 10

    # Each ring must connect multiple customer accounts
    for ring_id in unique_rings:
        ring_custs = fraud_txns[fraud_txns["fraud_ring_id"] == ring_id]["customer_id"].unique()
        assert len(ring_custs) >= 2, f"Ring {ring_id} contains only {len(ring_custs)} member(s)."


def test_reproducibility():
    """Verify that generating data with the same seed produces identical datasets."""
    gen1 = FintechDataGenerator(seed=12345)
    data1 = gen1.generate_all(num_customers=50, num_transactions=200, num_devices=30, num_ips=50, num_payment_methods=30, num_merchants=20)

    gen2 = FintechDataGenerator(seed=12345)
    data2 = gen2.generate_all(num_customers=50, num_transactions=200, num_devices=30, num_ips=50, num_payment_methods=30, num_merchants=20)

    for key in data1:
        pd.testing.assert_frame_equal(data1[key], data2[key])


def test_validator_engine(generated_data):
    """Verify that the DatasetValidator runs cleanly on valid generated datasets."""
    validator = DatasetValidator()
    result = validator.validate_all(generated_data)

    assert result.is_valid, f"Validation failed with errors: {result.errors}"
    assert len(result.errors) == 0
    assert result.stats["customer_count"] >= 2000
    assert result.stats["transaction_count"] >= 10000
    assert result.stats["fraud_ring_count"] >= 5


def test_legitimate_noise_shared_entities(generated_data):
    """Verify that legitimate users can share devices/IPs without being labeled fraud."""
    txns = generated_data["transactions"]
    legit_txns = txns[txns["is_fraud"] == 0]

    # Check that legitimate transactions have devices used by multiple distinct legitimate customers
    dev_to_custs = legit_txns.groupby("device_id")["customer_id"].nunique()
    shared_legit_devs = dev_to_custs[dev_to_custs > 1]
    assert len(shared_legit_devs) > 0, "Legitimate shared devices should exist as realistic noise."

    # Check that legitimate transactions have IPs used by multiple distinct legitimate customers
    ip_to_custs = legit_txns.groupby("ip_id")["customer_id"].nunique()
    shared_legit_ips = ip_to_custs[ip_to_custs > 1]
    assert len(shared_legit_ips) > 0, "Legitimate shared IPs should exist as realistic noise."


def test_no_pii_or_real_payment_secrets(generated_data):
    """Verify that no real card PANs, secrets, or API keys are present in datasets."""
    import re
    # Standard 16-digit card pattern
    pan_regex = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
    
    # Check payment methods
    pm_df = generated_data["payment_methods"]
    for col in pm_df.columns:
        for val in pm_df[col].astype(str):
            assert not pan_regex.search(val)
            assert "sk_test_" not in val and "sk_live_" not in val and "rzp_" not in val

    # Check transactions
    txns = generated_data["transactions"]
    for col in ["transaction_id", "payment_method_id", "customer_id"]:
        for val in txns[col].astype(str):
            assert "sk_test_" not in val and "sk_live_" not in val and "rzp_" not in val
