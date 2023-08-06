
def nominal_count(x):
    import numpy as np
    labels, counts = np.unique(x, return_counts=True)
    idx = np.flipud(np.argsort(counts))
    return np.c_[counts[idx], labels[idx]]

def nominal_mode(x):
    res = nominal_count(x)
    return res[0,1]
