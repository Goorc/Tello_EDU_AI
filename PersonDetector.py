import cv2
import numpy as np
import time
from yolov7_package import Yolov7Detector

class PersonDetectorYoloV3():

    def __init__(self,yoloConfig="yolov3.cfg", yoloWeights="yolov3.weights", yoloClasses="coco.names"):
        self.model = cv2.dnn.readNetFromDarknet(yoloConfig, yoloWeights)
        self.classes = []
        with open(yoloClasses, "r") as f:
            self.classes = [line.strip() for line in f.readlines()]

        # Festlegen der Schwellenwerte
        self.conf_threshold = 0.5
        self.nms_threshold = 0.4

    def detect(self, img):
        # Bildgröße anpassen und Normalisieren
        blob = cv2.dnn.blobFromImage(img, 1/255, (128,128), (0,0,0), True, crop=False)
        self.model.setInput(blob)
        output_layers = self.model.getUnconnectedOutLayersNames()
        layer_outputs = self.model.forward(output_layers)

        # Objekte erkennen und Klassennamen und Konfidenzen extrahieren
        class_ids = []
        confidences = []
        boxes = []
        for output in layer_outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > self.conf_threshold:
                    center_x = int(detection[0] * img.shape[1])
                    center_y = int(detection[1] * img.shape[0])
                    w = int(detection[2] * img.shape[1])
                    h = int(detection[3] * img.shape[0])
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        # Nicht-maximum-Unterdrückung ausführen, um Überlappungen zu vermeiden
        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.conf_threshold, self.nms_threshold)
        return indices, boxes

    def drawBoxesOnImg(self,img,indices,boxes):
        # Bounding-Boxen und Klassennamen zeichnen
        if len(indices) > 0:
            for i in indices.flatten():
                box = boxes[i]
                x, y, w, h = box
                cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
        return img


class PersonDetectorYoloV7():

    def __init__(self):
        self.detector = Yolov7Detector(traced=False,img_size=(128,128))

    def detect(self, img):
        classes, boxes, scores = self.detector.detect(img)    
        return classes, boxes, scores

    def drawBoxesOnImg(self,img,classes, boxes, scores):
        return self.detector.draw_on_image(img, boxes[0], scores[0], classes[0])




#Only if this file is executed directly
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    ret, img = cap.read()
    
    # detector = PersonDetector(yoloConfig="yoloTest\yolov3.cfg", yoloWeights="yoloTest\yolov3.weights", yoloClasses="yoloTest\coco.names")
    detector = PersonDetectorYoloV7()
    classes, boxes, scores = detector.detect(img)
    img = detector.drawBoxesOnImg(img,classes, boxes, scores)
    
    print("show image")
    cv2.imshow("test",img)
    
    # Abbrechen mit Taste 'q'
    while(True):
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break


