from djitellopy import tello
import KeyPressModule as kp
from time import sleep
import cv2
import numpy as np

def Yaw_follow(object_x, object_y, frame_width, frame_height):
    lr, fb, ud, yv = 0, 0, 0, 0
    # calculate the position of the object relative to the center of the frame
    frame_center_x, frame_center_y = frame_width // 2, frame_height // 2
    x_offset = object_x - frame_center_x

    max_yv = 70

    # generate steering commands based on the position of the object
    yv = int(x_offset/(0.5*frame_width)*max_yv)
    print("Yaw_Follow:", yv)
    rc_control = lr, fb, ud, yv
    return rc_control
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

def overlay(img, x, y):
    # Draw a red cross at the specified coordinates
    cv2.line(img, (x - 10, y), (x + 10, y), (0, 0, 255), 2)
    cv2.line(img, (x, y - 10), (x, y + 10), (0, 0, 255), 2)

kp.init()
me = tello.Tello()
me.connect()
print("Batterylevel:", me.get_battery(), "%")

def getKeyboardInput():

    lr, fb, ud, yv = 0,0,0,0
    manual_control = 1
    speed = 50

    if kp.getKey("LEFT"):
        lr = -speed
    elif kp.getKey("RIGHT"):
        lr = speed

    if kp.getKey("DOWN"):
        fb = -speed
    elif kp.getKey("UP"):
        fb = speed

    if kp.getKey("w"):
        ud = speed
    elif kp.getKey("s"):
        ud = -speed

    if kp.getKey("a"):
        yv = -speed
    elif kp.getKey("d"):
        yv = speed

    rc_control = [lr, fb, ud, yv, manual_control]
    if all(elem == 0 for elem in rc_control[:4]):
        rc_control[4] = 0

    if kp.getKey("q"): me.takeoff()
    if kp.getKey("e"): me.land()

    return rc_control

me.streamon()
prev_rc_control = [0,0,0,0,1]
rc_control = [0,0,0,0,1]
while True:
    img = me.get_frame_read().frame
    img = cv2.resize(img, (360,240))
    # Get the height and width of the image
    height, width, channels = img.shape

    obj_cords = green_tracker(img)
    rc_control = getKeyboardInput()
    if obj_cords is not None and rc_control[4] == 0:
        rc_control[3] = Yaw_follow(obj_cords[0],obj_cords[1],width, height)[3]
        overlay(img, obj_cords[0], obj_cords[1])
    elif obj_cords is None and rc_control[4] == 0 and prev_rc_control[3] is not 0:
        rc_control = prev_rc_control


    print(rc_control)
    me.send_rc_control(rc_control[0], rc_control[1], rc_control[2],rc_control[3])
    prev_rc_control = rc_control
    sleep(0.05)

    cv2.imshow("Image",img)
    cv2.waitKey(1)