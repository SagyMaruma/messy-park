import pygame
import struct

class Player:
    def __init__(self, player_id, start_x, start_y, color, image_path, role):
        # Player class, start position, color, and image path (image_path ignored for now)
        self.player_id = player_id
        self.role = role  # "Fire" or "Water"
        self.start_x, self.start_y = start_x, start_y
        self.rect = pygame.Rect(start_x, start_y, 50, 50)  # Square size 50x50
        self.color = color  # Use color for square representation
        self.velocity_x = self.velocity_y = 0
        self.gravity = 0.8
        self.jump_speed = -15
        self.is_jumping = self.is_double_jumping = False
        self.facing_right = True
        self.walk_frame = 0  # Still used for animation timing, even with squares
        self.frame_counter = 0
        self.is_inside_door = False  # New flag to track if player is inside the door

    def reset_position(self):
        """Resets player to starting position."""
        self.rect.x, self.rect.y = self.start_x, self.start_y
        self.velocity_x = self.velocity_y = 0
        self.is_jumping = self.is_double_jumping = False
        self.is_inside_door = False  # Reset door state

    def handle_input(self, keys, door):
        # Movement of the player
        self.velocity_x = 0
        if keys[pygame.K_a]:  # Walking to the left
            self.velocity_x = -5
            self.facing_right = False
        if keys[pygame.K_d]:  # Walking to the right
            self.velocity_x = 5
            self.facing_right = True
        if keys[pygame.K_w] and not self.is_jumping:  # First jump (W)
            self.is_jumping = True
            self.velocity_y = self.jump_speed
        if keys[pygame.K_SPACE] and self.is_jumping and not self.is_double_jumping:  # Double jump (SPACE)
            self.is_double_jumping = True
            self.velocity_y = self.jump_speed
        # Door interaction with arrow keys
        if keys[pygame.K_RIGHT] and self.rect.colliderect(door.rect) and not self.is_inside_door:
            self.is_inside_door = True
            self.rect.x = -100  # Move off-screen to "hide" the player
            self.rect.y = -100
        if keys[pygame.K_LEFT] and self.is_inside_door:
            self.is_inside_door = False
            self.rect.x, self.rect.y = self.start_x, self.start_y  # Exit back to start position

    def apply_gravity(self):
        # Adding gravity for the player
        if not self.is_inside_door:  # Only apply gravity if not inside door
            self.velocity_y += self.gravity

    def check_horizontal_collision(self, floors, players):
        """Checks horizontal collision with floors and other players."""
        if self.is_inside_door:
            return  # Skip collision checks if inside door
        for floor in floors:
            if self.rect.colliderect(floor.rect):
                if self.velocity_x > 0:  # Right
                    self.rect.right = floor.rect.left
                elif self.velocity_x < 0:  # Left
                    self.rect.left = floor.rect.right
                self.velocity_x = 0
        for player in players:
            if player != self and self.rect.colliderect(player.rect):
                if self.velocity_x > 0:  # Right
                    self.rect.right = player.rect.left
                elif self.velocity_x < 0:  # Left
                    self.rect.left = player.rect.right
                self.velocity_x = 0

    def check_vertical_collision(self, floors, players):
        """Checks vertical collision with floors and other players, resets if on wrong floor type."""
        if self.is_inside_door:
            return  # Skip collision checks if inside door
        self.is_jumping = True
        for floor in floors:
            if self.rect.colliderect(floor.rect):
                if self.velocity_y > 0:  # Fall into the floor
                    self.rect.bottom = floor.rect.top
                    self.velocity_y = 0
                    self.is_jumping = self.is_double_jumping = False
                    # Check floor type and reset if mismatched
                    if (floor.type == "fire" and self.role != "Fire") or (floor.type == "water" and self.role != "Water"):
                        self.reset_position()
                elif self.velocity_y < 0:  # Collision from below
                    self.rect.top = floor.rect.bottom
                    self.velocity_y = 0
        for player in players:
            if player != self and self.rect.colliderect(player.rect):
                if self.velocity_y > 0:  # Fall onto another player
                    self.rect.bottom = player.rect.top
                    self.velocity_y = 0
                    self.is_jumping = self.is_double_jumping = False
                elif self.velocity_y < 0:  # Hit player from below
                    self.rect.top = player.rect.bottom
                    self.velocity_y = 0

    def update(self, keys, floors, players, door, client_socket=None):
        """Updates the player's position and checks for collisions."""
        self.handle_input(keys, door)
        self.rect.x += self.velocity_x
        self.check_horizontal_collision(floors, players)
        self.apply_gravity()
        self.rect.y += self.velocity_y
        self.check_vertical_collision(floors, players)
        # Update animation state (for future use or visual feedback with squares)
        if self.velocity_x != 0:
            self.frame_counter += 1
            if self.frame_counter >= 8:
                self.walk_frame = (self.walk_frame + 1) % 2
                self.frame_counter = 0
        else:
            self.walk_frame = 0  # Reset to "still" when not moving
        # Send position after update to ensure server sync
        if client_socket:
            self.send_position(client_socket)

    def draw(self, screen):
        """Draw the player as a square on the screen."""
        if not self.is_inside_door:  # Only draw if not inside door
            pygame.draw.rect(screen, self.color, self.rect)

    def send_position(self, client_socket):
        """Sends the player's position and animation to the server."""
        data = struct.pack("3i?1i", self.player_id, self.rect.x, self.rect.y, self.facing_right, self.walk_frame)
        client_socket.sendall(data)

    def update_position(self, x, y, facing_right, walk_frame):
        """Updates the player's position and animation from the server."""
        self.rect.x = x
        self.rect.y = y
        self.facing_right = facing_right
        self.walk_frame = walk_frame
        # If position is off-screen (-100, -100), assume inside door
        if self.rect.x == -100 and self.rect.y == -100:
            self.is_inside_door = True
        else:
            self.is_inside_door = False