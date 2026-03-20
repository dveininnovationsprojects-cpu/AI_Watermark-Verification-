import psycopg
import numpy as np
from PIL import Image
import io
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from tensorflow.keras.preprocessing.image import ImageDataGenerator

conn = psycopg.connect(
    dbname="watermark",
    user="postgres",
    password="shive",
    host="localhost",
    port=5432
)

cur = conn.cursor()
cur.execute("SELECT data, lsb_val, dct_energy, watermarked FROM images;")
train_rows = cur.fetchall()

cur.execute("SELECT data, lsb_val, dct_energy, watermarked FROM images2;")
val_rows = cur.fetchall()



def process_rows(rows):
    images = []
    numeric_feats = []
    labels = []

    for img_bytes, f1, f2, label in rows:
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        img = img.resize((128,128))
        img = np.array(img,dtype=np.float32) / 255.0

        images.append(img)
        numeric_feats.append([f1, f2])
        labels.append(int(label))  # boolean → 0/1

    return np.array(images,dtype=np.uint8), np.array(numeric_feats), np.array(labels)

X_img_train, X_num_train, y_train = process_rows(train_rows)
X_img_val, X_num_val, y_val = process_rows(val_rows)

import tensorflow as tf
from tensorflow.keras import layers, Model
datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)

# Image branch
image_input = layers.Input(shape=(128,128,3))
x = layers.Conv2D(32, (3,3), activation="relu")(image_input)
x = layers.BatchNormalization()(x)
x = layers.MaxPooling2D()(x)
x = layers.Conv2D(64, (3,3), activation="relu")(x)
x = layers.BatchNormalization()(x)
x = layers.MaxPooling2D()(x)

x = layers.Conv2D(128,3,activation='relu')(x)
x = layers.BatchNormalization()(x)
x = layers.MaxPooling2D()(x)
x = layers.Flatten()(x)
# Combine

z = layers.Dense(64, activation="relu")(x)

output = layers.Dense(1, activation="sigmoid")(z)
model = Model(inputs=image_input, outputs=output)
model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy",tf.keras.metrics.Precision(name="precision"),
        tf.keras.metrics.Recall(name="recall"),
        tf.keras.metrics.AUC(name="auc")]
)
from tensorflow.keras.callbacks import EarlyStopping
model.summary()
early_stop = EarlyStopping(
    monitor="val_loss",
    patience=5,
    restore_best_weights=True
)
model.fit(
    X_img_train,
    y_train,
    validation_data=(X_img_val, y_val),
    epochs=100,
    batch_size=32,
    callbacks=[early_stop]
)
model.save("model3.keras")
print('model saved')