import math
def entropy(probs):
    eps = 1e-12
    return -sum(p * math.log(p + eps) for p in probs if p > 0)
