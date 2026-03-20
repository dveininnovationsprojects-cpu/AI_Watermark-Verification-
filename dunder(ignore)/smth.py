import cv2
import numpy as np
import os 
clean_images=[]
for file in os.listdir(r'D:\watermark_detect2\images'):
    f=os.path.join(r'D:\watermark_detect2\images',file)
    clean_images.append(f)
def dct_energy(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img = np.float32(img) / 255.0
    dct = cv2.dct(img)
    # Only use low-mid frequencies (e.g., top-left 32x32 for 512x512 image)
    h, w = dct.shape
    block = dct[:32, :32]
    # For all clean images
    
    return np.sum(block**2) / (block.shape[0] * block.shape[1])


energies = [dct_energy(path) for path in clean_images]
baseline = np.mean(energies)
std_dev = np.std(energies)
print(baseline)
print(std_dev)