import pygame
import struct

class Player:
    def __init__(self, player_id, start_x, start_y, color, image_path, role, 
                friction=1, acceleration=0.4, max_speed=5):
        self.player_id = player_id
        self.role = role
        self.start_x, self.start_y = start_x, start_y
        self.rect = pygame.Rect(start_x, start_y, 50, 50)
        self.color = color
        self.velocity_x = self.velocity_y = 0
        self.gravity = 0.8
        self.jump_speed = -15
        self.is_jumping = self.is_double_jumping = False
        self.facing_right = True
        self.walk_frame = 0
        self.frame_counter = 0
        self.is_inside_door = False
        self.health = 100
        # New movement variables
        self.friction = friction  # How quickly player slows down (0-1, lower = more friction)
        self.acceleration = acceleration  # How quickly player speeds up
        self.max_speed = max_speed  # Maximum horizontal speed
        self.current_speed = 0  # Current horizontal speed

    def reset_position(self):
        self.rect.x, self.rect.y = self.start_x, self.start_y
        self.velocity_x = self.velocity_y = 0
        self.current_speed = 0
        self.is_jumping = self.is_double_jumping = False
        self.is_inside_door = False
        self.health = 100

    def handle_input(self, keys, door, elevators):
        target_speed = 0  # Desired speed based on input
        if keys[pygame.K_a]:
            target_speed = -self.max_speed
            self.facing_right = False
        if keys[pygame.K_d]:
            target_speed = self.max_speed
            self.facing_right = True

        # Smoothly adjust current_speed towards target_speed
        speed_diff = target_speed - self.current_speed
        if speed_diff != 0:
            # Accelerate towards target speed
            accel_amount = min(abs(speed_diff), self.acceleration)
            self.current_speed += accel_amount * (speed_diff / abs(speed_diff))
        elif self.current_speed != 0:
            # Apply friction when no input
            friction_amount = min(abs(self.current_speed), self.friction)
            self.current_speed -= friction_amount * (self.current_speed / abs(self.current_speed))

        self.velocity_x = self.current_speed

        if keys[pygame.K_w] and not self.is_jumping:
            self.is_jumping = True
            self.velocity_y = self.jump_speed
        if keys[pygame.K_SPACE] and self.is_jumping and not self.is_double_jumping:
            self.is_double_jumping = True
            self.velocity_y = self.jump_speed
        if keys[pygame.K_RIGHT] and self.rect.colliderect(door.rect) and not self.is_inside_door:
            self.is_inside_door = True
            self.rect.x, self.rect.y = -100, -100
        if keys[pygame.K_LEFT] and self.is_inside_door:
            self.is_inside_door = False
            self.rect.x, self.rect.y = self.start_x, self.start_y
        if keys[pygame.K_e]:
            for elevator in elevators:
                if elevator.button_rect.colliderect(self.rect):
                    elevator.activate()

    def apply_gravity(self):
        if not self.is_inside_door:
            self.velocity_y += self.gravity

    def check_horizontal_collision(self, floors, players):
        if self.is_inside_door:
            return
        for floor in floors:
            if self.rect.colliderect(floor.rect):
                if self.velocity_x > 0:
                    self.rect.right = floor.rect.left
                elif self.velocity_x < 0:
                    self.rect.left = floor.rect.right
                self.velocity_x = 0
                self.current_speed = 0  # Reset speed on collision
        for player in players:
            if player != self and self.rect.colliderect(player.rect):
                if self.velocity_x > 0:
                    self.rect.right = player.rect.left
                elif self.velocity_x < 0:
                    self.rect.left = player.rect.right
                self.velocity_x = 0
                self.current_speed = 0  # Reset speed on collision

    def check_vertical_collision(self, floors, players, elevators):
        if self.is_inside_door:
            return
        self.is_jumping = True
        for floor in floors:
            if self.rect.colliderect(floor.rect):
                if self.velocity_y > 0:
                    self.rect.bottom = floor.rect.top
                    self.velocity_y = 0
                    self.is_jumping = self.is_double_jumping = False
                    if (floor.type == "fire" and self.role != "Fire") or (floor.type == "water" and self.role != "Water"):
                        self.reset_position()
                elif self.velocity_y < 0:
                    self.rect.top = floor.rect.bottom
                    self.velocity_y = 0
        for elevator in elevators:
            if self.rect.colliderect(elevator.rect) and elevator.is_active:
                if self.velocity_y > 0:
                    self.rect.bottom = elevator.rect.top
                    self.velocity_y = 0
                    self.is_jumping = self.is_double_jumping = False
                    self.rect.y -= 2
        for player in players:
            if player != self and self.rect.colliderect(player.rect):
                if self.velocity_y > 0:
                    self.rect.bottom = player.rect.top
                    self.velocity_y = 0
                    self.is_jumping = self.is_double_jumping = False
                elif self.velocity_y < 0:
                    self.rect.top = player.rect.bottom
                    self.velocity_y = 0

    def update(self, keys, floors, players, door, guns, elevators, client_socket=None):
        self.handle_input(keys, door, elevators)
        self.rect.x += self.velocity_x
        self.check_horizontal_collision(floors, players)
        self.apply_gravity()
        self.rect.y += self.velocity_y
        self.check_vertical_collision(floors, players, elevators)
        for gun in guns:
            if gun.shoot(self):
                self.health -= 10
                if self.health <= 0:
                    self.reset_position()
        if self.velocity_x != 0:
            self.frame_counter += 1
            if self.frame_counter >= 8:
                self.walk_frame = (self.walk_frame + 1) % 2
                self.frame_counter = 0
        else:
            self.walk_frame = 0
        if client_socket:
            self.send_position(client_socket)

    def draw(self, screen):
        if not self.is_inside_door:
            pygame.draw.rect(screen, self.color, self.rect)
            health_text = pygame.font.SysFont("Arial", 15).render(f"HP: {self.health}", True, (0, 0, 0))
            screen.blit(health_text, (self.rect.x, self.rect.y - 20))

    def send_position(self, client_socket):
        data = struct.pack("3i?1i", self.player_id, self.rect.x, self.rect.y, self.facing_right, self.walk_frame)
        client_socket.sendall(data)

    def update_position(self, x, y, facing_right, walk_frame):
        self.rect.x = x
        self.rect.y = y
        self.facing_right = facing_right
        self.walk_frame = walk_frame
        self.is_inside_door = (self.rect.x == -100 and self.rect.y == -100)