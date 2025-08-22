import pygame
import random
import sys
import math

# --- Initialization ---
# This line is required to start up the pygame module.
pygame.init()

# --- Game Constants ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
FPS = 60  # Frames per second, controls the game speed.

# Define colors using RGB tuples.
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
LIGHT_BLUE = (173, 216, 230)  # Color for the phasing walls
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)  # Color for the gun
GREEN = (0, 255, 0)  # For the health bar
UI_TEXT_COLOR = (50, 50, 50)  # Dark gray for UI text

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Circle Game")

# Set up the clock to control the frame rate
clock = pygame.time.Clock()

# Weapon properties
WEAPONS = {
    'pistol': {
        'max_ammo': 10,
        'cooldown_ms': 500,
        'reload_time_ms': 3000,
        'pellets': 1,
        'spread_angle': 0,  # No spread for pistol
        'base_damage': 20
    },
    'shotgun': {
        'max_ammo': 2,
        'cooldown_ms': 1500,
        'reload_time_ms': 5000,
        'pellets': 6,
        'spread_angle': 20,  # 20 degrees spread
        'base_damage': 15
    }
}

# --- Player, AI, and Bullet Classes ---
class Player:
    """
    Represents the player-controlled circle.
    """
    def __init__(self, x, y, radius, color, speed):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed = speed
        self.direction = (0, -1)  # Initial direction is up
        
        # Gun properties
        self.gun_size = (40, 10)
        self.gun_surface = pygame.Surface(self.gun_size, pygame.SRCALPHA)
        pygame.draw.rect(self.gun_surface, GRAY, (0, 0, self.gun_size[0], self.gun_size[1]))

    def draw(self, surface, mouse_pos):
        """
        Draws the player circle, the direction arrow, and the aiming gun on the screen.
        """
        # Draw the main player circle
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        
        # --- Draw the direction arrow ---
        center = (int(self.x), int(self.y))
        end_x = center[0] + self.direction[0] * self.radius
        end_y = center[1] + self.direction[1] * self.radius
        
        pygame.draw.line(surface, BLACK, center, (end_x, end_y), 3)

        arrow_size = 10
        direction_angle_rad = math.atan2(self.direction[1], self.direction[0])
        
        p1_x = end_x + math.cos(direction_angle_rad + 3 * math.pi / 4) * arrow_size
        p1_y = end_y + math.sin(direction_angle_rad + 3 * math.pi / 4) * arrow_size
        
        p2_x = end_x + math.cos(direction_angle_rad - 3 * math.pi / 4) * arrow_size
        p2_y = end_y + math.sin(direction_angle_rad - 3 * math.pi / 4) * arrow_size
        
        points = [(end_x, end_y), (p1_x, p1_y), (p2_x, p2_y)]
        
        pygame.draw.polygon(surface, BLACK, points)

        # --- Draw and rotate the aiming gun with a 180-degree limit ---
        delta_x_mouse = mouse_pos[0] - self.x
        delta_y_mouse = mouse_pos[1] - self.y
        mouse_angle_rad = math.atan2(delta_y_mouse, delta_x_mouse)
        player_angle_rad = math.atan2(self.direction[1], self.direction[0])
        angle_diff_rad = mouse_angle_rad - player_angle_rad

        while angle_diff_rad > math.pi:
            angle_diff_rad -= 2 * math.pi
        while angle_diff_rad < -math.pi:
            angle_diff_rad += 2 * math.pi

        clamped_diff_rad = max(-math.pi / 2, min(math.pi / 2, angle_diff_rad))
        final_angle_rad = player_angle_rad + clamped_diff_rad
        angle_deg = -math.degrees(final_angle_rad)

        rotated_gun = pygame.transform.rotate(self.gun_surface, angle_deg)
        
        center = (int(self.x), int(self.y))
        gun_rect = rotated_gun.get_rect(center=center)
        offset_dist = self.radius + 20
        gun_rect.centerx = center[0] + math.cos(final_angle_rad) * offset_dist
        gun_rect.centery = center[1] + math.sin(final_angle_rad) * offset_dist
        
        surface.blit(rotated_gun, gun_rect)

    def move(self, keys, walls):
        """
        Handles movement based on keyboard input, checking for diagonal movement.
        Also updates the player's direction vector.
        """
        dx, dy = 0, 0
        
        if keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_s]:
            dy = 1
        if keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_d]:
            dx = 1
            
        if dx != 0 or dy != 0:
            magnitude = math.sqrt(dx**2 + dy**2)
            normalized_dx = dx / magnitude
            normalized_dy = dy / magnitude
            
            new_x = self.x + normalized_dx * self.speed
            new_y = self.y + normalized_dy * self.speed
            
            temp_rect = pygame.Rect(new_x - self.radius, new_y - self.radius, self.radius * 2, self.radius * 2)

            collision = False
            for wall in walls:
                if wall['phase_timer'] == 0:
                    if temp_rect.colliderect(wall['rect']):
                        collision = True
                        break
            
            if not collision:
                self.x = new_x
                self.y = new_y
                self.direction = (normalized_dx, normalized_dy)

        self.clamp()

    def clamp(self):
        """Clamps the player's position to stay within the screen."""
        if self.x < self.radius:
            self.x = self.radius
        if self.x > SCREEN_WIDTH - self.radius:
            self.x = SCREEN_WIDTH - self.radius
        if self.y < self.radius:
            self.y = self.radius
        if self.y > SCREEN_HEIGHT - self.radius:
            self.y = SCREEN_HEIGHT - self.radius

