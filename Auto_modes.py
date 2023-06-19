import time
import math
import numpy as np


class WaypointNavigation:
    """
    This Class handles the tracking of the current position, as well as the calculation of the waypoints and the navigation of the drone to follow them.

    :param self.position: Position of the drone in the world coordinate system. The origin is where self.__init()__ is called. Positive X-Axis is in forward direction of tello at its boot, positive Y-Axis are to the right
    :param self.previous_state: The state of the drone from djitellopy at the previous call of self.update_position()
    :param self.search_parameters: Dictionary with "width" and "depth" of the grid made of the waypoints "distance" is the distance between the flight paths of the grid
    :param self.control_input_range: Dictionary of max and min absolute values of the control parameters which will be returned. Min needed so tello recognizes the movement
    :param self.relative_Waypoints: List of Dictionaries of the relative_waypoints in the coordinate system of the drone
    :param self.waypoints: List of Dictionaries of the waypoints in the world coordinate system
    :param self.waypoint_index: Indicates which waypoint is the next to be reached in navigate()
    :param self.mag_to_waypoint: Distance to next waypoint
    """

    def __init__(self, current_state, search_area_width=10, search_area_depth=10):

        self.position = {}
        self.previous_state = {}
        self.search_parameters = {"width": 0, "depth": 0, "distance": 9}
        self.control_input_range = {"maxlr": 60, "minlr": 20, "maxfb": 60, "minfb": 20, "maxud": 100, "minud": 0,
                               "maxyv": 70, "minyv": 0}
        self.relative_waypoints = []
        self.waypoints = []
        self.waypoint_index = 0
        self.mag_to_waypoint = 0

        self.previous_state = current_state
        self.position = {"x": 0, "y": 0, "z": 0, "yaw": current_state["yaw"], "time": time.time()}
        self.calculate_waypoints(search_area_width,search_area_depth)

    def update_position(self, current_state):
        """
        This method updates the position according to the velocities in current_state and previous_state.
        The units should be cm, but it's not. Due to accumulation of measurement inaccuracies the precision is quite low

        :param current_state: Current state of the drone from djitellopy

        """
        current_time = time.time()
        delta_t = current_time - self.position["time"]

        new_position = { "x": self.position["x"] + -(current_state["vgx"] + self.previous_state["vgx"]) / 2 * delta_t,
                                  "y": self.position["y"] + -(current_state["vgy"] + self.previous_state["vgy"]) / 2 * delta_t,
                                  "z": self.position["z"] + (current_state["vgz"] + self.previous_state["vgz"]) / 2 * delta_t,
                                  "yaw": current_state["yaw"],
                                  "time": current_time
                                  }
        self.previous_state = current_state
        self.position = new_position

    #
    def navigate(self, current_state):
        """
        This method returns the steering inputs for Tello to follow the waypoints

        :param current_state: Current state of the drone from djitellopy
        :return: rc_controls which can be sent to Tello
        """
        lr, fb, ud, yv = 0, 0, 0, 0
        self.update_position(current_state)

        vec_to_waypoint = np.array([self.waypoints[self.waypoint_index]["x"]-self.position["x"],
                                    self.waypoints[self.waypoint_index]["y"]-self.position["y"]])
        self.mag_to_waypoint = np.linalg.norm(vec_to_waypoint)

        if self.mag_to_waypoint != 0:
            #  calculating the angle between vec_to_waypoint and the vector [0,1] to get the angle to be rotated
            vec_forward = np.array([1,0])
            dot_product = np.dot(vec_to_waypoint, vec_forward)
            mag_forward = np.linalg.norm(vec_forward)
            cosine_angle = dot_product / (self.mag_to_waypoint * mag_forward)
            yaw_setpoint = np.degrees(np.arccos(cosine_angle))

            # setpoint has to be negative if vec_to_waypoint points into left halfplane
            if vec_to_waypoint[1]<0:
                yaw_setpoint = -yaw_setpoint

            yaw_measured = current_state["yaw"]

            #  value positive if tello should rotate clockwise, otherwise negative
            yaw_error = yaw_setpoint - yaw_measured
            if yaw_error > 180:
                yaw_error -= 360
            elif yaw_error < -180:
                yaw_error += 360
            yaw_error_normalized = yaw_error/180

            # P-Controller always aligning Tello, so it looks at the next waypoint
            yv = int(yaw_error_normalized * self.control_input_range["maxyv"]*3 )
            # Case1: yaw error to big, either because of new waypoint or because of outside disturbance
            if abs(yaw_error_normalized) > 0.05:
                lr, fb, ud = 0, 0, 0
            # Case2: P-Controller to fly towards the next waypoint by flying forwards
            else:
                fb = int(5*self.mag_to_waypoint)
                if abs(fb) > self.control_input_range["maxfb"]:
                    fb = int(fb / abs(fb) * self.control_input_range["maxfb"])
                elif 0 < abs(fb) < self.control_input_range["minfb"]:
                    fb = int(fb / abs(fb) * self.control_input_range["minfb"])

        # Detecting if waypoint is reached
        if self.mag_to_waypoint < 2:
            self.waypoint_index = self.waypoint_index + 1
            if self.waypoint_index > len(self.waypoints)-1:  # Stay at last waypoint if it is reached
                self.waypoint_index = self.waypoint_index - 1
                lr, fb, ud, yv = 0, 0, 0, 0
        rc_control = lr, fb, ud, yv
        return rc_control

    def calculate_waypoints(self, search_area_width=10, search_area_depth=10):
        """
        This method calculates the waypoints according to the user input or the default values

        :param search_area_width: Width of the area to be searched
        :param search_area_depth: Depth of the area to be searched
        """
        # Calculating relative waypoints in the coordinate system of the drone, z not needed since Tello maintains height
        self.relative_waypoints = []
        self.search_parameters["width"] = int(search_area_width)
        self.search_parameters["depth"] = int(search_area_depth)
        i_x = 0
        while i_x * self.search_parameters["distance"] < self.search_parameters["depth"]:
            if (i_x % 2) == 0:
                self.relative_waypoints.append({"y": 0, "x": i_x * self.search_parameters["distance"]})
                self.relative_waypoints.append(
                    {"y": self.search_parameters["width"], "x": i_x * self.search_parameters["distance"]})
            else:
                self.relative_waypoints.append(
                    {"y": self.search_parameters["width"], "x": i_x * self.search_parameters["distance"]})
                self.relative_waypoints.append({"y": 0, "x": i_x * self.search_parameters["distance"]})
            i_x = i_x + 1
        self.relative_waypoints.append({"y": 0, "x": 0})  # Last Waypoint will always be point of mission Start
        print("relative_waypoints: "+ str(self.relative_waypoints))
        # transforming the relative waypoints into absolute waypoints in the world coordinate system
        self.waypoint_index = 0
        self.waypoints = []
        point_zero = self.position
        yaw = math.radians(point_zero["yaw"])

        for rwp in self.relative_waypoints:
            x_new = point_zero["x"] + math.cos(yaw)*rwp["x"] + -math.sin(yaw)*rwp["y"]
            y_new = point_zero["y"] + math.sin(yaw)*rwp["x"] + math.cos(yaw)*rwp["y"]
            self.waypoints.append({"x":x_new,"y":y_new})



