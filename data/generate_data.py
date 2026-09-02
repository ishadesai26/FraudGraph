"""Synthetic Fintech Dataset Generator for FraudGraph.

Generates reproducible synthetic digital payment ecosystems comprising:
- Customers
- Transactions
- Devices
- IP Addresses
- Payment Instruments
- Merchants

Injects 7 distinct coordinated fraud ring archetypes with realistic background noise.
"""

import sys
import os
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from faker import Faker

# Ensure backend package can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.config.settings import get_settings


# Major Indian fintech and digital commerce hubs
CITIES = [
    "Mumbai",
    "Bengaluru",
    "Delhi",
    "Hyderabad",
    "Chennai",
    "Pune",
    "Kolkata",
    "Ahmedabad",
    "Jaipur",
    "Surat",
]

CUSTOMER_SEGMENTS = ["RETAIL", "PREMIUM", "STUDENT", "SALARIED", "SME"]
SEGMENT_WEIGHTS = [0.45, 0.15, 0.15, 0.20, 0.05]

DEVICE_TYPES = ["MOBILE", "DESKTOP", "TABLET"]
DEVICE_WEIGHTS = [0.75, 0.20, 0.05]

OS_BY_DEVICE = {
    "MOBILE": ["Android", "iOS"],
    "MOBILE_WEIGHTS": [0.80, 0.20],
    "DESKTOP": ["Windows", "macOS", "Linux"],
    "DESKTOP_WEIGHTS": [0.70, 0.25, 0.05],
    "TABLET": ["Android", "iPadOS"],
    "TABLET_WEIGHTS": [0.60, 0.40],
}

IP_TYPES = ["RESIDENTIAL", "MOBILE_CARRIER", "DATACENTER", "VPN", "PUBLIC_WIFI"]
IP_WEIGHTS = [0.45, 0.40, 0.05, 0.05, 0.05]

PAYMENT_TYPES = ["UPI", "CREDIT_CARD", "DEBIT_CARD", "NET_BANKING", "WALLET"]
PAYMENT_WEIGHTS = [0.55, 0.20, 0.15, 0.05, 0.05]

ISSUER_CATEGORIES = [
    "PUBLIC_BANK",
    "PRIVATE_BANK",
    "FINTECH_WALLET",
    "NEOBANK",
    "INTERNATIONAL_CARD",
]
ISSUER_WEIGHTS = [0.35, 0.45, 0.10, 0.08, 0.02]

MERCHANT_CATEGORIES = [
    "ECOMMERCE",
    "FOOD_DELIVERY",
    "GROCERY",
    "ELECTRONICS",
    "TRAVEL",
    "GAMING",
    "UTILITIES",
    "JEWELRY",
    "DIGITAL_ENTERTAINMENT",
    "FASHION",
]

MERCHANT_SIZES = ["SMALL", "MEDIUM", "LARGE", "ENTERPRISE"]
MERCHANT_SIZE_WEIGHTS = [0.40, 0.35, 0.20, 0.05]


