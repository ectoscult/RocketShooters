import pygame.draw
from pygame.math import Vector2
from pygame.transform import rotozoom
from pygame import time
from pygame import BLEND_RGB_ADD
from utils import load_sprite, load_animated_sprite, wrap_position, get_random_vel, get_random_time, glow
from math import sin, atan2, cos
from sounds import play_sound

UP = Vector2(0, -1)


class GameObject:
    def __init__(self, position, sprite, velocity):
        self.position = Vector2(position)
        self.sprite = sprite
        self.radius = sprite.get_width()/2
        self.velocity = Vector2(velocity)

    def draw(self, surface):
        angle = self.direction.angle_to(UP)
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)

    def move(self, surface):
        self.position = wrap_position(self.position + self.velocity, surface)

    def collides_with(self, object):
        distance = self.position.distance_to(object.position)
        return distance < self.radius + object.radius


class PlayerBulletNormal(GameObject):
    def __init__(self, position, velocity):
        self.direction = velocity
        super().__init__(position, load_sprite("PlayerBullet", True, 3), velocity)

    def move(self, surface):
        self.position = self.position + self.velocity


class EnemyBulletNormal(GameObject):
    def __init__(self, position, velocity, name):
        self.direction = velocity
        super().__init__(position, load_sprite(name, True, 3), velocity)

    def move(self, surface):
        self.position = self.position + self.velocity


class EnemyNormal(GameObject):
    bullet_speed = 5
    max_health = 25
    health_drop_chance = 20
    fire_rate_drop_chance = 5

    def __init__(self, position, create_bullet):
        self.current_health = self.max_health
        self.health_bar_length = self.max_health
        self.health_ratio = self.max_health / self.health_bar_length
        self.target_health = self.max_health
        self.health_change_speed = 1

        self.velocity = get_random_vel(3, 5)
        self.direction = self.velocity
        self.create_bullet = create_bullet

        self.last_shot = time.get_ticks()
        self.cooldown = get_random_time(500, 700)

        super().__init__(position, load_sprite("EnemyNormal", True, 3), self.velocity)

    def take_damage(self, damage):
        if self.target_health > 0:
            self.target_health -= damage
        if self.target_health <= 0:
            self.target_health = 0

    def health(self, surface):
        transition_width = 0
        transition_color = (255, 255, 255)

        if self.current_health > self.target_health:
            self.current_health -= self.health_change_speed
            transition_width = int((self.target_health - self.current_health)/self.health_ratio)
            transition_color = (232, 194, 93)

        bar_rect = pygame.Rect(self.position.x - self.health_bar_length/2, self.position.y + 30, self.current_health / self.health_ratio, 10)
        transition_bar_rect = pygame.Rect(bar_rect.right, self.position.y + 30, transition_width, 10)
        transition_bar_rect.normalize()

        pygame.draw.rect(surface, (178, 31, 1), bar_rect)
        pygame.draw.rect(surface, transition_color, transition_bar_rect)
        pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(self.position.x - self.health_bar_length/2, self.position.y + 30, self.max_health, 10), 2)

    def draw(self, surface):
        angle = self.direction.angle_to(UP)
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)

        self.health(surface)

    def shoot(self):
        current_time = time.get_ticks()

        if current_time - self.last_shot >= self.cooldown:
            self.last_shot = current_time

            bullet_velocity = self.direction * self.bullet_speed + self.velocity
            bullet = EnemyBulletNormal(self.position, bullet_velocity, "Bullet")
            self.create_bullet(bullet)
            play_sound("normal_enemy", "shoot", 0.1)


