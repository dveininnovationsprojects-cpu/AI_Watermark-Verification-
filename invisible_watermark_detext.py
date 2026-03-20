import cv2
import numpy as np
import matplotlib.pyplot as plt 
from scipy.fftpack import dct
def invis_test(img):
    score=0
    BLOCK = 8
    THRESHOLD = 0.1
    np.random.seed(42)
    if len(img.shape) == 2:
        gray = img
    elif img.shape[2] == 4:
        gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
    elif img.shape[2] == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gray = np.float32(gray)
    def block_dct(block):
        return dct(dct(block.T, norm='ortho').T, norm='ortho')

    def extract_dct_coeffs(image):
        h, w = image.shape
        coeffs = []
        for i in range(0, h - BLOCK, BLOCK):
            for j in range(0, w - BLOCK, BLOCK):
                block = image[i:i+BLOCK, j:j+BLOCK]
                dct_block = block_dct(block)
                coeffs.append(dct_block[3, 3])  # mid-frequency
        return np.array(coeffs)

    coeffs = extract_dct_coeffs(gray)
    watermark = np.random.choice([-1, 1], size=len(coeffs))
    correlation = np.corrcoef(coeffs, watermark)[0, 1]
    print("Correlation value:", correlation)

    if correlation > THRESHOLD:
        score+=1
    else:
        pass
    import pywt   
    img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    LL, (LH, HL, HH) = pywt.dwt2(img, 'haar')
    band = HL
    def block_dct(block):
        return dct(dct(block.T, norm='ortho').T, norm='ortho')
    coeffs = []
    for i in range(0, band.shape[0]-BLOCK, BLOCK):
        for j in range(0, band.shape[1]-BLOCK, BLOCK):
            block = band[i:i+BLOCK, j:j+BLOCK]
            dct_block = block_dct(block)
            coeffs.append(dct_block[3,3])
    coeffs = np.array(coeffs)
    hist, bins = np.histogram(coeffs, bins=50)
    print("Band shape:", band.shape)
    print("Number of DCT coeffs:", len(coeffs))
    # --- Variance ---
    var = np.var(coeffs)
    from scipy.stats import chisquare, entropy
    # --- Entropy ---
    hist_norm = hist / np.sum(hist)
    ent = entropy(hist_norm)

    # --- Chi-square test ---
    expected = np.ones_like(hist) * np.mean(hist)
    chi, p_value = chisquare(hist, expected)

    # --- Correlation with random watermark ---
    watermark = np.random.choice([-1,1], size=len(coeffs))
    corr = np.corrcoef(coeffs, watermark)[0,1]

    # --- Results ---
    print("Variance:", var)
    print("Entropy:", ent)
    print("Chi-square:", chi)
    print("p-value:", p_value)
    print("Correlation:", corr)

    # --- Decision Logic (heuristic thresholds) ---
    score2 = 0

    if var > 100: score2 += 1
    if ent > 3.5: score2 += 1
    if p_value < 0.05: score2 += 1
    if abs(corr) > 0.1: score2 += 1
    if score2 >= 2:
        score+=1
    
    #least significant bit
    
    img=np.uint8(img)
    lsb = img & 1
    counts = np.bincount(lsb.flatten(), minlength=2)
    print("counts:", counts)

    lsb_ratio = counts[0] / (counts[0] + counts[1])
    print("LSB ratio:", lsb_ratio)

    lsb_bias = abs(lsb_ratio - 0.5)
    print("LSB bias:", lsb_bias)
    print(lsb_bias)
    if lsb_bias<0.02 and lsb_bias>0:
        score+=1

    return  score
#print(invis_test(cv2.imread(r'd:\transformers for lmm\encrypt (1)\image.png')))