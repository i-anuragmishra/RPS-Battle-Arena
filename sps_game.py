import pygame
import random
import sys
import os

# --------------------------------------------------------------------------------
# Game Settings
# --------------------------------------------------------------------------------
WIDTH, HEIGHT = 800, 600
FPS = 60
OBJECT_RADIUS = 15  # for bounding box collisions
SPEED_RANGE = (-3, 3)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (30, 30, 30)

# Types
ROCK = "rock"
PAPER = "paper"
SCISSORS = "scissors"

# Button settings
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 40
BUTTON_COLOR = GRAY
BUTTON_HOVER_COLOR = WHITE
BUTTON_TEXT_COLOR = BLACK

# Pygame initialization
pygame.init()
pygame.display.set_caption("Rock-Paper-Scissors - Battle Simulation")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# --------------------------------------------------------------------------------
# Load Images
# --------------------------------------------------------------------------------
rock_img = pygame.image.load(os.path.join("/Users/anuragmishra/Documents/Development/ML_Resources/RPS/rock.png")).convert_alpha()
paper_img = pygame.image.load(os.path.join("/Users/anuragmishra/Documents/Development/ML_Resources/RPS/paper.png")).convert_alpha()
scissors_img = pygame.image.load(os.path.join("/Users/anuragmishra/Documents/Development/ML_Resources/RPS/scissors.png")).convert_alpha()

rock_img = pygame.transform.scale(rock_img, (40, 40))
paper_img = pygame.transform.scale(paper_img, (40, 40))
scissors_img = pygame.transform.scale(scissors_img, (40, 40))

# --------------------------------------------------------------------------------
# Button Class
# --------------------------------------------------------------------------------
class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.SysFont(None, 32)
        self.is_hovered = False

    def draw(self, surface):
        color = BUTTON_HOVER_COLOR if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect)
        text_surface = self.font.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

# --------------------------------------------------------------------------------
# RPSObject Class
# --------------------------------------------------------------------------------
class RPSObject:
    def __init__(self, kind, x, y, vx, vy):
        self.kind = kind
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.images = {
            ROCK: rock_img,
            PAPER: paper_img,
            SCISSORS: scissors_img
        }
        self.current_image = self.images[self.kind]

    def update(self):
        self.x += self.vx
        self.y += self.vy

        if self.x - OBJECT_RADIUS < 0:
            self.x = OBJECT_RADIUS
            self.vx = -self.vx
        elif self.x + OBJECT_RADIUS > WIDTH:
            self.x = WIDTH - OBJECT_RADIUS
            self.vx = -self.vx

        if self.y - OBJECT_RADIUS < 0:
            self.y = OBJECT_RADIUS
            self.vy = -self.vy
        elif self.y + OBJECT_RADIUS > HEIGHT:
            self.y = HEIGHT - OBJECT_RADIUS
            self.vy = -self.vy

    def draw(self, surface):
        rect = self.current_image.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(self.current_image, rect)

    def get_rect(self):
        return pygame.Rect(
            self.x - OBJECT_RADIUS,
            self.y - OBJECT_RADIUS,
            OBJECT_RADIUS * 2,
            OBJECT_RADIUS * 2
        )

    def set_kind(self, new_kind):
        self.kind = new_kind
        self.current_image = self.images[self.kind]

# --------------------------------------------------------------------------------
# Helper Functions
# --------------------------------------------------------------------------------
def rps_result(a_kind, b_kind):
    """
    Returns which kind (a_kind or b_kind) wins between the two,
    or None if tie.
    """
    if a_kind == b_kind:
        return None  # tie

    # Rock beats Scissors
    if (a_kind == ROCK and b_kind == SCISSORS):
        return a_kind
    if (b_kind == ROCK and a_kind == SCISSORS):
        return b_kind

    # Scissors beats Paper
    if (a_kind == SCISSORS and b_kind == PAPER):
        return a_kind
    if (b_kind == SCISSORS and a_kind == PAPER):
        return b_kind

    # Paper beats Rock
    if (a_kind == PAPER and b_kind == ROCK):
        return a_kind
    if (b_kind == PAPER and a_kind == ROCK):
        return b_kind

    return None

