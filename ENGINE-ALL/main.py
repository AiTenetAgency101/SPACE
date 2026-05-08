"""
ENGINE2 ORCHESTRATOR - 7 ENGINES SIMPLE
"""

from runner import run_engine
from pathlib import Path

# 7 Engines
ENGINES = [
    ("ultimate", {"msg": "ping"}),
    ("tenet", {"msg": "ping"}),
    ("worker365", {"msg": "ping"}),
    ("tron", {"n": 3029}),
    ("zha", {"msg": "ping"}),
    ("xyo", {"msg": "sync"}),
]

def run_cycle():
    """Execute one ENGINE cycle."""
    print("\n[ENGINE2] Starting cycle...\n")
    
    try:
        # Run all engines
        for engine_name, payload in ENGINES:
            result = run_engine(engine_name, payload)
            print(f"✓ {engine_name.upper():12s}: {result}")

        # Mark healthy
        Path("/tmp/engine_cycle_health").write_text("healthy")
        print("\n[ENGINE2] Cycle complete\n")
        return True

    except Exception as e:
        print(f"\n[ERROR] {e}\n")
        Path("/tmp/engine_cycle_health").write_text("unhealthy")
        return False


if __name__ == "__main__":
    run_cycle()
