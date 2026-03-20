import cv2
import numpy as np
from tensorflow.keras.models import load_model

model = load_model("cnn_10class_model.h5")

img = cv2.imread("test.jpg")

img = cv2.resize(img, (128,128))
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

img = img / 255.0
img = np.expand_dims(img, axis=0)

prediction = model.predict(img)

class_id = prediction.argmax()

print("Predicted class:", class_id)