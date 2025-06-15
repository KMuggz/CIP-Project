import os
import pygame
import sys
import random

# === Game Settings ===
# Set game window size, grid size, difficulty speeds, and scoring constants
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
SPEEDS = {'Easy': 8, 'Medium': 12, 'Hard': 18} 
"""
-> Speeds (Easy, Medium, Hard) map to frames-per-second (FPS).
-> Faster speeds = less time per frame = harder game.
"""
TARGET_SCORE = 50
DELIVERY_TIME = 8
OBSTACLES = 8  # Number of obstacles to place

# Define colors used throughout the game (RGB values)
COLORS = {
    'background': (0, 0, 0), # Black background
    'snake': (0, 200, 0), # Snake body (green)
    'head': (50, 255, 50), # Snake head (light green)
    'meal': (255, 176, 156), # 1-point meal (light red)
    '2pt_meal': (255, 255, 150), # 2-point meal (yellow)
    '3pt_meal': (204, 102, 0), # 3-point meal (orange)
    'obstacle': (0, 255, 255), # Obstacles (cyan)
    'home': (100, 100, 100), # Drop-off point (gray)
    'text': (255, 255, 255), # UI text (white)
    'pause_text': (255, 0, 0), # Pause text (red)
    'win_text': (255, 215, 0), # Win text (gold)
    'lose_text': (139, 0, 0), # Lose text (dark red)
    'timer': (255, 105, 180), # Timer bar (hot pink)
    'eye': (204, 102, 0) # Snake eyes (orange)
}

# === Initialize Pygame and set up window ===
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Hiss & Go Seek - Pygame Full Edition')
font = pygame.font.SysFont('Courier', 20)
clock = pygame.time.Clock()
music_on = True

# === Load background music (optional) ===
try: 
    pygame.mixer.music.load('snoozy beats - dreams in slow motion.mp3') # Load music file
    pygame.mixer.music.set_volume(0.5)  # Set volume to 50%
    pygame.mixer.music.play(-1)  # Play indefinitely
except:
    print("No background music found.")

high_score = 0  # Track the highest score for the loaded session

# === Utility Functions ===
def draw_text(text, x, y, color=COLORS['text']):
    """Draw a text string at (x, y) with specified color."""
    label = font.render(text, True, color)
    screen.blit(label, (x, y))

def draw_rect(color, x, y):
    """Draw a single grid-aligned rectangle block."""
    pygame.draw.rect(screen, color, (x, y, GRID_SIZE, GRID_SIZE))

def draw_eyes(x, y):
    """Draw two small eyes on the snake's head for visual appeal."""
    eye_radius = 2
    offset = 4
    pygame.draw.circle(screen, COLORS['eye'], (x + offset, y + offset), eye_radius)
    pygame.draw.circle(screen, COLORS['eye'], (x + GRID_SIZE - offset, y + offset), eye_radius)

def toggle_music():
    """Pause or resume background music."""
    global music_on
    if music_on:
        pygame.mixer.music.stop()
    else:
        try:
            pygame.mixer.music.play(-1)
        except:
            pass
    music_on = not music_on