class EnemySlow(GameObject):
    bullet_speed = 5
    max_health = 100
    health_drop_chance = 10
    fire_rate_drop_chance = 10

    def __init__(self, position, create_bullet):
        self.current_health = self.max_health
        self.health_bar_length = self.max_health
        self.health_ratio = self.max_health / self.health_bar_length
        self.target_health = self.max_health
        self.health_change_speed = 1

        self.velocity = get_random_vel(1, 2)
        self.direction = self.velocity
        self.create_bullet = create_bullet

        self.last_shot = time.get_ticks()
        self.cooldown = get_random_time(500, 700)

        super().__init__(position, load_sprite("EnemySlow", True, 3), self.velocity)

    def take_damage(self, damage):
        if self.target_health > 0:
            self.target_health -= damage
        if self.target_health <= 0:
            self.target_health = 0

    def health(self, surface):
        transition_width = 0
        transition_color = (255, 255, 255)

        if self.current_health > self.target_health:
            self.current_health -= self.health_change_speed
            transition_width = int((self.target_health - self.current_health)/self.health_ratio)
            transition_color = (232, 194, 93)

        bar_rect = pygame.Rect(self.position.x - self.health_bar_length/2, self.position.y + 30, self.current_health / self.health_ratio, 10)
        transition_bar_rect = pygame.Rect(bar_rect.right, self.position.y + 30, transition_width, 10)
        transition_bar_rect.normalize()

        pygame.draw.rect(surface, (178, 31, 1), bar_rect)
        pygame.draw.rect(surface, transition_color, transition_bar_rect)
        pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(self.position.x - self.health_bar_length/2, self.position.y + 30, self.max_health, 10), 2)

    def draw(self, surface):
        angle = self.direction.angle_to(UP)
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)

        self.health(surface)

    def shoot(self):
        current_time = time.get_ticks()

        if current_time - self.last_shot >= self.cooldown:
            self.last_shot = current_time

            bullet_velocity = self.direction * self.bullet_speed + self.velocity
            bullet = EnemyBulletNormal(self.position, bullet_velocity, "SlowBullet")
            self.create_bullet(bullet)
            play_sound("normal_enemy", "shoot", 0.1)


class SpaceShip(GameObject):
    maneuverability = 8
    acceleration = 0.5
    rocket_speed = 40
    max_health = 200
    max_speed = 15

    def __init__(self, position, create_rocket, health):
        self.current_health = health
        self.health_bar_length = 200
        self.health_ratio = self.max_health / self.health_bar_length
        self.target_health = health
        self.health_change_speed = 1

        self.create_rocket = create_rocket
        self.cooldown = 200
        self.last_shot = time.get_ticks()
        self.direction = Vector2(UP)

        self.shooting = 0
        self.accelerating = 0
        self.deaccelerating = 0

        self.spaceship_states = []

        for i in range(8):
            self.spaceship_states.append(load_animated_sprite("Spaceship", i, 13, 15, 3))

        super().__init__(position, self.spaceship_states[0], Vector2(0))

    def rotate(self, clockwise=True):
        sign = 1 if clockwise else -1
        angle = self.maneuverability * sign
        self.direction.rotate_ip(angle)

    def accelerate(self):
        self.velocity += self.direction * self.acceleration
        self.accelerating = 2

    def deaccelerate(self):
        self.velocity -= self.direction * self.acceleration
        self.deaccelerating = 2


    def shoot(self):
        current_time = time.get_ticks()

        if current_time - self.last_shot >= self.cooldown:
            self.last_shot = current_time
            bullet_velocity = self.direction * self.rocket_speed + 1.5 * self.velocity
            bullet = PlayerBulletNormal(self.position, bullet_velocity)
            bullet.position = self.position + bullet_velocity
            self.shooting = 2
            self.create_rocket(bullet)
            play_sound("player", "shoot")

    def take_damage(self, damage):
        if self.target_health > 0:
            self.target_health -= damage
        if self.target_health <= 0:
            self.target_health = 0

    def heal(self, amount):
        if self.target_health < self.max_health:
            self.target_health += amount
        if self.target_health >= self.max_health:
            self.target_health = self.max_health

    def health(self, surface, x, y, player):
        transition_width = 0
        transition_color = (255, 255, 255)

        if self.current_health < self.target_health:
            self.current_health += self.health_change_speed
            transition_width = int((self.target_health - self.current_health)/self.health_ratio)
            transition_color = (93, 232, 141)
        if self.current_health > self.target_health:
            self.current_health -= self.health_change_speed
            transition_width = int((self.target_health - self.current_health)/self.health_ratio)
            transition_color = (232, 194, 93)

        if player == 1:
            bar_rect = pygame.Rect(x, y, self.current_health / self.health_ratio, 10)
            transition_bar_rect = pygame.Rect(bar_rect.right, y, transition_width, 10)
            transition_bar_rect.normalize()
            max_rect = pygame.Rect(x, y, self.max_health, 10)
        elif player == 2:
            bar_rect = pygame.Rect(x, y, self.current_health / self.health_ratio, 10)
            bar_rect.right = x - 15
            transition_bar_rect = pygame.Rect(bar_rect.left, y, -transition_width, 10)
            transition_bar_rect.normalize()
            max_rect = pygame.Rect(x, y, self.max_health, 10)
            max_rect.right = x - 15

        pygame.draw.rect(surface, (178, 31, 1), bar_rect)
        pygame.draw.rect(surface, transition_color, transition_bar_rect)
        pygame.draw.rect(surface, (255, 255, 255), max_rect, 2)

    def move(self, surface):
        self.position = wrap_position(self.position + self.velocity, surface)

        if self.accelerating > 0:
            self.accelerating -= 1
        if self.shooting > 0:
            self.shooting -= 1
        if self.deaccelerating > 0:
            self.deaccelerating -= 1

        if self.accelerating == 0 and self.shooting == 0 and self.deaccelerating == 0:
            self.sprite = self.spaceship_states[0]
        if self.accelerating == 1 and self.shooting == 1 and self.deaccelerating == 1:
            self.sprite = self.spaceship_states[5]

        if self.accelerating == 1 and self.shooting == 0 and self.deaccelerating == 0:
            self.sprite = self.spaceship_states[3]
        if self.accelerating == 1 and self.shooting == 1 and self.deaccelerating == 0:
            self.sprite = self.spaceship_states[2]

        if self.accelerating == 0 and self.shooting == 1 and self.deaccelerating == 0:
            self.sprite = self.spaceship_states[1]
        if self.accelerating == 0 and self.shooting == 1 and self.deaccelerating == 1:
            self.sprite = self.spaceship_states[4]

        if self.accelerating == 0 and self.shooting == 0 and self.deaccelerating == 1:
            self.sprite = self.spaceship_states[7]
        if self.accelerating == 0 and self.shooting == 1 and self.deaccelerating == 1:
            self.sprite = self.spaceship_states[4]

        if self.accelerating == 1 and self.shooting == 0 and self.deaccelerating == 1:
            self.sprite = self.spaceship_states[6]

        if self.velocity.x > self.max_speed:
            self.velocity.x = self.max_speed
        if self.velocity.x < -self.max_speed:
            self.velocity.x = -self.max_speed
        if self.velocity.y > self.max_speed:
            self.velocity.y = self.max_speed
        if self.velocity.y < -self.max_speed:
            self.velocity.y = -self.max_speed


