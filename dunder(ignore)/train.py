from ultralytics import YOLO

def main():

    model = YOLO("yolov8n-cls.pt")

    model.train(
    data="datasets",
    epochs=50, 
    patience=5,
    imgsz=512,
    batch=8,
    workers=2,
    device=0
)

if __name__ == "__main__":
    main()
    