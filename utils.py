import random
import pygame.transform
from pygame.image import load
from pygame.math import Vector2
from pygame import Surface
from pygame import Color
from pygame import SRCALPHA


def load_sprite(name, with_alpha=True, scale_multi=1):
    path = f"Assets/{name}.png"
    loaded_sprite = load(path)

    if scale_multi != 1:
        x, y = loaded_sprite.get_size()
        loaded_sprite = pygame.transform.scale(loaded_sprite, (x*scale_multi, y*scale_multi))

    if with_alpha:
        return loaded_sprite.convert_alpha()
    else:
        return loaded_sprite.convert()


def load_animated_sprite(name, frame, x, y, scale_multi=1):
    path = f"Assets/{name}.png"
    sheet = load(path).convert_alpha()

    image = Surface((x, y), SRCALPHA).convert_alpha()
    image.blit(sheet, (0, 0), ((frame * x), 0, x, y))
    image = pygame.transform.scale(image, (x*scale_multi, y * scale_multi))
    image.set_colorkey((0,0,0))

    return image.convert_alpha()


def wrap_position(position, surface):
    x, y = position
    w, h = surface.get_size()
    return Vector2(x % w, y % h)


def get_random_pos(surface):
    return Vector2(
        random.randrange(surface.get_width()),
        random.randrange(surface.get_height())
    )


def get_random_vel(min_speed, max_speed):
    speed = random.randint(min_speed, max_speed)
    angle = random.randint(0, 360)
    return Vector2(speed, 0).rotate(angle)


def get_random_time(min_time, max_time):
    return round(random.uniform(min_time, max_time), 2)


def print_text(screen, text, font, center, description, color=Color("snow")):
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect()

    if description == 'title':
        center = Vector2(center) / 2
        rect.center = center
    elif description == 'score':
        x, y = center
        rect.center = Vector2((x / 2), y)
    elif description == 'player1':
        rect.center = center
        rect.left = 15
    elif description == 'player2':
        x, y = center
        rect.center = center
        rect.right = x - 15

    screen.blit(text_surface, rect)


def write_high_score(score, score_type):
    with open('high score.txt', 'r+') as file:
        data = file.readlines()
        if score_type == 'score':
            high_score = int(data[0].replace('\n1', ""))

            if high_score < score:
                file.seek(0)
                file.truncate(0)
                data[0] = str(score) + '\n'
                file.writelines(data)

        elif score_type == 'level':
            highest_level = int(data[1])

            if highest_level < score:
                file.seek(0)
                file.truncate(0)
                data[1] = str(score)
                file.writelines(data)

        file.close()


def read_high_score(score_type):
    with open('high score.txt', 'r') as file:
        if score_type == 'score':
            return file.readline()
        elif score_type == 'level':
            file.readline()
            return file.readline()


def roll_chance(chance):
    print(random.randint(1, chance))
    return random.randint(1, chance) == 1


def glow(x, y, color):
    surf = pygame.Surface((x*2, y*2))
    pygame.draw.ellipse(surf, color, pygame.Rect(x, y, x, y))
    surf.set_colorkey((0, 0, 0))
    return surf