class Shard(GameObject):
    healing_factor = 25

    def __init__(self, position, sprite, velocity, color1, color2):
        self.current_time = 0
        self.timer = 0
        self.cd = 1

        self.color1, self.color2 = color1, color2

        super().__init__(position, sprite, velocity)

        self.size = self.sx, self.sy = self.sprite.get_size()

    def draw(self, surface):
        blit_position = self.position - Vector2(self.radius)
        a = lambda x: x+(x-1)/2
        surface.blit(glow(self.sx * 2, self.sy * 2, self.color1),
                     (blit_position.x - self.sx * a(2), blit_position.y - self.sy * a(2)), special_flags=BLEND_RGB_ADD)
        surface.blit(glow(self.sx * 1.5, self.sy * 1.5, self.color2),
                     (blit_position.x - self.sx * a(1.5), blit_position.y - self.sy * a(1.5)), special_flags=BLEND_RGB_ADD)

        surface.blit(self.sprite, blit_position)

    def move(self, surface):
        self.current_time += 1
        if self.current_time - self.timer > self.cd:
            self.timer = self.current_time
            px, py = self.position
            self.position = Vector2(px, 2*(sin(0.1 * self.current_time))+py)

    def magnet(self, px, py, ix, iy):
        dx = px - ix
        dy = py - iy
        angle = atan2(dy, dx)
        self.position.x += 2 * cos(angle)
        self.position.y += 4 * sin(angle)


class HealthShard(Shard):
    healing_factor = 25
    name = "shard_health"

    def __init__(self, position):
        super().__init__(position, load_sprite("HealthShard", True, 2), Vector2(UP), (0, 40, 0), (0, 25, 0))

    def function(self, ship):
        ship.heal(self.healing_factor)


class FireRateShard(Shard):
    fire_rate_factor = 10
    name = "shard_fire_rate"

    def __init__(self, position):
        super().__init__(position, load_sprite("FireRateShard", True, 2), Vector2(UP), (40, 0, 0), (25, 0, 0))

    def function(self, ship):
        if ship.cooldown > 100:
            ship.cooldown -= self.fire_rate_factor
