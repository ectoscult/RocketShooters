import pygame
from models import EnemyNormal, EnemySlow, SpaceShip, HealthShard, FireRateShard
from utils import get_random_pos, print_text, write_high_score, read_high_score, roll_chance
from sounds import play_sound
from math import floor


class Boom:
    def __init__(self):
        self.level = 0
        self.score = 0
        self.player_scores = {
            "player1": 0,
            "player2": 0
        }
        self.high_score = read_high_score('score').replace('\n1', "")
        self.highest_level = read_high_score('level')
        self.game_start = False

        self.resolution = self.width, self.height = 800, 600
        self.init_pygame()
        self.screen = pygame.display.set_mode(self.resolution)
        self.time = pygame.time

        self.font = pygame.font.Font(None, 32)
        self.message = ""

        self.player_bullets = {
            "player1": [],
            "player2": []
        }
        self.enemy_bullets = {
            "normal": [],
            "slow": []
        }
        self.enemies = {
            "normal": [],
            "slow": []
        }
        self.player_ships = {
            "player1": SpaceShip((200, 300), self.player_bullets["player1"].append, 200),
            "player2": SpaceShip((600, 300), self.player_bullets["player2"].append, 200)
        }
        self.items = []

    def main_loop(self):
        while True:
            if self.game_start:
                self.game_logic()
            self.move_objs()
            self.handle_input()
            self.draw()

    def init_pygame(self):
        pygame.init()
        pygame.display.set_caption("Boom")

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.game_start = True

            if self.message:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.level = 0
                    self.score = 0
                    self.player_scores = {
                        "player1": 0,
                        "player2": 0
                    }
                    self.message = ""

                    self.player_bullets = {
                        "player1": [],
                        "player2": []
                    }
                    self.enemy_bullets = {
                        "normal": [],
                        "slow": []
                    }
                    self.enemies = {
                        "normal": [],
                        "slow": []
                    }
                    self.player_ships = {
                        "player1": SpaceShip((200, 300), self.player_bullets["player1"].append, 200),
                        "player2": SpaceShip((600, 300), self.player_bullets["player2"].append, 200)
                    }
                    self.items = []

        key_pressed = pygame.key.get_pressed()

        for player, ship in (*self.player_ships.items(),):
            if player == "player1" and ship:
                if key_pressed[pygame.K_d]:
                    ship.rotate(clockwise=True)
                if key_pressed[pygame.K_a]:
                    ship.rotate(clockwise=False)
                if key_pressed[pygame.K_w]:
                    ship.accelerate()
                if key_pressed[pygame.K_s]:
                    ship.deaccelerate()
                if key_pressed[pygame.K_SPACE]:
                    ship.shoot()
            if player == "player2" and ship:
                if key_pressed[pygame.K_RIGHT]:
                    ship.rotate(clockwise=True)
                if key_pressed[pygame.K_LEFT]:
                    ship.rotate(clockwise=False)
                if key_pressed[pygame.K_UP]:
                    ship.accelerate()
                if key_pressed[pygame.K_DOWN]:
                    ship.deaccelerate()
                if key_pressed[pygame.K_BACKSPACE]:
                    ship.shoot()

    def move_objs(self):
        for obj in self.get_objects():
            obj.move(self.screen)

    def game_logic(self):
        for player in self.player_bullets:
            for bullet in self.player_bullets[player][:]:
                if not self.screen.get_rect().collidepoint(bullet.position):
                    if bullet:
                        self.player_bullets[player].remove(bullet)

        for enemy in self.enemy_bullets:
            for bullet in self.enemy_bullets[enemy][:]:
                if not self.screen.get_rect().collidepoint(bullet.position):
                    if bullet:
                        self.enemy_bullets[enemy].remove(bullet)

        for item in self.items[:]:
            for ship in (*self.player_ships.values(),):
                if ship:
                    if item.collides_with(ship):
                        play_sound("misc", "item_pickup")
                        if item.name == "shard_health":
                            ship.heal(item.healing_factor)
                            self.items.remove(item)
                        if item.name == "shard_fire_rate":
                            if ship.cooldown > 100:
                                ship.cooldown -= item.fire_rate_factor
                            self.items.remove(item)

        def check_bullet_hit(player):
            to_remove = []
            for bullet in self.player_bullets[player][:]:
                for enemy_type in self.enemies:
                    for enemy in self.enemies[enemy_type][:]:
                        if enemy.collides_with(bullet):
                            self.score += enemy.max_health * 2 * self.level
                            self.player_scores[player] += enemy.max_health * 2 * self.level

                            write_high_score(self.score, 'score')
                            self.high_score = read_high_score('score')

                            to_remove.append(bullet)

                            enemy.take_damage(25)
                            play_sound("normal_enemy", "hurt")
            for bullet in to_remove[:]:
                if bullet in self.player_bullets[player]:
                    self.player_bullets[player].remove(bullet)

        check_bullet_hit('player1')
        check_bullet_hit('player2')

        for enemy_type in self.enemies:
            for enemy in self.enemies[enemy_type][:]:
                if enemy.target_health <= 0:
                    if roll_chance(enemy.health_drop_chance):
                        self.items.append(HealthShard(enemy.position))
                    if roll_chance(enemy.fire_rate_drop_chance):
                        self.items.append(FireRateShard(enemy.position))

                    self.enemies[enemy_type].remove(enemy)
                    play_sound("normal_enemy", "explosion")

        for enemy_type in self.enemy_bullets:
            for bullet in self.enemy_bullets[enemy_type][:]:
                for player in self.player_ships:
                    if self.player_ships[player]:
                        if self.player_ships[player].collides_with(bullet):
                            self.player_ships[player].take_damage(25)
                            if bullet:
                                self.enemy_bullets[enemy_type].remove(bullet)

                            if self.player_ships[player].target_health <= 0:
                                self.player_ships[player] = None
                                play_sound("player", "explosion")

        def check_enemy_spawn():
            while True:
                position = get_random_pos(self.screen)

                if self.player_ships["player1"] and not self.player_ships["player2"]:
                    if position.distance_to(self.player_ships["player1"].position) > 100:
                        return position
                if self.player_ships["player2"] and not self.player_ships["player1"]:
                    if position.distance_to(self.player_ships["player2"].position) > 100:
                        return position
                if self.player_ships["player1"] and self.player_ships["player2"]:
                    if position.distance_to(self.player_ships["player1"].position) > 100 \
                            and position.distance_to(self.player_ships["player2"].position) > 100:
                        return position

        def check_alive_enemies():
            for enemy_type in (*self.enemies.values(),):
                for enemies in enemy_type:
                    if enemies:
                        return True
            return False

        if not check_alive_enemies():
            for _ in range(floor(6 + round(self.level / 2))):
                position = check_enemy_spawn()
                self.enemies["normal"].append(EnemyNormal(position, self.enemy_bullets["normal"].append))

            if self.level >= 5:
                for _ in range(floor(self.level - 5)):
                    position = check_enemy_spawn()
                    self.enemies["slow"].append(EnemySlow(position, self.enemy_bullets["slow"].append))

            self.level += 1
            write_high_score(self.level, 'level')
            self.highest_level = read_high_score('level')

            if not self.player_ships["player1"]:
                self.player_ships["player1"] = SpaceShip((200, 300), self.player_bullets["player1"].append, 100)
            if not self.player_ships["player2"]:
                self.player_ships["player2"] = SpaceShip((600, 300), self.player_bullets["player2"].append, 100)

            if self.level > 1:
                play_sound("misc", "new_level")

        for enemy_type in self.enemies:
            if self.enemies[enemy_type] is not None:
                for enemy in self.enemies[enemy_type][:]:
                    enemy.shoot()

        if not self.player_ships["player1"] and not self.player_ships["player2"]:
            self.message = "You lost!"

    def draw(self):
        self.screen.fill((0, 0, 0))

        for object in self.get_objects():
            object.draw(self.screen)

        if self.message:
            print_text(self.screen, self.message, pygame.font.Font(None, 64), self.screen.get_size(), 'title')
            print_text(self.screen, "Press [Enter] to start a new game.", pygame.font.Font(None, 32),
                       (self.screen.get_width(), self.screen.get_height() / 2 + 30), 'score')

        def text():
            print_text(self.screen, "Level : {:,}".format(self.level), self.font, (self.screen.get_width(), 15),
                       'score')
            print_text(self.screen, "Score : {:,}".format(self.score), self.font, (self.screen.get_width(), 15 + 25),
                       'score')
            print_text(self.screen, "High Score : {:,}".format(int(self.high_score)), self.font,
                       (self.screen.get_width(),
                        15 + 25 * 2), 'score')
            print_text(self.screen, "Highest Level : {:,}".format(int(self.highest_level)), self.font,
                       (self.screen.get_width(), 15 + 25 * 3), 'score')

            print_text(self.screen, "Ship 1", self.font, (0, 15), "player1")
            print_text(self.screen, "Ship 2", self.font, (self.screen.get_width(), 15), "player2")
            print_text(self.screen, "{:,}".format(int(self.player_scores["player1"])), self.font,
                       (0, 15 + 25), "player1")
            print_text(self.screen, "{:,}".format(int(self.player_scores["player2"])), self.font,
                       (self.screen.get_width(), 15 + 25), "player2")

        text()

        if self.player_ships["player1"]:
            self.player_ships["player1"].health(self.screen, 15, 7 + 25 * 2, 1)
            for item in self.items[:]:
                if item.position.distance_to(self.player_ships["player1"].position) < 75:
                    item.magnet(self.player_ships["player1"].position.x, self.player_ships["player1"].position.y,
                                item.position.x, item.position.y)
        if self.player_ships["player2"]:
            self.player_ships["player2"].health(self.screen, self.screen.get_width(), 7 + 25 * 2, 2)
            for item in self.items[:]:
                if item.position.distance_to(self.player_ships["player2"].position) < 75:
                    item.magnet(self.player_ships["player2"].position.x, self.player_ships["player2"].position.y,
                                item.position.x, item.position.y)

        if not self.game_start:
            print_text(self.screen, "Boom", pygame.font.Font(None, 64), self.screen.get_size(), 'title')
            print_text(self.screen, "Press [Enter] to start a new game.", pygame.font.Font(None, 32),
                       (self.screen.get_width(), self.screen.get_height() / 2 + 30), 'score')

        pygame.display.flip()
        self.time.wait(30)

    def get_objects(self):
        objects = [*self.items]

        for ship in (*self.player_ships.values(),):
            if ship:
                objects.append(ship)
        for enemy_types in (*self.enemies.values(),):
            for enemy in enemy_types:
                if enemy:
                    objects.append(enemy)
        for player_bullets in (*self.player_bullets.values(),):
            for player_bullet in player_bullets:
                if player_bullet:
                    objects.append(player_bullet)
        for enemies_bullets in (self.enemy_bullets.values(),):
            for enemy_bullets in enemies_bullets:
                for enemy_bullet in enemy_bullets:
                    if enemy_bullet:
                        objects.append(enemy_bullet)

        return objects
