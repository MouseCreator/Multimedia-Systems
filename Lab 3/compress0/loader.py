from PIL import Image
import numpy as np

def load_image(file_path : str):
    image = Image.open(file_path).convert('L')
    image_matrix = np.array(image)
    return image_matrix.astype(np.int16)

def to_image(array : np.array, file_path : str):
    array_clipped = np.clip(array, 0, 255).astype(np.uint8)
    image = Image.fromarray(array_clipped, mode='L')
    image.save(file_path)