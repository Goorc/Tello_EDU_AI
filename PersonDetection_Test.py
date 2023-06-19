from djitellopy import tello
from time import sleep
from Detectors import PersonDetectorYoloV7
import cv2
import time

me = tello.Tello()
me.connect()
print("Batterylevel:", me.get_battery(), "%")

me.streamon()


detector = PersonDetectorYoloV7()


while True:
    sleep(0.05)

    time1 = time.time()

    img = me.get_frame_read().frame

    time2 = time.time()

    detector.detect(img)

    time3 = time.time()

    img = detector.drawBoxesOnImg(img)
    img = detector.drawTrackPointOnImg(img)

    time4 = time.time()

    print("Time to get frame:", time2-time1)
    print("Time to detect:", time3-time2)
    print("Time to draw:", time4-time3)

    # print("FPS:", 1/(time4-time1))

    cv2.imshow("Image",img)
    cv2.waitKey(1)    

    #img = cv2.resize(img, (360,240))
    #cv2.imshow("Image",img)
    cv2.waitKey(1)