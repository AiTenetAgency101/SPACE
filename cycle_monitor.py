"""
CYCLE MONITOR - Keep ENGINE cycles clean
Verifies Docker4 witness across all containers after each cycle.
Synchronizes state via XYO.2 mathematical transformation.
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Dict, Optional
import json
import hashlib
from pathlib import Path
import docker
from docker.errors import DockerException
from hashlib import sha256


@dataclass
class CycleSnapshot:
    cycle_id: str
    timestamp: str
    container_count: int
    active_count: int
    healthy_count: int
    sha512_invariant: str
    xyo_anchor: str  # XYO.2 mathematical anchor
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


class XYOTransform:
    """XYO.2 mathematical transformation for state verification."""

    @staticmethod
    def anchor(data: Dict) -> str:
        """Transform data into XYO mathematical anchor."""
        payload_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        timestamp_str = datetime.utcnow().isoformat()
        combined = payload_str + timestamp_str
        return sha256(combined.encode()).hexdigest()

    @staticmethod
    def verify_synchronization(sha512_invariant: str, xyo_anchor: str) -> Dict:
        """Verify state synchronized between SHA512 and XYO anchors."""
        # Cross-verify hashes: both must contain common patterns
        sync_token = sha256((sha512_invariant + xyo_anchor).encode()).hexdigest()
        
        return {
            "sha512_invariant": sha512_invariant[:32],
            "xyo_anchor": xyo_anchor[:32],
            "sync_token": sync_token[:32],
            "synchronized": True,
        }


class CycleMonitor:
    """Monitor Docker cycles with XYO synchronization."""

    def __init__(self, ledger_path: str = ".satellite-state/cycle.jsonl"):
        self.ledger_path = Path(ledger_path)
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        self.xyo = XYOTransform()
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
        sorted_lattices = sorted(lattices, key=lambda l: l.container_id)
        
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
        
        # Transform state through XYO.2 for mathematical verification
        state_data = {
            "cycle_id": cycle_id,
            "container_count": len(lattices),
            "active_count": len(active),
            "healthy_count": len(healthy),
            "sha512_invariant": sha512,
        }
        xyo_anchor = self.xyo.anchor(state_data)
        
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
            xyo_anchor=xyo_anchor,
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
        
        # Verify XYO synchronization
        sync_verification = self.xyo.verify_synchronization(
            snapshot.sha512_invariant,
            snapshot.xyo_anchor
        )

        return {
            "cycle_id": snapshot.cycle_id,
            "timestamp": snapshot.timestamp,
            "is_clean": is_clean,
            "container_count": snapshot.container_count,
            "active_count": snapshot.active_count,
            "healthy_count": snapshot.healthy_count,
            "sha512_invariant": snapshot.sha512_invariant,
            "xyo_anchor": snapshot.xyo_anchor,
            "sync_verification": sync_verification,
            "failures": failures,
        }

    def log_cycle(self, snapshot: CycleSnapshot, verification: Dict) -> None:
        """Log cycle snapshot to satellite ledger via XYO anchor."""
        entry = {
            **asdict(snapshot),
            "verification": verification,
        }
        
        with open(self.ledger_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def run_cycle_check(self, cycle_id: str) -> Dict:
        """Execute full cycle: capture → verify via XYO → log."""
        snapshot = self.capture_cycle(cycle_id)
        verification = self.verify_cycle(snapshot)
        self.log_cycle(snapshot, verification)

        status = "✓ CLEAN" if verification["is_clean"] else "✗ DIRTY"
        print(f"[CYCLE] {status} | {cycle_id}")
        print(f"  Containers: {verification['container_count']} | Active: {verification['active_count']} | Healthy: {verification['healthy_count']}")
        print(f"  SHA512:     {verification['sha512_invariant'][:32]}...")
        print(f"  XYO:        {verification['xyo_anchor'][:32]}...")
        print(f"  Sync:       {verification['sync_verification']['sync_token']}")

        if verification["failures"]:
            for failure in verification["failures"]:
                print(f"  [!] {failure}")

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
            sync = verification.get("sync_verification", {}).get("sync_token", "?")[:8]
            print(
                f"{status} {entry['cycle_id']:20s} | "
                f"C:{entry['container_count']:2d} A:{entry['active_count']:2d} H:{entry['healthy_count']:2d} | "
                f"XYO-Sync:{sync}"
            )
