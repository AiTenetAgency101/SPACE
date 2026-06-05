import pytest

from engine_core.automation_rules import (
    AutomationAction,
    AutomationRule,
    AutomationRulesEngine,
    setup_example_automations,
)


class DummyZHA:
    def __init__(self):
        self.calls = []

    async def set_device_state(self, device_id, state, sync_cycle=None):
        self.calls.append((device_id, state, sync_cycle))
        return True


def test_rule_condition_operators_cover_core_paths():
    rule = AutomationRule("r1", "Rule 1")
    state = {"temp": 22, "label": "kitchen_light_on"}

    assert rule._evaluate_condition(
        {"entity": "temp", "condition": "equals", "value": 22}, state
    )
    assert rule._evaluate_condition(
        {"entity": "temp", "condition": "not_equals", "value": 21}, state
    )
    assert rule._evaluate_condition(
        {"entity": "temp", "condition": "gt", "value": 20}, state
    )
    assert rule._evaluate_condition(
        {"entity": "temp", "condition": "lt", "value": 30}, state
    )
    assert rule._evaluate_condition(
        {"entity": "temp", "condition": "gte", "value": 22}, state
    )
    assert rule._evaluate_condition(
        {"entity": "temp", "condition": "lte", "value": 22}, state
    )
    assert rule._evaluate_condition(
        {"entity": "temp", "condition": "in_range", "value": [20, 25]}, state
    )
    assert rule._evaluate_condition(
        {"entity": "label", "condition": "contains", "value": "light"}, state
    )


def test_rule_can_execute_respects_enabled_and_cooldown(monkeypatch):
    rule = AutomationRule("r2", "Rule 2")
    rule.cooldown = 10
    rule.last_trigger_time = 100.0

    class FakeNow:
        @staticmethod
        def now():
            class TS:
                @staticmethod
                def timestamp():
                    return 105.0

            return TS()

    monkeypatch.setattr("engine_core.automation_rules.datetime", FakeNow)
    assert not rule.can_execute()

    rule.enabled = False
    assert not rule.can_execute()


@pytest.mark.asyncio
async def test_engine_evaluate_and_execute_rules_updates_metrics():
    zha = DummyZHA()
    engine = AutomationRulesEngine(zha_integration=zha)

    rule = engine.create_rule("motion", "Motion Lights")
    motion_condition = {
        "entity": "motion",
        "condition": "equals",
        "value": "on",
    }
    motion_action = AutomationAction(
        device_id="light_1", service="turn_on", data={"state": "on"}
    )
    rule.add_condition(motion_condition)
    rule.add_action(motion_action)

    matching = await engine.evaluate_triggers({"motion": "on"})
    assert matching == ["motion"]

    result = await engine.execute_rules(matching, sync_cycle=7)
    assert result["rules_executed"] == 1
    assert result["actions"] == 1
    assert engine.total_triggers == 1
    assert engine.total_automations == 1
    assert engine.total_actions == 1
    assert len(engine.rule_history) == 1
    assert zha.calls == [("light_1", "on", 7)]


def test_should_execute_false_when_condition_fails():
    rule = AutomationRule("r3", "Rule 3")
    lock_condition = {
        "entity": "lock",
        "condition": "equals",
        "value": "locked",
    }
    rule.add_condition(lock_condition)
    assert not rule.should_execute({"lock": "unlocked"})


@pytest.mark.asyncio
async def test_setup_example_automations_builds_expected_rules():
    engine = AutomationRulesEngine()
    await setup_example_automations(engine, None)

    assert len(engine.rules) == 4
    assert "morning_routine" in engine.rules
    assert engine.rules["motion_lights"].cooldown == 30
    assert engine.rules["temperature_control"].cooldown == 300
