from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional
import docker
from docker.errors import DockerException


# -------------------------
# 4-LAYER DOCKER WITNESS
# -------------------------
@dataclass
class Docker4:
    act: bool        # D_ACT   - container exists and is known
    state: bool      # D_STATE - container is in a valid state
    ehf: bool        # D_EHF   - resource band OK (CPU/memory within threshold)
    time_ok: bool    # D_TIME  - container time coherence


# -------------------------
# DOCKER LATTICE MODEL
# -------------------------
@dataclass
class DockerLattice:
    name: str
    container_id: str
    image: str
    status: str
    created_at: datetime
    docker4: Docker4
    health_status: Optional[str] = None
    memory_mb: Optional[float] = None
    cpu_percent: Optional[float] = None


# -------------------------
# REAL DOCKER SNAPSHOT
# (wired to Docker SDK)
# -------------------------
def snapshot_docker_lattices(
    memory_threshold_mb: float = 1024.0,
    cpu_threshold_percent: float = 80.0
) -> List[DockerLattice]:
    """
    Inspect real running/stopped containers via Docker SDK.
    
    Args:
        memory_threshold_mb: Warn if container exceeds this (ehf = False if over)
        cpu_threshold_percent: Warn if CPU usage exceeds this (ehf = False if over)
    
    Returns:
        List of DockerLattice objects with real container state
    """
    try:
        client = docker.from_env()
    except DockerException as e:
        print(f"[ERROR] Cannot connect to Docker daemon: {e}")
        return []

    lattices: List[DockerLattice] = []
    now = datetime.now(timezone.utc)

    try:
        containers = client.containers.list(all=True)
    except DockerException as e:
        print(f"[ERROR] Cannot list containers: {e}")
        return []

    for container in containers:
        try:
            # Basic container info
            name = container.name
            container_id = container.id[:12]  # Short ID
            image = container.image.tags[0] if container.image.tags else "unknown"
            status = container.status
            created_at = datetime.fromisoformat(
                container.attrs["Created"].replace("Z", "+00:00")
            )

            # Health status (if healthcheck defined)
            health_status = container.attrs.get("State", {}).get("Health", {}).get("Status")

            # Resource stats (only if running)
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
                    pass  # Stats not available for all drivers

            # 4-LAYER WITNESS
            act = True  # Container exists
            state = status in ["running", "exited", "created", "paused"]
            ehf = (
                (memory_mb is None or memory_mb <= memory_threshold_mb)
                and (cpu_percent is None or cpu_percent <= cpu_threshold_percent)
            )
            time_ok = True  # TODO: Compare container clock vs. host

            docker4 = Docker4(
                act=act,
                state=state,
                ehf=ehf,
                time_ok=time_ok,
            )

            lattice = DockerLattice(
                name=name,
                container_id=container_id,
                image=image,
                status=status,
                created_at=created_at,
                docker4=docker4,
                health_status=health_status,
                memory_mb=memory_mb,
                cpu_percent=cpu_percent,
            )
            lattices.append(lattice)

        except Exception as e:
            print(f"[WARN] Failed to inspect container: {e}")
            continue

    return lattices


# -------------------------
# DOCKER LATTICE FILTERS
# -------------------------
def filter_active_lattices(lattices: List[DockerLattice]) -> List[DockerLattice]:
    """Return only containers that are logically 'active'."""
    return [
        d for d in lattices
        if d.status.lower() == "running"
        and d.docker4.act
        and d.docker4.state
    ]


def filter_unhealthy_lattices(lattices: List[DockerLattice]) -> List[DockerLattice]:
    """Return containers with any D4 witness failing."""
    return [
        d for d in lattices
        if not (d.docker4.act and d.docker4.state and d.docker4.ehf and d.docker4.time_ok)
    ]


def find_lattice_by_name(lattices: List[DockerLattice], name: str) -> Optional[DockerLattice]:
    """Find a lattice by container name."""
    for d in lattices:
        if d.name == name:
            return d
    return None


# -------------------------
# REPORTING
# -------------------------
def report_lattices(lattices: List[DockerLattice], title: str = "DOCKER LATTICES") -> None:
    """Pretty-print lattice status."""
    print(f"\n{'='*70}")
    print(f"{title} ({len(lattices)} total)")
    print(f"{'='*70}")
    for d in lattices:
        witness = "✓" if all([d.docker4.act, d.docker4.state, d.docker4.ehf, d.docker4.time_ok]) else "✗"
        mem_str = f" | MEM: {d.memory_mb:.1f}MB" if d.memory_mb else ""
        cpu_str = f" | CPU: {d.cpu_percent:.1f}%" if d.cpu_percent else ""
        health_str = f" | HEALTH: {d.health_status}" if d.health_status else ""
        print(
            f"{witness} {d.name:20s} | {d.status:10s} | {d.image:30s}"
            f"{mem_str}{cpu_str}{health_str}"
        )
    print()


# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    print("[*] Inspecting Docker lattices...")

    all_lattices = snapshot_docker_lattices(
        memory_threshold_mb=512.0,
        cpu_threshold_percent=75.0,
    )

    if not all_lattices:
        print("[!] No containers found or Docker daemon unreachable.")
    else:
        report_lattices(all_lattices, "ALL DOCKER LATTICES")

        active = filter_active_lattices(all_lattices)
        report_lattices(active, "ACTIVE DOCKER LATTICES")

        unhealthy = filter_unhealthy_lattices(all_lattices)
        if unhealthy:
            report_lattices(unhealthy, "UNHEALTHY LATTICES (D4 witness failure)")

        # Example: lookup a specific container
        if all_lattices:
            first = all_lattices[0]
            print(f"\nDETAIL: {first.name}")
            print(f"  ID:        {first.container_id}")
            print(f"  Status:    {first.status}")
            print(f"  Created:   {first.created_at}")
            print(f"  D_ACT:     {first.docker4.act}")
            print(f"  D_STATE:   {first.docker4.state}")
            print(f"  D_EHF:     {first.docker4.ehf}")
            print(f"  D_TIME:    {first.docker4.time_ok}")
