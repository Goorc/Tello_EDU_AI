from djitellopy import tello
import KeyPressModule as kp
from time import sleep
from PersonDetector import PersonDetector
import cv2

kp.init()
me = tello.Tello()
me.connect()
print("Batterylevel:", me.get_battery(), "%")

me.streamon()


detector = PersonDetector(yoloConfig="yoloTest\yolov3.cfg", yoloWeights="yoloTest\yolov3.weights", yoloClasses="yoloTest\coco.names")


while True:
    sleep(0.05)
    img = me.get_frame_read().frame

    indices,boxes = detector.detect(img)
    img = detector.drawBoxesOnImg(img,indices,boxes)
    cv2.imshow("Image",img)
    cv2.waitKey(1)    

    #img = cv2.resize(img, (360,240))
    #cv2.imshow("Image",img)
    cv2.waitKey(1)