class AI:
    """
    Represents the AI-controlled circle with health, timed movement, and stopping.
    """
    def __init__(self, x, y, radius, color, speed):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed = speed
        self.health = 100  # Initial health value
        self.state = 'moving'
        self.stop_duration_frames = random.randint(60, 120)
        self.move_duration_frames = random.randint(120, 300)
        self.current_timer = self.move_duration_frames
        self.dx = random.choice([-1, 1])
        self.dy = random.choice([-1, 1])

    def draw(self, surface):
        """Draws the AI circle and its health bar on the screen."""
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Draw health bar
        health_bar_width = self.radius * 2
        health_bar_height = 10
        health_bar_x = self.x - health_bar_width / 2
        health_bar_y = self.y - self.radius - 15
        
        # Draw the background of the health bar
        pygame.draw.rect(surface, RED, (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        
        # Calculate the width of the current health portion
        current_health_width = (self.health / 100) * health_bar_width
        pygame.draw.rect(surface, GREEN, (health_bar_x, health_bar_y, current_health_width, health_bar_height))

    def move(self, walls):
        """
        Handles the AI's movement with a timer to stop periodically and checks for wall collisions.
        """
        if self.health <= 0:
            return  # Don't move if defeated
            
        self.current_timer -= 1
        
        if self.current_timer <= 0:
            if self.state == 'moving':
                self.state = 'stopped'
                self.current_timer = self.stop_duration_frames
            else:
                self.state = 'moving'
                self.current_timer = self.move_duration_frames
                self.dx = random.choice([-1, 1])
                self.dy = random.choice([-1, 1])

        if self.state == 'moving':
            next_x = self.x + self.dx * self.speed
            next_y = self.y + self.dy * self.speed
            temp_rect = pygame.Rect(next_x - self.radius, next_y - self.radius, self.radius * 2, self.radius * 2)

            collision = False
            for wall in walls:
                if wall['phase_timer'] == 0:
                    if temp_rect.colliderect(wall['rect']):
                        collision = True
                        break
            
            if not collision:
                self.x = next_x
                self.y = next_y
            else:
                self.dx *= -1
                self.dy *= -1
                
            if self.x <= self.radius or self.x >= SCREEN_WIDTH - self.radius:
                self.dx *= -1
            if self.y <= self.radius or self.y >= SCREEN_HEIGHT - self.radius:
                self.dy *= -1

    def take_damage(self, amount):
        """Reduces the AI's health by the given amount."""
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def is_alive(self):
        """Checks if the AI is still alive."""
        return self.health > 0

    def get_rect(self):
        """Returns a rect object for collision detection."""
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

class Bullet:
    """
    Represents a bullet projectile fired by the player.
    """
    def __init__(self, x, y, angle, base_damage):
        self.x = x
        self.y = y
        self.radius = 5
        self.speed = 15  # Increased speed for more dynamic gameplay
        self.base_damage = base_damage
        
        # Store initial position for distance calculation
        self.start_x = x
        self.start_y = y
        
        # Calculate velocity vector from angle
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed

    def update(self):
        """Updates the bullet's position."""
        self.x += self.dx
        self.y += self.dy
        
    def calculate_damage(self):
        """Calculates damage based on distance from the player."""
        distance = math.sqrt((self.x - self.start_x)**2 + (self.y - self.start_y)**2)
        # Damage falls off with distance. Linear falloff.
        # Max damage at 0 distance, 0 damage at 300 pixel distance.
        damage_factor = max(0, 1 - distance / 300) 
        return self.base_damage * damage_factor

    def draw(self, surface):
        """Draws the bullet on the screen."""
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), self.radius)
        
    def get_rect(self):
        """Returns a rect object for collision detection."""
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

