import cv2
import pygame
from pygame.locals import *
import time
import numpy as np

def getKey(keyName):
    ans = False
    for eve in pygame.event.get(): pass
    keyInput = pygame.key.get_pressed()
    myKey = getattr(pygame, 'K_{}' .format(keyName))
    if keyInput[myKey]:
        ans = True
    pygame.display.update()
    return ans

img = cv2.imread("123.png")
# Initialize Pygame
pygame.init()

# Set up the Pygame window
window_width = 640
window_height = 480
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Pygame Window")

# Button setup
button_width = 100
button_height = 50
button_padding = 20

# Button 1
button1_x = (window_width - (button_width + button_padding) * 2) // 2
button1_y = window_height - button_height - button_padding
button1_rect = pygame.Rect(button1_x, button1_y, button_width, button_height)
button1_caption = "Button 1"

# Button 2
button2_x = button1_x + button_width + button_padding
button2_y = button1_y
button2_rect = pygame.Rect(button2_x, button2_y, button_width, button_height)
button2_caption = "Button 2"

# Run the main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if button1_rect.collidepoint(mouse_pos):
                menu = "1"
            elif button2_rect.collidepoint(mouse_pos):
                menu = "2"

    # Convert the frame from BGR to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Convert the frame to a Pygame surface
    frame_surface = pygame.surfarray.make_surface(img_rgb)

    # Scale the frame surface to fit the window size
    frame_surface = pygame.transform.scale(frame_surface, (window_width, window_height))

    # Blit the frame surface onto the Pygame window
    window.blit(frame_surface, (0, 0))

    # Draw the buttons
    pygame.draw.rect(window, (150, 150, 150), button1_rect)
    pygame.draw.rect(window, (150, 150, 150), button2_rect)

    # Render the button captions
    font = pygame.font.Font(None, 24)  # You can adjust the font size here
    button1_text = font.render(button1_caption, True, (255, 255, 255))
    button2_text = font.render(button2_caption, True, (255, 255, 255))

    # Center the button captions
    button1_text_rect = button1_text.get_rect(center=button1_rect.center)
    button2_text_rect = button2_text.get_rect(center=button2_rect.center)

    # Blit the button captions onto the buttons
    window.blit(button1_text, button1_text_rect)
    window.blit(button2_text, button2_text_rect)

    # Update the display

    pygame.display.update()
    if getKey("LEFT"):
        print("LEFT")
    if getKey("RIGHT"):
        print("RIGHT")
# Release the camera and quit Pygame
pygame.quit()
