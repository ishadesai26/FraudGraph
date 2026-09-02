"""Application configuration loaded from environment variables."""

import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

# Base Directory of the Project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env if present
load_dotenv(BASE_DIR / ".env")


@dataclass
class Settings:
    """FraudGraph project settings and parameters."""
    
    app_env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Random seed for reproducible synthetic generation
    random_seed: int = int(os.getenv("RANDOM_SEED", "42"))
    
    # Dataset generation defaults
    num_customers: int = int(os.getenv("NUM_CUSTOMERS", "2000"))
    num_transactions: int = int(os.getenv("NUM_TRANSACTIONS", "10000"))
    num_devices: int = int(os.getenv("NUM_DEVICES", "500"))
    num_ips: int = int(os.getenv("NUM_IPS", "1000"))
    num_payment_methods: int = int(os.getenv("NUM_PAYMENT_METHODS", "500"))
    num_merchants: int = int(os.getenv("NUM_MERCHANTS", "100"))
    
    # Paths
    base_dir: Path = BASE_DIR
    raw_data_dir: Path = BASE_DIR / os.getenv("DATA_RAW_DIR", "data/raw")
    processed_data_dir: Path = BASE_DIR / os.getenv("DATA_PROCESSED_DIR", "data/processed")


_settings_instance = None


def get_settings() -> Settings:
    """Get or create singleton configuration settings instance."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance
