import cv2
import numpy as np
import time
import math
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

    def __init__(self,resolution=(128,128)):
        self.detector = Yolov7Detector(traced=False,img_size=resolution,conf_thres=0.6)
        self.classes = None
        self.boxes = None
        self.scores = None
        self.detections = None

        self.point_distance_factor = 1.5
        self.score_factor = 0.25

        self.trackedPerson = None    
        # self.trackedPersonBox = None
        # self.trackedPersonScore = None
        # self.trackedPoint = None

    def detect(self, img):
        classes, boxes, scores = self.detector.detect(img)    
        
        self.classes = []
        self.boxes = []
        self.scores = []

        self.detections = []

        self.trackedPersonBox = None
        self.trackedPersonScore = None

        for i in range(len(classes[0])):
            if(classes[0][i] == 0):
                centerPoint = self.calcBoxCenter(boxes[0][i])
                detection = {"center":centerPoint,"box": boxes[0][i],"score":scores[0][i]}
                self.detections.append(detection)

        #if there is no tracked Person yet search for detection with highest score
        if(self.trackedPerson == None):

            






    def calcBoxCenter(self,box):
        x1,y1,x2,y2 = box
        x = (x1+x2)/2
        y = (y1+y2)/2
        return (x,y)
    

    def drawTrackPointOnImg(self,img):
        if(self.trackedPoint is None):
            return img
        else:
           #draw crosshair
            # black = np.zeros((480,640,3), np.uint8)
            # self.trackedPoint = (320,240)
            cv2.line(img,(self.trackedPoint["x"]-10,self.trackedPoint["y"]),(self.trackedPoint["x"]+10,self.trackedPoint["y"]),(0,255,0),thickness=2)
            cv2.line(img,(self.trackedPoint["x"],self.trackedPoint["y"]-10),(self.trackedPoint["x"],self.trackedPoint["y"]+10),(0,255,0),thickness=2)

           
            return img


    def drawTrackedPersonOnImg(self,img):
        if(self.trackedPersonBox is None):
            return img
        else:
            #get points as integer
            x1,y1,x2,y2 = self.trackedPersonBox
            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)
            cv2.rectangle(img, (x1,y1), (x2,y2), (255,0,0), 1)
            # cv2.line(img,(x1,y1),(x2,y2),(0,255,0),thickness=2)

            self.drawTrackPointOnImg(img)
            return img


    def drawBoxesOnImg(self,img):
        
        if(self.classes is None or self.boxes is None or self.scores is None):
            print("No detection yet")
            return img

        return self.detector.draw_on_image(img, self.boxes, self.scores, self.classes)




#Only if this file is executed directly
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    ret, img = cap.read()
    
    #resize image
    img = cv2.resize(img,(640,480))

    # detector = PersonDetector(yoloConfig="yoloTest\yolov3.cfg", yoloWeights="yoloTest\yolov3.weights", yoloClasses="yoloTest\coco.names")
    detector = PersonDetectorYoloV7()
    classes, boxes, scores = detector.detect(img)
    # img = detector.drawBoxesOnImg(img)
    # img = detector.drawTrackPointOnImg(img)
    img = detector.drawTrackedPersonOnImg(img)


    print("show image")
    cv2.imshow("test",img)
    
    # Abbrechen mit Taste 'q'
    while(True):
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break


