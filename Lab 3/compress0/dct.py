import numpy as np

import utils
from psnr import psnr
from loader import load_image, to_image


quantization_table = np.array([
    [16, 11, 10, 16, 24, 40, 51, 61],
    [12, 12, 14, 19, 26, 58, 60, 55],
    [14, 13, 16, 24, 40, 57, 69, 56],
    [14, 17, 22, 29, 51, 87, 80, 62],
    [18, 22, 37, 56, 68, 109, 103, 77],
    [24, 35, 55, 64, 81, 104, 113, 92],
    [49, 64, 78, 87, 103, 121, 120, 101],
    [72, 92, 95, 98, 112, 100, 103, 99]
])


def dct_matrix() -> np.array:
    t = np.zeros((8, 8))
    for p in range(0, 8):
        for q in range(0, 8):
            if p == 0:
                t[p][q] = 1 / np.sqrt(8)
            else:
                t[p][q] = 0.5 * np.cos(np.pi * (2 * q + 1) * p / 16)
    return t

t_matrix = dct_matrix()

def dct(shifted_image : np.array):
    return t_matrix @ shifted_image @ t_matrix.T
def idct(shifted_image : np.array):
    return t_matrix.T @ shifted_image @ t_matrix

def compress_block(block : np.array):
    shifted = block - 128
    after_dct = dct(shifted)
    quantized = np.round(after_dct / quantization_table)
    return np.round(quantized)
def compress(input_image : np.array):
    input_image = input_image.copy()
    n = input_image.shape[0] // 8
    for i in range(n):
        for j in range(n):
            block = input_image[i * 8:(i + 1) * 8, j * 8:(j + 1) * 8]
            new_block = compress_block(block)
            input_image[i * 8:(i + 1) * 8, j * 8:(j + 1) * 8] = new_block
    return input_image

def decompress_block(block : np.array):
    dequantized = block.astype(np.int16) * quantization_table
    before_dct = idct(dequantized)
    return np.clip(before_dct + 128, 0, 255)

def decompress(input_image : np.array):
    input_image = input_image.copy()
    n = input_image.shape[0] // 8
    for i in range(n):
        for j in range(n):
            block = input_image[i * 8:(i + 1) * 8, j * 8:(j + 1) * 8]
            new_block = decompress_block(block)
            input_image[i * 8:(i + 1) * 8, j * 8:(j + 1) * 8] = new_block
    return input_image
print("DCT transform")
WORK_DIR = "dct/"
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

