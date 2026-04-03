import os
from dotenv import load_dotenv

load_dotenv()

BUILDER_CODE = os.getenv("VAULT_BUILDER_CODE", "SPAGHETTIVAULT1")
PERFORMANCE_FEE_PCT = float(os.getenv("PERFORMANCE_FEE_PCT", "0.15"))
