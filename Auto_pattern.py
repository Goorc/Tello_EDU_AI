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
    waypoints = []  # List of dictionaries of the waypoints in the Auto_search
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
                self.waypoints.append({"y": 0, "x": i_x*self.view_distance})
                self.waypoints.append({"y": self.search_area["width"], "x": i_x*self.view_distance})
            else:
                self.waypoints.append({"y": self.search_area["width"], "x": i_x*self.view_distance})
                self.waypoints.append({"y": 0, "x": i_x*self.view_distance})
            i_x = i_x+1
        self.waypoints.append({"y": 0, "x": 0})  # Last Waypoint will always be point of mission Start

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
        #Proportional Controller for reaching the waypoint with maximum Speed of SearchSpeed
        pGain =5

        #left-right
        lr = int(pGain * (self.waypoints[self.nextWaypointIndex]["y"] - self.relative_position["y"]))
        if abs(lr) > self.maxControlInput:
            lr = int(lr/abs(lr)*self.maxControlInput)
        elif 0 < abs(lr) < self.minControlInput:
            lr = int(lr / abs(lr) * self.minControlInput)
        #front-back
        fb = int(pGain * (self.waypoints[self.nextWaypointIndex]["x"] - self.relative_position["x"]))
        if abs(fb) > self.maxControlInput:
            fb = int(fb / abs(fb) * self.maxControlInput)
        elif 0 < abs(fb) < self.minControlInput:
            fb = int(fb / abs(fb) * self.minControlInput)



        distance_to_waypoint = math.sqrt((self.waypoints[self.nextWaypointIndex]["y"]-self.relative_position["y"])**2 +
                                (self.waypoints[self.nextWaypointIndex]["x"]-self.relative_position["x"])**2)
        #print("Current Waypoint:" + str(self.waypoints[self.nextWaypointIndex]))

        if distance_to_waypoint < 1:  # Detecting if waypoint is reached
            self.nextWaypointIndex = self.nextWaypointIndex + 1
            if self.nextWaypointIndex > len(self.waypoints)-1:  # Stay at last waypoint if it is reached
                self.nextWaypointIndex = self.nextWaypointIndex - 1
                lr, fb, ud, yv = 0, 0, 0, 0
        rc_control = lr, fb, ud, yv
        return rc_control
