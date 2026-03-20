import cv2
from ultralytics import YOLO
import numpy as np
def predict(img):
    model = YOLO("weights\best.pt")
    results = model(img, conf=0.4)
    return results[0].probs.data

#f=open(r"c:\Users\lenovo\OneDrive\Pictures\banker 2.jpg",'rb')
#nparr = np.frombuffer(f.read(), np.uint8)
#img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#print(predict(img))