def create_objects(num_rock=10, num_paper=10, num_scissors=10):
    """Create and return a list of RPSObject instances with objects starting at triangle vertices."""
    objects = []
    
    # Define the three vertices of the triangle
    vertices = [
        (WIDTH//4, HEIGHT//4),           # Top-left vertex
        (3*WIDTH//4, HEIGHT//4),         # Top-right vertex
        (WIDTH//2, 3*HEIGHT//4),         # Bottom vertex
    ]
    
    # Map types to vertices
    type_positions = {
        ROCK: vertices[0],
        PAPER: vertices[1],
        SCISSORS: vertices[2]
    }
    
    def create_object_at_position(kind, base_x, base_y):
        # Add some small random offset to prevent perfect overlap
        x = base_x + random.randint(-20, 20)
        y = base_y + random.randint(-20, 20)
        vx = random.randint(*SPEED_RANGE)
        vy = random.randint(*SPEED_RANGE)
        # Ensure we don't get zero velocity
        while vx == 0 and vy == 0:
            vx = random.randint(*SPEED_RANGE)
            vy = random.randint(*SPEED_RANGE)
        return RPSObject(kind, x, y, vx, vy)

    # Create objects for each type at their respective vertices
    for _ in range(num_rock):
        base_x, base_y = type_positions[ROCK]
        objects.append(create_object_at_position(ROCK, base_x, base_y))
    
    for _ in range(num_paper):
        base_x, base_y = type_positions[PAPER]
        objects.append(create_object_at_position(PAPER, base_x, base_y))
    
    for _ in range(num_scissors):
        base_x, base_y = type_positions[SCISSORS]
        objects.append(create_object_at_position(SCISSORS, base_x, base_y))

    return objects

def countdown_sequence():
    """
    Displays a 3-second countdown (3, 2, 1, Go!) on screen.
    During countdown, objects won't move.
    """
    font = pygame.font.SysFont(None, 96)
    for i in range(3, 0, -1):
        screen.fill((30, 30, 30))
        text_surface = font.render(str(i), True, (255, 255, 255))
        rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text_surface, rect)
        pygame.display.flip()
        pygame.time.delay(1000)  # 1 second

    # Display "Go!"
    screen.fill((30, 30, 30))
    text_surface = font.render("Go!", True, (255, 255, 255))
    rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text_surface, rect)
    pygame.display.flip()
    pygame.time.delay(1000)

def draw_counters(surface, objects):
    """Draw counters for each object type"""
    counts = {
        ROCK: sum(1 for obj in objects if obj.kind == ROCK),
        PAPER: sum(1 for obj in objects if obj.kind == PAPER),
        SCISSORS: sum(1 for obj in objects if obj.kind == SCISSORS)
    }
    
    font = pygame.font.SysFont(None, 32)
    y_pos = 20
    for kind, count in counts.items():
        text = f"{kind.capitalize()}: {count}"
        text_surface = font.render(text, True, WHITE)
        surface.blit(text_surface, (20, y_pos))
        y_pos += 30

def main():
    # Create replay button
    replay_button = Button(WIDTH - BUTTON_WIDTH - 20, 20, BUTTON_WIDTH, BUTTON_HEIGHT, "Replay")
    
    def start_game():
        return create_objects(10, 10, 10)

    objects = start_game()
    countdown_sequence()

    running = True
    game_over = False
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle replay button
            if game_over and replay_button.handle_event(event):
                objects = start_game()
                game_over = False
                countdown_sequence()

        if not game_over:
            # Update all objects
            for obj in objects:
                obj.update()

            # Handle collisions
            collisions_to_resolve = []
            for i in range(len(objects)):
                for j in range(i + 1, len(objects)):
                    if objects[i].get_rect().colliderect(objects[j].get_rect()):
                        collisions_to_resolve.append((i, j))

            # Sort collisions by higher index first
            collisions_to_resolve.sort(key=lambda x: x[1], reverse=True)

            for (i, j) in collisions_to_resolve:
                if i >= len(objects) or j >= len(objects):
                    continue

                winner_kind = rps_result(objects[i].kind, objects[j].kind)
                if winner_kind is None:
                    continue
                else:
                    if winner_kind == objects[i].kind:
                        objects[j].set_kind(objects[i].kind)
                    else:
                        objects[i].set_kind(objects[j].kind)

        # Clear screen
        screen.fill(DARK_GRAY)

        # Draw objects
        for obj in objects:
            obj.draw(screen)

        # Draw counters
        draw_counters(screen, objects)

        # Check if game is over
        kinds_left = set(o.kind for o in objects)
        if len(kinds_left) == 1 and not game_over:
            game_over = True
            winner_kind = kinds_left.pop()
            font = pygame.font.SysFont(None, 64)
            text_surface = font.render(f"{winner_kind.capitalize()} Wins!", True, WHITE)
            text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(text_surface, text_rect)

        # Draw replay button if game is over
        if game_over:
            replay_button.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()