class YawFollow:
    """
    This class makes it possible to keep an object which position is known in the center of the frame by rotating Tello along the Yaw-Axis
    """
    def navigate(obj_cords):
        """
        This method returns the appropriate rc_control values to keep the object with the known coordinates in the
        center of the frame

        :param obj_cords: Dictionary of the x, y coordinates of the object as well as the width and height of the image the object has been identified
        :return: rc_controls which can be sent to Tello
        """
        lr, fb, ud, yv = 0, 0, 0, 0

        # calculate the position of the object relative to the center of the frame
        frame_center_x, frame_center_y = obj_cords["img_width"] // 2, obj_cords["img_height"] // 2
        x_offset = obj_cords["x"] - frame_center_x

        # generate steering commands based on the position of the object
        max_yv = 70
        yv = int(x_offset / (0.5 * obj_cords["img_width"]) * max_yv)

        rc_control = lr, fb, ud, yv
        return rc_control


if __name__ == '__main__':
    test_current_state = {"vgx": 0,"vgy":0,"vgz":0,"yaw":0}
    auto_search = WaypointNavigation(test_current_state)

    test_waypoints = []
    test_waypoints.append({"x":0,"y":0})
    test_waypoints.append({"x":1,"y":0})
    test_waypoints.append({"x":0,"y":1})

    auto_search.relative_waypoints = test_waypoints

    auto_search.position["x"] = 5
    auto_search.position["y"] = 7.5
    auto_search.position["yaw"] = 90
    auto_search.calculate_waypoints()
    print("done")

