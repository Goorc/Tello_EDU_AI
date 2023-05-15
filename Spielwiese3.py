import pygame
from pygame.locals import *

class GUI:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Set up the Pygame window
        self.window_width = 640
        self.window_height = 480
        self.window = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Pygame Window")

        # Font setup
        self.font = pygame.font.Font(None, 24)  # Adjust the font properties as needed

        # Text field setup
        self.text_field_rect = pygame.Rect(50, 50, 200, 30)
        self.text_field_text = ""

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_BACKSPACE:
                        self.text_field_text = self.text_field_text[:-1]
                    else:
                        self.text_field_text += event.unicode

            self.window.fill((255, 255, 255))  # Fill the window with white color

            # Render the text field
            pygame.draw.rect(self.window, (200, 200, 200), self.text_field_rect)
            text_surface = self.font.render(self.text_field_text, True, (0, 0, 0))
            self.window.blit(text_surface, (self.text_field_rect.x + 5, self.text_field_rect.y + 5))

        pygame.display.update()

        pygame.quit()

# Create an instance of the GUI class and run the program
gui = GUI()
gui.run()