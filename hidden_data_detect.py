from PIL import Image
from PIL.ExifTags import TAGS
import zipfile
from io import BytesIO
import cv2


def hid_data(img):
    img2=Image.fromarray(img)
    exif = img2.getexif()
    dict={}
    if exif is not None:
        for tag, value in exif.items():
            dict[TAGS.get(tag)]=value
    op=None
    success, buffer = cv2.imencode(".jpg", img)   # or ".png"
    file_obj = BytesIO(buffer.tobytes())

    # Now file_obj is a file-like object
    file_obj.seek(0)
    data = file_obj.read()
    print(exif,data[0])
    if zipfile.is_zipfile(BytesIO(data)) :
        op='Possible hidden zip file'
    return dict,op
#good