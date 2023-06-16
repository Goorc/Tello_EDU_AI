import time
import math
import numpy as np
class Auto_search:

    relative_position = {} #the position of the drone relative to the point where the self.__init__() is called
    start_time = 0
    previous_state = {} # the state of the drone in the previous calculation of the position of the drone
    search_area = {"width": 0, "depth": 0}
    maxControlInput = 30  # the maximum control input of the Auto_search algorithme per control axis
    minControlInput = 20  # should not be necessary, but below a certain speed the drone does not register a movement and therefore the relative position does not change
    view_distance = 3  # determines how far the drone can recognize a human, mainly influences the granularity of the search pattern
    relative_waypoints = []  # List of dictionaries of the relative_waypoints in the Auto_search
    waypoints = []
    nextWaypointIndex = 0   # Indicates which waypoint is the next to be reached in  Auto_search()
    Auto_search_active = False  # is used as a status indicator to whether the automatic search is active or not

    def __init__(self, current_state, search_area_width=10, search_area_depth=10):
        self.previous_state = current_state
        self.relative_position = {"x": 0, "y": 0, "z": 0, "yaw": current_state["yaw"], "yaw_at_start": current_state["yaw"], "time": time.time()}
        self.start_time = time.time()
        self.search_area = {"width": search_area_width, "depth": search_area_depth}
        self.yaw_at_start = current_state["yaw"]
        # Calculating Waypoints, z not needed since Tello maintains height
        i_x = 0
        while i_x*self.view_distance < self.search_area["depth"]:
            if (i_x % 2) == 0:
                self.relative_waypoints.append({"y": 0, "x": i_x*self.view_distance})
                self.relative_waypoints.append({"y": self.search_area["width"], "x": i_x*self.view_distance})
            else:
                self.relative_waypoints.append({"y": self.search_area["width"], "x": i_x*self.view_distance})
                self.relative_waypoints.append({"y": 0, "x": i_x*self.view_distance})
            i_x = i_x+1
        self.relative_waypoints.append({"y": 0, "x": 0})  # Last Waypoint will always be point of mission Start

    # Tracks the relative position of the drone in relation to the position of the initialization of the Object
    # the unit should be cm since vgx is in cm/s and time.time() in seconds but this does not really match
    # due to accumulation of measurement inaccuracies the precision is quite low
    def update_relative_position(self, current_state):
        current_time = time.time()
        delta_t = current_time - self.relative_position["time"]

        new_relative_position = { "x": self.relative_position["x"] + -(current_state["vgx"] + self.previous_state["vgx"]) / 2 * delta_t,
                                  "y": self.relative_position["y"] + -(current_state["vgy"] + self.previous_state["vgy"]) / 2 * delta_t,
                                  "z": self.relative_position["z"] + (current_state["vgz"] + self.previous_state["vgz"]) / 2 * delta_t,
                                  "time": current_time
                                  }
        self.previous_state = current_state
        self.relative_position = new_relative_position

    #resets the relative position, used when eg. starting an autonomous searh
    def reset_relative_position(self,current_state):
        self.previous_state = current_state
        self.relative_position = {"x": 0, "y": 0, "z": 0, "yaw": current_state["yaw"],"yaw_at_start": current_state["yaw"], "time": time.time()}
        self.yaw_at_start = current_state["yaw"]
        self.nextWaypointIndex = 0

    #returns the steering inputs for the Tello drone to follow the calculated Waypoints
    def Auto_search(self, current_state):
        lr, fb, ud, yv = 0, 0, 0, 0
        self.update_relative_position(current_state)

        distance_to_waypoint = math.sqrt((self.relative_waypoints[self.nextWaypointIndex]["y"]-self.relative_position["y"])**2 +
                                (self.relative_waypoints[self.nextWaypointIndex]["x"]-self.relative_position["x"])**2)
        #Proportional Controller for reaching the waypoint with maximum Speed of SearchSpeed
        pGain =5

        vec_to_waypoint = np.array([self.waypoints[self.nextWaypointIndex]["x"]-self.relative_position["x"],
                                    self.waypoints[self.nextWaypointIndex]["y"]-self.relative_position["y"]])

        #  calculating the angle between vec_to_waypoint and the vector [0,1] ot get the angle to be rotated
        vec_forward = np.array([1,0])
        dot_product = np.dot(vec_to_waypoint, vec_forward)
        magnitude1 = np.linalg.norm(vec_to_waypoint)
        magnitude2 = np.linalg.norm(vec_forward)
        cosine_angle = dot_product / (magnitude1 * magnitude2)
        angle = np.degrees(np.arccos(cosine_angle))

        # if vec_to_waypoint points into left half plane angle is supposed to be negative
        if vec_to_waypoint["x"] < 0:
            angle = -angle

        #  value positive if drone has to rotate clockwise negative if counterclockwise rotation is needed to correct
        yaw_error = angle - current_state["yaw"]
        yaw_error_normalized = yaw_error/180

        # P controller for Yaw error
        max_yv = 70
        yv = int(yaw_error_normalized * max_yv)

        #Case1: yaw error to big, either because of new waypoint or because disturbance of outside
        if yaw_error > 10:
            lr, fb, ud = 0, 0, 0

        #Case2: align yaw AND fly towards it by flying forward, the closer the distance to the waypoint, the slower the speed
        else:
            fb = int(pGain*magnitude1)
            if abs(fb) > self.maxControlInput:
                fb = int(fb / abs(fb) * self.maxControlInput)
            elif 0 < abs(fb) < self.minControlInput:
                fb = int(fb / abs(fb) * self.minControlInput)

        # Detecting if waypoint is reached
        if distance_to_waypoint < 1:
            self.nextWaypointIndex = self.nextWaypointIndex + 1
            if self.nextWaypointIndex > len(self.relative_waypoints)-1:  # Stay at last waypoint if it is reached
                self.nextWaypointIndex = self.nextWaypointIndex - 1
                lr, fb, ud, yv = 0, 0, 0, 0
        rc_control = lr, fb, ud, yv
        return rc_control


    def calculateWaypoints(self):
        #this function transforms the relative waypoints into absolute waypoints. relative_position is used as coordination system
        point_zero = self.relative_position
        yaw = math.radians(point_zero["yaw"])

        for rwp in self.relative_waypoints:
            x_new = point_zero["x"] + math.cos(yaw)*rwp["x"] + math.sin(yaw)*rwp["y"]
            y_new = point_zero["y"] + -math.sin(yaw)*rwp["x"] + math.cos(yaw)*rwp["y"]
            self.waypoints.append({"x":x_new,"y":y_new})


if __name__ == '__main__':
    test_current_state = {"vgx": 0,"vgy":0,"vgz":0,"yaw":0}
    auto_search = Auto_search(test_current_state)

    test_waypoints = []
    test_waypoints.append({"x":0,"y":0})
    test_waypoints.append({"x":1,"y":0})
    test_waypoints.append({"x":0,"y":1})

    auto_search.relative_waypoints = test_waypoints

    auto_search.relative_position["x"] = 5
    auto_search.relative_position["y"] = 7.5
    auto_search.relative_position["yaw"] = 90
    auto_search.calculateWaypoints()
    print("done")

