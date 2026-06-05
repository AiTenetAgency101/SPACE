from engine_core.ehf_frequency import (
    BioMetrics,
    CircadianPhase,
    CircadianRhythmEngine,
    CognitiveState,
    EHFFrequencyEngine,
)


def test_circadian_phase_boundaries():
    circ = CircadianRhythmEngine()
    assert circ.get_circadian_phase(23.0) == CircadianPhase.DEEP_SLEEP
    assert circ.get_circadian_phase(3.0) == CircadianPhase.LIGHT_SLEEP
    assert circ.get_circadian_phase(6.5) == CircadianPhase.WAKE_UP
    assert circ.get_circadian_phase(8.0) == CircadianPhase.MORNING_PEAK
    assert circ.get_circadian_phase(10.0) == CircadianPhase.FOCUS_WINDOW
    assert circ.get_circadian_phase(13.5) == CircadianPhase.POST_LUNCH_DIP
    assert circ.get_circadian_phase(16.0) == CircadianPhase.AFTERNOON_PEAK


def test_analyze_biometrics_and_status_thresholds():
    engine = EHFFrequencyEngine()
    metrics = BioMetrics(
        heart_rate_variability=80,
        stress_score=20,
        sleep_quality=90,
        energy_level=95,
    )

    analysis = engine.analyze_biometrics(metrics)

    assert analysis["overall_performance"] == 86.25
    assert analysis["status"] == "OPTIMAL"
    assert engine._get_performance_status(59.9) == "BELOW_OPTIMAL"
    assert engine._get_performance_status(60.0) == "FAIR"
    assert engine._get_performance_status(70.0) == "GOOD"
    assert engine._get_performance_status(80.0) == "OPTIMAL"
    assert engine._get_performance_status(90.0) == "PEAK_PERFORMANCE"


def test_cognitive_state_and_frequency_mapping():
    engine = EHFFrequencyEngine()
    assert (
        engine.get_cognitive_state(CircadianPhase.FOCUS_WINDOW)
        == CognitiveState.DEEP_WORK
    )
    assert engine.get_optimal_frequency(CognitiveState.DEEP_WORK) == 6.0


def test_recommendations_cover_alert_paths(monkeypatch):
    engine = EHFFrequencyEngine()
    engine.current_metrics = BioMetrics(
        heart_rate=105,
        sleep_quality=60,
        stress_score=75,
        energy_level=40,
        glucose_level=150,
    )

    monkeypatch.setattr(
        engine.circadian,
        "get_circadian_phase",
        lambda current_hour=None: CircadianPhase.POST_LUNCH_DIP,
    )

    recs = engine.get_recommendations()

    joined = "\n".join(recs)
    assert "High HR" in joined
    assert "Poor sleep" in joined
    assert "High stress" in joined
    assert "Low energy" in joined
    assert "High glucose" in joined
    assert "Afternoon dip" in joined
    assert "Recovery phase" in joined


def test_status_payload_contains_expected_fields(monkeypatch):
    engine = EHFFrequencyEngine()
    monkeypatch.setattr(
        engine.circadian,
        "get_circadian_phase",
        lambda current_hour=None: CircadianPhase.MORNING_PEAK,
    )

    status = engine.get_ehf_status()

    assert status["circadian_phase"] == CircadianPhase.MORNING_PEAK.value
    assert status["cognitive_state"] == CognitiveState.PEAK_FOCUS.value
    assert status["optimal_frequency"].endswith("Hz")
    assert "biomarkers" in status
    assert "recommendations" in status
