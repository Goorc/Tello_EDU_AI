import GUI
from djitellopy import tello
from time import sleep
import cv2
import numpy as np
#
import logging
logging.getLogger('djitellopy').setLevel(logging.WARNING)

def Yaw_follow(data):
    lr, fb, ud, yv = 0, 0, 0, 0
    # calculate the position of the object relative to the center of the frame
    frame_center_x, frame_center_y = data["img_width"] // 2, data["img_height"] // 2
    x_offset = data["x"] - frame_center_x

    max_yv = 70

    # generate steering commands based on the position of the object
    yv = int(x_offset / (0.5 * data["img_width"]) * max_yv)
    rc_control = lr, fb, ud, yv
    print("Yaw_Follow:", rc_control)
    return rc_control
# gets the coordinates of the recognized object on the picture and returns steering commands appropriate to keep said
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
        # Get the height and width of the image
        height, width, channels = image.shape
        return {"x": cx, "y": cy, "img_width": width, "img_height": height}
    else:
        return None


def keyboard2control(keys_pressed):
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 50

    if "DOWN" in keys_pressed:
        fb = -speed
    elif "UP" in keys_pressed:
        fb = speed
    if "LEFT" in keys_pressed:
        lr = -speed
    elif "RIGHT" in keys_pressed:
        lr = speed
    if "w" in keys_pressed:
        ud = speed
    elif "s" in keys_pressed:
        ud = -speed
    if "a" in keys_pressed:
        yv = -speed
    elif "d" in keys_pressed:
        yv = speed
    if "q" in keys_pressed and not me.is_flying:
        me.takeoff()
    elif "q" in keys_pressed and me.is_flying:
        me.land()
    if "h" in keys_pressed:
        me.stop()
    rc_control = [lr, fb, ud, yv]
    return rc_control


gui = GUI.GuiObject()
me = tello.Tello()
me.connect()
print("Batterylevel:", me.get_battery(), "%")
print(me.get_current_state())
me.streamon()
rc_control = [0, 0, 0, 0]
gui.draw(me.get_frame_read().frame,me.get_current_state())

while True:
    img = me.get_frame_read().frame

    keys_pressed = gui.getKeyboardInput()
    print(keys_pressed)
    print(gui.flight_mode[0])
    if "SPACE" in keys_pressed and "Auto" in gui.flight_mode[0]: #Search on
        print("search on")
        obj_cords = green_tracker(img)
        rc_control = [0,0,0,20]
        if obj_cords is not None: #if Object found then track
            rc_control = Yaw_follow(obj_cords)
            gui.overlay(img, obj_cords["x"], obj_cords["y"])
    else:   #Manual
        rc_control = keyboard2control(keys_pressed)

    me.send_rc_control(rc_control[0], rc_control[1], rc_control[2], rc_control[3])
    sleep(0.05)

    gui.draw(img,me.get_current_state())
