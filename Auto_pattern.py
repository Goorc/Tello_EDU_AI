import time
class Auto_search:

    start_time = 0
    relative_position = {}
    previous_state = {}
    search_area = {}
    search_speed = 20
    grid_distance = 10

    def __init__(self, current_state, search_area_width, search_area_depth):
        self.previous_state = current_state
        self.relative_position = {"x": 0, "y": 0, "z": 0, "time": time.time()}
        self.start_time = time.time()
        self.search_area = {"width": search_area_width, "depth": search_area_depth}

    def update_relative_position(self, current_state):
        print(self.relative_position)
        current_time = time.time()
        delta_t = current_time - self.relative_position["time"]
        print(delta_t)
        new_relative_position = { "x": self.relative_position["x"] + (current_state["vgx"] + self.previous_state["vgx"]) / 2 * delta_t,
                                  "y": self.relative_position["y"] + (current_state["vgy"] + self.previous_state["vgy"]) / 2 * delta_t,
                                  "z": self.relative_position["z"] + (current_state["vgz"] + self.previous_state["vgz"]) / 2 * delta_t,
                                  "time": current_time
                                  }
        self.previous_state = current_state
        self.relative_position = new_relative_position

    def Auto_search(self, current_state):
        lr, fb, ud, yv = 0, 0, 0, 0
        self.update_relative_position(current_state)

