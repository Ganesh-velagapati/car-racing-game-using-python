import random
import sys
import math
from time import sleep
import pygame
from pathlib import Path
from pygame import gfxdraw

# Initialize pygame's font module
pygame.font.init()


class CarRacing:
    def __init__(self):
        print("Initializing Pygame...")
        pygame.init()
        print("Pygame initialized successfully")
        pygame.display.set_caption('Turbo Racing -- Ganesh Ram')
        print("Pygame initialized")
        
        # Enable double buffering and hardware acceleration for better performance
        self.initialize_display()
        
        # Fonts with fallbacks
        try:
            self.title_font = pygame.font.SysFont('Arial Black', 60)
            self.large_font = pygame.font.SysFont('Arial Black', 40)
            self.medium_font = pygame.font.SysFont('Arial', 30)
            self.small_font = pygame.font.SysFont('Arial', 20)
        except:
            # Fallback to default fonts if specified fonts are not available
            self.title_font = pygame.font.SysFont(None, 60)
            self.large_font = pygame.font.SysFont(None, 40)
            self.medium_font = pygame.font.SysFont(None, 30)
            self.small_font = pygame.font.SysFont(None, 20)
        
        # Color definitions
        self.colors = {
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'red': (231, 76, 60),
            'dark_red': (192, 57, 43),
            'blue': (52, 152, 219),
            'dark_blue': (41, 128, 185),
            'green': (46, 204, 113),
            'dark_green': (39, 174, 96),
            'asphalt': (44, 62, 80),
            'concrete': (127, 140, 141),
            'grass': (22, 160, 133),
            'yellow': (241, 196, 15),
            'orange': (230, 126, 34),
            'sky': (52, 152, 219),
            'light_gray': (200, 200, 200)
        }
        
        # Game states
        self.STATE_MENU = 0
        self.STATE_PLAYING = 1
        self.STATE_GAME_OVER = 2
        self.state = self.STATE_MENU
        
        # Initialize game state and pre-render elements
        self.initialize()
        self.pre_render_static_elements()
        print("Game initialization complete")

    def initialize_display(self):
        """Initialize the game display with the specified resolution."""
        print("Initializing display...")
        self.display_width = 800
        self.display_height = 650
        print(f"Display dimensions: {self.display_width}x{self.display_height}")
        
        # Check available display modes
        try:
            print("Available display modes:", pygame.display.list_modes())
        except Exception as e:
            print(f"Could not get display modes: {e}")
            
        # Set up the game display
        print("Creating display window...")
        try:
            flags = pygame.DOUBLEBUF | pygame.HWSURFACE
            self.gameDisplay = pygame.display.set_mode((self.display_width, self.display_height), flags)
            print(f"Display created successfully: {self.gameDisplay}")
            print(f"Display info: {pygame.display.Info()}")
            pygame.display.set_caption('Turbo Racing')
            self.clock = pygame.time.Clock()
            print("Display and clock initialized")
        except Exception as e:
            print(f"ERROR: Failed to create display: {e}")
            raise

    def initialize(self):
        print("Initializing game state...")
        self.crashed = False
        self.paused = False
        self.score = 0
        self.high_score = 0
        self.road_markings = []
        self.road_mark_surfaces = {}
        self.last_score = -1
        self.last_high_score = -1
        print(f"Game state initialized. Current state: {self.state}")
        
        # Try to load high score
        try:
            with open('highscore.txt', 'r') as f:
                self.high_score = int(f.read())
        except:
            self.high_score = 0

        # Player car properties
        self.car_x_coordinate = (self.display_width * 0.45)
        self.car_y_coordinate = (self.display_height * 0.7)
        self.car_width = 60
        self.car_height = 100
        self.car_speed = 8

        # Enemy cars
        self.enemy_cars = []
        self.enemy_car_speed = 5
        self.enemy_spawn_rate = 60  # frames
        self.enemy_spawn_counter = 0
        
        # Road properties
        self.road_width = 400
        self.road_x = (self.display_width - self.road_width) // 2
        self.road_marks_width = 10
        self.road_marks_height = 50
        self.road_marks_gap = 50
        
        # Initialize road markings
        self.road_markings = []
        for i in range(0, self.display_height * 2, self.road_marks_height + self.road_marks_gap):
            self.road_markings.append(pygame.Rect(
                self.display_width // 2 - self.road_marks_width // 2,
                i,
                self.road_marks_width,
                self.road_marks_height
            ))
            
        # Background scrolling
        self.bg_y1 = 0
        self.bg_y2 = -self.display_height
        self.bg_speed = 5
        self.count = 0
        
        # Particles for effects
        self.particles = []
        
        # Initialize road mark surfaces dictionary
        self.road_mark_surfaces = {}
        
        # Pre-render static elements
        self.pre_render_static_elements()
        
        # Initialize score surfaces
        self.score_surface = self.medium_font.render(f"Score: {self.score}", True, self.colors['white'])
        self.high_score_surface = self.small_font.render(f"High Score: {self.high_score}", True, self.colors['yellow'])
        self.last_score = self.score
        self.last_high_score = self.high_score
        
        # Game state
        if self.state != self.STATE_MENU:
            self.state = self.STATE_PLAYING

    def spawn_enemy_car(self):
        """Spawn a new enemy car with random properties."""
        # Define possible car colors (RGB tuples)
        car_colors = [
            (255, 0, 0),    # Red
            (0, 0, 255),    # Blue
            (0, 255, 0),    # Green
            (255, 255, 0),  # Yellow
            (255, 0, 255),  # Purple
            (0, 255, 255),  # Cyan
            (255, 165, 0),  # Orange
        ]
        
        # Randomly select a color for the new car
        color = random.choice(car_colors)
        
        # Calculate lane positions (3 possible lanes)
        lane_width = self.road_width // 3
        lane = random.randint(0, 2)
        
        # Calculate x position based on the selected lane
        x = self.road_x + 20 + (lane * lane_width) + (lane_width // 2) - (self.car_width // 2)
        
        # Randomize x position slightly within the lane for more natural movement
        x += random.randint(-10, 10)
        
        # Ensure the car stays within road boundaries
        x = max(self.road_x + 20, min(x, self.road_x + self.road_width - 20 - self.car_width))
        
        # Create the new enemy car
        new_car = {
            'x': x,
            'y': -self.car_height,  # Start above the screen
            'speed': random.uniform(self.enemy_car_speed * 0.8, self.enemy_car_speed * 1.2),
            'color': color,
            'lane': lane  # Store lane for potential AI behavior
        }
        
        # Add the new car to the list
        self.enemy_cars.append(new_car)
        
        # Return the created car in case we want to use it
        return new_car
    
    def check_collisions(self):
        """Check for collisions between player car and other game objects."""
        if self.crashed:
            return
            
        # Create player car rectangle
        player_rect = pygame.Rect(
            self.car_x_coordinate + 5,  # Add small padding
            self.car_y_coordinate + 5,
            self.car_width - 10,        # Reduce width to make hitbox smaller than visual
            self.car_height - 10        # Reduce height to make hitbox smaller than visual
        )
        
        # Check collision with road boundaries
        if (self.car_x_coordinate < self.road_x + 20 or 
            self.car_x_coordinate + self.car_width > self.road_x + self.road_width - 20):
            self.handle_collision()
            return
            
        # Check collision with enemy cars
        for car in self.enemy_cars:
            # Create enemy car rectangle with some padding
            enemy_rect = pygame.Rect(
                car['x'] + 5,
                car['y'] + 5,
                self.car_width - 10,
                self.car_height - 10
            )
            
            if player_rect.colliderect(enemy_rect):
                self.handle_collision()
                return
    
    def handle_collision(self):
        """Handle what happens when a collision occurs."""
        # Only process collision if not already crashed
        if not self.crashed:
            self.crashed = True
            
            # Create explosion particles at player position
            self.create_explosion(
                self.car_x_coordinate + self.car_width // 2,
                self.car_y_coordinate + self.car_height // 2
            )
            
            # Save high score if needed
            if self.score > self.high_score:
                self.high_score = self.score
                try:
                    with open('highscore.txt', 'w') as f:
                        f.write(str(self.high_score))
                except:
                    pass  # Don't crash if we can't save the high score
            
            # Change game state to game over
            self.state = self.STATE_GAME_OVER
    
    def create_explosion(self, x, y):
        """Create explosion effect at the given position."""
        colors = [
            (255, 200, 0),  # Yellow
            (255, 100, 0),  # Orange
            (255, 50, 0),   # Red
            (200, 0, 0)     # Dark red
        ]
        
        # Create multiple particles for explosion
        for _ in range(20):
            angle = random.uniform(0, 6.28)  # Random angle in radians
            speed = random.uniform(1, 5)
            size = random.randint(2, 6)
            lifetime = random.randint(20, 40)
            
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': size,
                'lifetime': lifetime,
                'color': random.choice(colors),
                'last_update': pygame.time.get_ticks()
            })
    
    def update_particles(self):
        """Update particle effects with optimized performance."""
        if not self.particles:
            return
            
        current_time = pygame.time.get_ticks()
        
        # Only update a portion of particles each frame for better performance
        particles_to_update = len(self.particles)
        update_step = max(1, particles_to_update // 10)  # Update ~10% of particles per frame
        
        # Process particles in chunks
        for i in range(0, particles_to_update, update_step):
            if i >= len(self.particles):
                break
                
            particle = self.particles[i]
            
            # Update position with time-based movement for smoothness
            frame_time = (current_time - particle.get('last_update', current_time)) / 16.67  # Normalize to 60 FPS
            particle['x'] += particle['vx'] * frame_time
            particle['y'] += particle['vy'] * frame_time
            particle['vy'] += 0.2 * frame_time  # Gravity with frame time adjustment
            particle['lifetime'] -= frame_time
            particle['last_update'] = current_time
        
        # Clean up dead particles (only check every few frames)
        if current_time % 3 == 0:  # Only check every 3rd frame
            self.particles = [p for p in self.particles if p['lifetime'] > 0]

    def update_game(self):
        """Update game state with optimized performance."""
        # Update score (only every 5 frames to reduce CPU usage)
        if self.count % 5 == 0:
            self.score = self.count // 10
        
        # Spawn new enemy cars with adaptive difficulty
        self.enemy_spawn_counter += 1
        if self.enemy_spawn_counter >= max(30, 90 - (self.score // 1000)):  # Adjust spawn rate based on score
            self.spawn_enemy_car()
            self.enemy_spawn_counter = 0
            
            # Gradually increase difficulty based on score
            if random.random() < 0.3:  # 30% chance to increase speed
                self.enemy_car_speed = min(15, self.enemy_car_speed + 0.1)
                self.bg_speed = min(10, self.bg_speed + 0.05)
        
        # Update enemy cars with optimized loop
        current_time = pygame.time.get_ticks()
        
        # Only update particles every other frame for better performance
        if current_time % 2 == 0:
            self.update_particles()
        
        # Use list comprehension for faster enemy updates
        self.enemy_cars = [
            car for car in self.enemy_cars 
            if car['y'] <= self.display_height + 100
        ]
        
        # Update positions of remaining enemy cars
        for car in self.enemy_cars:
            car['y'] += car['speed']
        
        # Update background scrolling with smooth sub-pixel movement
        scroll_amount = self.bg_speed * (self.clock.get_fps() / 60.0)  # Normalize speed to 60 FPS
        self.bg_y1 = (self.bg_y1 + scroll_amount) % self.display_height
        self.bg_y2 = (self.bg_y2 + scroll_amount) % self.display_height
        
        # Update road markings with the same scroll amount
        for mark in self.road_markings:
            mark.y = (mark.y + scroll_amount) % (self.display_height * 2)
        
        # Only check collisions every other frame to reduce CPU usage
        if current_time % 2 == 0:
            self.check_collisions()
        
        # Increment counter for score
        self.count += 1

    def create_car_surface(self, color, is_player=True):
        """Create a pre-rendered car surface for better performance."""
        # Create a surface for the car with per-pixel alpha
        car_surface = pygame.Surface((self.car_width + 20, self.car_height + 20), pygame.SRCALPHA)
        
        # Car dimensions
        wheel_radius = 10
        body_height = self.car_height - wheel_radius
        body_y = 5
        
        # Draw car body (simplified for better performance)
        body_rect = pygame.Rect(5, body_y, self.car_width - 10, body_height - 5)
        
        # Main body with solid color and border
        pygame.draw.rect(car_surface, color, body_rect, border_radius=5)
        pygame.draw.rect(car_surface, (0, 0, 0, 150), body_rect, 2, border_radius=5)
        
        # Add a simple highlight
        highlight = pygame.Rect(body_rect.x + 2, body_rect.y + 2, 
                              body_rect.width - 4, body_rect.height // 3)
        pygame.draw.rect(car_surface, (255, 255, 255, 50), highlight, border_radius=3)
        
        # Add windows
        window_width = body_rect.width - 20
        window_height = body_rect.height // 3
        window_y = body_rect.height // 4
        window_rect = pygame.Rect(body_rect.x + 10, body_rect.y + window_y, 
                                 window_width, window_height)
        pygame.draw.rect(car_surface, (50, 80, 120, 180), window_rect, border_radius=3)
        pygame.draw.rect(car_surface, (0, 0, 0, 100), window_rect, 1, border_radius=3)
        
        # Add window divider
        pygame.draw.line(car_surface, (0, 0, 0, 100), 
                        (body_rect.centerx, window_rect.top),
                        (body_rect.centerx, window_rect.bottom), 2)
        
        # Draw wheels (simplified)
        wheel_color = (30, 30, 30)
        wheel_rim = (100, 100, 100)
        wheel_positions = [
            (5, body_y + body_height - 15),  # Front left
            (self.car_width - 15, body_y + body_height - 15),  # Front right
            (5, body_y - 5),  # Rear left
            (self.car_width - 15, body_y - 5)  # Rear right
        ]
        
        for wx, wy in wheel_positions:
            # Wheel shadow
            pygame.draw.ellipse(car_surface, (0, 0, 0, 80), 
                              (wx, wy + 3, 10, 15))
            # Wheel
            pygame.draw.ellipse(car_surface, wheel_color, 
                              (wx, wy, 10, 15))
            # Rim
            pygame.draw.ellipse(car_surface, wheel_rim, 
                              (wx + 2, wy + 2, 6, 11))
        
        # Add car details based on type
        if is_player:
            # Player car has headlights
            pygame.draw.circle(car_surface, (255, 240, 180), 
                             (10, 15), 4)
            pygame.draw.circle(car_surface, (255, 240, 180), 
                             (self.car_width - 10, 15), 4)
            
            # Add a racing stripe
            stripe = pygame.Rect(body_rect.centerx - 10, body_y + 10, 
                               20, body_height - 20)
            pygame.draw.rect(car_surface, (255, 255, 255, 100), stripe)
        else:
            # Enemy car has taillights
            pygame.draw.rect(car_surface, (255, 50, 50), 
                           (5, body_y + body_height - 15, 8, 6))
            pygame.draw.rect(car_surface, (255, 50, 50), 
                           (self.car_width - 13, body_y + body_height - 15, 8, 6))
        
        return car_surface

    def draw_car(self, x, y, color, is_player=True):
        """Draw a car at the specified position with optimized rendering."""
        # Only redraw if the car has moved or is a different type
        if is_player:
            if not hasattr(self, 'player_car_surface') or not hasattr(self, 'last_player_pos') or \
               abs(self.last_player_pos[0] - x) > 0.5 or abs(self.last_player_pos[1] - y) > 0.5:
                self.player_car_surface = self.create_car_surface(color, is_player=True)
                self.last_player_pos = (x, y)
            car_surface = self.player_car_surface
        else:
            if not hasattr(self, 'enemy_car_surfaces'):
                self.enemy_car_surfaces = {}
            
            # Use a simplified color key to reduce surface recreations
            color_key = (color[0] // 10 * 10, color[1] // 10 * 10, color[2] // 10 * 10)
            
            if color_key not in self.enemy_car_surfaces:
                self.enemy_car_surfaces[color_key] = self.create_car_surface(color, is_player=False)
            
            car_surface = self.enemy_car_surfaces[color_key]
        
        # Draw the car with sub-pixel precision for smoother movement
        self.gameDisplay.blit(car_surface, (int(x) - 10, int(y) - 5))

    def racing_window(self):
        """Main game loop that handles the game states and rendering."""
        print("Starting game loop...")
        running = True
        clock = pygame.time.Clock()
        print("Pre-rendering static elements...")
        self.pre_render_static_elements()
        print("Static elements pre-rendered")
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Handle key presses for game states
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == self.STATE_PLAYING:
                            self.paused = not self.paused
                        else:
                            running = False
                    
                    if self.state == self.STATE_MENU:
                        if event.key == pygame.K_RETURN:  # Start game
                            self.state = self.STATE_PLAYING
                            self.initialize()
                            # Reset game state
                            self.paused = False
                            self.score = 0
                            self.game_over = False
                        elif event.key == pygame.K_ESCAPE:  # Quit from menu
                            running = False
                    
                    elif self.state == self.STATE_GAME_OVER:
                        if event.key == pygame.K_RETURN:  # Start new game
                            self.state = self.STATE_PLAYING
                            self.initialize()
                        elif event.key == pygame.K_m:  # Go back to menu
                            self.state = self.STATE_MENU
                        elif event.key == pygame.K_ESCAPE:  # Quit game
                            running = False
                    
                    elif self.state == self.STATE_PLAYING and not self.paused:
                        if event.key == pygame.K_p:
                            self.paused = not self.paused
            
            # Clear the screen with black
            self.gameDisplay.fill(self.colors['black'])
            
            # Update game state based on current state
            print(f"Current game state: {self.state}")
            try:
                if self.state == self.STATE_MENU:
                    print("Rendering menu...")
                    self.draw_menu()
                
                elif self.state == self.STATE_PLAYING:
                    if not self.paused:
                        print("Updating game...")
                        self.update_game()
                    else:
                        print("Game is paused")
                        self.draw_pause_screen()
                
                elif self.state == self.STATE_GAME_OVER:
                    print("Rendering game over screen...")
                    self.draw_game_over()
                
            except Exception as e:
                print(f"Error in game loop: {e}")
                # Fallback rendering
                self.gameDisplay.fill((255, 0, 0))  # Red screen to indicate error
                error_text = self.medium_font.render(f"Error: {str(e)}", True, (255, 255, 255))
                self.gameDisplay.blit(error_text, (50, 50))
            
            # Force update the display
            pygame.display.flip()
            print("Display updated")
            
            # Update the display
            pygame.display.flip()
            
            # Cap the frame rate to 60 FPS
            clock.tick(60)
        
        # Quit Pygame when the loop ends
        pygame.quit()
        
    def pre_render_static_elements(self):
        """Pre-render elements that don't change often for better performance."""
        print("Pre-rendering sky...")
        # Pre-render the sky gradient
        self.sky_surface = pygame.Surface((self.display_width, self.display_height // 2))
        for y in range(0, self.display_height // 2, 2):
            shade = int((y / (self.display_height // 2)) * 100)
            color = (
                min(255, self.colors['sky'][0] + shade),
                min(255, self.colors['sky'][1] + shade),
                min(255, self.colors['sky'][2] + shade)
            )
            pygame.draw.rect(self.sky_surface, color, (0, y, self.display_width, 2))
        
        print("Pre-rendering grass...")
        # Pre-render the grass surface with texture
        self.grass_surface = pygame.Surface((self.display_width, self.display_height), pygame.SRCALPHA)
        self.grass_surface.fill(self.colors['grass'])
        
        # Add some grass texture
        for _ in range(100):  # More grass lines for better coverage
            x = random.randint(0, self.display_width)
            y = random.randint(0, self.display_height)
            dark_grass = (
                int(self.colors['grass'][0] * 0.8), 
                int(self.colors['grass'][1] * 0.8), 
                int(self.colors['grass'][2] * 0.8)
            )
            pygame.draw.line(
                self.grass_surface, 
                dark_grass, 
                (x, y), 
                (x + random.randint(5, 15), y), 
                1
            )
                        
        print("Pre-rendering road markings...")
        # Pre-render road markings
        self.road_mark_surfaces = {}
        for y in range(0, self.display_height, 50):
            perspective = y / self.display_height
            width = int(10 * (1 - perspective * 0.3))
            height = int(30 * (1 - perspective * 0.1))
            
            if (width, height) not in self.road_mark_surfaces:
                mark = pygame.Surface((width, height), pygame.SRCALPHA)
                pygame.draw.rect(mark, (255, 255, 200), (0, 0, width, height))
                self.road_mark_surfaces[(width, height)] = mark
                
        # Pre-render HUD background
        self.hud_surface = pygame.Surface((200, 100), pygame.SRCALPHA)
        pygame.draw.rect(self.hud_surface, (0, 0, 0, 150), 
                        self.hud_surface.get_rect(), border_radius=5)

    def draw_road(self):
        """Draw the road with optimized rendering and perspective effects."""
        try:
            # Draw sky (pre-rendered or fallback)
            if not hasattr(self, 'sky_surface') or not self.sky_surface:
                self.gameDisplay.fill(self.colors['sky'])
            else:
                self.gameDisplay.blit(self.sky_surface, (0, 0))
            
            # Draw grass (pre-rendered or fallback)
            grass_y = self.display_height // 2
            if not hasattr(self, 'grass_surface') or not self.grass_surface:
                pygame.draw.rect(self.gameDisplay, self.colors['grass'], 
                              (0, grass_y, self.display_width, self.display_height - grass_y))
            else:
                self.gameDisplay.blit(self.grass_surface, (0, grass_y))
            
            # Draw road with perspective
            road_top = self.display_height * 0.4
            road_bottom = self.display_height
            road_width = self.display_width * 0.6
            
            # Draw road base
            pygame.draw.polygon(self.gameDisplay, self.colors['asphalt'], [
                (self.display_width//2 - road_width//2, road_top),
                (self.display_width//2 + road_width//2, road_top),
                (self.display_width//2 + road_width, road_bottom),
                (self.display_width//2 - road_width, road_bottom)
            ])
            
            # Draw road shoulders
            shoulder_width = 20
            pygame.draw.polygon(self.gameDisplay, self.colors['concrete'], [
                (self.display_width//2 - road_width//2, road_top),
                (self.display_width//2 - road_width//2 - shoulder_width, road_top),
                (self.display_width//2 - road_width, road_bottom),
                (self.display_width//2 - road_width + shoulder_width, road_bottom)
            ])
            pygame.draw.polygon(self.gameDisplay, self.colors['concrete'], [
                (self.display_width//2 + road_width//2, road_top),
                (self.display_width//2 + road_width//2 + shoulder_width, road_top),
                (self.display_width//2 + road_width, road_bottom),
                (self.display_width//2 + road_width - shoulder_width, road_bottom)
            ])
            
            # Draw center line
            line_height = 40
            line_gap = 30
            for y in range(int(road_top), int(road_bottom), line_height + line_gap):
                perspective = (y - road_top) / (road_bottom - road_top)
                line_width = int(10 * (1 - perspective * 0.3))
                line_x = self.display_width // 2 - line_width // 2
                line_rect = pygame.Rect(line_x, y, line_width, line_height)
                pygame.draw.rect(self.gameDisplay, (255, 255, 200), line_rect)
                
            # Draw score and high score
            if not hasattr(self, 'score_surface'):
                self.score_surface = self.medium_font.render(f"Score: {self.score}", True, self.colors['white'])
            if not hasattr(self, 'high_score_surface'):
                self.high_score_surface = self.small_font.render(f"High Score: {self.high_score}", True, self.colors['yellow'])
                
            self.gameDisplay.blit(self.score_surface, (20, 20))
            self.gameDisplay.blit(self.high_score_surface, (20, 60))
                
        except Exception as e:
            print(f"Error in draw_road: {e}")
            # Fallback rendering
            self.gameDisplay.fill(self.colors['sky'])
            pygame.draw.rect(self.gameDisplay, self.colors['grass'], 
                          (0, self.display_height // 2, self.display_width, self.display_height // 2))
            
            # Ensure road markings are initialized
            if not hasattr(self, 'road_markings') or not self.road_markings:
                print("Initializing road markings...")
                self.road_markings = [pygame.Rect(
                    self.display_width // 2 - 5,
                    y,
                    10,
                    50
                ) for y in range(0, self.display_height * 2, 100)]
            
            # Calculate visible road segments (only draw what's on screen)
            start_y = max(0, int(self.bg_y1) - 10)
            end_y = min(self.display_height, start_y + self.display_height + 20)
            
            # Draw road with perspective (reduced resolution for better performance)
            for y in range(start_y, end_y, 15):
                # Calculate perspective based on screen position
                screen_y = (y - int(self.bg_y1)) % self.display_height
                perspective = y / self.display_height
                
                # Calculate road width and position with perspective
                road_width = int(self.road_width * (1 + perspective * 0.8))
                road_x = (self.display_width - road_width) // 2
                
                # Calculate color with perspective-based shading
                shade = int(perspective * 40)
                road_color = (
                    max(0, min(255, self.colors['asphalt'][0] - shade)),
                    max(0, min(255, self.colors['asphalt'][1] - shade)),
                    max(0, min(255, self.colors['asphalt'][2] - shade))
                )
                
                # Draw road segment
                pygame.draw.rect(self.gameDisplay, road_color, 
                              (road_x, screen_y, road_width, 15))
            
            # Draw road markings
            for mark in self.road_markings:
                if not hasattr(mark, 'y'):
                    continue
                    
                screen_y = (mark.y - int(self.bg_y1)) % (self.display_height * 2)
                if 0 <= screen_y <= self.display_height:
                    perspective = mark.y / (self.display_height * 2)
                    width = int(10 * (1 - perspective * 0.3))
                    height = int(30 * (1 - perspective * 0.1))
                    
                    # Draw road marking
                    pygame.draw.rect(
                        self.gameDisplay, 
                        (255, 255, 200),
                        (self.display_width // 2 - width // 2, screen_y, width, height)
                    )
            
            # Draw road shoulders
            shoulder_color = (100, 100, 100)
            shoulder_width = 20
            
            # Left shoulder
            pygame.draw.rect(
                self.gameDisplay, 
                shoulder_color,
                (self.road_x - shoulder_width, 0, shoulder_width, self.display_height)
            )
            
            # Right shoulder
            pygame.draw.rect(
                self.gameDisplay, 
                shoulder_color,
                (self.road_x + self.road_width, 0, shoulder_width, self.display_height)
            )
            
        except Exception as e:
            print(f"Error in draw_road: {e}")
            # Fallback rendering if something goes wrong
            self.gameDisplay.fill(self.colors['sky'])
            pygame.draw.rect(
                self.gameDisplay, 
                self.colors['grass'], 
                (0, self.display_height // 2, self.display_width, self.display_height // 2)
            )
            # Update score display if score changed
            if not hasattr(self, 'last_score') or self.last_score != self.score:
                self.score_surface = self.medium_font.render(
                    f"Score: {self.score}", 
                    True, 
                    self.colors['white']
                )
                self.last_score = self.score
            
            # Draw score and high score
            self.gameDisplay.blit(self.score_surface, (20, 20))
            
            # Update high score display if high score changed
            if not hasattr(self, 'last_high_score') or self.last_high_score != self.high_score:
                self.high_score_surface = self.small_font.render(
                    f"High Score: {self.high_score}", 
                    True, 
                    self.colors['yellow']
                )
                self.last_high_score = self.high_score
            self.gameDisplay.blit(self.high_score_surface, (20, 60))
            
            # Return the HUD area that was updated
            return pygame.Rect(10, 10, 200, 100)
    
    def draw_game_over(self):
        """Draw the game over screen with score and options."""
        try:
            # Draw the road as background
            self.draw_road()
            
            # Draw semi-transparent overlay
            overlay = pygame.Surface((self.display_width, self.display_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Semi-transparent black
            self.gameDisplay.blit(overlay, (0, 0))
            
            # Draw game over text with shadow for better visibility
            game_over_text = self.title_font.render("GAME OVER", True, self.colors['red'])
            shadow_offset = 3
            shadow_surface = self.title_font.render("GAME OVER", True, (0, 0, 0))
            
            # Draw shadow
            self.gameDisplay.blit(shadow_surface,
                               (self.display_width//2 - game_over_text.get_width()//2 + shadow_offset,
                                self.display_height//3 - game_over_text.get_height()//2 + shadow_offset))
            
            # Draw main text
            self.gameDisplay.blit(game_over_text,
                               (self.display_width//2 - game_over_text.get_width()//2,
                                self.display_height//3 - game_over_text.get_height()//2))
            
            # Draw score and high score
            score_text = self.large_font.render(f"Score: {self.score}", True, self.colors['white'])
            high_score_text = self.large_font.render(f"High Score: {self.high_score}", True, self.colors['yellow'])
            
            self.gameDisplay.blit(score_text,
                               (self.display_width//2 - score_text.get_width()//2,
                                self.display_height//2 - score_text.get_height() - 20))
            
            self.gameDisplay.blit(high_score_text,
                               (self.display_width//2 - high_score_text.get_width()//2,
                                self.display_height//2 + 20))
            
            # Draw instructions with better spacing and visual hierarchy
            restart_text = self.medium_font.render("Press ENTER to Play Again", True, self.colors['white'])
            menu_text = self.medium_font.render("Press M for Menu", True, self.colors['light_gray'])
            quit_text = self.medium_font.render("Press ESC to Quit", True, self.colors['light_gray'])
            
            # Draw a semi-transparent background for better text visibility
            text_bg = pygame.Surface((max(restart_text.get_width(), menu_text.get_width(), quit_text.get_width()) + 40, 
                                    restart_text.get_height() * 3 + 40), pygame.SRCALPHA)
            text_bg.fill((0, 0, 0, 150))
            
            # Position the text background
            text_bg_rect = text_bg.get_rect(center=(self.display_width//2, self.display_height * 2//3 + 40))
            self.gameDisplay.blit(text_bg, text_bg_rect)
            
            # Position the text
            self.gameDisplay.blit(restart_text,
                               (self.display_width//2 - restart_text.get_width()//2,
                                text_bg_rect.top + 20))
            
            self.gameDisplay.blit(menu_text,
                               (self.display_width//2 - menu_text.get_width()//2,
                                text_bg_rect.top + 20 + restart_text.get_height() + 10))
            
            self.gameDisplay.blit(quit_text,
                               (self.display_width//2 - quit_text.get_width()//2,
                                text_bg_rect.top + 20 + (restart_text.get_height() + 10) * 2))
        
        except Exception as e:
            print(f"Error in draw_game_over: {e}")
            # Fallback rendering
            self.gameDisplay.fill(self.colors['black'])
            error_text = self.medium_font.render("Error in game over screen", True, (255, 0, 0))
            self.gameDisplay.blit(error_text, (50, 50)) 

    def draw_menu(self):
        """Draw the main menu screen with improved visual feedback."""
        try:
            # Draw the road as background
            self.draw_road()
            
            # Draw semi-transparent overlay with vignette effect
            overlay = pygame.Surface((self.display_width, self.display_height), pygame.SRCALPHA)
            # Draw gradient from transparent to dark at edges
            for y in range(self.display_height):
                # Calculate alpha based on distance from center
                dist_from_center = abs(y - self.display_height//2) / (self.display_height/2)
                alpha = int(100 + 100 * dist_from_center)  # 100-200 alpha range
                pygame.draw.line(overlay, (0, 0, 0, alpha), 
                               (0, y), (self.display_width, y))
            
            self.gameDisplay.blit(overlay, (0, 0))
            
            # Draw animated title with glow effect
            title_glow = pygame.Surface((self.display_width, 150), pygame.SRCALPHA)
            glow_radius = 50 + 5 * math.sin(pygame.time.get_ticks() * 0.002)  # Pulsing effect
            pygame.draw.circle(title_glow, (255, 215, 0, 30), 
                             (self.display_width//2, 75), int(glow_radius))
            self.gameDisplay.blit(title_glow, (0, 50))
            
            # Draw title with gradient and shadow
            title_text = self.title_font.render("TURBO RACING", True, (255, 255, 255))
            
            # Create a gradient for the title
            title_surface = pygame.Surface((title_text.get_width(), title_text.get_height()), pygame.SRCALPHA)
            for x in range(title_text.get_width()):
                # Create a horizontal gradient from yellow to orange
                r = 255
                g = 215 - int(100 * (x / title_text.get_width()))
                b = 0
                pygame.draw.line(title_surface, (r, g, b, 255), 
                               (x, 0), (x, title_text.get_height()))
            
            # Apply the text as a mask
            title_surface.blit(title_text, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            # Draw shadow with offset
            shadow_offset = 5
            shadow_surface = pygame.Surface((title_text.get_width(), title_text.get_height()), pygame.SRCALPHA)
            shadow_surface.blit(title_surface, (0, 0))
            shadow_surface.set_alpha(100)
            
            # Draw multiple shadow layers for depth
            for i in range(3, 0, -1):
                shadow_alpha = 50 - (i * 10)
                shadow_surface.set_alpha(shadow_alpha)
                self.gameDisplay.blit(shadow_surface,
                                   (self.display_width//2 - title_text.get_width()//2 + shadow_offset * i,
                                    self.display_height//4 - title_text.get_height()//2 + shadow_offset * i))
            
            # Draw main title
            self.gameDisplay.blit(title_surface,
                               (self.display_width//2 - title_text.get_width()//2,
                                self.display_height//4 - title_text.get_height()//2))
            
            # Menu options with hover effect
            menu_items = [
                {"text": "START GAME", "action": "start", "selected": False},
                {"text": "CONTROLS", "action": "controls", "selected": False},
                {"text": "QUIT", "action": "quit", "selected": False}
            ]
            
            # Get mouse position for hover effect
            mouse_pos = pygame.mouse.get_pos()
            
            # Draw menu items with animations
            for i, item in enumerate(menu_items):
                # Calculate position
                y_pos = self.display_height//2 + i * 70
                
                # Check for mouse hover
                text_surface = self.large_font.render(item["text"], True, self.colors['white'])
                text_rect = text_surface.get_rect(center=(self.display_width//2, y_pos))
                
                # Check if mouse is over this item
                if text_rect.collidepoint(mouse_pos):
                    item["selected"] = True
                    # Draw hover effect
                    hover_surface = pygame.Surface((text_rect.width + 40, text_rect.height + 20), pygame.SRCALPHA)
                    pygame.draw.rect(hover_surface, (255, 255, 255, 30), hover_surface.get_rect(), 
                                   border_radius=10)
                    self.gameDisplay.blit(hover_surface, 
                                       (text_rect.x - 20, text_rect.y - 10))
                    
                    # Handle click
                    if pygame.mouse.get_pressed()[0]:  # Left mouse button
                        if item["action"] == "start":
                            self.state = self.STATE_PLAYING
                            self.initialize()
                            self.paused = False
                            self.score = 0
                            self.game_over = False
                        elif item["action"] == "quit":
                            pygame.quit()
                            return
                else:
                    item["selected"] = False
                
                # Draw the text with glow if selected
                if item["selected"]:
                    # Draw glow
                    glow_surface = pygame.Surface((text_rect.width + 20, text_rect.height + 20), pygame.SRCALPHA)
                    glow_radius = 20 + 5 * math.sin(pygame.time.get_ticks() * 0.005)  # Pulsing glow
                    pygame.draw.rect(glow_surface, (255, 255, 255, 50), 
                                   glow_surface.get_rect(), border_radius=10)
                    self.gameDisplay.blit(glow_surface, 
                                       (text_rect.x - 10, text_rect.y - 10))
                    
                    # Draw the text with a brighter color
                    text_color = (255, 255, 255)
                else:
                    # Fade between colors
                    color_value = 150 + int(105 * (0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.002 + i * 0.5)))
                    text_color = (color_value, color_value, color_value)
                
                text_surface = self.large_font.render(item["text"], True, text_color)
                self.gameDisplay.blit(text_surface, 
                                   (self.display_width//2 - text_surface.get_width()//2,
                                    y_pos - text_surface.get_height()//2))
            
            # Draw controls help at the bottom
            controls_text = self.small_font.render("ARROWS: Move   SPACE: Brake   P: Pause   ESC: Menu/Quit", 
                                                 True, self.colors['light_gray'])
            self.gameDisplay.blit(controls_text,
                               (self.display_width//2 - controls_text.get_width()//2,
                                self.display_height - 40))
            
            # Draw version/credit text at the bottom right
            credit_text = self.small_font.render("© 2023 Turbo Racing", True, self.colors['light_gray'])
            self.gameDisplay.blit(credit_text,
                               (self.display_width - credit_text.get_width() - 20,
                                self.display_height - 30))
        
        except Exception as e:
            print(f"Error in draw_menu: {e}")
            # Fallback to simple menu if there's an error
            self.gameDisplay.fill(self.colors['black'])
            
            # Draw title with shadow effect
            title = self.title_font.render("TURBO RACING", True, self.colors['white'])
            title_shadow = self.title_font.render("TURBO RACING", True, (50, 50, 50))
            
            # Draw title with shadow
            self.gameDisplay.blit(title_shadow, 
                               (self.display_width//2 - title.get_width()//2 + 3, 
                                self.display_height//4 - title.get_height()//2 + 3))
            self.gameDisplay.blit(title, 
                               (self.display_width//2 - title.get_width()//2, 
                                self.display_height//4 - title.get_height()//2))
            
            # Draw menu options
            options = ["Press ENTER to Start", "Press ESC to Quit"]
            for i, option in enumerate(options):
                text = self.medium_font.render(option, True, self.colors['white'])
                self.gameDisplay.blit(text, 
                                   (self.display_width//2 - text.get_width()//2,
                                    self.display_height//2 + i * 50))
            
            # Draw controls help
            controls = "ARROWS: Move   SPACE: Brake   P: Pause"
            controls_text = self.small_font.render(controls, True, self.colors['light_gray'])
            self.gameDisplay.blit(controls_text, 
                               (self.display_width//2 - controls_text.get_width()//2,
                                self.display_height - 50))
    
    def draw_pause_screen(self):
        """Draw the pause screen overlay."""
        # Only re-render pause screen elements if they don't exist or the screen was resized
        if not hasattr(self, 'pause_overlay') or \
           self.pause_overlay.get_size() != (self.display_width, self.display_height):
            
            # Create semi-transparent overlay
            self.pause_overlay = pygame.Surface((self.display_width, self.display_height), pygame.SRCALPHA)
            self.pause_overlay.fill((0, 0, 0, 150))
            
            # Create pause text surface
            self.pause_text = self.large_font.render("PAUSED", True, self.colors['white'])
            self.continue_text = self.medium_font.render(
                "Press P or ESC to continue", 
                True, 
                self.colors['white']
            )
        
        # Draw the pre-rendered overlay
        self.gameDisplay.blit(self.pause_overlay, (0, 0))
        
        # Draw the pre-rendered text
        self.gameDisplay.blit(
            self.pause_text,
            (self.display_width//2 - self.pause_text.get_width()//2, 
             self.display_height//2 - 50)
        )
        
        self.gameDisplay.blit(
            self.continue_text,
            (self.display_width//2 - self.continue_text.get_width()//2, 
             self.display_height//2 + 20)
        )
        
        # Update only the area where the pause screen is drawn
        pygame.display.flip()


if __name__ == '__main__':
    car_racing = CarRacing()
    car_racing.racing_window()