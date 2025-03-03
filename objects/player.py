import pygame
import struct
import math


class Player:
    def __init__(self, player_id, start_x, start_y, color, image_path):
        #player class, start position, color and image path.
        self.player_id = player_id
        self.rect = pygame.Rect(start_x, start_y, 50, 50)  # sqaure size 50x50.

        # loading aniamtion images.
        self.walk_images_right = [
            pygame.transform.scale(
                pygame.image.load("assets/player_walk_1.png").convert_alpha(),
                (250, 400),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/player_walk_2.png").convert_alpha(),
                (250, 400),
            ),
        ]
        self.walk_images_left = [
            pygame.transform.flip(img, True, False) for img in self.walk_images_right
        ]

        self.original_image_right = pygame.image.load(
            image_path
        ).convert_alpha()  # Load the original player image
        self.original_image_right = pygame.transform.scale(
            self.original_image_right, (250, 400)
        )
        self.original_image_left = pygame.transform.flip(
            self.original_image_right, True, False
        )

        self.image = (
            self.original_image_right
        )  # the current image (it can be left or right).
        self.color = color
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 0.8
        self.jump_speed = -15
        self.is_jumping = False
        self.is_double_jumping = False  # bl for double jump.
        self.facing_right = True  # bl for the left right dircation.
        self.walk_frame = 0  # current frame for the walk aniamtion.
        self.frame_counter = 0  # frame counter.

    def handle_input(self, keys):
        # movment of the playe.
        self.velocity_x = 0
        if keys[pygame.K_a]:  # walking to the left.
            self.velocity_x = -5
            self.facing_right = False

        if keys[pygame.K_d]:  # walking to righ.
            self.velocity_x = 5
            self.facing_right = True

        # First jump (W).
        if keys[pygame.K_w] and not self.is_jumping:
            self.is_jumping = True
            self.velocity_y = self.jump_speed

        # Double jump (SPACE).
        if keys[pygame.K_SPACE] and self.is_jumping and not self.is_double_jumping:
            self.is_double_jumping = True
            self.velocity_y = self.jump_speed

    def apply_gravity(self):
        # adding gravity for the player.
        self.velocity_y += self.gravity

    def check_horizontal_collision(self, floors, players):
        """checks the horizontal collision with the floors and other players."""
        for floor in floors:
            if self.rect.colliderect(floor.rect):
                if self.velocity_x > 0:  # right
                    self.rect.right = floor.rect.left
                elif self.velocity_x < 0:  # left 
                    self.rect.left = floor.rect.right
                self.velocity_x = 0  # stop the movement when collision.

        for player in players:
            if player != self and self.rect.colliderect(player.rect):
                if self.velocity_x > 0:  # right
                    self.rect.right = player.rect.left

                elif self.velocity_x < 0:  # left
                    self.rect.left = player.rect.right
                self.velocity_x = 0  # stop the movement when collision.

    def check_vertical_collision(self, floors, players):
        """checks the vertical collision with the floors and other players."""
        self.is_jumping = True
        for floor in floors:
            if self.rect.colliderect(floor.rect):
                if self.velocity_y > 0:  # fall into the floor.
                    self.rect.bottom = floor.rect.top
                    self.velocity_y = 0
                    self.is_jumping = False
                    self.is_double_jumping = False  # start again jumping
                elif self.velocity_y < 0:  # check clossion with the floor from the bottom.
                    self.rect.top = floor.rect.bottom
                    self.velocity_y = 0

        # check collision with other player.
        for player in players:
            if player != self and self.rect.colliderect(player.rect):  # check collision with other player.
                if self.velocity_y > 0:  # fall on other player.
                    self.rect.bottom = player.rect.top
                    self.velocity_y = 0
                    self.is_jumping = False
                    self.is_double_jumping = False  # start again jumping
                elif self.velocity_y < 0:  # check collision with other player from the bottom.
                    self.rect.top = player.rect.bottom
                    self.velocity_y = 0

    # def apply_rope(self, other_player, rope_length):
    #     """
    #     checks and applies the rope force between the two players.
    #     """
    #     dx = other_player.rect.centerx - self.rect.centerx
    #     dy = other_player.rect.centery - self.rect.centery
    #     distance = math.sqrt(dx**2 + dy**2)

    #     if distance > rope_length:  # if the distance is more than the rope length
    #         # calculate the pull factor and angle between the two players.
    #         pull_factor = (distance - rope_length) * 0.1
    #         angle = math.atan2(dy, dx)

    #         self.rect.x += int(math.cos(angle) * pull_factor)

    #         if self.rect.centery < other_player.rect.centery:  # if the player above
    #             other_player.rect.y -= int(math.sin(angle) * pull_factor)
    #         elif self.rect.centery > other_player.rect.centery:  # if the player below
    #             self.rect.y += int(math.sin(angle) * pull_factor)

    def update(self, keys, floors, players, rope_data=None):
        """updates the player's position and checks for collisions."""
        self.handle_input(keys)
        self.rect.x += self.velocity_x
        self.check_horizontal_collision(floors, players)  # checks horizontal collision
        self.apply_gravity()
        self.rect.y += self.velocity_y
        self.check_vertical_collision(floors, players)  # check vertical collision

        # start the rope.
        if rope_data:
            self.apply_rope(*rope_data)

        # update the animation of the player.
        if self.velocity_x != 0:  
            self.frame_counter += 1
            if self.frame_counter >= 8:  #change the frame evry 10 frames.
                self.walk_frame = (self.walk_frame + 1) % 2
                self.frame_counter = 0
            if self.facing_right:
                self.image = self.walk_images_right[self.walk_frame]
            else:
                self.image = self.walk_images_left[self.walk_frame]
        else:  # if the player is not moving, keep the original image.
            if self.facing_right:
                self.image = self.original_image_right
            else:
                self.image = self.original_image_left

    def draw(self, screen):
        """draw the player on the screen."""
        image_rect = self.image.get_rect(center=self.rect.center)
        screen.blit(self.image, image_rect.topleft)

    def send_position(self, client_socket):
        """sends the player's position to the other players(server)."""
        data = struct.pack("3i", self.player_id, self.rect.x, self.rect.y)
        client_socket.sendall(data)

    def update_position(self, x, y):
        """upades the player's position(from the server)."""
        self.rect.x = x
        self.rect.y = y
