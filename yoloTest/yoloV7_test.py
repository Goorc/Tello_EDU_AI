from yolov7_package import Yolov7Detector
import cv2
import numpy as np

if __name__ == '__main__':
    img = cv2.imread('1683118246142.png')
    #img = np.asarray(img, dtype=np.uint8)
    print("image read")
    det = Yolov7Detector(traced=False)
    classes, boxes, scores = det.detect(img)
    img = det.draw_on_image(img, boxes[0], scores[0], classes[0])

    cv2.imshow("image", img)
    cv2.waitKey()