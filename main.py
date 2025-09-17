import pygame
import math
import os

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Gravity Assist Simulation")

GRAVITY_CONSTANT = 5
PLANET_RADIUS = 50
PLANET_MASS = 100
CRAFT_MASS = 5
FPS = 60
CRAFT_SIZE = 20  
VELOCITY_DIVISOR = 100

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

def load_image_safe(filename, size):
    """Safely load an image file, create a colored circle if file not found"""
    try:
        if os.path.exists(filename):
            img = pygame.image.load(filename)
            return pygame.transform.scale(img, size)
        else:
            print(f"Warning: {filename} not found, using default shape")
            return None
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None


background_img = load_image_safe("background.jpg", (SCREEN_WIDTH, SCREEN_HEIGHT))
planet_img = load_image_safe("jupiter.png", (PLANET_RADIUS * 2, PLANET_RADIUS * 2))
spaceship_img = load_image_safe("spaceship.png", (CRAFT_SIZE, CRAFT_SIZE))


class Planet:
    def __init__(self, x, y, mass):
        self.x = x
        self.y = y
        self.mass = mass
    
    def draw(self):
        if planet_img:
            screen.blit(planet_img, (self.x - PLANET_RADIUS, self.y - PLANET_RADIUS))
        else:
            # Draw default planet if image not found
            pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), PLANET_RADIUS)
            pygame.draw.circle(screen, WHITE, (int(self.x - 15), int(self.y - 15)), 10)

# Spacecraft class
class Spacecraft:
    def __init__(self, x, y, vx, vy, mass):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.mass = mass
        self.angle = 0  # Track rotation angle for the spaceship
        self.trail = []  # Trail of previous positions with speed data
        self.max_trail_length = 50  # Increased for better trail effect
        self.speed_history = []  # Track speed for each trail point
    
    def update(self, planet):
        dx = planet.x - self.x
        dy = planet.y - self.y
        distance = math.hypot(dx, dy)
        
        # Newton's law of gravity
        if distance > 0:
            force = (GRAVITY_CONSTANT * self.mass * planet.mass) / (distance ** 2)
            angle = math.atan2(dy, dx)
            ax = (force / self.mass) * math.cos(angle)
            ay = (force / self.mass) * math.sin(angle)
            
            self.vx += ax
            self.vy += ay
        
        # Calculate current speed
        current_speed = math.hypot(self.vx, self.vy)
        
        # Add current position and speed to trail
        self.trail.append((int(self.x), int(self.y)))
        self.speed_history.append(current_speed)
        
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
            self.speed_history.pop(0)
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Calculate rotation angle based on velocity direction
        # Add 90 degrees to make the front of the spaceship point forward
        if self.vx != 0 or self.vy != 0:
            self.angle = math.degrees(math.atan2(self.vy, self.vx)) + 90
    
    def get_speed_color(self, speed, alpha_factor):
        """Generate color based on speed with alpha blending - 3 color gradient"""
        # Normalize speed (assuming max interesting speed is around 15)
        normalized_speed = min(speed / 15.0, 1.0)
        
        if normalized_speed < 0.5:
            # Violet to Cyan
            progress = normalized_speed / 0.5
            r = int((138 + (0 - 138) * progress) * alpha_factor)
            g = int((43 + (255 - 43) * progress) * alpha_factor)
            b = int((226 + (255 - 226) * progress) * alpha_factor)
        else:
            # Cyan to Red
            progress = (normalized_speed - 0.5) / 0.5
            r = int((0 + (255 - 0) * progress) * alpha_factor)
            g = int((255 + (100 - 255) * progress) * alpha_factor)
            b = int((255 + (0 - 255) * progress) * alpha_factor)
        
        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
    
    def draw(self):
        # Draw enhanced speed-based trail
        if len(self.trail) > 1:
            for i in range(1, len(self.trail)):
                # Calculate alpha based on position in trail (newer = more opaque)
                alpha_factor = i / len(self.trail)
                
                # Get speed at this point
                speed = self.speed_history[i-1] if i-1 < len(self.speed_history) else 0
                
                # Get color based on speed
                trail_color = self.get_speed_color(speed, alpha_factor)
                
                # Calculate line thickness based on speed (faster = thicker trail)
                thickness = max(1, int(2 + (speed / 5.0) * 3))
                
                # Draw trail segment
                if i < len(self.trail):
                    pygame.draw.line(screen, trail_color, self.trail[i-1], self.trail[i], thickness)
                    
                    # Add glow effect for high speeds
                    if speed > 5:
                        glow_color = (trail_color[0] // 3, trail_color[1] // 3, trail_color[2] // 3)
                        pygame.draw.line(screen, glow_color, self.trail[i-1], self.trail[i], thickness + 2)
        
        # Draw speed-based particles at the current position
        current_speed = math.hypot(self.vx, self.vy)
        if current_speed > 3:  # Only show particles when moving fast
            # Create particle effect behind the spacecraft
            particle_color = self.get_speed_color(current_speed, 0.8)
            
            # Calculate opposite direction of movement for particle placement
            if current_speed > 0:
                particle_angle = math.atan2(self.vy, self.vx) + math.pi  # Opposite direction
                
                # Create multiple particles
                for i in range(3):
                    offset_distance = 10 + i * 5
                    particle_x = self.x + math.cos(particle_angle) * offset_distance
                    particle_y = self.y + math.sin(particle_angle) * offset_distance
                    
                    # Add some randomness to particle position
                    particle_x += (i - 1) * 3
                    particle_y += (i - 1) * 3
                    
                    particle_size = max(1, int(3 - i))
                    pygame.draw.circle(screen, particle_color, 
                                     (int(particle_x), int(particle_y)), particle_size)
        
        # Draw the spacecraft
        if spaceship_img:
            # Rotate the spaceship image based on velocity direction
            rotated_spaceship = pygame.transform.rotate(spaceship_img, -self.angle)
            rotated_rect = rotated_spaceship.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated_spaceship, rotated_rect)
        else:
            # Draw default spaceship shape if image not found
            # Draw as triangle pointing in direction of movement
            points = []
            # Adjust angle for proper forward direction
            angle_rad = math.radians(self.angle - 90)  # Subtract 90 to point forward
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            
            # Triangle points relative to center (nose pointing up)
            relative_points = [(0, -10), (-6, 8), (6, 8)]
            
            for px, py in relative_points:
                # Rotate point
                rx = px * cos_a - py * sin_a
                ry = px * sin_a + py * cos_a
                points.append((int(self.x + rx), int(self.y + ry)))
            
            pygame.draw.polygon(screen, RED, points)
            pygame.draw.polygon(screen, WHITE, points, 2)
        
        # Draw speed indicator with realistic values
        current_speed = math.hypot(self.vx, self.vy)
        # Convert to km/s (realistic spacecraft speeds)
        realistic_speed = current_speed * 2.5  # Scale factor for realistic speeds
        speed_color = self.get_speed_color(current_speed, 1.0)
        speed_text = f"{realistic_speed:.1f} km/s"
        font = pygame.font.Font(None, 18)
        speed_surface = font.render(speed_text, True, speed_color)
        screen.blit(speed_surface, (int(self.x - 25), int(self.y - 25)))

