"""Dataset validation script CLI for FraudGraph."""

import sys
from pathlib import Path

# Ensure backend package can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.utils.validator import main

if __name__ == "__main__":
    main()
