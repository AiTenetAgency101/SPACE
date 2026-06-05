def momentum(history):
    if len(history) < 2:
        return 0.0
    return history[-1] - history[-2]
