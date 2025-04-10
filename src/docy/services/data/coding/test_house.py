import pygame

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 800, 600
BACKGROUND_COLOR = (50, 50, 50)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the screen with a color
    screen.fill(BACKGROUND_COLOR)

    # Draw a simple house
    pygame.draw.rect(screen, (255, 0, 0), (100, 100, 300, 400))  # Red rectangle for the house body
    pygame.draw.polygon(screen, (0, 255, 0), [(250, 400), (350, 350), (250, 300)], 2)  # Green triangle for the roof
    pygame.draw.circle(screen, (0, 0, 255), (275, 250), 20)  # Blue circle for the door

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
