import numpy as np
def scale_matrix(matrix):
    min_val = np.min(matrix)
    max_val = np.max(matrix)

    scaled_matrix = 255 * (matrix - min_val) / (max_val - min_val)
    scaled_matrix = np.round(scaled_matrix).astype(int)

    return scaled_matrix