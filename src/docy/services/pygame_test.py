import pygame
import sys

# Initialize Pygame
pygame.init()

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WINDOW_TITLE = "Simple Pygame House"

# Colors (RGB tuples)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
RED = (200, 0, 0)        # Darker red for roof
DARK_BLUE = (0, 0, 139)    # Darker blue for door
YELLOW = (255, 255, 0)
SKY_BLUE = (135, 206, 235) # Background color

# House dimensions and positioning
HOUSE_X = (SCREEN_WIDTH - 300) // 2 # Center the house base horizontally
HOUSE_Y = SCREEN_HEIGHT - 350       # Position house towards bottom
HOUSE_WIDTH = 300
HOUSE_HEIGHT = 200

ROOF_HEIGHT = 100
ROOF_POINTS = [
    (HOUSE_X, HOUSE_Y),                          # Top-left of house base
    (HOUSE_X + HOUSE_WIDTH, HOUSE_Y),            # Top-right of house base
    (HOUSE_X + HOUSE_WIDTH / 2, HOUSE_Y - ROOF_HEIGHT) # Peak of the roof
]

DOOR_WIDTH = 60
DOOR_HEIGHT = 100
DOOR_X = HOUSE_X + (HOUSE_WIDTH - DOOR_WIDTH) // 2 # Center door horizontally
DOOR_Y = HOUSE_Y + HOUSE_HEIGHT - DOOR_HEIGHT      # Align door with house bottom

WINDOW_SIZE = 50
WINDOW_X = HOUSE_X + 40 # Position window left of center
WINDOW_Y = HOUSE_Y + 40 # Position window vertically
WINDOW_PANE_WIDTH = 2

# --- Setup Display ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)

# --- Main Game Loop ---
running = True
while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: # Allow quitting with ESC key
                 running = False

    # --- Drawing ---
    # Fill background
    screen.fill(SKY_BLUE)

    # Draw house body (rectangle)
    pygame.draw.rect(screen, BROWN, (HOUSE_X, HOUSE_Y, HOUSE_WIDTH, HOUSE_HEIGHT))

    # Draw roof (polygon)
    pygame.draw.polygon(screen, RED, ROOF_POINTS)

    # Draw door (rectangle)
    pygame.draw.rect(screen, DARK_BLUE, (DOOR_X, DOOR_Y, DOOR_WIDTH, DOOR_HEIGHT))

    # Draw window (rectangle)
    pygame.draw.rect(screen, YELLOW, (WINDOW_X, WINDOW_Y, WINDOW_SIZE, WINDOW_SIZE))
    # Draw window panes (lines)
    pygame.draw.line(screen, BLACK,
                     (WINDOW_X + WINDOW_SIZE / 2, WINDOW_Y),                  # Top-middle
                     (WINDOW_X + WINDOW_SIZE / 2, WINDOW_Y + WINDOW_SIZE),    # Bottom-middle
                     WINDOW_PANE_WIDTH)
    pygame.draw.line(screen, BLACK,
                     (WINDOW_X, WINDOW_Y + WINDOW_SIZE / 2),                  # Left-middle
                     (WINDOW_X + WINDOW_SIZE, WINDOW_Y + WINDOW_SIZE / 2),    # Right-middle
                     WINDOW_PANE_WIDTH)

    # --- Update Display ---
    pygame.display.flip() # Make everything drawn visible

# --- Cleanup ---
pygame.quit()
sys.exit()
