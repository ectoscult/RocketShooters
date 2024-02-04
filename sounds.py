import pygame
from pygame import mixer

pygame.init()


def path(name):
    return f"Assets/Sounds/{name}.wav"


player_dict = {
    "shoot": mixer.Sound(path("PlayerShoot")),
    "explosion": mixer.Sound(path("PlayerExplosion")),
}

normal_enemy_dict = {
    "shoot": mixer.Sound(path("EnemyShoot")),
    "hurt": mixer.Sound(path("EnemyHurt")),
    "explosion": mixer.Sound(path("EnemyExplosion"))
}

misc_dict = {
    "new_level": mixer.Sound(path("NewLevel")),
    "item_pickup": mixer.Sound(path("ItemPickup"))
}


def play_sound(object, sound, volume=1):
    if object == "player":
        player_dict[f"{sound}"].set_volume(volume)
        player_dict[f"{sound}"].play()
    elif object == "normal_enemy":
        normal_enemy_dict[f"{sound}"].set_volume(volume)
        normal_enemy_dict[f"{sound}"].play()
    elif object == "misc":
        misc_dict[f"{sound}"].set_volume(volume)
        misc_dict[f"{sound}"].play()