# Create spacecraft from two mouse points
def launch_craft(start_pos, end_pos):
    sx, sy = start_pos
    ex, ey = end_pos
    vx = (ex - sx) / VELOCITY_DIVISOR
    vy = (ey - sy) / VELOCITY_DIVISOR
    return Spacecraft(sx, sy, vx, vy, CRAFT_MASS)

# Draw background
def draw_background():
    if background_img:
        screen.blit(background_img, (0, 0))
    else:
        # Draw gradient background if image not found
        for y in range(SCREEN_HEIGHT):
            color_ratio = y / SCREEN_HEIGHT
            color = (int(10 * color_ratio), int(20 * color_ratio), int(50 + 100 * color_ratio))
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # Draw stars
        for i in range(50):
            x = (i * 37) % SCREEN_WIDTH
            y = (i * 67) % SCREEN_HEIGHT
            pygame.draw.circle(screen, WHITE, (x, y), 1)

# Main simulation loop
def run_simulation():
    clock = pygame.time.Clock()
    planet = Planet(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, PLANET_MASS)
    crafts = []
    launch_start = None
    running = True
    
    print("Enhanced Gravity Assist Simulation Started!")
    print("Controls:")
    print("- Click and drag to launch spacecraft")
    print("- ESC or close window to quit")
    print("- R to reset simulation")
    print("- Trail colors: Violet (slow) -> Cyan (medium) -> Yellow/Red (fast)")
    print("- Speed shown in realistic km/s values")
    
    while running:
        clock.tick(FPS)
        mouse = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    crafts.clear()
                    print("Simulation reset!")
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if launch_start:
                    crafts.append(launch_craft(launch_start, mouse))
                    print(f"Spacecraft launched! Total: {len(crafts)}")
                    launch_start = None
                else:
                    launch_start = mouse
        
        # Draw everything
        draw_background()
        
        # Draw launch preview
        if launch_start:
            pygame.draw.line(screen, WHITE, launch_start, mouse, 2)
            # Draw spaceship preview at launch position
            if spaceship_img:
                preview_rect = spaceship_img.get_rect(center=launch_start)
                screen.blit(spaceship_img, preview_rect)
            else:
                pygame.draw.circle(screen, RED, launch_start, 8)
        
        # Update and draw spacecraft
        for craft in crafts[:]:
            craft.draw()
            craft.update(planet)
            
            # Remove off-screen or collided objects
            out_of_bounds = not (-50 <= craft.x <= SCREEN_WIDTH + 50 and 
                               -50 <= craft.y <= SCREEN_HEIGHT + 50)
            hit_planet = math.hypot(craft.x - planet.x, craft.y - planet.y) <= PLANET_RADIUS + CRAFT_SIZE//2
            
            if out_of_bounds or hit_planet:
                crafts.remove(craft)
        
        # Draw planet
        planet.draw()
        
        # Draw UI info
        font = pygame.font.Font(None, 24)
        text = font.render(f"Spacecraft: {len(crafts)} | Press R to reset | ESC to quit", True, WHITE)
        screen.blit(text, (10, 10))
        

        
        pygame.display.update()
    
    pygame.quit()
    print("Simulation ended!")

if __name__ == "__main__":
    run_simulation()