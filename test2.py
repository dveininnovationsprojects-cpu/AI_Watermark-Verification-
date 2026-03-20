import cv2
from ultralytics import YOLO
import numpy as np
def predict(img):
    model = YOLO(r"D:\SHIVESANGKER-Water Mark Project\SHIVESANGKER-Water Mark Project\runs\classify\train11\weights\best.pt")
    results = model(img, conf=0.4)
    return results[0].probs.data
def predict(img):
    return [0.5, 0.5]
#f=open(r"c:\Users\lenovo\OneDrive\Pictures\banker 2.jpg",'rb')
#nparr = np.frombuffer(f.read(), np.uint8)
#img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#print(predict(img))
