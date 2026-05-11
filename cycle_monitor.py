"""
CYCLE MONITOR - Keep ENGINE cycles clean
Verifies Docker4 witness across all containers after each cycle.
Maintains state synchronization and detects cycle failures.
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Dict, Optional
import json
import hashlib
from pathlib import Path
import docker
from docker.errors import DockerException


@dataclass
class CycleSnapshot:
    cycle_id: str
    timestamp: str
    container_count: int
    active_count: int
    healthy_count: int
    sha512_invariant: str
    lattices_json: str  # Serialized lattice state


@dataclass
class Docker4:
    act: bool
    state: bool
    ehf: bool
    time_ok: bool


@dataclass
class DockerLattice:
    name: str
    container_id: str
    image: str
    status: str
    created_at: str
    docker4: Dict
    health_status: Optional[str] = None
    memory_mb: Optional[float] = None
    cpu_percent: Optional[float] = None


class CycleMonitor:
    """Monitor Docker cycles and maintain state cleanliness."""

    def __init__(self, ledger_path: str = ".satellite-state/cycle.jsonl"):
        self.ledger_path = Path(ledger_path)
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.client = docker.from_env()
        except DockerException as e:
            print(f"[ERROR] Docker not available: {e}")
            self.client = None

    def snapshot_lattices(
        self,
        memory_threshold_mb: float = 512.0,
        cpu_threshold_percent: float = 75.0,
    ) -> List[DockerLattice]:
        """Capture current Docker state as lattices."""
        if not self.client:
            return []

        lattices: List[DockerLattice] = []
        try:
            containers = self.client.containers.list(all=True)
        except DockerException:
            return []

        for container in containers:
            try:
                name = container.name
                container_id = container.id[:12]
                image = container.image.tags[0] if container.image.tags else "unknown"
                status = container.status
                created_at = container.attrs["Created"].replace("Z", "+00:00")
                health_status = container.attrs.get("State", {}).get("Health", {}).get("Status")

                memory_mb = None
                cpu_percent = None
                if status == "running":
                    try:
                        stats = container.stats(stream=False)
                        memory_mb = stats["memory_stats"]["usage"] / (1024 * 1024)
                        cpu_delta = (
                            stats["cpu_stats"]["cpu_usage"]["total_usage"]
                            - stats["precpu_stats"]["cpu_usage"]["total_usage"]
                        )
                        system_delta = (
                            stats["cpu_stats"]["system_cpu_usage"]
                            - stats["precpu_stats"]["system_cpu_usage"]
                        )
                        cpu_cores = len(stats["cpu_stats"]["cpu_usage"].get("percpu_usage", []))
                        if system_delta > 0:
                            cpu_percent = (cpu_delta / system_delta) * 100.0 * cpu_cores
                    except Exception:
                        pass

                # 4-LAYER WITNESS
                act = True
                state = status in ["running", "exited", "created", "paused"]
                ehf = (
                    (memory_mb is None or memory_mb <= memory_threshold_mb)
                    and (cpu_percent is None or cpu_percent <= cpu_threshold_percent)
                )
                time_ok = True

                docker4_dict = {
                    "act": act,
                    "state": state,
                    "ehf": ehf,
                    "time_ok": time_ok,
                }

                lattice = DockerLattice(
                    name=name,
                    container_id=container_id,
                    image=image,
                    status=status,
                    created_at=created_at,
                    docker4=docker4_dict,
                    health_status=health_status,
                    memory_mb=memory_mb,
                    cpu_percent=cpu_percent,
                )
                lattices.append(lattice)

            except Exception:
                continue

        return lattices

    def compute_sha512_invariant(self, lattices: List[DockerLattice]) -> str:
        """Compute SHA512 hash of lattice state for verification."""
        # Sort by container ID for deterministic ordering
        sorted_lattices = sorted(lattices, key=lambda l: l.container_id)
        
        # Create canonical JSON representation
        data = []
        for lattice in sorted_lattices:
            data.append({
                "name": lattice.name,
                "container_id": lattice.container_id,
                "status": lattice.status,
                "docker4": lattice.docker4,
            })
        
        canonical = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha512(canonical.encode()).hexdigest()

    def capture_cycle(self, cycle_id: str) -> CycleSnapshot:
        """Capture a cycle snapshot after engines complete."""
        lattices = self.snapshot_lattices()
        active = [l for l in lattices if l.status == "running" and l.docker4["act"] and l.docker4["state"]]
        healthy = [
            l for l in lattices
            if all([l.docker4["act"], l.docker4["state"], l.docker4["ehf"], l.docker4["time_ok"]])
        ]

        sha512 = self.compute_sha512_invariant(lattices)
        
        # Serialize lattices to JSON
        lattices_data = []
        for l in lattices:
            lattices_data.append({
                "name": l.name,
                "container_id": l.container_id,
                "image": l.image,
                "status": l.status,
                "docker4": l.docker4,
                "memory_mb": l.memory_mb,
                "cpu_percent": l.cpu_percent,
                "health_status": l.health_status,
            })

        snapshot = CycleSnapshot(
            cycle_id=cycle_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            container_count=len(lattices),
            active_count=len(active),
            healthy_count=len(healthy),
            sha512_invariant=sha512,
            lattices_json=json.dumps(lattices_data),
        )

        return snapshot

    def verify_cycle(self, snapshot: CycleSnapshot) -> Dict:
        """Verify cycle state — all witnesses must pass."""
        lattices_data = json.loads(snapshot.lattices_json)
        
        failures = []
        for lattice in lattices_data:
            d4 = lattice["docker4"]
            if not all([d4["act"], d4["state"], d4["ehf"], d4["time_ok"]]):
                failures.append(f"{lattice['name']}: D4 witness failed")

        is_clean = len(failures) == 0 and snapshot.active_count > 0

        return {
            "cycle_id": snapshot.cycle_id,
            "timestamp": snapshot.timestamp,
            "is_clean": is_clean,
            "container_count": snapshot.container_count,
            "active_count": snapshot.active_count,
            "healthy_count": snapshot.healthy_count,
            "sha512_invariant": snapshot.sha512_invariant,
            "failures": failures,
        }

    def log_cycle(self, snapshot: CycleSnapshot, verification: Dict) -> None:
        """Log cycle snapshot to satellite ledger."""
        entry = {
            **asdict(snapshot),
            "verification": verification,
        }
        
        with open(self.ledger_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def run_cycle_check(self, cycle_id: str) -> Dict:
        """Execute full cycle: capture → verify → log."""
        print(f"\n[*] Running cycle check: {cycle_id}")
        
        snapshot = self.capture_cycle(cycle_id)
        verification = self.verify_cycle(snapshot)
        self.log_cycle(snapshot, verification)

        # Report
        status = "✓ CLEAN" if verification["is_clean"] else "✗ DIRTY"
        print(f"{status} | Cycle: {cycle_id}")
        print(f"  Containers: {verification['container_count']} | Active: {verification['active_count']} | Healthy: {verification['healthy_count']}")
        print(f"  SHA512: {verification['sha512_invariant'][:32]}...")

        if verification["failures"]:
            print(f"  [!] Failures detected:")
            for failure in verification["failures"]:
                print(f"      - {failure}")

        return verification

    def tail_ledger(self, lines: int = 10) -> None:
        """Display last N cycle entries from ledger."""
        if not self.ledger_path.exists():
            print("[!] Ledger not found")
            return

        with open(self.ledger_path, "r") as f:
            all_lines = f.readlines()
            recent = all_lines[-lines:] if len(all_lines) > lines else all_lines

        print(f"\n[Ledger: {self.ledger_path}] (last {len(recent)} entries)")
        for line in recent:
            entry = json.loads(line)
            verification = entry.get("verification", {})
            status = "✓" if verification.get("is_clean") else "✗"
            print(
                f"{status} {entry['cycle_id']:20s} | "
                f"Containers: {entry['container_count']:3d} | "
                f"Active: {entry['active_count']:3d} | "
                f"Healthy: {entry['healthy_count']:3d}"
            )

    def compare_snapshots(self, cycle_id_1: str, cycle_id_2: str) -> Dict:
        """Compare SHA512 invariants between two cycles."""
        entries = []
        with open(self.ledger_path, "r") as f:
            for line in f:
                entry = json.loads(line)
                if entry["cycle_id"] in [cycle_id_1, cycle_id_2]:
                    entries.append(entry)

        if len(entries) != 2:
            return {"error": "Cycles not found"}

        e1, e2 = entries[0], entries[1]
        match = e1["sha512_invariant"] == e2["sha512_invariant"]

        return {
            "cycle_1": e1["cycle_id"],
            "cycle_2": e2["cycle_id"],
            "sha512_match": match,
            "sha512_1": e1["sha512_invariant"][:32],
            "sha512_2": e2["sha512_invariant"][:32],
        }


# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    monitor = CycleMonitor()

    # Run a cycle check
    verification = monitor.run_cycle_check("cycle-001")

    # Display ledger
    monitor.tail_ledger(5)

    # Compare cycles (if multiple exist)
    print("\n[*] Checking ledger for comparisons...")
    with open(monitor.ledger_path, "r") as f:
        lines = f.readlines()
        if len(lines) >= 2:
            e1 = json.loads(lines[-2])
            e2 = json.loads(lines[-1])
            comparison = monitor.compare_snapshots(e1["cycle_id"], e2["cycle_id"])
            print(f"Comparison: {comparison}")
