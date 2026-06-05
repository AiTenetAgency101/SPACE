import pytest

from engine_core.tron_rhythm import TRONRhythmEngine


@pytest.mark.asyncio
async def test_heartbeat_phase_drains_energy_by_device_count():
    engine = TRONRhythmEngine(node_id="node-a")
    engine.register_zha_device("d1")
    engine.register_zha_device("d2")
    start_energy = engine.energy_balance

    await engine.heartbeat_phase()

    assert engine.energy_balance == start_energy - 1.0


@pytest.mark.asyncio
async def test_consensus_phase_updates_efficiency_up_and_down():
    engine = TRONRhythmEngine(node_id="node-a")
    engine.register_node("node-b")
    engine.register_node("node-c")

    baseline = engine.consensus_efficiency
    await engine.consensus_phase()  # no quorum yet
    assert engine.consensus_efficiency < baseline

    key = f"cycle_{engine.current_cycle}"
    engine.consensus_votes[key] = {"node-a", "node-b"}
    before_success = engine.consensus_efficiency
    await engine.consensus_phase()
    assert engine.consensus_efficiency >= before_success


@pytest.mark.asyncio
async def test_execution_phase_adds_action_metadata():
    engine = TRONRhythmEngine(node_id="node-a")
    actions = [{"device": "light-1", "command": "sync"}]

    await engine.execution_phase(actions)

    assert "executed_at" in actions[0]
    assert actions[0]["cycle"] == engine.current_cycle


def test_register_unregister_and_status_snapshot():
    engine = TRONRhythmEngine(node_id="node-a")
    engine.register_node("node-b")
    engine.register_zha_device("dev-1")
    engine.unregister_zha_device("dev-1")

    status = engine.get_grid_status()
    assert status["node_id"] == "node-a"
    assert status["nodes"] == 2
    assert status["zha_devices"] == 0


@pytest.mark.asyncio
async def test_run_tron_cycle_increments_cycle_and_nonce():
    engine = TRONRhythmEngine(node_id="node-a", grid_frequency=1.0)
    engine.phase_allocations = {phase: 0 for phase in engine.phase_allocations}

    await engine.run_tron_cycle(
        zha_state={"ok": True}, actions=[{"device": "x", "command": "c"}]
    )

    assert engine.current_cycle == 1
    assert engine.grid_nonce == 1
    assert len(engine.state_ledger) == 1
