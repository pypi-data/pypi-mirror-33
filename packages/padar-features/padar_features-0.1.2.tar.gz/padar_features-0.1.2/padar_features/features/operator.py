import numpy as np

def apply_over_subwins(X, func, subwins, **kwargs):
    win_length = int(np.floor(X.shape[0] / subwins))
    start_index = np.ceil((X.shape[0] % subwins) / 2)
    result = []
    for i in range(0, subwins):
        indices = int(start_index) + np.array(range(
            i * win_length,
            (i + 1) * win_length
        ))
        subwin_X = X[indices, :]
        result.append(func(subwin_X, **kwargs))
    return result
