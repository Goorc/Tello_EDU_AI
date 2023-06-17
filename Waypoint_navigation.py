import time
import math
import numpy as np
class Waypoint_navigation:

    position = {} #the position of the drone relative to the point where the self.__init__() is called
    start_time = 0
    previous_state = {} # the state of the drone in the previous calculation of the position of the drone
    search_area = {"width": 0, "depth": 0}
    view_distance = 9  # determines how far the drone can recognize a human, mainly influences the granularity of the search pattern
    # the max and min absolute value of the control inputs of the corrosponting controlaxis
    # max is needed to avoid overshoot, min is needed because otherwise the drone does not register a movement and the position won't be updated
    control_input_range = {"maxlr": 60, "minlr": 20, "maxfb": 60 , "minfb":20, "maxud":100, "minud":0, "maxyv":100, "minyv":0}
    relative_waypoints = []  # List of dictionaries of the relative_waypoints in the Auto_search
    waypoints = []
    nextWaypointIndex = 0   # Indicates which waypoint is the next to be reached in  Auto_search()
    navigator_active = False  # is used as a status indicator to whether the automatic search is active or not

    def __init__(self, current_state, search_area_width=30, search_area_depth=30):
        self.previous_state = current_state
        self.position = {"x": 0, "y": 0, "z": 0, "yaw": current_state["yaw"], "time": time.time()}
        self.start_time = time.time()
        self.search_area = {"width": search_area_width, "depth": search_area_depth}
        self.yaw_at_start = current_state["yaw"]
        # Calculating relative waypoints in the coordinate system of the drone, z not needed since Tello maintains height
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
    def update_position(self, current_state):
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

    #returns the steering inputs for the Tello drone to follow the calculated Waypoints
    def navigate(self, current_state):
        lr, fb, ud, yv = 0, 0, 0, 0
        self.update_position(current_state)

        distance_to_waypoint = math.sqrt((self.waypoints[self.nextWaypointIndex]["y"]-self.position["y"])**2 +
                                (self.waypoints[self.nextWaypointIndex]["x"]-self.position["x"])**2)

        vec_to_waypoint = np.array([self.waypoints[self.nextWaypointIndex]["x"]-self.position["x"],
                                    self.waypoints[self.nextWaypointIndex]["y"]-self.position["y"]])
        #print("next_waypoint" +str(self.waypoints[self.nextWaypointIndex])+ "  index:" + str(self.nextWaypointIndex))
        #print("vec_to_waypoint: "+ str(vec_to_waypoint))

        if distance_to_waypoint != 0:
            #  calculating the angle between vec_to_waypoint and the vector [0,1] to get the angle to be rotated
            #print("yaw: "+str(current_state["yaw"]))
            vec_forward = np.array([1,0])
            dot_product = np.dot(vec_to_waypoint, vec_forward)
            mag_to_waypoint = np.linalg.norm(vec_to_waypoint)
            mag_forward = np.linalg.norm(vec_forward)
            cosine_angle = dot_product / (mag_to_waypoint * mag_forward)
            angle = np.degrees(np.arccos(cosine_angle))
            #print("angle: "+str(angle))

            # if vec_to_waypoint points into left half plane angle is supposed to be negative
            if vec_to_waypoint[1] < 0:
                angle = -angle

            #  value positive if drone has to rotate clockwise negative if counterclockwise rotation is needed to correct
            yaw_error = angle - current_state["yaw"]
            #print("yaw_error: "+ str(yaw_error))
            yaw_error_normalized = yaw_error/180

            # P controller always aligning the Drone so it looks at the next waypoint
            max_yv = 100
            yv = int(yaw_error_normalized * max_yv * 5)

            #Case1: yaw error to big, either because of new waypoint or because of outside disturbance
            if abs(yaw_error) > 5:
                lr, fb, ud = 0, 0, 0
            #Case2: P controller to fly towards the next waypoint by flying forward
            else:
                fb = int(5*mag_to_waypoint)
                if abs(fb) > self.control_input_range["maxfb"]:
                    fb = int(fb / abs(fb) * self.control_input_range["maxfb"])
                elif 0 < abs(fb) < self.control_input_range["minfb"]:
                    fb = int(fb / abs(fb) * self.control_input_range["minfb"])

        # Detecting if waypoint is reached
        if distance_to_waypoint < 3:
            self.nextWaypointIndex = self.nextWaypointIndex + 1
            if self.nextWaypointIndex > len(self.waypoints)-1:  # Stay at last waypoint if it is reached
                self.nextWaypointIndex = self.nextWaypointIndex - 1
                lr, fb, ud, yv = 0, 0, 0, 0
        rc_control = lr, fb, ud, yv
        print("rc_control"+ str(rc_control))
        return rc_control


    def calculateWaypoints(self):
        #this function transforms the relative waypoints into absolute waypoints. position is used as coordination system
        self.nextWaypointIndex = 0
        self.waypoints = []
        point_zero = self.position
        yaw = math.radians(point_zero["yaw"])

        for rwp in self.relative_waypoints:
            x_new = point_zero["x"] + math.cos(yaw)*rwp["x"] + -math.sin(yaw)*rwp["y"]
            y_new = point_zero["y"] + math.sin(yaw)*rwp["x"] + math.cos(yaw)*rwp["y"]
            self.waypoints.append({"x":x_new,"y":y_new})
        print("current position:" + str(self.position))
        print("calculated Waypoints:"+ str(self.waypoints))


if __name__ == '__main__':
    test_current_state = {"vgx": 0,"vgy":0,"vgz":0,"yaw":0}
    auto_search = Waypoint_navigation(test_current_state)

    test_waypoints = []
    test_waypoints.append({"x":0,"y":0})
    test_waypoints.append({"x":1,"y":0})
    test_waypoints.append({"x":0,"y":1})

    auto_search.relative_waypoints = test_waypoints

    auto_search.position["x"] = 5
    auto_search.position["y"] = 7.5
    auto_search.position["yaw"] = 90
    auto_search.calculateWaypoints()
    print("done")