# --- Main Game Loop ---
def main():
    """
    The main function that runs the game.
    """
    player = Player(
        x=SCREEN_WIDTH // 4,
        y=SCREEN_HEIGHT // 2,
        radius=25,
        color=RED,
        speed=5
    )
    
    ai = AI(
        x=SCREEN_WIDTH * 3 // 4,
        y=SCREEN_HEIGHT // 2,
        radius=25,
        color=BLUE,
        speed=3
    )

    walls = []
    bullets = []  # List to hold all active bullets
    
    # New state variables for weapon, shooting and reloading
    current_weapon = 'pistol'
    current_ammo = WEAPONS[current_weapon]['max_ammo']
    last_shot_time = 0
    last_reload_time = 0

    game_state = "playing"  # Can be "playing" or "win"
    
    # Set up the font for the message and UI
    font = pygame.font.Font(None, 74)
    ui_font = pygame.font.Font(None, 36)

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()
        
        # Check for reload condition if ammo is empty
        if current_ammo == 0 and current_time - last_reload_time >= WEAPONS[current_weapon]['reload_time_ms']:
            current_ammo = WEAPONS[current_weapon]['max_ammo']

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    current_weapon = 'pistol'
                    current_ammo = WEAPONS[current_weapon]['max_ammo']
                    last_shot_time = current_time  # Reset cooldown on switch
                if event.key == pygame.K_2:
                    current_weapon = 'shotgun'
                    current_ammo = WEAPONS[current_weapon]['max_ammo']
                    last_shot_time = current_time  # Reset cooldown on switch
                if event.key == pygame.K_e:
                    # Logic to create walls
                    if player.direction == (0, -1) or player.direction == (0, 1):
                        wall_width = 100
                        wall_height = 20
                    elif player.direction == (-1, 0) or player.direction == (1, 0):
                        wall_width = 20
                        wall_height = 100
                    else:
                        wall_width = 20
                        wall_height = 100
                    
                    offset = player.radius + 5
                    spawn_x = player.x + player.direction[0] * offset
                    spawn_y = player.y + player.direction[1] * offset
                    
                    new_wall_rect = pygame.Rect(
                        spawn_x - wall_width / 2,
                        spawn_y - wall_height / 2,
                        wall_width,
                        wall_height
                    )
                    
                    walls.append({
                        'rect': new_wall_rect,
                        'color': BROWN,
                        'phase_timer': 0
                    })
                
                if event.key == pygame.K_g:
                    # Check for wall phasing based on player direction
                    phasing_distance = player.radius * 4  # Max distance to phase a wall
                    found_wall_to_phase = False
                    
                    for wall in walls:
                        if wall['phase_timer'] == 0:
                            # Calculate the vector from player to the wall's center
                            wall_center = wall['rect'].center
                            wall_vec = (wall_center[0] - player.x, wall_center[1] - player.y)
                            
                            # Calculate distance and check if it's within range
                            distance = math.sqrt(wall_vec[0]**2 + wall_vec[1]**2)
                            if distance <= phasing_distance:
                                # Normalize the wall vector
                                if distance > 0:
                                    norm_wall_vec = (wall_vec[0] / distance, wall_vec[1] / distance)
                                else:
                                    norm_wall_vec = (0, 0)  # Handle case where player is at wall center
                                
                                # Calculate dot product to check if they are facing the wall
                                # A dot product > 0.7 means the angle is less than ~45 degrees
                                dot_product = player.direction[0] * norm_wall_vec[0] + player.direction[1] * norm_wall_vec[1]
                                
                                if dot_product > 0.7:
                                    wall['color'] = LIGHT_BLUE
                                    wall['phase_timer'] = 60
                                    found_wall_to_phase = True
                                    break  # Only phase one wall at a time

            # New event handler for left mouse button click
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and game_state == "playing":
                # Check for cooldown and ammo
                if current_time - last_shot_time >= WEAPONS[current_weapon]['cooldown_ms'] and current_ammo > 0:
                    
                    # Get the necessary angles for the bullet direction
                    delta_x_mouse = mouse_pos[0] - player.x
                    delta_y_mouse = mouse_pos[1] - player.y
                    mouse_angle_rad = math.atan2(delta_y_mouse, delta_x_mouse)
                    player_angle_rad = math.atan2(player.direction[1], player.direction[0])
                    angle_diff_rad = mouse_angle_rad - player_angle_rad

                    while angle_diff_rad > math.pi:
                        angle_diff_rad -= 2 * math.pi
                    while angle_diff_rad < -math.pi:
                        angle_diff_rad += 2 * math.pi

                    clamped_diff_rad = max(-math.pi / 2, min(math.pi / 2, angle_diff_rad))
                    final_angle_rad = player_angle_rad + clamped_diff_rad
                    
                    # Calculate the bullet's starting position at the tip of the gun
                    gun_length = 40
                    gun_tip_offset = player.radius + gun_length

                    # Fire multiple pellets if it's the shotgun
                    for _ in range(WEAPONS[current_weapon]['pellets']):
                        # Add a random spread to the angle
                        spread_rad = math.radians(WEAPONS[current_weapon]['spread_angle'])
                        angle_offset = random.uniform(-spread_rad / 2, spread_rad / 2)
                        pellet_angle = final_angle_rad + angle_offset

                        spawn_x = player.x + math.cos(pellet_angle) * gun_tip_offset
                        spawn_y = player.y + math.sin(pellet_angle) * gun_tip_offset
                        
                        bullets.append(Bullet(spawn_x, spawn_y, pellet_angle, WEAPONS[current_weapon]['base_damage']))
                    
                    # Update game state after shooting
                    current_ammo -= 1
                    last_shot_time = current_time
                    if current_ammo == 0:
                        last_reload_time = current_time  # Start reload timer


        # Update game state only if the game is still playing
        if game_state == "playing":
            keys = pygame.key.get_pressed()
            player.move(keys, walls)
            ai.move(walls)

            # Update and handle bullets
            bullets_to_remove = []
            for bullet in bullets:
                bullet.update()
                
                # Check if the bullet hits the AI
                if ai.is_alive() and ai.get_rect().colliderect(bullet.get_rect()):
                    damage_dealt = bullet.calculate_damage()
                    ai.take_damage(damage_dealt)
                    bullets_to_remove.append(bullet)
                
                # Check if bullet goes off screen
                if bullet.x < 0 or bullet.x > SCREEN_WIDTH or bullet.y < 0 or bullet.y > SCREEN_HEIGHT:
                    bullets_to_remove.append(bullet)
            
            # Remove bullets that need to be removed
            for bullet in bullets_to_remove:
                if bullet in bullets:
                    bullets.remove(bullet)
            
            # Check for win condition
            if not ai.is_alive():
                game_state = "win"
            

        # Fill the screen with a solid color.
        screen.fill(WHITE)

        for wall in walls:
            if wall['phase_timer'] > 0:
                wall['phase_timer'] -= 1
                if wall['phase_timer'] == 0:
                    wall['color'] = BROWN
            pygame.draw.rect(screen, wall['color'], wall['rect'])

        player.draw(screen, mouse_pos)
        
        # Only draw the AI if it's alive
        if ai.is_alive():
            ai.draw(screen)
        
        # Draw all active bullets
        for bullet in bullets:
            bullet.draw(screen)

        # Draw the Ammo UI
        ammo_text = f"Ammo: {current_ammo} / {WEAPONS[current_weapon]['max_ammo']}"
        ammo_color = RED if current_ammo == 0 else UI_TEXT_COLOR
        
        ammo_surface = ui_font.render(ammo_text, True, ammo_color)
        screen.blit(ammo_surface, (10, 10))
        
        # Draw the Weapon UI
        weapon_text = f"Weapon: {current_weapon.upper()}"
        weapon_surface = ui_font.render(weapon_text, True, UI_TEXT_COLOR)
        screen.blit(weapon_surface, (10, 50))
            
        # Display win message if game is over
        if game_state == "win":
            text = font.render("You Win!", True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            # Draw a semi-transparent background for the message
            background_rect = text_rect.inflate(20, 20)
            pygame.draw.rect(screen, (200, 200, 200, 150), background_rect)
            pygame.draw.rect(screen, BLACK, background_rect, 3)
            screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
