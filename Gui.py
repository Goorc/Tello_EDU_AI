import cv2
import numpy as np
import pygame
from pygame.locals import *


class GuiObject:
    """
        The GuiObject class provides functionality for creating and managing a Pygame-based graphical user interface (GUI). It handles user inputs, such as button clicks and keyboard events, and displays information on the OSD.

        :param self.flight_mode: The current flight mode (default: "Manual").
        :param self.prev_flight_mode: The flight_mode in the previous call of self.draw().
    """
    def __init__(self) -> None:
        """
        Initializes the GuiObject instance and sets up the Pygame window and GUI elements.
        """
        self.flight_mode = "Manual"
        self.prev_flight_mode = ""
        # Initialize Pygame
        pygame.init()

        # Initialize video feed size
        self.image_width = 640
        self.image_height = 480

        # Set up the Pygame window
        self.window_width = 1280
        self.window_height = 720
        self.window = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Tello_EDU_AI GUI")

        # Button setup
        self.button_width = 100
        self.button_height = 50
        self.button_padding = 20

        # Button 1
        self.button1_x = (self.window_width - (self.button_width + self.button_padding) * 2) // 2
        self.button1_y = self.window_height - self.button_height - self.button_padding
        self.button1_rect = pygame.Rect(self.button1_x, self.button1_y, self.button_width, self.button_height)
        self.button1_caption = "Manual"

        # Button 2
        self.button2_x = self.button1_x + self.button_width + self.button_padding
        self.button2_y = self.button1_y
        self.button2_rect = pygame.Rect(self.button2_x, self.button2_y, self.button_width, self.button_height)
        self.button2_caption = "Auto"

        # Font setup
        self.font = pygame.font.SysFont("consolas", 24)  # Adjust the font properties as needed

        # Text field setup
        self.text_field_pos_rect = pygame.Rect(self.image_width+50, 15, 500, 30)
        self.text_field_pos_text = ""
        self.text_field_posx_rect = pygame.Rect(self.image_width+50, 45, 500, 30)
        self.text_field_posx_text = ""
        self.text_field_posy_rect = pygame.Rect(self.image_width+200, 45, 0, 30)
        self.text_field_posy_text = ""
        self.text_field_posz_rect = pygame.Rect(self.image_width+350, 45, 0, 30)
        self.text_field_posz_text = ""

        self.text_field_bat_rect = pygame.Rect(self.image_width+50, 100, 180, 30)
        self.text_field_bat_text = ""

        self.text_field_status_rect = pygame.Rect(50, self.window_height-120, 700, 30)
        self.text_field_status_text = ""

        # Text input setup
        self.text_input_position = {"x": self.image_width+50, "y": 155, "padding": 50}
        self.search_area_name = self.font.render("Search Area", True, (0, 0, 0))
        self.depth_name = self.font.render("Depth:", True, (0, 0, 0))
        self.width_name = self.font.render("Width:", True, (0, 0, 0))
        self.depth_rect = pygame.Rect(self.text_input_position["x"]+110,
                                      self.text_input_position["y"]+1*self.text_input_position["padding"], 200, 40)
        self.width_rect = pygame.Rect(self.text_input_position["x"]+110,
                                       self.text_input_position["y"]+2*self.text_input_position["padding"], 200, 40)
        self.depth_text = "10"  # Default depth value
        self.width_text = "10"  # Default width value
        self.selected_input = None
        #Waypoint information
        self.waypoint_information_rect = pygame.Rect(self.text_input_position["x"], self.text_input_position["y"], 0, 30)
        self.waypoint_information_text = "Next Waypoint:"
        self.waypoint_index_rect = pygame.Rect(self.text_input_position["x"], self.text_input_position["y"]+50, 0, 30)
        self.waypoint_index_text = ""
        self.waypoint_x_rect = pygame.Rect(self.text_input_position["x"], self.text_input_position["y"]+80, 0, 30)
        self.waypoint_x_text = ""
        self.waypoint_y_rect = pygame.Rect(self.text_input_position["x"]+150, self.text_input_position["y"]+80, 0, 30)
        self.waypoint_y_text = ""
        self.waypoint_mag_rect = pygame.Rect(self.text_input_position["x"], self.text_input_position["y"]+110, 0, 30)
        self.waypoint_mag_text = ""

    def getKeyboardInput(self) -> str:
        """
        Retrieves the currently pressed keys from the keyboard.

        :return: String which indicate the relevant keys pressed
        """
        keys_pressed = []
        if self.getKey("LEFT"):
            keys_pressed.append("LEFT")
        if self.getKey("RIGHT"):
            keys_pressed.append("RIGHT")
        if self.getKey("DOWN"):
            keys_pressed.append("DOWN")
        if self.getKey("UP"):
            keys_pressed.append("UP")
        if self.getKey("w"):
            keys_pressed.append("w")
        if self.getKey("s"):
            keys_pressed.append("s")
        if self.getKey("a"):
            keys_pressed.append("a")
        if self.getKey("d"):
            keys_pressed.append("d")
        if self.getKey("l"):
            keys_pressed.append("l")
        if self.getKey("h"):
            keys_pressed.append("h")
        if self.getKey("SPACE"):
            keys_pressed.append("SPACE")
        return keys_pressed
    def getKey(self,keyName:str) -> str:
        """
        Returns a Boolean indicating whether a specific key is currently pressed.
        :param keyName: Name of specific key
        :return: True if key is pressed
        """
        ans = False
        for eve in pygame.event.get(): pass
        keyInput = pygame.key.get_pressed()
        myKey = getattr(pygame, 'K_{}'.format(keyName))
        if keyInput[myKey]:
            ans = True
        pygame.display.update()
        return ans

    def get_search_area_size(self) -> dict:
        """
        Returns the dimensions of the search area as a dictionary.
        :return: dimensions of the search area as a dictionary
        """
        return {"width": self.width_text, "depth": self.depth_text}

    def draw(self, img: np.ndarray, data_for_osd:dict) -> None:
        """
        Draws the GUI on the Pygame window based on the provided image and OSD data.

        :param img: Image of the video feed to be implemented into the gui
        :param data_for_osd: Dictionary containing the data for the on screen display of relevant mission parameters
        """
        self.prev_flight_mode = self.flight_mode
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    if self.selected_input == "width":
                        self.width_text = self.width_text[:-1]
                    else:
                        self.depth_text = self.depth_text[:-1]
                elif event.key <= 127:  # Ignore non-ASCII characters
                    char = chr(event.key)
                    if char.isdigit():
                        if self.selected_input == "width":
                            self.width_text += char
                        else:
                            self.depth_text += char
            elif event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.button1_rect.collidepoint(mouse_pos):
                    self.flight_mode = "Manual"
                elif self.button2_rect.collidepoint(mouse_pos):
                    self.flight_mode = "Auto"
                elif self.depth_rect.collidepoint(mouse_pos):
                    self.selected_input = "depth"
                elif self.width_rect.collidepoint(mouse_pos):
                    self.selected_input = "width"
            elif self.prev_flight_mode == "Manual" and self.flight_mode == "Auto":
                # save input values if fligth_mode switches to Auto
                if self.depth_text == "":
                    self.depth_text = "10"
                if self.width_text == "":
                    self.width_text = "10"
                print("Depth:", self.depth_text)  # Replace with your desired logic
                print("Width:", self.width_text)  # Replace with your desired logic
                self.selected_input = None
        # Gray background for the window
        self.window.fill((220, 220, 220))

        # drawing tracking point on img
        if "person_cords" in data_for_osd:
            if data_for_osd["person_cords"] is not None:
                midpoint = (data_for_osd["person_cords"]["x"], data_for_osd["person_cords"]["y"])
                cv2.circle(img, midpoint, 10, (0 , 0, 150), 2)

        # Transpose and flip the image to correct the rotation
        img = cv2.transpose(img)
        img = cv2.resize(img, (self.image_height, self.image_width))

        # Convert the frame from BGR to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Convert the frame to a Pygame surface
        frame_surface = pygame.surfarray.make_surface(img_rgb)

        # Blit the frame surface onto the Pygame window
        self.window.blit(frame_surface, (0, 0))

        # Draw the buttons
        color_active = (0,150,0)
        color_inactive = (150, 150, 150)
        if "Manual" in self.flight_mode:
            pygame.draw.rect(self.window, color_active, self.button1_rect)
            pygame.draw.rect(self.window, color_inactive, self.button2_rect)

        elif "Auto" in self.flight_mode:
            pygame.draw.rect(self.window, color_inactive, self.button1_rect)
            pygame.draw.rect(self.window, color_active, self.button2_rect)

        # Render the button captions
        font = pygame.font.SysFont("consolas", 20)  # You can adjust the font size here
        button1_text = font.render(self.button1_caption, True, (255, 255, 255))
        button2_text = font.render(self.button2_caption, True, (255, 255, 255))

        # Center the button captions
        button1_text_rect = button1_text.get_rect(center=self.button1_rect.center)
        button2_text_rect = button2_text.get_rect(center=self.button2_rect.center)

        # Blit the button captions onto the buttons
        self.window.blit(button1_text, button1_text_rect)
        self.window.blit(button2_text, button2_text_rect)

        # Render the text fields
        # Battery
        pygame.draw.rect(self.window, (192, 192, 192), self.text_field_bat_rect)
        bat_color = (0, 150, 0)
        if data_for_osd["current_state"]["bat"] < 30:
            bat_color = (150,0,0)
        text_surface_bat = self.font.render("Battery: " + str(data_for_osd["current_state"]["bat"]) + "%", True, bat_color)
        self.window.blit(text_surface_bat, (self.text_field_bat_rect.x + 5, self.text_field_bat_rect.y + 5))
        # Position
        if "position" in data_for_osd:
            pos_x = str(round(data_for_osd["position"]["x"], 1))
            pos_y = str(round(data_for_osd["position"]["y"], 1))
            pos_z = str(round(data_for_osd["position"]["z"], 1))
        else:
            pos_x = "Na"
            pos_y = "Na"
            pos_z = "Na"
        pygame.draw.rect(self.window, (192, 192, 192), self.text_field_pos_rect)
        pygame.draw.rect(self.window, (192, 192, 192), self.text_field_posx_rect)
        pos_color = (0, 0, 0)
        text_surface_pos = self.font.render("Position:", True, pos_color)
        text_surface_posx = self.font.render("X: " + pos_x, True, pos_color)
        text_surface_posy = self.font.render("Y: " + pos_y, True, pos_color)
        text_surface_posz = self.font.render("Z: " + pos_z, True, pos_color)
        self.window.blit(text_surface_pos, (self.text_field_pos_rect.x + 5, self.text_field_pos_rect.y + 5))
        self.window.blit(text_surface_posx, (self.text_field_posx_rect.x + 5, self.text_field_posx_rect.y + 5))
        self.window.blit(text_surface_posy, (self.text_field_posy_rect.x + 5, self.text_field_posy_rect.y + 5))
        self.window.blit(text_surface_posz, (self.text_field_posz_rect.x + 5, self.text_field_posz_rect.y + 5))
        # Status
        status_color = (0, 0, 0)
        if self.flight_mode == "Manual":
            status_msg = "Switch to Auto to search area in front of drone"
        elif self.flight_mode == "Auto" and not "SPACE" in data_for_osd["keys_pressed"]:
            status_msg = "Hold SPACE to search Area"
        elif self.flight_mode == "Auto" and "SPACE" in data_for_osd["keys_pressed"] and data_for_osd["person_cords"] is None:
            number_of_waypoints = len(data_for_osd["waypoints"])
            status_msg = "Searching"
        elif self.flight_mode == "Auto" and "SPACE" in data_for_osd["keys_pressed"] and data_for_osd["person_cords"] is not None:
            status_msg = "Person found"
            status_color = (150, 0, 0)
        else:
            status_msg = "Unexpected Status"
        pygame.draw.rect(self.window, (192, 192, 192), self.text_field_status_rect)
        text_surface_status = self.font.render(status_msg, True, status_color)
        self.window.blit(text_surface_status, (self.text_field_status_rect.x + 5, self.text_field_status_rect.y + 5))

        # Render the input Box background
        pygame.draw.rect(self.window, (192, 192, 192),
                         pygame.Rect(self.text_input_position["x"], self.text_input_position["y"], 500, 160))
        if self.flight_mode == "Manual":
            # Render the input names
            self.window.blit(self.search_area_name, (self.text_input_position["x"]+5, self.text_input_position["y"]+5))
            self.window.blit(self.depth_name, (self.text_input_position["x"]+5, self.text_input_position["y"]+1*self.text_input_position["padding"]))
            self.window.blit(self.width_name, (self.text_input_position["x"]+5, self.text_input_position["y"]+2*self.text_input_position["padding"]))

            # Draw the input boxes
            pygame.draw.rect(self.window, (255, 255, 255), self.depth_rect)
            pygame.draw.rect(self.window, (255, 255, 255), self.width_rect)

            # Render the input text
            depth_box = self.font.render(self.depth_text, True, (0, 0, 0))
            width_box = self.font.render(self.width_text, True, (0, 0, 0))
            self.window.blit(depth_box, (self.depth_rect.x + 5, self.depth_rect.y + 5))
            self.window.blit(width_box, (self.width_rect.x + 5, self.width_rect.y + 5))

            # Highlight the selected input box
            if self.selected_input == "depth":
                pygame.draw.rect(self.window, (0, 0, 255), self.depth_rect, 2)
            elif self.selected_input == "width":
                pygame.draw.rect(self.window, (0, 0, 255), self.width_rect, 2)
        elif data_for_osd["waypoints"]:
            # Render the Waypoint information text
            text_surface_waypoint_information = self.font.render(self.waypoint_information_text, True, (0,0,0))
            self.window.blit(text_surface_waypoint_information,
                             (self.waypoint_information_rect.x + 5, self.waypoint_information_rect.y + 5))
            n_waypoints = len(data_for_osd["waypoints"])
            self.waypoint_index_text = "Index: " + str(data_for_osd["waypoint_index"]+1) + " of " + str(n_waypoints)
            text_surface_waypoint_index = self.font.render(self.waypoint_index_text, True, (0,0,0))
            self.window.blit(text_surface_waypoint_index,
                             (self.waypoint_index_rect.x + 5, self.waypoint_index_rect.y + 5))
            self.waypoint_x_text = "X: " + str(round(data_for_osd["waypoints"][data_for_osd["waypoint_index"]]["x"],1))
            text_surface_waypoint_x = self.font.render(self.waypoint_x_text, True, (0,0,0))
            self.window.blit(text_surface_waypoint_x,
                             (self.waypoint_x_rect.x + 5, self.waypoint_x_rect.y + 5))
            self.waypoint_y_text = "Y: " + str(round(data_for_osd["waypoints"][data_for_osd["waypoint_index"]]["y"],1))
            text_surface_waypoint_y = self.font.render(self.waypoint_y_text, True, (0,0,0))
            self.window.blit(text_surface_waypoint_y,
                             (self.waypoint_y_rect.x + 5, self.waypoint_y_rect.y + 5))
            self.waypoint_mag_text = "Distance: " + str(round(data_for_osd["mag_to_waypoint"],1))
            text_surface_waypoint_mag = self.font.render(self.waypoint_mag_text, True, (0,0,0))
            self.window.blit(text_surface_waypoint_mag,
                             (self.waypoint_mag_rect.x + 5, self.waypoint_mag_rect.y + 5))

        # Update the display
        pygame.display.update()