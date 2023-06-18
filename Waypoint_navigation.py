import time
import math
import numpy as np
class Waypoint_navigation:

    position = {} #the position of the drone in the world coordinate system. The origin is where self.__init()__ is called. positive X-Axis is in forward direction, positive Y-Axis is to the right of the drone at the time of turning the drone on (not the the initialisation of this class)
    previous_state = {} # the state of the drone in the previous calculation of the position of the drone
    search_parameters = {"width": 0, "depth": 0, "distance": 9} #width and depth of the square which is search and distance between the lines of the searchpattern
    # the max and min absolute value of the control inputs of the corrosponting controlaxis
    # max is needed to avoid overshoot, min is needed because otherwise the drone does not register a movement and the position won't be updated
    control_input_range = {"maxlr": 60, "minlr": 20, "maxfb": 60 , "minfb":20, "maxud":100, "minud":0, "maxyv":70, "minyv":0}
    relative_waypoints = []  # List of dictionaries of the relative_waypoints in the coordinate system of the drone
    waypoints = [] # List of dictionaries of the waypoints in the world coordinate system
    waypoint_index = 0   # Indicates which waypoint is the next to be reached in  navigate()
    mag_to_waypoint = 0

    def __init__(self, current_state, search_area_width=10, search_area_depth=10):
        self.previous_state = current_state
        self.position = {"x": 0, "y": 0, "z": 0, "yaw": current_state["yaw"], "time": time.time()}
        self.calculate_waypoints(search_area_width,search_area_depth)

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

        vec_to_waypoint = np.array([self.waypoints[self.waypoint_index]["x"]-self.position["x"],
                                    self.waypoints[self.waypoint_index]["y"]-self.position["y"]])
        self.mag_to_waypoint = np.linalg.norm(vec_to_waypoint)
        #print("next_waypoint" +str(self.waypoints[self.waypoint_index])+ "  index:" + str(self.waypoint_index))
        #print("vec_to_waypoint: "+ str(vec_to_waypoint))

        if self.mag_to_waypoint != 0:
            #  calculating the angle between vec_to_waypoint and the vector [0,1] to get the angle to be rotated
            #print("yaw: "+str(current_state["yaw"]))
            vec_forward = np.array([1,0])
            dot_product = np.dot(vec_to_waypoint, vec_forward)
            mag_forward = np.linalg.norm(vec_forward)
            cosine_angle = dot_product / (self.mag_to_waypoint * mag_forward)
            yaw_setpoint = np.degrees(np.arccos(cosine_angle))

            #setpoint has to be negative if vec to waypoint points into left halfplane
            if vec_to_waypoint[1]<0:
                yaw_setpoint = -yaw_setpoint

            yaw_measured = current_state["yaw"]
            #print("yaw_setpoint: " + str(yaw_setpoint))
            #  value positive if drone has to rotate clockwise negative if counterclockwise rotation is needed to correct
            yaw_error = yaw_setpoint - yaw_measured

            if yaw_error > 180:
                yaw_error -= 360
            elif yaw_error < -180:
                yaw_error += 360

            #print("yaw_error: "+ str(yaw_error))
            yaw_error_normalized = yaw_error/180

            # P controller always aligning the Drone, so it looks at the next waypoint
            max_yv = 100
            yv = int(yaw_error_normalized * max_yv*3 )

            #Case1: yaw error to big, either because of new waypoint or because of outside disturbance
            if abs(yaw_error_normalized) > 0.05:
                lr, fb, ud = 0, 0, 0
            #Case2: P controller to fly towards the next waypoint by flying forward
            else:
                fb = int(5*self.mag_to_waypoint)
                if abs(fb) > self.control_input_range["maxfb"]:
                    fb = int(fb / abs(fb) * self.control_input_range["maxfb"])
                elif 0 < abs(fb) < self.control_input_range["minfb"]:
                    fb = int(fb / abs(fb) * self.control_input_range["minfb"])

            #print("\n ----------------")
            #print("next_waypoint: "+str(self.waypoints[self.waypoint_index])+ "index: "+str(self.waypoint_index))
            #print("position: "+str(self.position))
            #print("self.mag_to_waypoint:" + str(self.mag_to_waypoint))
            #print("yaw_setpoint: "+ str(yaw_setpoint))
            #print("yaw_error: "+str(yaw_error))
            #print("----------------\n")
        # Detecting if waypoint is reached
        if self.mag_to_waypoint < 2:
            self.waypoint_index = self.waypoint_index + 1
            if self.waypoint_index > len(self.waypoints)-1:  # Stay at last waypoint if it is reached
                self.waypoint_index = self.waypoint_index - 1
                lr, fb, ud, yv = 0, 0, 0, 0
        rc_control = lr, fb, ud, yv
        #print("rc_control"+ str(rc_control))
        return rc_control

    def calculate_waypoints(self, search_area_width=10, search_area_depth=10):
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
        #transforming the relative waypoints into absolute waypoints. position is used as coordination system
        self.waypoint_index = 0
        self.waypoints = []
        point_zero = self.position
        yaw = math.radians(point_zero["yaw"])

        for rwp in self.relative_waypoints:
            x_new = point_zero["x"] + math.cos(yaw)*rwp["x"] + -math.sin(yaw)*rwp["y"]
            y_new = point_zero["y"] + math.sin(yaw)*rwp["x"] + math.cos(yaw)*rwp["y"]
            self.waypoints.append({"x":x_new,"y":y_new})
        #print("current position:" + str(self.position))
        #print("calculated Waypoints:"+ str(self.waypoints))


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

