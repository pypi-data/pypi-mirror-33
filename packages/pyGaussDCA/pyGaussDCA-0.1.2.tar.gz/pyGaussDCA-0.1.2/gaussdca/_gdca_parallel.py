import numpy as np


def _compute_weights(alignment, theta: float, n_cols: int, depth: int):
    _thresh = np.floor(theta * n_cols)
    weights = np.ones(depth, dtype=np.float64)

    if theta == 0:
        Meff = depth
        return Meff, weights

    #omp parallel for
    for i in range(depth - 1):
        this_vec = alignment[i, :]
        for j in range(i + 1, depth):
            _dist = np.sum(this_vec != alignment[j, :])

            if _dist < _thresh:
                weights[i] += 1.
                weights[j] += 1.

    weights[:] = 1. / weights
    Meff = weights.sum()
    return Meff, weights


# pythran export compute_weights( int8[:, :])
def compute_weights(alignment_T):
    n_cols = alignment_T.shape[1]
    depth = alignment_T.shape[0]

    theta = 0.3
    meff, weights = _compute_weights(alignment_T, theta, n_cols, depth)
    return meff, weights
