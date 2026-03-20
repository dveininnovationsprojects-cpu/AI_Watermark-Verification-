import cv2
import numpy as np
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

# read image
def check_vis(img):
    text1=pytesseract.image_to_string(img)
    img=cv2.resize(img,None,fx=2.0,fy=2.0)
    draw = img.copy()

    # convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # morphological gradient (highlights text strokes)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    gradient = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)

    # threshold
    _, bw = cv2.threshold(
        gradient,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # connect horizontally aligned text
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30,5))
    connected = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)

    # find contours
    contours, _ = cv2.findContours(
        connected,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )
    dic={}
    m=0
    for c in contours:

        x, y, w, h = cv2.boundingRect(c)

        aspect_ratio = w / float(h)

        # filter text-like boxes
        if w > 80 and h > 15 and aspect_ratio > 2:

            roi = img[y:y+h, x:x+w]

            text = pytesseract.image_to_string(
                roi,
                config="--oem 3 --psm 7"
            )

            if text.strip():
                dic[f"Detected text {m}:"]= text
                m+=1
            cv2.rectangle(draw,(x,y),(x+w,y+h),(0,255,0),2)
    draw=cv2.resize(draw,None,fx=0.5,fy=0.5)
    return text1,dic,draw