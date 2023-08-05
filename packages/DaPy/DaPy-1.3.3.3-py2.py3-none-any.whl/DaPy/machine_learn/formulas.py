def sigmoid(x, beta, diff=False):
    if diff:
        return x * ( -x + 1)
    return 1.0 / (exp(-x * beta) + 1)

def softmax():
    return None
