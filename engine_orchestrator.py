"""
ENGINE2 CYCLE ORCHESTRATOR
Runs Einstein + Newton engines in clean cycles with state verification.
"""

from cycle_monitor import CycleMonitor
from datetime import datetime
import time


class EngineOrchestrator:
    """Orchestrate ENGINE cycles with cycle monitoring."""

    def __init__(self):
        self.monitor = CycleMonitor()
        self.cycle_count = 0

    def run_einstein_cycle(self):
        """Einstein: frame logic, relativity, perspective shifts."""
        print("[ENGINE] Running Einstein cycle...")
        # TODO: Wire to your actual Einstein engine logic
        time.sleep(0.5)  # Simulate work
        print("[ENGINE] Einstein cycle complete")

    def run_newton_cycle(self):
        """Newton: force logic, constraints, push/pull invariants."""
        print("[ENGINE] Running Newton cycle...")
        # TODO: Wire to your actual Newton engine logic
        time.sleep(0.5)  # Simulate work
        print("[ENGINE] Newton cycle complete")

    def execute_cycle(self):
        """Execute one full cycle: Einstein → Newton → Verify."""
        self.cycle_count += 1
        cycle_id = f"cycle-{self.cycle_count:06d}"
        timestamp = datetime.now().isoformat()

        print(f"\n{'='*70}")
        print(f"[CYCLE START] {cycle_id} @ {timestamp}")
        print(f"{'='*70}")

        # Run engines
        self.run_einstein_cycle()
        self.run_newton_cycle()

        # Verify cycle cleanliness
        verification = self.monitor.run_cycle_check(cycle_id)

        # Report
        if verification["is_clean"]:
            print(f"[✓ CYCLE CLEAN] All 4-layer witnesses verified")
        else:
            print(f"[✗ CYCLE DIRTY] Witness failures detected")
            for failure in verification["failures"]:
                print(f"    {failure}")

        print(f"{'='*70}\n")

        return verification

    def run_continuous(self, interval_seconds: float = 30.0):
        """Run cycles continuously."""
        print(f"[*] Starting continuous cycles (interval: {interval_seconds}s)")
        try:
            while True:
                self.execute_cycle()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n[*] Stopping orchestrator")

    def tail_ledger(self, lines: int = 10):
        """Display recent cycle history."""
        self.monitor.tail_ledger(lines)


if __name__ == "__main__":
    orchestrator = EngineOrchestrator()

    # Run a few cycles
    for _ in range(3):
        orchestrator.execute_cycle()

    # Show ledger
    print("\n[*] Recent cycle history:")
    orchestrator.tail_ledger(5)

    # Uncomment for continuous cycles:
    # orchestrator.run_continuous(interval_seconds=60.0)
