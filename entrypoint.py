"""
Docker entry point with optional demo mode.
Allows running in demo mode for local testing or API mode for production.
"""

import os
import sys
import subprocess

MODE = os.getenv("MODE", "api").lower()

if MODE == "demo":
    print("Running in DEMO mode...")
    subprocess.run([sys.executable, "demo.py"])
else:
    print("Running in API mode...")
    subprocess.run([sys.executable, "orchestrator.py"])
