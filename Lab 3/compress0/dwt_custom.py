import numpy as np

import utils
from psnr import psnr
from loader import load_image, to_image


def avg_val(i1, i2):
    return (i1 + i2) / 2
def avg_dif(i1, i2):
    return (i1 - i2) / 2
def dwt_1d(array : np.array):
    xd = array.copy()

    p = xd.copy()

    xd[0] = avg_val(p[0], p[1])
    xd[1] = avg_val(p[2], p[3])
    xd[2] = avg_val(p[4], p[5])
    xd[3] = avg_val(p[6], p[7])
    xd[4] = avg_dif(p[0], p[1])
    xd[5] = avg_dif(p[2], p[3])
    xd[6] = avg_dif(p[4], p[5])
    xd[7] = avg_dif(p[6], p[7])

    p = xd.copy()

    xd[0] = avg_val(p[0], p[1])
    xd[1] = avg_val(p[2], p[3])
    xd[2] = avg_dif(p[0], p[1])
    xd[3] = avg_dif(p[2], p[3])

    p = xd.copy()

    xd[0] = avg_val(p[0], p[1])
    xd[1] = avg_dif(p[0], p[1])

    return xd
def idwt_1d(array : np.array):

    output = np.zeros(8)

    output[0] = array[0] + array[1]
    output[1] = array[0] - array[1]

    p = output.copy()

    output[0] = p[0] + array[2]
    output[1] = p[0] - array[2]
    output[2] = p[1] + array[3]
    output[3] = p[1] - array[3]

    p = output.copy()

    output[0] = p[0] + array[4]
    output[1] = p[0] - array[4]
    output[2] = p[1] + array[5]
    output[3] = p[1] - array[5]
    output[4] = p[2] + array[6]
    output[5] = p[2] - array[6]
    output[6] = p[3] + array[7]
    output[7] = p[3] - array[7]

    return output


def dwt(block : np.array):
   for i in range(0, 8):
       block[i, :] = dwt_1d(block[i, :])
   for i in range(0, 8):
       block[:, i] = dwt_1d(block[:, i])
   return block


def inverse_dwt(block : np.array):
    for i in range(0, 8):
        block[:, i] = idwt_1d(block[:, i])
    for i in range(0, 8):
        block[i, :] = idwt_1d(block[i, :])
    return block

def compress_block(block : np.array):
    after_wavelet = dwt(block)
    quantized = after_wavelet
    return np.round(quantized)

def compress(input_image : np.array):
    input_image = input_image.astype(np.float32)
    n = input_image.shape[0] // 8
    for i in range(n):
        for j in range(n):
            block = input_image[i * 8:(i + 1) * 8, j * 8:(j + 1) * 8]
            new_block = compress_block(block)
            input_image[i * 8:(i + 1) * 8, j * 8:(j + 1) * 8] = new_block
    return input_image

def decompress_block(block : np.array):
    before_wavelet = inverse_dwt(block)
    return before_wavelet

def decompress(input_image : np.array):
    input_image = input_image.astype(np.float32)
    n = input_image.shape[0] // 8
    for i in range(n):
        for j in range(n):
            block = input_image[i * 8:(i + 1) * 8, j * 8:(j + 1) * 8]
            new_block = decompress_block(block)
            input_image[i * 8:(i + 1) * 8, j * 8:(j + 1) * 8] = new_block
    return input_image

print("Custom Wavelet transform")
WORK_DIR = "dwt_custom/"
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

