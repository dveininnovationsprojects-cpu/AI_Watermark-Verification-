import cv2
import numpy as np
#only if a tempate for the watermark is available
# Load the main image and template (watermark sample)
def template_det(img,temp):
    img.seek(0) 
    temp.seek(0)
    nparr = np.frombuffer(img.read(), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    nparr2=np.frombuffer(temp.read(),np.uint8)
    template = cv2.imdecode(nparr2,cv2.IMREAD_COLOR)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    h_img, w_img = img_gray.shape
    h_tmp, w_tmp = template_gray.shape

    if h_tmp > h_img or w_tmp > w_img:
        scale = min(w_img / w_tmp, h_img / h_tmp)
        template_gray = cv2.resize(template_gray, None, fx=scale, fy=scale)
    # Template matching
    res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)

    if len(loc[0]) > 0:
        return True
    else:
        return  False
