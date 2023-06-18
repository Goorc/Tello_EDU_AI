import GUI
import Waypoint_navigation
from djitellopy import tello
from time import sleep
import cv2
import numpy as np
from PersonDetector import PersonDetectorYoloV7
#
import logging

logging.getLogger('djitellopy').setLevel(logging.WARNING)

# gets the coordinates of the recognized object on the picture and returns steering commands appropriate to keep said
# object in the center of the frame by turning the drone about the yaw axis
def Yaw_follow(data):
    lr, fb, ud, yv = 0, 0, 0, 0
    # calculate the position of the object relative to the center of the frame
    frame_center_x, frame_center_y = data["img_width"] // 2, data["img_height"] // 2
    x_offset = data["x"] - frame_center_x

    max_yv = 70

    # generate steering commands based on the position of the object
    yv = int(x_offset / (0.5 * data["img_width"]) * max_yv)
    rc_control = lr, fb, ud, yv
    #print("Yaw_Follow:", rc_control)
    return rc_control

#returns the coordinates of the biggest coherent green dot in the Image. Can be used as a test instead of a person tracker
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

def person_tracker(image):
    trackpoint = person_detector.detect(image)
    return trackpoint

#converts he pressed keys into control commands which can be sent to tello
def keyboard2control(keys_pressed):
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 70 #range -100 to 100. Negative values invert the controls

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


me = tello.Tello()
me.connect()
gui = GUI.GuiObject()
waypoint_navigator = Waypoint_navigation.Waypoint_navigation(me.get_current_state())
me.streamon()
rc_control = [0, 0, 0, 0]
#gui.draw(me.get_frame_read().frame, me.get_current_state(), waypoint_navigator.position)
person_detector = PersonDetectorYoloV7()
print(me.get_current_state())
while True:
    img = me.get_frame_read().frame
    person_cords = None
    #Registering Keyboard Inputs
    keys_pressed = gui.getKeyboardInput()
    #Converting keyboard inputs into control commands for Tello
    rc_control = keyboard2control(keys_pressed)
    #Updating relative Position of Tello
    waypoint_navigator.update_position(me.get_current_state())
    if "Auto" in gui.flight_mode:  # Flight mode is Auto
        if not waypoint_navigator.navigator_active: #Check if first loop where flight mode is Auto to calculate position of Waypoints in world coordinate system
            search_area_size = gui.get_search_area_size()
            waypoint_navigator.calculate_waypoints(search_area_size["width"],search_area_size["depth"])
            waypoint_navigator.navigator_active = True
        if "SPACE" in keys_pressed: #if flight mode is Auto Space as dead man switch is pressed drone follows Waypoints
            rc_control = waypoint_navigator.navigate(me.get_current_state())
            person_cords = person_tracker(img)
            #print(person_cords)
            if person_cords is not None:
                rc_control = Yaw_follow(person_cords)
            #print("Yaw: " + str(me.get_yaw()))
            #print(waypoint_navigator.position)
            #print(rc_control)
    else:  # Flight mode is Manual
        waypoint_navigator.navigator_active = False
    #Sending rc controls either set by keyboard input or Algorithm to drone
    me.send_rc_control(rc_control[0], rc_control[1], rc_control[2], rc_control[3])
    sleep(0.05)

    #drawing the Gui including camera feed
    data_for_osd = {"current_state": me.get_current_state(),
                    "person_cords": person_cords, "position": waypoint_navigator.position,
                    "mag_to_waypoint": waypoint_navigator.mag_to_waypoint, "waypoints": waypoint_navigator.waypoints,
                    "waypoint_index": waypoint_navigator.waypoint_index,
                    "keys_pressed": keys_pressed}
    gui.draw(img, data_for_osd)