def place_random(exclude):
    """Generate a random grid position not in the exclude list."""
    while True:
        x = random.randint(0, WIDTH // GRID_SIZE - 1)
        y = random.randint(0, HEIGHT // GRID_SIZE - 1)
        if (x, y) not in exclude:
            return (x, y)

def welcome_screen():
    """Display the start menu and handle difficulty selection."""
    selecting = True
    selected_speed = 'Medium'
    while selecting:
        screen.fill(COLORS['background'])
        draw_text('Hiss & Go Seek', 150, 80)
        draw_text('Select Difficulty:', 150, 140)
        draw_text('1 - Easy', 180, 180)
        draw_text('2 - Medium', 180, 210)
        draw_text('3 - Hard', 180, 240)
        draw_text('M - Toggle Music', 150, 280)
        pygame.display.flip() # Update the display

        # Handle keypress events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: # pressing the 1 key selects Easy
                    selected_speed = 'Easy'
                    selecting = False
                elif event.key == pygame.K_2: # pressing the 2 key selects Medium
                    selected_speed = 'Medium'
                    selecting = False
                elif event.key == pygame.K_3: # pressing the 3 key selects Hard
                    selected_speed = 'Hard'
                    selecting = False
                elif event.key == pygame.K_m: # pressing M toggles music
                    toggle_music()

    return SPEEDS[selected_speed]  # Return speed value based on selection

def run_game(speed):
    """
    Main game loop: handles logic, rendering, collision, and scoring.
    """
    global high_score # Track high score across sessions
    dx, dy = 1, 0  # Snake initial direction (right)
    snake = [(5, 5), (4, 5), (3, 5)]  # Initial snake body (3 segments: head {1}, body {2})
    home = (0, HEIGHT // GRID_SIZE - 1)  # Drop-off point in bottom-left
    obstacles = [place_random(snake + [home]) for _ in range(OBSTACLES)]  # Places a number of static obstacles as defined in OBSTACLES
    meal = place_random(snake + obstacles + [home])  # Place first meal
    meals_spawned = 1
    meal_value = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]  # Meal point value
    score = 0
    timer = 0  # Countdown to deliver
    carrying = 0  # Current meal value being carried
    game_over = False
    paused = False

    while True:
        screen.fill(COLORS['background'])  # Clear screen each frame

        # === Handle Input Events ===
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and dy == 0:
                    dx, dy = 0, -1
                elif event.key == pygame.K_DOWN and dy == 0:
                    dx, dy = 0, 1
                elif event.key == pygame.K_LEFT and dx == 0:
                    dx, dy = -1, 0
                elif event.key == pygame.K_RIGHT and dx == 0:
                    dx, dy = 1, 0
                elif event.key == pygame.K_r:
                    run_game(speed)
                elif event.key == pygame.K_m:
                    toggle_music()
                elif event.key == pygame.K_p:
                    paused = not paused

        if not game_over and not paused:
            # === Move the Snake ===
            head = ((snake[0][0] + dx) % (WIDTH // GRID_SIZE),
                    (snake[0][1] + dy) % (HEIGHT // GRID_SIZE))

            if head in obstacles:
                game_over = True

            snake.insert(0, head)
            snake.pop()

            # === Meal Pickup ===
            if head == meal:
                carrying = meal_value
                timer = DELIVERY_TIME * speed  # Start delivery countdown
                meal = (-1, -1)  # Hide the meal

            # === Delivery ===
            if carrying and head == home:
                score += carrying
                carrying = 0
                timer = 0
                if score > high_score:
                    high_score = score
                meal = place_random(snake + obstacles + [home])
                meals_spawned += 1
                # Occasionally upgrade meal value
                if meals_spawned % 10 == 0:
                    meal_value = random.choice([2, 3])
                else:
                    meal_value = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]

            # === Countdown Failure ===
            if timer > 0:
                timer -= 1
                if timer == 0 and carrying:
                    game_over = True

        # === Draw Game Elements ===
        for x, y in snake:
            draw_rect(COLORS['head'] if (x, y) == snake[0] else COLORS['snake'], x * GRID_SIZE, y * GRID_SIZE)
            if (x, y) == snake[0]:
                draw_eyes(x * GRID_SIZE, y * GRID_SIZE)

        draw_rect(COLORS['home'], home[0] * GRID_SIZE, home[1] * GRID_SIZE)
        for ox, oy in obstacles:
            draw_rect(COLORS['obstacle'], ox * GRID_SIZE, oy * GRID_SIZE)

        if meal != (-1, -1):
            # Color based on point value
            if meal_value == 2:
                color = COLORS['2pt_meal']
            elif meal_value == 3:
                color = COLORS['3pt_meal']
            else:
                color = COLORS['meal']
            draw_rect(color, meal[0] * GRID_SIZE, meal[1] * GRID_SIZE)

        # UI / HUD Elements
        draw_text(f"Score: {score}/{TARGET_SCORE}", 10, 10, COLORS['timer'])
        draw_text(f"High Score: {high_score}", 320, 10, COLORS['timer'])

        if timer > 0:
            timer_color = (255, 0, 0) if timer <= 3 * speed else COLORS['timer']
            draw_text(f"Time Left: {timer//speed}s", 10, 30, timer_color)
            """ -> shows the user how much time is left to deliver the meal
                -> timer turns red when less than 3 seconds remain, to urge the player to hurry """
            
        if paused:
            draw_text("PAUSED. Press P to resume", 130, HEIGHT // 2, COLORS['pause_text'])

        # === Game End Conditions ===
        if score >= TARGET_SCORE:
            draw_text("YOU WIN! Press R to restart", 100, HEIGHT // 2, COLORS['win_text'])
            game_over = True

        if game_over and score < TARGET_SCORE:
            draw_text("GAME OVER! Press R to restart", 90, HEIGHT // 2, COLORS['lose_text'])

        pygame.display.flip()
        clock.tick(speed)  # Limit game loop speed


def main():
    """Entry point: shows welcome screen and launches the game."""
    speed = welcome_screen()
    run_game(speed) 


if __name__ == '__main__':
    main()
