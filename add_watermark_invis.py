import cv2
from imwatermark import WatermarkEncoder, WatermarkDecoder
import numpy as np

def add_invis(img,data):
    img.seek(0)
    nparr = np.frombuffer(img.read(), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    data=data.encode('utf-8')
    secret_key=len(data)
    encoder = WatermarkEncoder()
    encoder.set_watermark('bytes', data)
    watermarked = encoder.encode(img, 'dwtDct')
    watermarked=cv2.cvtColor(watermarked,cv2.COLOR_BGR2RGB)
    return watermarked,secret_key

def search_invis(img,secret_key):
    secret_key=int(secret_key)
    
    decoder = WatermarkDecoder('bytes',secret_key*8)
    wm = decoder.decode(img, 'dwtDct')
    return wm

