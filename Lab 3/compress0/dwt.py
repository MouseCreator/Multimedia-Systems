import numpy as np

import utils
from psnr import psnr
from loader import load_image, to_image


def avg_val(i1, i2):
    return (i1 + i2) / 2


def avg_dif(i1, i2):
    return (i1 - i2) / 2


def dwt_1d(array: np.array):
    n = len(array)
    half_n = n // 2
    output = np.zeros(n)

    for i in range(half_n):
        output[i] = avg_val(array[2 * i], array[2 * i + 1])  # Approximation
        output[half_n + i] = avg_dif(array[2 * i], array[2 * i + 1])  # Detail

    return output


def idwt_1d(array: np.array):
    n = len(array)
    half_n = n // 2
    output = np.zeros(n)

    for i in range(half_n):
        output[2 * i] = array[i] + array[half_n + i]
        output[2 * i + 1] = array[i] - array[half_n + i]

    return output

LEVELS = 2
def dwt(block : np.array):
    (n, m) = block.shape
    for level in range(0, LEVELS):
       for i in range(0, n):
           block[i, :] = dwt_1d(block[i, :])
       for i in range(0, m):
           block[:, i] = dwt_1d(block[:, i])
    return block


def inverse_dwt(block : np.array):
    (n, m) = block.shape
    for level in range(0, LEVELS):
        for i in range(0, m):
            block[:, i] = idwt_1d(block[:, i])
        for i in range(0, n):
            block[i, :] = idwt_1d(block[i, :])
    return block

def compress_block(block : np.array):
    after_wavelet = dwt(block)
    quantized = after_wavelet
    return np.round(quantized)

def compress(input_image : np.array):
    input_image = input_image.astype(np.float32)
    input_image = compress_block(input_image)
    return input_image

def decompress_block(block : np.array):
    before_wavelet = inverse_dwt(block)
    return before_wavelet

def decompress(input_image : np.array):
    input_image = input_image.astype(np.float32)
    input_image = decompress_block(input_image)
    return input_image

print("Wavelet transform")
WORK_DIR = "dwt/"
FILENAME = "lena.png"
INPUT_DIR = "input/"
split = FILENAME.split(".", 2)
short_name = split[0]
extension = "." + split[1]
initial = load_image(INPUT_DIR + FILENAME)

compressed = compress(initial)
compressed_portrait = utils.scale_matrix(compressed)
to_image(compressed_portrait, WORK_DIR + short_name + "_c" + extension)
decompressed = decompress(compressed)
to_image(decompressed, WORK_DIR + short_name + "_d" + extension)

_psnr = psnr(initial, decompressed)

print(f"PSNR: {_psnr}")

