import cv2
import numpy as np

#returns the coordinates of the biggest coherent green dot in the Image. Can be used as a test instead of a person tracker
class Green_detector:
    def detect(image):
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
