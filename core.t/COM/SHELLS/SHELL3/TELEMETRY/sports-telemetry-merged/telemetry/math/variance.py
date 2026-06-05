def variance(history):
    if not history:
        return 0.0
    mean = sum(history) / len(history)
    return sum((x - mean) ** 2 for x in history) / len(history)
