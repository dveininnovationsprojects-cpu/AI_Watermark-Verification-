from PIL import Image
import piexif
from io import BytesIO
import cv2 
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
def add_exif(img,date):
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(rgb_img)
    
    exif_dict = {
    "Exif": {
        piexif.ExifIFD.DateTimeOriginal: u"2026:02:10 12:00:00",
        piexif.ExifIFD.LensMake: u"{}".format(date),
    },
    }

    exif_bytes = piexif.dump(exif_dict)
    buffer=BytesIO()
    img.save(buffer, exif=exif_bytes,format='jpeg')
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    return img
