import numpy as np
def mse(image1 : np.array, image2: np.array):
    [n, m] = image1.shape
    dev_sum = 0
    for i in range(0, n):
        for j in range(0, m):
            dev = image1[i, j] - image2[i, j]
            dev_sum += dev.item() * dev.item()
    return dev_sum / (m * n)


def psnr(image1 : np.array, image2 : np.array):
    r = 255
    _mse = mse(image1, image2)
    if _mse != 0:
        return 10 * np.log10(r*r/_mse)
    return -1