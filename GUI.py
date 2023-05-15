import cv2
import pygame
from pygame.locals import *
import time
import numpy as np

class GuiObject:

    menu = ["Manual",0,0]
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Set up the Pygame window
        self.window_width = 640
        self.window_height = 480
        self.window = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Pygame Window")

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
        self.button2_caption = "Search"

        # Font setup
        self.font = pygame.font.Font(None, 24)  # Adjust the font properties as needed

        # Text field setup
        self.text_field_rect = pygame.Rect(50, 50, 200, 30)
        self.text_field_text = ""
    def getKeyboardInput(self):
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
        if self.getKey("q"):
            keys_pressed.append("q")
        if self.getKey("h"):
            keys_pressed.append("h")
        if self.getKey("SPACE"):
            keys_pressed.append("SPACE")
        if self.getKey("m"):
            keys_pressed.append("m")
        return keys_pressed
    def getKey(self,keyName):
        ans = False
        for eve in pygame.event.get(): pass
        keyInput = pygame.key.get_pressed()
        myKey = getattr(pygame, 'K_{}'.format(keyName))
        if keyInput[myKey]:
            ans = True
        pygame.display.update()
        return ans

    # Run the main game loop
    def draw(self, img, current_state):
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.button1_rect.collidepoint(mouse_pos):
                    self.menu = [1, 0, 0]
                    print(self.menu)
                elif self.button2_rect.collidepoint(mouse_pos):
                    self.menu = [2, 0, 0]
                    print(self.menu)

        # Transpose and flip the image to correct the rotation
        img = cv2.transpose(img)
        img = cv2.resize(img, (480, 640))



        # Convert the frame from BGR to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Convert the frame to a Pygame surface
        frame_surface = pygame.surfarray.make_surface(img_rgb)

        # Blit the frame surface onto the Pygame window
        self.window.blit(frame_surface, (0, 0))

        # Draw the buttons
        pygame.draw.rect(self.window, (150, 150, 150), self.button1_rect)
        pygame.draw.rect(self.window, (150, 150, 150), self.button2_rect)

        # Render the button captions
        font = pygame.font.Font(None, 24)  # You can adjust the font size here
        button1_text = font.render(self.button1_caption, True, (255, 255, 255))
        button2_text = font.render(self.button2_caption, True, (255, 255, 255))

        # Center the button captions
        button1_text_rect = button1_text.get_rect(center=self.button1_rect.center)
        button2_text_rect = button2_text.get_rect(center=self.button2_rect.center)

        # Blit the button captions onto the buttons
        self.window.blit(button1_text, button1_text_rect)
        self.window.blit(button2_text, button2_text_rect)

        # Render the text field
        pygame.draw.rect(self.window, (200, 200, 200), self.text_field_rect)
        text_surface = self.font.render(str(current_state["bat"]) + "%", True, (0, 0, 0))
        self.window.blit(text_surface, (self.text_field_rect.x + 5, self.text_field_rect.y + 5))

        # Update the display
        pygame.display.update()

    def overlay(self,img, x, y):
        # Draw a red cross at the specified coordinates
        cv2.line(img, (x - 10, y), (x + 10, y), (0, 0, 255), 2)
        cv2.line(img, (x, y - 10), (x, y + 10), (0, 0, 255), 2)


