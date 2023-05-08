import cv2
import numpy as np
import time

# Laden des vortrainierten Modells
model = cv2.dnn.readNetFromDarknet("yolov3.cfg", "yolov3.weights")

# Liste mit den Namen der erkannten Objekte
classes = []
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# Festlegen der Schwellenwerte
conf_threshold = 0.5
nms_threshold = 0.4

# Webcam initialisieren
cap = cv2.VideoCapture(0)

while True:
    # Bild von der Webcam lesen
    time1 = time.time()
    ret, img = cap.read()
    time2 = time.time()

    # Bildgröße anpassen und Normalisieren
    blob = cv2.dnn.blobFromImage(img, 1/255, (128,128), (0,0,0), True, crop=False)

    # Bild durch das Modell leiten
    model.setInput(blob)
    output_layers = model.getUnconnectedOutLayersNames()
    layer_outputs = model.forward(output_layers)

    # Objekte erkennen und Klassennamen und Konfidenzen extrahieren
    class_ids = []
    confidences = []
    boxes = []
    for output in layer_outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > conf_threshold:
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
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

    time3 = time.time()

    # Bounding-Boxen und Klassennamen zeichnen
    if len(indices) > 0:
        for i in indices.flatten():
            box = boxes[i]
            x, y, w, h = box
            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
            cv2.putText(img, classes[class_ids[i]], (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

    time4 = time.time()

    #print time measurements
    print(f'capture time={time2-time1}, forward propagation time={time3-time2}, drawing time={time4-time3}')
    # Bild anzeigen
    cv2.imshow("Personenerkennung", img)

    # Abbrechen mit Taste 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Ressourcen freigeben und Fenster schließen
cap.release()
cv2.destroyAllWindows()