class FintechDataGenerator:
    """Generates synthetic fintech transactions and entity tables with injected fraud rings."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.fake = Faker("en_IN")
        self._set_seed(seed)
        
        # Fixed time horizon: 60 days of transaction activity
        self.end_date = datetime(2026, 3, 1, 23, 59, 59)
        self.start_date = self.end_date - timedelta(days=60)

    def _set_seed(self, seed: int):
        random.seed(seed)
        np.random.seed(seed)
        Faker.seed(seed)

    def generate_devices(self, count: int) -> pd.DataFrame:
        """Generates synthetic device records."""
        records = []
        for i in range(1, count + 1):
            dev_id = f"DEV_{i:04d}"
            dev_type = random.choices(DEVICE_TYPES, weights=DEVICE_WEIGHTS, k=1)[0]
            if dev_type == "MOBILE":
                os_name = random.choices(
                    OS_BY_DEVICE["MOBILE"], weights=OS_BY_DEVICE["MOBILE_WEIGHTS"], k=1
                )[0]
            elif dev_type == "DESKTOP":
                os_name = random.choices(
                    OS_BY_DEVICE["DESKTOP"], weights=OS_BY_DEVICE["DESKTOP_WEIGHTS"], k=1
                )[0]
            else:
                os_name = random.choices(
                    OS_BY_DEVICE["TABLET"], weights=OS_BY_DEVICE["TABLET_WEIGHTS"], k=1
                )[0]

            age_days = random.randint(15, 1800)
            records.append({
                "device_id": dev_id,
                "device_type": dev_type,
                "os": os_name,
                "device_age_days": age_days,
            })
        return pd.DataFrame(records)

    def generate_ip_addresses(self, count: int) -> pd.DataFrame:
        """Generates synthetic IP address entities with location mapping."""
        records = []
        for i in range(1, count + 1):
            ip_id = f"IP_{i:05d}"
            ip_type = random.choices(IP_TYPES, weights=IP_WEIGHTS, k=1)[0]
            city = random.choice(CITIES)
            
            # Very small portion of datacenter / vpn ips might appear international
            if ip_type in ["DATACENTER", "VPN"] and random.random() < 0.15:
                country = random.choice(["SG", "US", "AE", "GB", "NL"])
            else:
                country = "IN"

            records.append({
                "ip_id": ip_id,
                "ip_type": ip_type,
                "country": country,
                "city": city,
            })
        return pd.DataFrame(records)

    def generate_payment_methods(self, count: int) -> pd.DataFrame:
        """Generates synthetic payment instruments without storing sensitive information."""
        records = []
        for i in range(1, count + 1):
            pm_id = f"PM_{i:04d}"
            p_type = random.choices(PAYMENT_TYPES, weights=PAYMENT_WEIGHTS, k=1)[0]
            issuer = random.choices(ISSUER_CATEGORIES, weights=ISSUER_WEIGHTS, k=1)[0]
            records.append({
                "payment_method_id": pm_id,
                "payment_type": p_type,
                "issuer_category": issuer,
            })
        return pd.DataFrame(records)

    def generate_merchants(self, count: int) -> pd.DataFrame:
        """Generates merchant registry records."""
        records = []
        for i in range(1, count + 1):
            m_id = f"MERCH_{i:04d}"
            category = random.choice(MERCHANT_CATEGORIES)
            size = random.choices(MERCHANT_SIZES, weights=MERCHANT_SIZE_WEIGHTS, k=1)[0]
            city = random.choice(CITIES)
            records.append({
                "merchant_id": m_id,
                "merchant_category": category,
                "merchant_size": size,
                "city": city,
            })
        return pd.DataFrame(records)

    def generate_customers(self, count: int) -> pd.DataFrame:
        """Generates customer accounts with demographic and account metadata."""
        records = []
        for i in range(1, count + 1):
            c_id = f"CUST_{i:05d}"
            # Normal distribution of customer age, clamped between 18 and 75
            age = int(np.clip(np.random.normal(34, 11), 18, 75))
            segment = random.choices(CUSTOMER_SEGMENTS, weights=SEGMENT_WEIGHTS, k=1)[0]
            
            # Account creation between 65 and 1200 days prior to end_date
            account_age_days = random.randint(65, 1200)
            created_at = self.end_date - timedelta(
                days=account_age_days,
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59),
            )
            city = random.choice(CITIES)

            records.append({
                "customer_id": c_id,
                "customer_age": age,
                "customer_segment": segment,
                "account_age_days": account_age_days,
                "country": "IN",
                "city": city,
                "account_created_at": created_at.isoformat(),
            })
        return pd.DataFrame(records)

    def generate_transactions(
        self,
        num_transactions: int,
        customers_df: pd.DataFrame,
        devices_df: pd.DataFrame,
        ips_df: pd.DataFrame,
        payment_methods_df: pd.DataFrame,
        merchants_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """Generates realistic transaction log with 7 injected fraud ring archetypes."""
        
        customer_ids = customers_df["customer_id"].tolist()
        device_ids = devices_df["device_id"].tolist()
        ip_ids = ips_df["ip_id"].tolist()
        pm_ids = payment_methods_df["payment_method_id"].tolist()
        merch_ids = merchants_df["merchant_id"].tolist()

        pm_type_lookup = payment_methods_df.set_index("payment_method_id")["payment_type"].to_dict()
        cust_city_lookup = customers_df.set_index("customer_id")["city"].to_dict()
        cust_created_lookup = customers_df.set_index("customer_id")["account_created_at"].to_dict()

        # Build natural customer behavioral affinity mapping
        # Each customer has: primary device, 20% have secondary device; primary IP, secondary IPs; primary PM
        cust_profiles = {}
        for cid in customer_ids:
            primary_dev = random.choice(device_ids)
            secondary_dev = random.choice(device_ids) if random.random() < 0.25 else primary_dev
            
            primary_ip = random.choice(ip_ids)
            secondary_ip = random.choice(ip_ids) if random.random() < 0.40 else primary_ip
            
            primary_pm = random.choice(pm_ids)
            secondary_pm = random.choice(pm_ids) if random.random() < 0.30 else primary_pm
            
            preferred_merchants = random.sample(merch_ids, k=min(len(merch_ids), random.randint(3, 8)))

            cust_profiles[cid] = {
                "devices": [primary_dev, secondary_dev],
                "ips": [primary_ip, secondary_ip],
                "payment_methods": [primary_pm, secondary_pm],
                "merchants": preferred_merchants,
            }

        # -------------------------------------------------------------
        # 1. GENERATE INJECTED FRAUD RINGS (7 DISTINCT ARCHETYPES)
        # -------------------------------------------------------------
        fraud_transactions: List[Dict] = []
        used_fraud_cust_ids = set()

        # Definition of 7 Fraud Rings with dynamic indexing into entity pools
        rings_config = [
            {
                "ring_id": "RING_01",
                "fraud_type": "shared_device",
                "num_members": 7,
                "num_txns": 38,
                "shared_devices": [device_ids[11 % len(device_ids)], device_ids[12 % len(device_ids)]],
                "amount_range": (3500.0, 18000.0),
                "desc": "Emulator device farm shared across 7 accounts",
            },
            {
                "ring_id": "RING_02",
                "fraud_type": "shared_ip",
                "num_members": 8,
                "num_txns": 42,
                "shared_ips": [ip_ids[44 % len(ip_ids)]],
                "amount_range": (1500.0, 9500.0),
                "desc": "Datacenter proxy IP rotating account attacks",
            },
            {
                "ring_id": "RING_03",
                "fraud_type": "shared_payment",
                "num_members": 6,
                "num_txns": 35,
                "shared_pms": [pm_ids[87 % len(pm_ids)], pm_ids[88 % len(pm_ids)]],
                "amount_range": (12000.0, 48000.0),
                "desc": "Stolen credit card syndication across synthetic accounts",
            },
            {
                "ring_id": "RING_04",
                "fraud_type": "coordinated_timing",
                "num_members": 6,
                "num_txns": 30,
                "amount_range": (5000.0, 24000.0),
                "desc": "Synchronized burst attacks in narrow 2-minute time windows",
            },
            {
                "ring_id": "RING_05",
                "fraud_type": "merchant_targeting",
                "num_members": 8,
                "num_txns": 40,
                "target_merchants": [merch_ids[22 % len(merch_ids)], merch_ids[23 % len(merch_ids)]],
                "amount_range": (28000.0, 85000.0),
                "desc": "Coordinated liquidation attack on high-ticket electronics merchants",
            },
            {
                "ring_id": "RING_06",
                "fraud_type": "geographic",
                "num_members": 7,
                "num_txns": 36,
                "amount_range": (7500.0, 32000.0),
                "desc": "Impossible speed location jumps and multi-city proxy routing",
            },
            {
                "ring_id": "RING_07",
                "fraud_type": "mixed",
                "num_members": 10,
                "num_txns": 54,
                "shared_devices": [device_ids[94 % len(device_ids)]],
                "shared_ips": [ip_ids[119 % len(ip_ids)]],
                "shared_pms": [pm_ids[149 % len(pm_ids)]],
                "target_merchants": [merch_ids[44 % len(merch_ids)], merch_ids[45 % len(merch_ids)]],
                "amount_range": (18000.0, 92000.0),
                "desc": "Multi-vector organized crime ring combining shared device, IP, and mule cards",
            },
        ]

        cust_cursor = 10 if len(customer_ids) >= 100 else 0
        for r in rings_config:
            # Safely slice members from customer_ids
            members_count = min(r["num_members"], max(2, len(customer_ids) // len(rings_config)))
            start_idx = cust_cursor % len(customer_ids)
            r_members = [
                customer_ids[(start_idx + j) % len(customer_ids)]
                for j in range(members_count)
            ]
            cust_cursor += members_count + 1
            used_fraud_cust_ids.update(r_members)

            # Generate specific fraud patterns
            ring_id = r["ring_id"]
            ftype = r["fraud_type"]

            if ftype == "shared_device":
                devs = r["shared_devices"]
                for _ in range(r["num_txns"]):
                    cid = random.choice(r_members)
                    mid = random.choice(merch_ids)
                    pid = random.choice(cust_profiles[cid]["payment_methods"])
                    ipid = random.choice(cust_profiles[cid]["ips"])
                    dev = random.choice(devs)
                    # Clustered timestamps in last 20 days
                    tx_time = self.end_date - timedelta(
                        days=random.randint(1, 20),
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59),
                        seconds=random.randint(0, 59),
                    )
                    amount = round(random.uniform(*r["amount_range"]), 2)
                    fraud_transactions.append({
                        "customer_id": cid,
                        "merchant_id": mid,
                        "device_id": dev,
                        "ip_id": ipid,
                        "payment_method_id": pid,
                        "timestamp": tx_time.isoformat(),
                        "amount": amount,
                        "currency": "INR",
                        "transaction_status": "SUCCESS" if random.random() < 0.90 else "FAILED",
                        "payment_type": pm_type_lookup[pid],
                        "city": cust_city_lookup[cid],
                        "is_fraud": 1,
                        "fraud_ring_id": ring_id,
                        "fraud_type": ftype,
                    })

            elif ftype == "shared_ip":
                shared_ip = r["shared_ips"][0]
                for _ in range(r["num_txns"]):
                    cid = random.choice(r_members)
                    mid = random.choice(merch_ids)
                    dev = random.choice(cust_profiles[cid]["devices"])
                    pid = random.choice(cust_profiles[cid]["payment_methods"])
                    tx_time = self.end_date - timedelta(
                        days=random.randint(1, 25),
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59),
                        seconds=random.randint(0, 59),
                    )
                    amount = round(random.uniform(*r["amount_range"]), 2)
                    fraud_transactions.append({
                        "customer_id": cid,
                        "merchant_id": mid,
                        "device_id": dev,
                        "ip_id": shared_ip,
                        "payment_method_id": pid,
                        "timestamp": tx_time.isoformat(),
                        "amount": amount,
                        "currency": "INR",
                        "transaction_status": "SUCCESS" if random.random() < 0.92 else "FAILED",
                        "payment_type": pm_type_lookup[pid],
                        "city": cust_city_lookup[cid],
                        "is_fraud": 1,
                        "fraud_ring_id": ring_id,
                        "fraud_type": ftype,
                    })

            elif ftype == "shared_payment":
                shared_pms = r["shared_pms"]
                for _ in range(r["num_txns"]):
                    cid = random.choice(r_members)
                    mid = random.choice(merch_ids)
                    dev = random.choice(cust_profiles[cid]["devices"])
                    ipid = random.choice(cust_profiles[cid]["ips"])
                    pid = random.choice(shared_pms)
                    tx_time = self.end_date - timedelta(
                        days=random.randint(1, 30),
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59),
                        seconds=random.randint(0, 59),
                    )
                    amount = round(random.uniform(*r["amount_range"]), 2)
                    fraud_transactions.append({
                        "customer_id": cid,
                        "merchant_id": mid,
                        "device_id": dev,
                        "ip_id": ipid,
                        "payment_method_id": pid,
                        "timestamp": tx_time.isoformat(),
                        "amount": amount,
                        "currency": "INR",
                        "transaction_status": "SUCCESS" if random.random() < 0.88 else "FAILED",
                        "payment_type": pm_type_lookup[pid],
                        "city": cust_city_lookup[cid],
                        "is_fraud": 1,
                        "fraud_ring_id": ring_id,
                        "fraud_type": ftype,
                    })

            elif ftype == "coordinated_timing":
                # Multiple distinct clusters of synchronized burst seconds
                burst_centers = [
                    self.end_date - timedelta(days=d, hours=h, minutes=m)
                    for d, h, m in [(5, 14, 30), (12, 21, 15), (19, 3, 45), (28, 18, 20)]
                ]
                for i in range(r["num_txns"]):
                    cid = r_members[i % len(r_members)]
                    burst_center = burst_centers[i % len(burst_centers)]
                    # Offset within +/- 90 seconds
                    tx_time = burst_center + timedelta(seconds=random.randint(-90, 90))
                    dev = random.choice(cust_profiles[cid]["devices"])
                    ipid = random.choice(cust_profiles[cid]["ips"])
                    pid = random.choice(cust_profiles[cid]["payment_methods"])
                    mid = random.choice(merch_ids)
                    amount = round(random.uniform(*r["amount_range"]), 2)
                    fraud_transactions.append({
                        "customer_id": cid,
                        "merchant_id": mid,
                        "device_id": dev,
                        "ip_id": ipid,
                        "payment_method_id": pid,
                        "timestamp": tx_time.isoformat(),
                        "amount": amount,
                        "currency": "INR",
                        "transaction_status": "SUCCESS",
                        "payment_type": pm_type_lookup[pid],
                        "city": cust_city_lookup[cid],
                        "is_fraud": 1,
                        "fraud_ring_id": ring_id,
                        "fraud_type": ftype,
                    })

            elif ftype == "merchant_targeting":
                target_merchs = r["target_merchants"]
                for _ in range(r["num_txns"]):
                    cid = random.choice(r_members)
                    mid = random.choice(target_merchs)
                    dev = random.choice(cust_profiles[cid]["devices"])
                    ipid = random.choice(cust_profiles[cid]["ips"])
                    pid = random.choice(cust_profiles[cid]["payment_methods"])
                    tx_time = self.end_date - timedelta(
                        days=random.randint(1, 15),
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59),
                        seconds=random.randint(0, 59),
                    )
                    amount = round(random.uniform(*r["amount_range"]), 2)
                    fraud_transactions.append({
                        "customer_id": cid,
                        "merchant_id": mid,
                        "device_id": dev,
                        "ip_id": ipid,
                        "payment_method_id": pid,
                        "timestamp": tx_time.isoformat(),
                        "amount": amount,
                        "currency": "INR",
                        "transaction_status": "SUCCESS" if random.random() < 0.95 else "PENDING",
                        "payment_type": pm_type_lookup[pid],
                        "city": cust_city_lookup[cid],
                        "is_fraud": 1,
                        "fraud_ring_id": ring_id,
                        "fraud_type": ftype,
                    })

            elif ftype == "geographic":
                for _ in range(r["num_txns"]):
                    cid = random.choice(r_members)
                    home_city = cust_city_lookup[cid]
                    # Disparate anomalous city
                    remote_city = random.choice([c for c in CITIES if c != home_city])
                    mid = random.choice(merch_ids)
                    dev = random.choice(cust_profiles[cid]["devices"])
                    ipid = random.choice(cust_profiles[cid]["ips"])
                    pid = random.choice(cust_profiles[cid]["payment_methods"])
                    tx_time = self.end_date - timedelta(
                        days=random.randint(1, 35),
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59),
                        seconds=random.randint(0, 59),
                    )
                    amount = round(random.uniform(*r["amount_range"]), 2)
                    fraud_transactions.append({
                        "customer_id": cid,
                        "merchant_id": mid,
                        "device_id": dev,
                        "ip_id": ipid,
                        "payment_method_id": pid,
                        "timestamp": tx_time.isoformat(),
                        "amount": amount,
                        "currency": "INR",
                        "transaction_status": "SUCCESS" if random.random() < 0.85 else "FAILED",
                        "payment_type": pm_type_lookup[pid],
                        "city": remote_city,
                        "is_fraud": 1,
                        "fraud_ring_id": ring_id,
                        "fraud_type": ftype,
                    })

            elif ftype == "mixed":
                dev = r["shared_devices"][0]
                ipid = r["shared_ips"][0]
                pid = r["shared_pms"][0]
                target_merchs = r["target_merchants"]
                for _ in range(r["num_txns"]):
                    cid = random.choice(r_members)
                    mid = random.choice(target_merchs) if random.random() < 0.70 else random.choice(merch_ids)
                    use_dev = dev if random.random() < 0.75 else random.choice(cust_profiles[cid]["devices"])
                    use_ip = ipid if random.random() < 0.80 else random.choice(cust_profiles[cid]["ips"])
                    use_pm = pid if random.random() < 0.70 else random.choice(cust_profiles[cid]["payment_methods"])
                    
                    tx_time = self.end_date - timedelta(
                        days=random.randint(1, 20),
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59),
                        seconds=random.randint(0, 59),
                    )
                    amount = round(random.uniform(*r["amount_range"]), 2)
                    fraud_transactions.append({
                        "customer_id": cid,
                        "merchant_id": mid,
                        "device_id": use_dev,
                        "ip_id": use_ip,
                        "payment_method_id": use_pm,
                        "timestamp": tx_time.isoformat(),
                        "amount": amount,
                        "currency": "INR",
                        "transaction_status": "SUCCESS" if random.random() < 0.90 else "PENDING",
                        "payment_type": pm_type_lookup[use_pm],
                        "city": cust_city_lookup[cid],
                        "is_fraud": 1,
                        "fraud_ring_id": ring_id,
                        "fraud_type": ftype,
                    })

        # -------------------------------------------------------------
        # 2. GENERATE LEGITIMATE TRANSACTIONS & NATURAL NOISE
        # -------------------------------------------------------------
        num_fraud_txns = len(fraud_transactions)
        num_legit_txns = max(0, num_transactions - num_fraud_txns)
        legit_transactions: List[Dict] = []

        # Diurnal distribution weights for hour of day (low early morning, high afternoon & evening)
        hour_weights = [
            0.01, 0.005, 0.005, 0.005, 0.01, 0.02, # 00 - 05
            0.03, 0.05, 0.07, 0.08, 0.08, 0.08,    # 06 - 11
            0.09, 0.09, 0.07, 0.06, 0.06, 0.07,    # 12 - 17
            0.09, 0.09, 0.08, 0.06, 0.04, 0.02     # 18 - 23
        ]

        for _ in range(num_legit_txns):
            cid = random.choice(customer_ids)
            profile = cust_profiles[cid]
            
            # Legitimate shared device / shared IP noise:
            # 5% chance legitimate user uses a shared family device or public device
            if random.random() < 0.05:
                dev = random.choice(device_ids)
            else:
                dev = random.choice(profile["devices"])

            # 8% chance legitimate user uses an office / cafe / mobile roaming IP
            if random.random() < 0.08:
                ipid = random.choice(ip_ids)
            else:
                ipid = random.choice(profile["ips"])

            # 5% chance legitimate user uses an alternate payment instrument
            if random.random() < 0.05:
                pid = random.choice(pm_ids)
            else:
                pid = random.choice(profile["payment_methods"])

            # 70% merchant affinity, 30% random merchant
            if random.random() < 0.70:
                mid = random.choice(profile["merchants"])
            else:
                mid = random.choice(merch_ids)

            # Legitimate transaction amount tiers:
            # 65% low (₹50 - ₹1,500), 28% medium (₹1,500 - ₹15,000), 7% high (₹15,000 - ₹95,000)
            amt_tier = random.random()
            if amt_tier < 0.65:
                amount = round(np.random.exponential(scale=350) + 50.0, 2)
                amount = min(amount, 1500.0)
            elif amt_tier < 0.93:
                amount = round(random.uniform(1500.0, 15000.0), 2)
            else:
                amount = round(random.uniform(15000.0, 95000.0), 2)

            # Timestamp generation (within 60 days, ensuring it's strictly after customer creation)
            days_ago = random.randint(0, 59)
            hour = random.choices(range(24), weights=hour_weights, k=1)[0]
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            
            tx_time = self.end_date - timedelta(days=days_ago, hours=hour, minutes=minute, seconds=second)
            
            # Ensure chronological order with respect to account creation
            created_dt = datetime.fromisoformat(cust_created_lookup[cid])
            if tx_time <= created_dt:
                tx_time = created_dt + timedelta(hours=random.randint(1, 24))

            # Status distribution: 94% SUCCESS, 4% FAILED, 2% PENDING
            status_roll = random.random()
            if status_roll < 0.94:
                status = "SUCCESS"
            elif status_roll < 0.98:
                status = "FAILED"
            else:
                status = "PENDING"

            # 97% of transactions occur in the customer's home city, 3% travel/roaming
            tx_city = cust_city_lookup[cid] if random.random() < 0.97 else random.choice(CITIES)

            legit_transactions.append({
                "customer_id": cid,
                "merchant_id": mid,
                "device_id": dev,
                "ip_id": ipid,
                "payment_method_id": pid,
                "timestamp": tx_time.isoformat(),
                "amount": amount,
                "currency": "INR",
                "transaction_status": status,
                "payment_type": pm_type_lookup[pid],
                "city": tx_city,
                "is_fraud": 0,
                "fraud_ring_id": "",
                "fraud_type": "",
            })

        # Combine all transactions, sort chronologically, and assign unique transaction IDs
        all_txns = fraud_transactions + legit_transactions
        all_txns.sort(key=lambda x: x["timestamp"])

        for idx, txn in enumerate(all_txns, start=1):
            txn["transaction_id"] = f"TXN_{idx:05d}"

        # Reorder columns explicitly
        ordered_cols = [
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
        ]

        txns_df = pd.DataFrame(all_txns)[ordered_cols]
        return txns_df

    def generate_all(
        self,
        num_customers: int = 2000,
        num_transactions: int = 10000,
        num_devices: int = 500,
        num_ips: int = 1000,
        num_payment_methods: int = 500,
        num_merchants: int = 100,
    ) -> Dict[str, pd.DataFrame]:
        """Generates all 6 relational datasets."""
        devices_df = self.generate_devices(num_devices)
        ips_df = self.generate_ip_addresses(num_ips)
        pm_df = self.generate_payment_methods(num_payment_methods)
        merchants_df = self.generate_merchants(num_merchants)
        customers_df = self.generate_customers(num_customers)
        transactions_df = self.generate_transactions(
            num_transactions, customers_df, devices_df, ips_df, pm_df, merchants_df
        )

        return {
            "customers": customers_df,
            "transactions": transactions_df,
            "devices": devices_df,
            "ip_addresses": ips_df,
            "payment_methods": pm_df,
            "merchants": merchants_df,
        }

    def save_datasets(self, datasets: Dict[str, pd.DataFrame], output_dir: Path) -> None:
        """Saves generated DataFrames to CSV files."""
        output_dir.mkdir(parents=True, exist_ok=True)
        for name, df in datasets.items():
            filepath = output_dir / f"{name}.csv"
            df.to_csv(filepath, index=False)


def main():
    """CLI execution entrypoint."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    settings = get_settings()
    generator = FintechDataGenerator(seed=settings.random_seed)

    print(f"Generating synthetic fintech dataset with seed={settings.random_seed}...")
    datasets = generator.generate_all(
        num_customers=settings.num_customers,
        num_transactions=settings.num_transactions,
        num_devices=settings.num_devices,
        num_ips=settings.num_ips,
        num_payment_methods=settings.num_payment_methods,
        num_merchants=settings.num_merchants,
    )

    output_dir = settings.raw_data_dir
    generator.save_datasets(datasets, output_dir)

    txns_df = datasets["transactions"]
    fraud_txns = txns_df[txns_df["is_fraud"] == 1]
    unique_rings = fraud_txns["fraud_ring_id"].nunique()
    fraud_vol = fraud_txns["amount"].sum()

    print("\n" + "=" * 40)
    print("DATASET GENERATION SUMMARY")
    print("=" * 40)
    print(f"Customers: {len(datasets['customers'])}")
    print(f"Transactions: {len(txns_df)}")
    print(f"Devices: {len(datasets['devices'])}")
    print(f"IP addresses: {len(datasets['ip_addresses'])}")
    print(f"Payment methods: {len(datasets['payment_methods'])}")
    print(f"Merchants: {len(datasets['merchants'])}")
    print(f"Fraud rings: {unique_rings}")
    print(f"Fraud transactions: {len(fraud_txns)}")
    try:
        print(f"Fraud transaction volume: ₹{fraud_vol:,.2f}")
    except UnicodeEncodeError:
        print(f"Fraud transaction volume: INR {fraud_vol:,.2f}")
    print(f"Saved to: {output_dir}")
    print("=" * 40)


if __name__ == "__main__":
    main()

