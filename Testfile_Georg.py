from djitellopy import tello
#import KeyPressModule as kp
from time import sleep
import cv2
import numpy as np

def Yaw_follow(object_x, object_y, frame_width, frame_height):
    lr, fb, ud, yv = 0, 0, 0, 0
    # calculate the position of the object relative to the center of the frame
    frame_center_x, frame_center_y = frame_width // 2, frame_height // 2
    x_offset = object_x - frame_center_x

    # generate steering commands based on the position of the object
    if x_offset < -10:
        yv = -20
    elif x_offset > 10:
        yv = 20
    else:
        yv = 0

    control_values = lr, fb, ud, yv
    return control_values
#gets the coordinates of the recognized object on the picture and returns steering commands appropriate to keept said
# object in the center of the frame by turning the drone about the yaw axis

def green_tracker(image):
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
        return [cx, cy]
    else:
        return None

#kp.init()
me = tello.Tello()
me.connect()
print("Batterylevel:", me.get_battery(), "%")

def getKeyboardInput():
    lr, fb, ud, yv = 0,0,0,0
    #if kp.getKey("q"): me.takeoff()
    #if kp.getKey("e"): me.land()

    return [lr, fb, ud, yv]

me.streamon()


while True:
    img = me.get_frame_read().frame
    img = cv2.resize(img, (360,240))
    cv2.imshow("Image",img)
    cv2.waitKey(1)
    # Get the height and width of the image
    height, width, channels = img.shape

    obj_cords = green_tracker(img)
    if obj_cords is not None:
        vals = Yaw_follow(obj_cords[0],obj_cords[1],width, height)
    else:
        vals = [0,0,0,-10]
    print(vals)
    #me.send_rc_control(vals[0], vals[1], vals[2],vals[3])
    sleep(0.05)