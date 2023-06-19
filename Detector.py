import cv2
import numpy as np
import time
from yolov7_package import Yolov7Detector


class PersonDetectorYoloV7():

    """
    Class to detect Persons in an image. It uses the Yolo objetd-detection system.
    For a given image the system detects all Persons and generate a tracking position in pixels.
    """

    def __init__(self, resolution=(128, 128)):
        self.detector = Yolov7Detector(traced=False, img_size=resolution, conf_thres=0.6)
        self.classes = None
        self.boxes = None
        self.scores = None

        self.trackedPersonBox = None
        self.trackedPersonScore = None
        self.trackedPoint = None

    def detect(self, img):
        classes, boxes, scores = self.detector.detect(img)

        self.classes = []
        self.boxes = []
        self.scores = []

        self.trackedPersonBox = None
        self.trackedPersonScore = None

        for i in range(len(classes[0])):
            if (classes[0][i] == 0):

                if (self.trackedPersonScore is None):
                    self.trackedPersonScore = scores[0][i]
                    self.trackedPersonBox = boxes[0][i]
                else:
                    if (scores[0][i] > self.trackedPersonScore):
                        self.trackedPersonScore = scores[0][i]
                        self.trackedPersonBox = boxes[0][i]

                # boxes[0][i][0] = 100
                # boxes[0][i][1] = 90
                # boxes[0][i][2] = 300
                # boxes[0][i][3] = 100

                self.classes.append(classes[0][i])
                self.boxes.append(boxes[0][i])
                self.scores.append(scores[0][i])

        if (self.trackedPersonBox is not None):
            x1, y1, x2, y2 = self.trackedPersonBox

            x = (x1 + x2) / 2
            y = (y1 + y2) / 2
            self.trackedPoint = {"x": int(x), "y": int(y), "img_width": img.shape[1], "img_height": img.shape[0]}
            return self.trackedPoint
        return None

    def drawTrackPointOnImg(self, img):
        if (self.trackedPoint is None):
            return img
        else:
            # draw crosshair
            # black = np.zeros((480,640,3), np.uint8)
            # self.trackedPoint = (320,240)
            cv2.line(img, (self.trackedPoint["x"] - 10, self.trackedPoint["y"]),
                     (self.trackedPoint["x"] + 10, self.trackedPoint["y"]), (0, 255, 0), thickness=2)
            cv2.line(img, (self.trackedPoint["x"], self.trackedPoint["y"] - 10),
                     (self.trackedPoint["x"], self.trackedPoint["y"] + 10), (0, 255, 0), thickness=2)

            return img

    def drawTrackedPersonOnImg(self, img):
        if (self.trackedPersonBox is None):
            return img
        else:
            # get points as integer
            x1, y1, x2, y2 = self.trackedPersonBox
            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 1)
            # cv2.line(img,(x1,y1),(x2,y2),(0,255,0),thickness=2)

            self.drawTrackPointOnImg(img)
            return img

    def drawBoxesOnImg(self, img):

        if (self.classes is None or self.boxes is None or self.scores is None):
            print("No detection yet")
            return img

        return self.detector.draw_on_image(img, self.boxes, self.scores, self.classes)


class Green_detector:
    """
        This Class can be used to recognise the biggest coherent green dot in the Image. Can be used as a test instead of the person tracker
    """
    def detect(image):
        """
        Returns the coordinates of the biggest coherent green dot in the Image. Can be used as a test instead of the person tracker

        :param image: input image to be analyzed
        :return: Dictionary with position of tracked object and image size
        """
        # Convert the image to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Define the lower and upper bounds of the green color
        lower_green = np.array([50, 50, 50])
        upper_green = np.array([70, 255, 255])

        # Create a mask for the green color
        mask = cv2.inRange(hsv, lower_green, upper_green)

        # Find the contours of the green dots
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Find the biggest green dot and get its coordinates
        biggest_area = 0
        biggest_contour = None
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > biggest_area:
                biggest_area = area
                biggest_contour = contour

        if biggest_contour is not None:
            moments = cv2.moments(biggest_contour)
            cx = int(moments['m10'] / moments['m00'])
            cy = int(moments['m01'] / moments['m00'])

            # Get the height and width of the image
            height, width, channels = image.shape
            return {"x": cx, "y": cy, "img_width": width, "img_height": height}
        else:
            return None

# Only if this file is executed directly
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    ret, img = cap.read()

    # resize image
    img = cv2.resize(img, (640, 480))

    # detector = PersonDetector(yoloConfig="yoloTest\yolov3.cfg", yoloWeights="yoloTest\yolov3.weights", yoloClasses="yoloTest\coco.names")
    detector = PersonDetectorYoloV7()
    classes, boxes, scores = detector.detect(img)
    # img = detector.drawBoxesOnImg(img)
    # img = detector.drawTrackPointOnImg(img)
    img = detector.drawTrackedPersonOnImg(img)

    print("show image")
    cv2.imshow("test", img)

    # Abbrechen mit Taste 'q'
    while (True):
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break