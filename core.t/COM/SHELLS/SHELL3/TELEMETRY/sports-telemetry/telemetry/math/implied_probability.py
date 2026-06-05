def implied_probability(decimal_odds: float) -> float:
    return 1.0 / decimal_odds if decimal_odds > 0 else 0.0
