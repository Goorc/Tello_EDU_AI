"""
The Main module houses the main loop and some additional functions which are needed to control the drone
"""
from djitellopy import tello
from time import sleep
from PersonDetector import PersonDetectorYoloV7
from Auto_modes import WaypointNavigation
from Auto_modes import YawFollow
from Gui import GuiObject
import logging

logging.getLogger('djitellopy').setLevel(logging.WARNING)  # suppress annoying warnings


def keyboard_to_control(keys_pressed, control_value = 70):
    """
    Converts the pressed keys on the keyboard into the corresponding rc controls wich can be sent to tello, also handles takeoff and landing commands

    :param keys_pressed: List of relevant keys pressed on the computer Keyboard
    :param control_value: value of rc_control if key is pressed range from -100 to 100, negative values to invert
    :return: The rc controls according to keys_pressed

    """
    lr, fb, ud, yv = 0, 0, 0, 0

    if "DOWN" in keys_pressed:
        fb = -control_value
    elif "UP" in keys_pressed:
        fb = control_value
    if "LEFT" in keys_pressed:
        lr = -control_value
    elif "RIGHT" in keys_pressed:
        lr = control_value
    if "w" in keys_pressed:
        ud = control_value
    elif "s" in keys_pressed:
        ud = -control_value
    if "a" in keys_pressed:
        yv = -control_value
    elif "d" in keys_pressed:
        yv = control_value
    if "q" in keys_pressed and not me.is_flying:
        me.takeoff()
    elif "q" in keys_pressed and me.is_flying:
        me.land()
    if "h" in keys_pressed:
        me.stop()
    return [lr, fb, ud, yv]


me = tello.Tello()
me.connect()
gui = GuiObject()
person_detector = PersonDetectorYoloV7()
waypoint_navigator = WaypointNavigation(me.get_current_state())
yaw_follower = YawFollow()
me.streamon()
rc_control = [0, 0, 0, 0]

# Main Loop
while True:
    person_cords = None
    img = me.get_frame_read().frame

    #Registering Keyboard Inputs and converting keyboard inputs into control commands for Tello
    keys_pressed = gui.getKeyboardInput()
    rc_control = keyboard_to_control(keys_pressed) # Default flight_mode is Manual

    #Updating relative Position of Tello
    waypoint_navigator.update_position(me.get_current_state())

    # check if flight_mode is Auto
    if gui.flight_mode == "Auto":
        if gui.prev_flight_mode == "Manual":  # Check if first loop where flight mode is Auto
            search_area_size = gui.get_search_area_size()
            waypoint_navigator.calculate_waypoints(search_area_size["width"],search_area_size["depth"])
        if "SPACE" in keys_pressed:  # SPACE as dead man switch
            rc_control = waypoint_navigator.navigate(me.get_current_state())
            person_cords = person_detector.detect(img)
            if person_cords is not None:
                rc_control = YawFollow.navigate(person_cords)

    # Sending rc controls either set by keyboard input or Auto_modes to drone
    me.send_rc_control(rc_control[0], rc_control[1], rc_control[2], rc_control[3])
    sleep(0.05)

    # drawing the gui including camera feed
    data_for_osd = {"current_state": me.get_current_state(),
                    "person_cords": person_cords, "position": waypoint_navigator.position,
                    "mag_to_waypoint": waypoint_navigator.mag_to_waypoint, "waypoints": waypoint_navigator.waypoints,
                    "waypoint_index": waypoint_navigator.waypoint_index,
                    "keys_pressed": keys_pressed}
    gui.draw(img, data_for_osd)
