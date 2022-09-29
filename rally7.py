#!/usr/bin/env python

"""
A racing game from Infukor!

Copyright (C) 2006, 2007 Paul Boddie <paul@boddie.org.uk>

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

#__version__ = "1.0.9"

import pygame
import sys, os
from glob import glob
import random
import time
import math

# System status.

START_GAME, END_SEQUENCE, QUIT_GAME, END_GAME, GAME_OVER, \
    QUIT_PRESENTATION, SHOW_START, SHOW_TITLES, SHOW_INSTRUCTIONS, \
    START_DEMO, RESET_DISPLAY, SHOW_HELP = range(1, 13)

# Configuration.

class ConfigError(Exception):
    pass

class Config:

    "A registry of configuration settings."

    have_audio = 1

    # Game display and timing properties.

    clock = None # initialised later
    framerate = 30
    repeat_delay, repeat_interval = 200, 200
    next_screen_delay = 5000
    end_music_delay = 500 # when no audio exists
    demo_timer_limit = framerate * 50

    # Template values for the big screen size.

    big_screen_size = 720, 720
    big_car_speed = 12
    big_computer_speed_advantage = 1

    # Actual values for the current screen size.

    screen_flags = 0
    screen_size = 720, 720
    car_speed = 12
    computer_speed_advantage = 1

    # Cabinet settings.

    hi_score = 20000
    credits = 0
    sound = 1
    skip_intros = 0
    left_buttons = (pygame.K_z, pygame.K_LEFT)
    right_buttons = (pygame.K_x, pygame.K_RIGHT)
    up_buttons = (pygame.K_k, pygame.K_UP)
    down_buttons = (pygame.K_m, pygame.K_DOWN)
    smoke_buttons = (pygame.K_l, pygame.K_SPACE)
    snapshot_buttons = (pygame.K_s,)
    coin_buttons = (pygame.K_c,)
    start_buttons = (pygame.K_1,)
    quit_buttons = (pygame.K_ESCAPE,)
    demo_buttons = (pygame.K_d,)
    reset_small_buttons = (pygame.K_F1,)
    reset_medium_buttons = (pygame.K_F2,)
    reset_big_buttons = (pygame.K_F3,)
    reset_fullscreen_buttons = (pygame.K_F4,)
    reset_window_buttons = (pygame.K_F5,)
    help_buttons = (pygame.K_h,)
    snapshot_prefix = "snapshot-"

    # Gameplay properties.

    game_fuel_length = 100
    challenging_fuel_length = 50
    smoke_penalty = 12

    # Game data locations and configuration.

    data_dir = os.path.join(os.path.split(sys.argv[0])[0], "data")
    if not os.path.exists(data_dir):
        data_dir = "/usr/share/rally7/data"

    size_dir = "big"
    music = {}
    music_types = ["wav", "ogg", "mid"]

    # Game data registry and properties.

    specials = {}
    objects = {}
    characters = {}
    infos = {}
    special_size = 0, 0
    object_size = 0, 0
    character_size = 0, 0
    info_size = 0, 0

    wall_sets = []
    bgcolour = (255, 160, 90)

    # Maps.

    symbols = {
        "*" : "scenery",
        "#" : "solid-block",
        "/" : "corner-top-left",
        "?" : "corner-top-right",
        "L" : "corner-bottom-left",
        "J" : "corner-bottom-right",
        "-" : "edge-top",
        ")" : "edge-right",
        "(" : "edge-left",
        "_" : "edge-bottom",
        "<" : "end-left",
        "^" : "end-top",
        ">" : "end-right",
        "V" : "end-bottom",
        "=" : "wall-horizontal",
        "|" : "wall-vertical",
        "O" : "single-block"
        }

    space_or_group_symbols = " 0123456789"
    wall_names = "corner-top-left", "corner-top-right", "corner-bottom-left", "corner-bottom-right", \
        "edge-top", "edge-right", "edge-left", "edge-bottom", "end-left", "end-top", "end-right", \
        "end-bottom", "wall-horizontal", "wall-vertical", "single-block", "solid-block"

    # The size of the play area, along with the offset from the top left of the
    # map to the actual play area.

    map_size = 32, 56
    map_border = 5, 6
    start_area_x = map_border[0] + 10, map_border[0] + 20
    start_area_y = map_border[1] + 48, map_border[1] + 55

    map = [
            "******************************************",
            "******************************************",
            "******************************************",
            "******************************************",
            "******************************************",
            "******************************************",
            "*****       1       ::::::::    2    *****",
            "***** ### ##### ## X X X:### ####### *****",
            "***** ### ##### ## X # X:###         *****",
            "*****              X # X XXX ### ###2*****",
            "*****1############      :::: ### ### *****",
            "*****               ### ####         *****",
            "*****    ###### # ##### #### ####### *****",
            "*****# #      # # ###                *****",
            "*****# # #### # # ### ### ######### #*****",
            "*****# # #    # # ### ### #       # #*****",
            "*****# # #3## # #     ### #       # #*****",
            "*****  # # ##3# # ### ### # ##### # #*****",
            "***** ## #    # # ### ### # ##### # #*****",
            "***** ## # #### #         #       # #*****",
            "*****    #      # ### ##  ### 4#### #*****",
            "***** ## # ###### ### ##  ### X#### #*****",
            "***** ##          ### ##  ### X####  *****",
            "***** ###########5###      4         *****",
            "*****      ##                  ### ##*****",
            "***** #### ## #######  ######  ### ##*****",
            "***** ####  5     ###  ######   6  ##*****",
            "***** #### ## ### ###      ##  ###  #*****",
            "*****      ## ###      ##  ##  ###  #*****",
            "*****# ###### #######  ##6 ##  #### #*****",
            "*****#                 ##           #*****",
            "*****# ###### #######  ######  #### #*****",
            "*****# ###### #######  ######  #### #*****",
            "*****#     7                         *****",
            "*****# ### ## #### ##  ### ##  #### #*****",
            "*****# ### ## #### ##  ### ##  #### #*****",
            "*****#7### ## ##           ##  ##   #*****",
            "*****# ### ## ## # ##  ### ##8 ## # #*****",
            "*****#             ##  ###     ## # #*****",
            "*****# ## ### #### ##      ##     #  *****",
            "*****# ## ### #### ##  ### ##  ##### *****",
            "*****#          ## ##  ### ##  ##### *****",
            "*****# #### ###                8     *****",
            "*****  #### ###                      *****",
            "*****         ### ## ### ####  ## ## *****",
            "*****  ## ### ### ## ### ####  ## ## *****",
            "*****  ## ### ###        ####  ## ## *****",
            "*****   # ### ### ## ###       ##    *****",
            "*****9 ##         ##     # ##  ## ##0*****",
            "*****  ## ##### #### ### # ##  ## ## *****",
            "*****  ## ##### #### ### # ##  ## ## *****",
            "*****                    #        ## *****",
            "*****## ### ## ##### ### # ##  ## ## *****",
            "*****## ### ## ##### ### # ##  ## ## *****",
            "*****##   9                ##  ## ## *****",
            "*****## ### ## # # # # # # ##  ## ## *****",
            "*****## ### ## # # # # # # ##        *****",
            "*****    ##    # # # # # #     ##### *****",
            "***** ##    ## # # # # # # ## 0##### *****",
            "***** ## ##### # # # # # # ##     ## *****",
            "***** ## ##### # # # # # # ##  ## ## *****",
            "*****                          ##    *****",
            "******************************************",
            "******************************************",
            "******************************************",
            "******************************************",
            "******************************************",
            "******************************************",
        ]

    map_conversions = [
        (
            ". ."
            " ##"
            ".#.", "/"
        ),
        (
            ". ."
            "###"
            ".#.", "-"
        ),
        (
            ". ."
            "## "
            ".#.", "?"
        ),
        (
            ".#."
            " ##"
            ".#.", "("
        ),
        (
            ".#."
            "## "
            ".#.", ")"
        ),
        (
            ".#."
            "###"
            ". .", "_"
        ),
        (
            ".#."
            " ##"
            ". .", "L"
        ),
        (
            ".#."
            "## "
            ". .", "J"
        ),
        (
            ". ."
            " # "
            ".#.", "^"
        ),
        (
            ".#."
            " # "
            ".#.", "|"
        ),
        (
            ".#."
            " # "
            ". .", "V"
        ),
        (
            ". ."
            " ##"
            ". .", "<"
        ),
        (
            ". ."
            "###"
            ". .", "="
        ),
        (
            ". ."
            "## "
            ". .", ">"
        ),
        (
            ". ."
            " # "
            ". .", "O"
        )
        ]

def map_to_exact(position):
    x, y = position
    return x * Config.object_size[0], y * Config.object_size[1]

def exact_to_map(position):
    x, y = position
    map_x, offset_x = divmod(x, Config.object_size[0])
    map_y, offset_y = divmod(y, Config.object_size[1])
    return map(int, (map_x, offset_x, map_y, offset_y))

def exact(position):
    map_x, offset_x, map_y, offset_y = exact_to_map(position)
    return offset_x == 0 and offset_y == 0

def match_conversion(s):
    if s[4] != "#":
        return None
    for pattern, symbol in Config.map_conversions:
        matched = 1
        for c in range(0, 9):
            if not (pattern[c] == "#" and s[c] not in Config.space_or_group_symbols or
                pattern[c] == " " and s[c] in Config.space_or_group_symbols or
                pattern[c] == "."):
                matched = 0
                break
        if matched:
            return symbol
    return None

# Initialisation functions.

def set_small_screen():
    Config.screen_size = Config.big_screen_size[0] / 2, Config.big_screen_size[1] / 2
    Config.car_speed = Config.big_car_speed / 2
    Config.computer_speed_advantage = float(Config.big_computer_speed_advantage) / 2
    Config.size_dir = "small"

def set_medium_screen():
    Config.screen_size = int(Config.big_screen_size[0] * float(4) / 5), int(Config.big_screen_size[1] * float(4) / 5)
    Config.car_speed = Config.big_car_speed * float(4) / 5
    Config.computer_speed_advantage = float(Config.big_computer_speed_advantage) * float(4) / 5
    Config.size_dir = "medium"

def set_big_screen():
    Config.screen_size = Config.big_screen_size
    Config.car_speed = Config.big_car_speed
    Config.computer_speed_advantage = Config.big_computer_speed_advantage
    Config.size_dir = "big"

def set_fullscreen():
    Config.screen_flags = pygame.FULLSCREEN

def set_window():
    Config.screen_flags = 0

def init(screen):
    load_images()
    load_music()

    Config.character_size = init_images(Config.characters)

    write(screen, cpos(5, 4), (255, 0, 0), "RALLY 7 PYGAME CABINET")
    write(screen, cpos(5, 6), (255, 255, 255), "PRESS H FOR CONTROL SET")
    pygame.display.flip()

    Config.object_size = init_images(Config.objects)
    Config.special_size = init_images(Config.specials)
    Config.info_size = init_images(Config.infos)

    write(screen, cpos(5, 8), (127, 127, 127), "LOADED IMAGES")
    pygame.display.flip()

    init_score_images(Config.objects)

    Config.wall_sets = []
    Config.wall_sets.append({})
    init_walls(Config.wall_sets[0], (180, 0, 0), (0, 255, 0), "trees")

    write(screen, cpos(5, 10), (0, 255, 0), "LOADED SCENERY 1")
    pygame.display.flip()

    Config.wall_sets.append({})
    init_walls(Config.wall_sets[1], (0, 0, 180), (0, 255, 255), "ocean")

    write(screen, cpos(5, 12), (0, 255, 255), "LOADED SCENERY 2")
    pygame.display.flip()

    Config.wall_sets.append({})
    init_walls(Config.wall_sets[2], (100, 0, 0), (200, 100, 200), "mountains")

    write(screen, cpos(5, 14), (200, 100, 100), "LOADED SCENERY 3")
    pygame.display.flip()

    time.sleep(1)

def init_walls(set, start_colour, end_colour, scenery):
    set["corner-top-left"] = image_copy(Config.objects["corner"])
    set["corner-top-right"] = pygame.transform.rotate(Config.objects["corner"], 270)
    set["corner-bottom-right"] = pygame.transform.rotate(Config.objects["corner"], 180)
    set["corner-bottom-left"] = pygame.transform.rotate(Config.objects["corner"], 90)

    set["edge-top"] = image_copy(Config.objects["edge"])
    set["edge-right"] = pygame.transform.rotate(Config.objects["edge"], 270)
    set["edge-bottom"] = pygame.transform.rotate(Config.objects["edge"], 180)
    set["edge-left"] = pygame.transform.rotate(Config.objects["edge"], 90)

    set["end-left"] = image_copy(Config.objects["end"])
    set["end-top"] = pygame.transform.rotate(Config.objects["end"], 270)
    set["end-right"] = pygame.transform.rotate(Config.objects["end"], 180)
    set["end-bottom"] = pygame.transform.rotate(Config.objects["end"], 90)

    set["wall-horizontal"] = image_copy(Config.objects["wall"])
    set["wall-vertical"] = pygame.transform.rotate(Config.objects["wall"], 90)

    set["solid-block"] = image_copy(Config.objects["solid"])
    set["single-block"] = image_copy(Config.objects["single"])

    for wall_name in Config.wall_names:
        recolour(set[wall_name], start_colour, end_colour)

    set["scenery"] = Config.objects[scenery]

def image_copy(image):

    """
    Copy 'image' either using the Pygame 1.7 image copying method or an
    equivalent method call.
    """

    if hasattr(image, "copy"):
        return image.copy()
    else:
        return image.convert(image)

def load_images():

    "Load the images, forgetting any previously stored images."

    Config.specials = {}
    Config.objects = {}
    Config.characters = {}
    Config.infos = {}

    for directory, dictionary in [(".", Config.objects), ("characters", Config.characters), ("special", Config.specials), ("info", Config.infos)]:
        subdirectory = os.path.join(Config.data_dir, directory, Config.size_dir)

        if not os.path.exists(subdirectory):
            raise ConfigError(
                "Images directory %s not present: please download the full game or prepare the images as documented." % subdirectory)

        pattern = os.path.join(subdirectory, "*" + os.extsep + "png")
        for filename in glob(pattern):
            path, ext = os.path.splitext(filename)
            path, name = os.path.split(path)
            dictionary[name] = pygame.image.load(filename).convert_alpha()

def load_music():
    subdirectory = os.path.join(Config.data_dir, "music")

    if not os.path.exists(subdirectory):
        raise ConfigError(
            "Music directory %s not present: please download the full game or prepare the music as documented." % subdirectory)

    for music_type in Config.music_types:
        pattern = os.path.join(subdirectory, "*" + os.extsep + music_type)
        for filename in glob(pattern):
            path, ext = os.path.splitext(filename)
            path, name = os.path.split(path)
            if not Config.music.get(name):
                Config.music[name] = []
            Config.music[name].append(filename)

def play_music(name):
    if not Config.have_audio:
        set_music_end(1)
        return 1

    for music in Config.music[name]:
        try:
            pygame.mixer.music.load(music)
            pygame.mixer.music.play()
            set_music_end(1)
            return 1
        except pygame.error:
            pass

    return 0

def stop_music():
    if Config.have_audio:
        pygame.mixer.music.fadeout(500)
    set_music_end(0)

def init_images(images):
    max_size = 0, 0
    for image in images.values():
        max_size = max(max_size, image.get_rect().size)
    return max_size

def init_score_images(images):
    for i in range(100, 2100, 100):
        init_score_image(images, str(i), 4)
    init_score_image(images, "x2", 5)
    init_score_image(images, "???", 5)

def init_score_image(images, s, width):
    size = Config.character_size[0] * width
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    write(surface, (0, size * float(3)/8), (255, 255, 255), s)
    Config.objects[s] = pygame.transform.rotozoom(surface, 0, float(Config.object_size[0]) / size)

def switch_map(map, new_walls=0):
    for y in range(1, len(map) - 1):
        row = map[y]
        if new_walls:
            new_row = row.replace(":", " ").replace("X", "#")
        else:
            new_row = row.replace(":", "#").replace("X", " ")
        map[y] = new_row

def convert_map(map):
    for y in range(1, len(map) - 1):
        row = map[y]
        new_row = [row[0]]
        for x in range(1, len(row) - 1):
            pattern = map[y-1][x-1:x+2] + row[x-1:x+2] + map[y+1][x-1:x+2]
            symbol = match_conversion(pattern)
            if symbol is not None:
                new_row.append(symbol)
            else:
                new_row.append(row[x])
        new_row.append(row[x+1])
        map[y] = "".join(new_row)

# Display functions.

def cpos(x, y):
    return Config.character_size[0] * x, Config.character_size[1] * y

def write(surface, position, colour, text):
    x, y = position
    for c in text:
        image = Config.characters.get(c.upper())
        if image is None:
            x += Config.character_size[0]
            continue
        pixels = pygame.surfarray.pixels3d(image)
        pixels[:,:,0] = colour[0]
        pixels[:,:,1] = colour[1]
        pixels[:,:,2] = colour[2]
        del pixels
        surface.blit(image, (x, y))
        x += image.get_rect().width

def recolour(image, start_colour, end_colour):
    sr, sg, sb = start_colour
    er, eg, eb = end_colour
    pixels = pygame.surfarray.pixels3d(image)
    for y in range(0, len(pixels)):
        row = pixels[y]
        for x in range(0, len(row)):
            cell = row[x]
            r = float(cell[0]) / 255
            g = float(cell[1]) / 255
            b = float(cell[2]) / 255
            row[x] = (1-r)*sr + r*er, (1-g)*sg + g*eg, (1-b)*sb + b*eb
    del pixels

def brightness(colour, level):
    return colour[0] * level, colour[1] * level, colour[2] * level

# Event functions.

def coin_inserted(event):
    return event.type == pygame.KEYDOWN and event.key in Config.coin_buttons

def start_requested(event):
    return event.type == pygame.KEYDOWN and event.key in Config.start_buttons

def quit_requested(event):
    return event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key in Config.quit_buttons

def help_requested(event):
    return event.type == pygame.KEYDOWN and event.key in Config.help_buttons

def reset_requested(event):
    if event.type == pygame.KEYDOWN:
        if event.key in Config.reset_small_buttons:
            set_small_screen()
        elif event.key in Config.reset_medium_buttons:
            set_medium_screen()
        elif event.key in Config.reset_big_buttons:
            set_big_screen()
        elif event.key in Config.reset_fullscreen_buttons:
            set_fullscreen()
        elif event.key in Config.reset_window_buttons:
            set_window()
        else:
            return 0
        return 1
    return 0

def snapshot_requested(event):
    return event.type == pygame.KEYDOWN and event.key in Config.snapshot_buttons

def demo_requested(event):
    return event.type == pygame.KEYDOWN and event.key in Config.demo_buttons

def next_screen_requested(event):
    return event.type == pygame.USEREVENT

def set_next_screen(enabled, delay=None):
    if enabled:
        pygame.time.set_timer(pygame.USEREVENT, delay or Config.next_screen_delay)
    else:
        pygame.time.set_timer(pygame.USEREVENT, 0)

def set_music_end(enabled):
    if Config.have_audio:
        if enabled:
            pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
        else:
            pygame.mixer.music.set_endevent()
    elif enabled:
        pygame.time.set_timer(pygame.USEREVENT + 1, Config.end_music_delay)
    else:
        pygame.time.set_timer(pygame.USEREVENT + 1, 0)

def music_ended(event):
    return event.type == pygame.USEREVENT + 1

def save_screen(screen):
    pygame.image.save(screen, "%s%d.png" % (Config.snapshot_prefix, time.time()))

# Utility functions.

def sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0

# Handlers for different sections of the game.

class Handler:

    """
    An abstract handler. Subclasses should implement the following methods:

    show        To show the initial state of the handler on screen.
    update      To update the state of the handler.
    """

    def __init__(self, screen, info=None):
        self.screen = screen
        self.info = info

class Info(Handler):

    """
    The information panel, which manages different kinds of information as well
    as displaying it, notably...

      * Scores: player, high score and scoring.
      * Fuel level indicators, although the fuel level is maintained elsewhere.
      * Radar markers showing the positions of cars and flags.
      * The current level.

    The following sequence of method calls are used on Info objects:

      1. start_game
      2. start_level
      3. start_life
      4. end_life (only if a life was lost) or...
         next_level (only if the level was cleared)
      5. end_game

    The Info class provides no 'mainloop' method since it does not take control
    of events itself. Instead, objects call the other methods directly.
    """

    info_colour = (0, 0, 0)
    radar_colour = (0, 0, 180)

    def __init__(self, *args):
        Handler.__init__(self, *args)

        # Configure the display.

        self.markers = []
        self.info_position = cpos(28, 0)
        self.info_size = cpos(8, 24)
        self.radar_position = cpos(28, 7)
        self.radar_size = cpos(8, 14)
        self.dot_size = float(self.radar_size[0]) / Config.map_size[0], float(self.radar_size[1]) / Config.map_size[1]
        self.dot_flash_counter = 0
        self.dot_flash_rate = int(0.5 * Config.framerate)
        self.dot_flash_state = 1
        self.fuel_position = cpos(28.2, 6.2)
        self.fuel_size = cpos(7.6, 0.6)

        # High score and new high score status.

        self.old_hi_score = Config.hi_score
        self.new_hi_score = 0

        # Cabinet status.

        self.in_game = 0
        self.score = 0
        self.level = 1
        self.lives = 0

        # Placeholder values.

        self.player = None
        self.score_flag = 100
        self.fuel_capacity = None
        self.fuel_unit = None
        self.fuel_score_unit = None

    def is_challenging_level(self):
        return (self.level + 1) % 4 == 0

    def start_game(self):

        "Set up the game, resetting player score, level and lives details."

        self.in_game = 1
        self.score = 0
        self.level = 1
        self.lives = 3
        self.new_hi_score = 0

    def start_level(self):

        """
        Start a level, causing the display to be updated with the new level
        details.
        """

        self.show_level()

    def next_level(self):

        "Move to the next level."

        self.level += 1

    def start_life(self, player):

        """
        Start a life with a game level, initialising the given 'player'. Note
        that a life can be started many times without being ended.
        """

        # Define the fuel tank dimensions.

        if self.is_challenging_level():
            self.fuel_capacity = Config.framerate * Config.challenging_fuel_length
        else:
            self.fuel_capacity = Config.framerate * Config.game_fuel_length

        self.fuel_unit = float(self.fuel_size[0]) / self.fuel_capacity
        self.fuel_score_unit = self.fuel_capacity / (10 * Config.framerate)

        # Define the player, adding fuel properties.

        self.player = player
        self.player.fuel = self.fuel_capacity
        self.player.fuel_empty = self.fuel_capacity / 5 # was 6

        # Flag score resets when a new life is started.

        self.score_flag = 100 * self.level

        # Update the lives indicator - this happens more frequently than at
        # level setup and less frequently than the other updates.

        self.update_lives()

    def end_life(self):

        "End a player life."

        self.lives -= 1

    def end_game(self):

        "End the current game, checking for a new high score."

        self.in_game = 0
        if Config.hi_score > self.old_hi_score:
            self.old_hi_score = Config.hi_score
            # Trigger the congratulations!
            self.new_hi_score = 1

    def show(self):

        "Set up the screen with a view of this panel."

        screen = self.screen
        screen.fill(self.info_colour, pygame.Rect(self.info_position, self.info_size))
        screen.fill(self.radar_colour, pygame.Rect(self.radar_position, self.radar_size))
        write(screen, cpos(28, 0), (255, 255, 255), "HI-SCORE")
        self._write_score(Config.hi_score, 1, (255, 0, 0))
        if self.in_game:
            write(screen, cpos(28, 2), (255, 255, 255), "1UP")
            write(screen, cpos(30, 5), (0, 255, 0), "FUEL")
            self._fuel_gauge()
        self.show_level()

    def show_level(self):

        "Show level and score details on the panel."

        screen = self.screen
        self._write_score(self.level, 22, (255, 255, 255))
        write(screen, cpos(28, 22), (255, 255, 255), "ROUND") # writes over the blanked row
        self._write_score(self.score, 3, (0, 255, 255))

    def _write_score(self, score, y, colour):
        screen = self.screen
        s = str(score)
        screen.fill(self.info_colour, pygame.Rect(cpos(28, y), cpos(8, 1)))
        write(screen, cpos(36-len(s), y), colour, s)

    def _fuel_gauge(self):
        screen = self.screen
        big_dot = cpos(0.2, 0.2)
        small_dot = cpos(0.1, 0.1)
        y_big = self.fuel_position[1] - big_dot[1] - small_dot[1]
        y_small = self.fuel_position[1] - small_dot[1] * 2
        x = self.fuel_position[0]
        x_inc = self.fuel_size[0] / 10

        for i in range(0, 11):
            if i % 5:
                colour = (255, 255, 0)
                size = small_dot
                y = y_small
            else:
                colour = (255, 0, 0)
                size = big_dot
                y = y_big
            screen.fill(colour, pygame.Rect((x, y), size))
            x += x_inc

    def update(self, objects):

        """
        Refresh the information on the panel using the given 'objects' to
        reposition markers on the radar.
        """

        screen = self.screen
        self.reset_markers()

        # Plot new markers, where appropriate.

        self.markers = []
        for object in objects:
            map_x, offset_x, map_y, offset_y = exact_to_map(object.position)
            map_x, map_y = map_x - Config.map_border[0], map_y - Config.map_border[1]
            position = self.radar_position[0] + map_x * self.dot_size[0], self.radar_position[1] + map_y * self.dot_size[1]
            self.markers.append((position, object))

        self.update_markers()
        self.update_fuel()

    def reset_markers(self):

        "Erase the markers on the radar."

        screen = self.screen
        for position, object in self.markers:
            self.screen.fill(self.radar_colour, pygame.Rect(position, self.dot_size))

    def update_markers(self):

        "Update the markers on the radar."

        screen = self.screen
        for position, object in self.markers:

            # Make the player flash on and off.

            if not isinstance(object, Player) or self.dot_flash_state:

                # Indicate "targeted" objects.

                if getattr(object, "targeted", 0):
                    screen.fill(brightness(object.radar_colour, 0.5), pygame.Rect(position, self.dot_size))
                else:
                    screen.fill(object.radar_colour, pygame.Rect(position, self.dot_size))

        # Loop the counter, changing the state on every loop.

        self.dot_flash_counter = (self.dot_flash_counter + 1) % self.dot_flash_rate
        if self.dot_flash_counter == 0:
            self.dot_flash_state = not self.dot_flash_state

    def update_flag(self, flag):

        """
        Change the state of the given 'flag' to show that it has been collected,
        increasing the player's score.
        """

        if flag is not None:
            if flag.flag_type == "S":
                self.score_flag = self.score_flag * 2
            flag.image = Config.objects[str(self.score_flag)]
            self.score += self.score_flag
        self.update_score()

    def update_score(self):

        "Update the score display, changing the high score if appropriate."

        self._write_score(self.score, 3, (0, 255, 255))
        if self.score > Config.hi_score:
            Config.hi_score = self.score
            self._write_score(Config.hi_score, 1, (255, 0, 0))

    def update_lives(self):

        "Update the lives display."

        screen = self.screen
        position = cpos(28, 21)
        screen.fill(self.info_colour, pygame.Rect(position, cpos(8, 1)))
        for life in range(0, min(self.lives, 4)):
            screen.blit(Config.infos["life"], position)
            position = position[0] + Config.info_size[0], position[1]

    def update_fuel(self):

        "Update the fuel indicator."

        screen = self.screen
        empty_width = math.ceil((self.fuel_capacity - self.player.fuel) * self.fuel_unit)
        full_width = int(self.player.fuel * self.fuel_unit)
        screen.fill(self.info_colour, pygame.Rect(self.fuel_position, self.fuel_size))
        screen.fill(self.player.fuel_colour, pygame.Rect((self.fuel_position[0] + empty_width, self.fuel_position[1]), (full_width, self.fuel_size[1])))

    def drain_fuel(self):

        """
        Update the fuel information, also reducing the player's fuel, in
        association with either the end of a level or the collection of a lucky
        checkpoint flag.
        """

        if self.player.fuel > 0:
            self.player.fuel -= self.fuel_score_unit
            self.score += 20
            self.reset_markers()
            self.update_fuel()
            self.update_markers()
            self.update_score()
            return 1
        else:
            return 0

class Titles(Handler):

    "The game title screen, showing the different game objects."

    def show(self):

        "Show the game objects, along with the information panel."

        screen = self.screen
        screen.fill((255, 160, 90))
        self.info.show()
        screen.blit(Config.specials["logo"], cpos(9, 0.5))
        write(screen, cpos(10, 4.5), (255, 255, 255), "CAST")
        write(screen, cpos(8, 6.5), (255, 255, 255), "MY CAR")
        write(screen, cpos(8, 8.5), (255, 255, 255), "RED CAR")
        write(screen, cpos(8, 10.5), (255, 255, 255), "CHECK POINT")
        write(screen, cpos(8, 12.5), (255, 255, 255), "SPECIAL CHECK POINT")
        write(screen, cpos(8, 14.5), (255, 255, 255), "LUCKY CHECK POINT")
        write(screen, cpos(8, 16.5), (255, 255, 255), "ROCK (DANGER!)")
        write(screen, cpos(8, 18.5), (255, 255, 255), "SMOKE SCREEN")
        write(screen, cpos(10, 21.5), (240, 0, 0), "INFUKOR")
        screen.blit(Config.objects["car"], cpos(4, 6))
        screen.blit(Config.objects["car-red"], cpos(4, 8))
        screen.blit(Config.objects["flag"], cpos(4, 10))
        screen.blit(Config.objects["flag-S"], cpos(4, 12))
        screen.blit(Config.objects["flag-L"], cpos(4, 14))
        screen.blit(Config.objects["rock"], cpos(4, 16))
        screen.blit(Config.objects["smoke"], cpos(4, 18))

    def mainloop(self):

        """
        Invoke the show method and wait for input events or a timer event,
        returning the next game state.
        """

        screen = self.screen
        self.show()
        pygame.display.flip()

        set_next_screen(1)
        while 1:
            Config.clock.tick(Config.framerate)
            for event in pygame.event.get():
                if quit_requested(event):
                    return QUIT_PRESENTATION
                elif reset_requested(event):
                    return RESET_DISPLAY
                elif help_requested(event):
                    return SHOW_HELP
                elif coin_inserted(event):
                    Config.credits += 1
                    return SHOW_START
                elif next_screen_requested(event):
                    return SHOW_INSTRUCTIONS
                elif snapshot_requested(event):
                    save_screen(screen)
                elif demo_requested(event):
                    return START_DEMO

class Help(Handler):

    "The game help screen, showing controls."

    def show(self):

        "Show the controls."

        screen = self.screen
        screen.fill((0, 0, 0))
        write(screen, cpos(2, 1), (255, 0, 0),  "RALLY 7 DEFAULT CONTROL SET")
        write(screen, cpos(2, 3), (127, 127, 127),  "F1-F3      - DISPLAY SIZE")
        write(screen, cpos(2, 5), (127, 127, 127),  "F4-F5      - DISPLAY MODE")
        write(screen, cpos(2, 7), (255, 255, 255),  "C          - INSERT COIN")
        write(screen, cpos(2, 9), (255, 255, 255),  "1          - 1UP PLAYER START")
        write(screen, cpos(2, 11), (255, 255, 255), "Z OR LEFT  - LEFT")
        write(screen, cpos(2, 13), (255, 255, 255), "X OR RIGHT - RIGHT")
        write(screen, cpos(2, 15), (255, 255, 255), "K OR UP    - UP")
        write(screen, cpos(2, 17), (255, 255, 255), "M OR DOWN  - DOWN")
        write(screen, cpos(2, 19), (255, 255, 255), "L OR SPACE - SMOKE")

    def show_text(self, state):
        screen = self.screen
        if state:
            write(screen, cpos(2, 21), (255, 255, 255), "ESCAPE     - EXIT")
        else:
            screen.fill((0, 0, 0), pygame.Rect(cpos(2, 21), cpos(17, 1)))

    def mainloop(self):

        """
        Invoke the show method and wait for input events or a timer event,
        returning the next game state.
        """

        screen = self.screen
        self.show()
        pygame.display.flip()

        counter = 0
        state = 0
        while 1:
            Config.clock.tick(Config.framerate)
            for event in pygame.event.get():
                if quit_requested(event):
                    return SHOW_TITLES
                elif reset_requested(event):
                    return RESET_DISPLAY
                elif help_requested(event):
                    return SHOW_HELP
                elif coin_inserted(event):
                    Config.credits += 1
                    return SHOW_START
                elif snapshot_requested(event):
                    save_screen(screen)
                elif demo_requested(event):
                    return START_DEMO

            # Loop counter every 1s.

            counter = (counter + 1) % Config.framerate

            # Every 1s...

            if counter == 0:
                state = not state
                self.show_text(state)
                pygame.display.flip()

class Instructions(Handler):

    "The screen showing the game instructions."

    def show(self):

        "Show the game instructions."

        screen = self.screen
        screen.fill(Config.bgcolour)
        self.info.show()
        write(screen, cpos(8, 2.5), (240, 0, 0), "INSTRUCTIONS")
        write(screen, cpos(5, 4.5), (255, 255, 255), "BY DODGING RED CARS")
        write(screen, cpos(9, 6.5), (255, 255, 255), "AND ROCKS")
        write(screen, cpos(7, 8.5), (255, 255, 255), "CLEAR 10 FLAGS")
        write(screen, cpos(4, 10.5), (255, 255, 255), "BEFORE FUEL RUNS OUT")
        write(screen, cpos(17, 14.5), (255, 255, 255), "PTS")
        self.show_flag("flag")
        self.show_flag_score("100")
        write(screen, cpos(10, 21.5), (240, 0, 0), "INFUKOR")

    def show_text(self, index):

        "Show some text according to the given 'index'."

        screen = self.screen
        screen.fill(Config.bgcolour, pygame.Rect(cpos(8, 21.5), cpos(11, 1)))
        if index == 0:
            write(screen, cpos(10, 21.5), (240, 0, 0), "INFUKOR")
        else:
            write(screen, cpos(8, 21.5), (240, 0, 0), "GPL LICENSE")

    def show_flag(self, name):

        "Show a particular kind of flag, indicated by 'name'."

        screen = self.screen
        screen.fill(Config.bgcolour, pygame.Rect(cpos(7, 14), Config.object_size))
        screen.blit(Config.objects[name], cpos(7, 14))

    def show_flag_score(self, name, name2=None):

        """
        Show a flag score, using 'name' and the optional 'name2' to indicate the
        images used to present the score.
        """

        screen = self.screen
        position = cpos(11, 14)
        screen.fill(Config.bgcolour, pygame.Rect(position, Config.object_size))
        screen.blit(Config.objects[name], position)
        new_position = (position[0] + Config.object_size[0], position[1])
        screen.fill(Config.bgcolour, pygame.Rect(new_position, Config.object_size))
        if name2:
            screen.blit(Config.objects[name2], new_position)

    def mainloop(self):

        """
        Invoke the show method, and update the display to show different scoring
        details until an input event or a timer event takes place. Return the
        next game state.
        """

        screen = self.screen
        self.show()
        pygame.display.flip()

        set_next_screen(1, 12000)
        counter = 0
        flags = ["flag", "flag-S", "flag-L"]
        flag_index = 0
        text_index = 0
        while 1:
            Config.clock.tick(Config.framerate)
            for event in pygame.event.get():
                if quit_requested(event):
                    return QUIT_PRESENTATION
                elif reset_requested(event):
                    return RESET_DISPLAY
                elif help_requested(event):
                    return SHOW_HELP
                elif coin_inserted(event):
                    Config.credits += 1
                    return SHOW_START
                elif next_screen_requested(event):
                    return START_DEMO
                elif snapshot_requested(event):
                    save_screen(screen)
                elif demo_requested(event):
                    return START_DEMO

            # Loop counter every 3s.

            counter = (counter + 1) % (Config.framerate * 3)

            # Every 3s...

            if counter == 0:
                flag_index = (flag_index + 1) % len(flags)
                self.show_flag(flags[flag_index])

                text_index = (text_index + 1) % 2
                self.show_text(text_index)

            # Every 1s...

            if counter % Config.framerate == 0:
                if flag_index == 0:
                    self.show_flag_score(str(100 * (counter / Config.framerate) % 1000 + 100))
                elif flag_index == 1:
                    self.show_flag_score(str(100 * (counter / Config.framerate) % 1000 + 100), "x2")
                else:
                    self.show_flag_score("???")
                pygame.display.flip()

class Challenging(Handler):

    "The screen used to communicate details of a challenging stage."

    def __init__(self, ncars, nrocks, *args):
        Handler.__init__(self, *args)
        self.ncars = ncars
        self.nrocks = nrocks

    def show(self):

        "Show the main instruction text along with the information panel."

        screen = self.screen
        screen.fill(Config.bgcolour)
        self.info.show()
        write(screen, cpos(6, 2.5), (240, 0, 0), "CHALLENGING STAGE")
        write(screen, cpos(5, 4.5), (255, 255, 255), "RED CARS DON'T MOVE")
        write(screen, cpos(5, 6.5), (255, 255, 255), "UNTIL FUEL RUNS OUT")

    def show_object(self, name, position):

        "Show a game object with the given 'name' at the given 'position'."

        screen = self.screen
        screen.blit(Config.objects[name], position)

    def mainloop(self):

        """
        Invoke the show method and present the instructions gradually, waiting
        for a user event or the end of the music before returning a game state
        code.
        """

        screen = self.screen
        self.show()
        pygame.display.flip()

        play_music("challenging_intro_theme")

        set_next_screen(0)
        counter = 0
        state = 0
        while 1:
            Config.clock.tick(Config.framerate)
            for event in pygame.event.get():
                if quit_requested(event):
                    stop_music()
                    return QUIT_GAME
                elif coin_inserted(event):
                    Config.credits += 1
                elif music_ended(event):
                    return END_SEQUENCE
                elif snapshot_requested(event):
                    save_screen(screen)

            # Loop counter every 2s.

            counter = (counter + 1) % (Config.framerate * 2)

            # Every 2s...

            if counter == 0:
                state += 1
                if state == 1:
                    write(screen, cpos(14, 10.5), (255, 255, 255), "= %d" % self.ncars)
                    self.show_object("car-red", cpos(10, 10))
                elif state == 2:
                    write(screen, cpos(14, 14.5), (255, 255, 255), "= %d" % self.nrocks)
                    self.show_object("rock", cpos(10, 14))
                pygame.display.flip()

        pygame.time.delay(2000)

class Start(Handler):

    "The screen inviting the player to start the game."

    def show(self):
        screen = self.screen
        screen.fill((0, 0, 0))
        self.info.show()
        screen.blit(Config.specials["logo"], cpos(9, 0.5))
        self.show_text(1)
        self.show_credits()

    def show_text(self, state):
        screen = self.screen
        if state:
            write(screen, cpos(6, 8.5), (255, 255, 255), "PRESS 1UP TO START")
        else:
            screen.fill((0, 0, 0), pygame.Rect(cpos(6, 8.5), cpos(18, 1)))

    def show_credits(self):
        screen = self.screen
        screen.fill((0, 0, 0), pygame.Rect(cpos(10, 21.5), cpos(10, 1)))
        write(screen, cpos(10, 21.5), (255, 0, 0), "CREDITS %2d" % min(Config.credits, 99))

    def mainloop(self):
        screen = self.screen
        self.show()
        pygame.display.flip()

        set_next_screen(0)
        state = 1
        counter = 0
        while 1:
            Config.clock.tick(Config.framerate)
            for event in pygame.event.get():
                if quit_requested(event):
                    return QUIT_GAME
                elif coin_inserted(event):
                    Config.credits += 1
                    self.show_credits()
                    pygame.display.flip()
                elif start_requested(event):
                    Config.credits -= 1
                    return START_GAME
                elif snapshot_requested(event):
                    save_screen(screen)

            # Loop counter every 1s.

            counter = (counter + 1) % Config.framerate

            # Every 1s...

            if counter == 0:
                state = not state
                self.show_text(state)
                pygame.display.flip()

class GameOver(Handler):

    "The screen showing the player that the game is over."

    def show(self):
        screen = self.screen
        screen.fill((0, 0, 0))
        self.info.show()
        self.show_text(1)

    def show_text(self, state):
        screen = self.screen
        screen.fill((0, 0, 0), pygame.Rect(cpos(10, 10.5), cpos(10, 1)))
        write(screen, cpos(10, 10.5), (255, 255 * state, 255 * state), "GAME OVER!")

    def show_credits(self):
        screen = self.screen
        screen.fill((0, 0, 0), pygame.Rect(cpos(10, 21.5), cpos(10, 1)))
        write(screen, cpos(10, 21.5), (255, 0, 0), "CREDITS %2d" % min(Config.credits, 99))

    def mainloop(self):
        screen = self.screen
        self.show()
        pygame.display.flip()

        set_next_screen(1)
        state = 1
        counter = 0
        while 1:
            Config.clock.tick(Config.framerate)
            for event in pygame.event.get():
                if quit_requested(event):
                    return QUIT_GAME
                elif coin_inserted(event):
                    Config.credits += 1
                    self.show_credits()
                    pygame.display.flip()
                elif next_screen_requested(event):
                    return END_GAME
                elif snapshot_requested(event):
                    save_screen(screen)

            # Loop counter every 1s.

            counter = (counter + 1) % Config.framerate

            # Every 1s...

            if counter == 0:
                state = not state
                self.show_text(state)
                pygame.display.flip()

class HighScore(Handler):

    "The screen indicating that a new high score was set."

    def show(self):
        screen = self.screen
        screen.fill((0, 0, 0))
        self.info.show()
        screen.blit(Config.specials["logo"], cpos(9, 0.5))
        self.show_text(0)

    def show_text(self, state):
        screen = self.screen
        on = [(255 * (state == n)) for n in range(1, 5)]
        screen.fill((0, 0, 0), pygame.Rect(cpos(7.5, 8.5), cpos(17, 7)))
        write(screen, cpos(8, 8.5), (255, on[0], on[0]), "YOU SET TODAY'S")
        write(screen, cpos(10, 10.5), (255, 255, on[1]), "HIGH SCORE!")
        write(screen, cpos(9, 12.5), (on[2], 255, on[2]), "NOW TRY FOR A")
        write(screen, cpos(7.5, 14.5), (on[3], on[3], 255), "NEW WORLD RECORD!")

    def show_credits(self):
        screen = self.screen
        screen.fill((0, 0, 0), pygame.Rect(cpos(10, 21.5), cpos(10, 1)))
        write(screen, cpos(10, 21.5), (255, 0, 0), "CREDITS %2d" % min(Config.credits, 99))

    def mainloop(self):
        screen = self.screen
        self.show()
        pygame.display.flip()

        set_next_screen(1, 10000)
        state = 0
        counter = 0
        while 1:
            Config.clock.tick(Config.framerate)
            for event in pygame.event.get():
                if quit_requested(event):
                    return QUIT_GAME
                elif coin_inserted(event):
                    Config.credits += 1
                    self.show_credits()
                    pygame.display.flip()
                elif next_screen_requested(event):
                    return GAME_OVER
                elif snapshot_requested(event):
                    save_screen(screen)

            # Loop counter every 1s.

            counter = (counter + 1) % Config.framerate

            # Every 1s...

            if counter == 0:
                state = (state + 1) % 5
                self.show_text(state)
                pygame.display.flip()

class GameEngine(Handler):

    """
    A game controller, providing a view onto the game action and incorporating
    the information panel - see Info for more details.

    The following sequence of method calls are used on Game objects:

      1. start_game
      2. start_level
      3. start_life
      4. end_life (only if a life was lost) or...
         next_level (only if the level was cleared)
      5. end_game

    Generally, only the 'mainloop' method is called by other objects, and it
    ensures the correct invocation of the other methods, notably 'show' and
    'update'.
    """

    def __init__(self, *args):
        Handler.__init__(self, *args)

        # Get the offset of the player from the top left of the view.

        self.view_size = cpos(28, 24)
        self.player_centre = self.view_size[0] / 2, self.view_size[1] / 2
        self.player_offset = (self.view_size[0] - Config.object_size[0]) / 2, (self.view_size[1] - Config.object_size[1]) / 2
        self.view_map_size = self.view_size[0] / Config.object_size[0], self.view_size[1] / Config.object_size[1]

        self.info.start_game() # sets in_game mode for the object

    def start_level(self):

        # Level attributes.

        self.current_map = Config.map[:]
        switch_map(self.current_map, self.info.is_challenging_level())
        convert_map(self.current_map)
        Config.objects.update(Config.wall_sets[(self.info.level - 1) % len(Config.wall_sets)])

        # Set the flag and rock counts.

        nflags = 10
        nrocks = (self.info.level - 1) % 10

        # Randomly generate the rows upon which flags and rocks occur.

        flags_samples = (
            random.sample(range(0, 10), nflags),
            random.sample(range(0, 10), nflags)
            )
            
        rocks_samples = (
            random.sample(range(0, 10), nrocks),
            [random.randint(0, 1) for i in range(0, nrocks)]
            )

        # Flags and radar markers. Note that the markers disappear before the
        # flags (and their score indicators).

        self.flags = self.place_flags(self.current_map, flags_samples)
        self.rocks = self.place_rocks(self.current_map, rocks_samples)
        self.radar_flags = self.flags[:]

        # Work out the number of red cars in advance (needed for initialising
        # the challenging stage introduction). See start_life for the actual
        # initialisation of red cars.

        self.ncars = 3
        if self.info.level % 2 == 0:
            self.ncars += 2
        if self.info.is_challenging_level():
            self.ncars += 3

        self.info.start_level()

    def next_level(self):
        self.info.next_level()

    def start_life(self):

        # Account for map borders.

        bx, by = Config.map_border

        # Cars and smoke.

        self.player = self.player_class((bx + 15, by + 50), Config.objects["car"], self)
        self.red_cars = [
            Computer((0, -1), (bx + 13, by + 54), Config.objects["car-red"], self),
            Computer((0, -1), (bx + 15, by + 54), Config.objects["car-red"], self),
            Computer((0, -1), (bx + 17, by + 54), Config.objects["car-red"], self),
            ]
        self.smoke = []

        # Additional cars.

        if self.info.level % 2 == 0:
            self.red_cars.append(Computer((0, -1), (bx + 11, by + 54), Config.objects["car-red"], self))
            self.red_cars.append(Computer((0, -1), (bx + 19, by + 54), Config.objects["car-red"], self))

        if self.info.is_challenging_level():
            self.red_cars.append(Computer((0, 1), (bx + 13, by + 1), Config.objects["car-red"], self))
            self.red_cars.append(Computer((0, 1), (bx + 15, by + 1), Config.objects["car-red"], self))
            self.red_cars.append(Computer((0, 1), (bx + 17, by + 1), Config.objects["car-red"], self))

        # Groups.

        self.opponents = self.red_cars + self.rocks

        # Play status.

        self.bang = 0
        self.complete = 0
        self.draining_fuel = 0
        self.stopped = 0
        self.stopping = 0

        # Configure the information panel.

        self.info.start_life(self.player)

        # Additional configuration.

        if self.info.is_challenging_level():
            for red_car in self.red_cars:
                red_car.immobile = 1

    def end_life(self):
        self.info.end_life()
        stop_music()

    def place_flags(self, map, samples):
        flags = []
        specials = random.sample(range(0, len(samples[0])), 2)
        i = 0
        for x, y in self._place_objects(map, samples):
            if i == specials[0]:
                flag = Config.objects["flag-S"]
                flag_type = "S"
            elif i == specials[1]:
                flag = Config.objects["flag-L"]
                flag_type = "L"
            else:
                flag = Config.objects["flag"]
                flag_type = None
            flags.append(Flag(flag_type, (x, y), flag, self))
            i += 1
        return flags

    def place_rocks(self, map, samples):
        rocks = []
        for group, occurrence in zip(*samples):
            nfound = 0
            for y in range(0, Config.map_size[1]):
                y = y + Config.map_border[1]
                row = map[y]
                count = row.count(str(group))
                if occurrence < nfound + count:
                    x = nfound + count - occurrence - 1
                    index = row.index(str(group))
                    while x > 0:
                        index = row.index(str(group), index + 1)
                        x -= 1
                    rocks.append(Rock((index, y), Config.objects["rock"], self))
                    break
                nfound += count
        return rocks

    def _place_objects(self, map, samples):

        # Produce the objects as coordinates in the results list.

        results = []
        for y, x in zip(*samples):
            y = int(float(y)/10 * Config.map_size[1]) + Config.map_border[1]
            row = map[y]

            # Do not place objects in the start area.

            if Config.start_area_y[1] >= y >= Config.start_area_y[0]:
                count = (row[:Config.start_area_x[0]] + row[Config.start_area_x[1] + 1:]).count(" ")
            else:
                count = row.count(" ")

            x = int(float(x)/10 * count)
            index = row.index(" ")
            while x > 0:
                index = row.index(" ", index + 1)

                # Do not place objects in the start area.

                if y < Config.start_area_y[0] or index < Config.start_area_x[0] or index > Config.start_area_x[1]:
                    x -= 1
            results.append((index, y))

        return results

    def show(self):

        "Set up the screen with a view of the game."

        screen = self.screen
        screen.fill(Config.bgcolour)
        self.info.show()

    def update(self):

        """
        Refresh the game state, showing a view onto the scrolling map and any
        immediately visible game objects.
        """

        screen = self.screen.subsurface(pygame.Rect((0, 0), self.view_size))
        screen.fill(Config.bgcolour)

        map_x, offset_x, map_y, offset_y = exact_to_map(
            (self.player.position[0] - self.player_offset[0], self.player.position[1] - self.player_offset[1])
            )

        # NOTE: If the character or object size changes, the view size will
        # NOTE: change, resulting in a different number of map cells being shown
        # NOTE: and the possible need to review this.

        map_x_start, map_x_end = map_x, map_x + self.view_map_size[0] + 2 # includes extra column
        map_y_start, map_y_end = map_y, map_y + self.view_map_size[1] + 1

        # Start off the top with a partial row.

        blit_y = -offset_y

        for y in range(map_y_start, map_y_end):
            blit_x = -offset_x

            # Any partial leftmost column plus the remaining "guaranteed" columns.

            for x in range(map_x_start, map_x_end):
                self._blit_symbol(screen, x, y, blit_x, blit_y)
                blit_x += Config.object_size[0]

            blit_y += Config.object_size[1]

        # Show the game objects.

        for other in self.flags + self.smoke + self.opponents:
            other.blit(screen, self.player_centre, self.player.position)
        self.player.blit(screen, self.player_centre)

    def _blit_symbol(self, screen, x, y, blit_x, blit_y):

        """
        Missing cells should be avoided with a suitably big map, but not if the
        character or object size changes. One strategy is to use exceptions,
        possibly with a speed penalty:

        try:
            c = self.current_map[y][x]
        except IndexError:
            c = "*"
        """

        c = self.current_map[y][x]
        symbol = Config.symbols.get(c)
        image = Config.objects.get(symbol)
        if image is not None:
            screen.blit(image, (blit_x, blit_y))

    def check(self, position):
        map_x, offset_x, map_y, offset_y = exact_to_map(position)
        return self.check_map(map_x, map_y)

    def check_map(self, map_x, map_y):
        return self.current_map[map_y][map_x] in Config.space_or_group_symbols

    def make_smoke(self, position, direction):
        if not exact(position):
            return 0
        direction = Config.object_size[0]/2 + sign(-direction[0]) * Config.object_size[0], \
            Config.object_size[1]/2 + sign(-direction[1]) * Config.object_size[1]
        map_x, offset_x, map_y, offset_y = exact_to_map((position[0] + direction[0], position[1] + direction[1]))
        if self.check_map(map_x, map_y):
            self.smoke.append(Smoke((map_x, map_y), Config.objects["smoke"], self))
            return 1
        else:
            return 0

    def remove_smoke(self, smoke):
        self.smoke.remove(smoke)

    def flag_collected(self, flag):
        self.radar_flags.remove(flag)
        self.info.update_flag(flag)
        if flag.flag_type == "L" and self.radar_flags:
            self.draining_fuel = 1
            self.draining_fuel_level = self.player.fuel
        if not self.radar_flags:
            self.complete = 1

    def remove_flag(self, flag):
        self.flags.remove(flag)

    def player_collided(self, player, other):
        self.bang = 1

    def player_fuel_low(self, player):
        if self.info.is_challenging_level():
            for red_car in self.red_cars:
                red_car.immobile = 0
        self.stopping = 1

    def player_stopped(self, player):
        self.stopped = 1

    def collisions(self):
        participants = [self.player] + self.opponents + self.smoke + self.flags
        while participants:
            participant = participants[0]
            for other in participants[1:]:
                diff_x = participant.position[0] - other.position[0]
                diff_y = participant.position[1] - other.position[1]
                if abs(diff_x) < Config.object_size[0] and \
                    abs(diff_y) < Config.object_size[1]:
                    participant.collide(other, (sign(diff_x), sign(diff_y)))
                    other.collide(participant, (sign(-diff_x), sign(-diff_y)))
            participants.remove(participant)

    def switch_music(self):
        if self.stopping:
            if self.music == "fuel_theme":
                stop_music()
                return
            else:
                self.music = "fuel_theme"
        elif self.info.is_challenging_level():
            if self.music == "main_theme":
                self.music = "challenging_theme"
            elif self.music == "challenging_theme":
                self.music = "main_theme"
        play_music(self.music)

# Game objects.

class Object:

    "A generic game object supporting blitting and collisions."

    def __init__(self, position, image, game):
        self.position = map_to_exact(position)
        self.image = image
        self.game = game

    def blit(self, screen, centre, position=None):
        if position is not None:
            centre = (centre[0] + self.position[0] - position[0]), (centre[1] + self.position[1] - position[1])
        x = centre[0] - self.image.get_rect().width / 2
        y = centre[1] - self.image.get_rect().height / 2
        screen.blit(self.image, (x, y))

    def collide(self, other, rebound):
        pass

class Car(Object):

    """
    A car game object with additional support for autonomous movement, map wall
    detection and rotation.
    """

    def __init__(self, speed, direction, *args):
        Object.__init__(self, *args)

        self.speed = speed
        self.direction = (sign(direction[0]) * self.speed, sign(direction[1]) * self.speed)
        self.requested_direction = None
        self.angle = self._get_angle(self.direction)
        self.new_angle = self.angle
        self.angle_step = 0

    def _get_angle(self, direction):
        return (sign(direction[0]) * -90 + (sign(direction[1]) + 1) / 2 * 180) % 360

    def _set_angle_step(self, angle):
        da = (angle - self.angle) % 360
        if da > 180:
            self.angle_step = 15 * -sign(da)
        else:
            self.angle_step = 15 * sign(da)

    def blit(self, screen, centre, position=None):
        rotated = pygame.transform.rotate(self.image, self.angle)
        if position is not None:
            centre = (centre[0] + self.position[0] - position[0]), (centre[1] + self.position[1] - position[1])
        x = centre[0] - rotated.get_rect().width / 2
        y = centre[1] - rotated.get_rect().height / 2
        screen.blit(rotated, (x, y))

    def opposite(self, direction):
        return direction[0] == -self.direction[0] and direction[1] == -self.direction[1]

    def detect(self, position, direction):
        x1, y1 = position
        x2, y2 = x1 + Config.object_size[0] - 1, y1 + Config.object_size[1] - 1
        dx, dy = direction

        if dy == 0:
            new_x1, new_x2 = x1 + dx, x2 + dx
            if dx < 0:
                if self.game.check((new_x1, y1)) and self.game.check((new_x1, y2)):
                    return new_x1, y1
            else:
                if self.game.check((new_x2, y1)) and self.game.check((new_x2, y2)):
                    return new_x1, y1
        else:
            new_y1, new_y2 = y1 + dy, y2 + dy
            if dy < 0:
                if self.game.check((x1, new_y1)) and self.game.check((x2, new_y1)):
                    return x1, new_y1
            else:
                if self.game.check((x1, new_y2)) and self.game.check((x2, new_y2)):
                    return x1, new_y1

        return None

    def move(self, direction):
        position = self.detect(self.position, direction)
        if position is not None:
            self.position = position
            return 1
        else:
            return 0

    def move_to_exact(self, direction):
        map_x, offset_x, map_y, offset_y = exact_to_map(self.position)
        if offset_x == 0 and offset_y == 0:
            return 0

        dx, dy = direction

        if dy == 0:
            if divmod(offset_x + dx, Config.object_size[0])[0] == 0:
                return 0
            if dx > 0:
                map_x += 1
        else:
            if divmod(offset_y + dy, Config.object_size[1])[0] == 0:
                return 0
            if dy > 0:
                map_y += 1

        position = map_to_exact((map_x, map_y))
        self.position = position
        return 1

    def _get_turns(self):
        transposed = self.direction[1], self.direction[0]
        transposed_angle = self._get_angle(transposed)
        return [
            (transposed, transposed_angle),
            ((-self.direction[1], -self.direction[0]), (transposed_angle + 180) % 360),
            ((-self.direction[0], -self.direction[1]), (self.new_angle + 180) % 360)
            ]

    def _update_turns(self, turns):
        if random.randint(0, 1):
            turns.insert(0, turns[1])
            del turns[2]

    def update(self):

        "Update the position of the car."

        # If a direction change is requested and the car is either reversing its
        # direction or is in an exact map cell (thus being able to safely move
        # up/down/across) and if such a move is possible, then change the
        # direction.

        if self.requested_direction is not None and (self.opposite(self.requested_direction) or exact(self.position)) and \
            self.move(self.requested_direction):

            self.direction = self.requested_direction
            self.new_angle = self._get_angle(self.direction)
            self._set_angle_step(self.new_angle)
            self.requested_direction = None

        # Otherwise, if a direction change could not be executed, attempt to put
        # the car onto the next exact map cell, provided it is close enough to
        # do so.

        elif self.requested_direction is not None and self.move_to_exact(self.direction):
            pass

        # If the car cannot be moved in its normal direction and it cannot be
        # placed on the next exact map cell, evaluate other directions.

        elif not self.move(self.direction) and not self.move_to_exact(self.direction):

            # Get a list of possible "turns".

            turns = self._get_turns()

            # Vary the choices somewhat.

            self._update_turns(turns)

            # Choose a new automatic direction.

            for direction, angle in turns:
                self._set_angle_step(angle)
                if self.move(direction):
                    break

            self.new_angle = angle
            self.direction = direction

        # Update the car's current angle until the target angle is reached.

        if self.angle != self.new_angle:
            self.angle = (self.angle + self.angle_step) % 360
        else:
            self.angle_step = 0

class Player(Car):

    """
    A player version of the car game object, with user control and specialised
    collision routines, along with fuel usage and smoke production support.
    """

    radar_colour = (255, 255, 255)
    fuel_full_colour = (255, 255, 0)
    fuel_empty_colour = (255, 0, 0)

    def __init__(self, *args):
        Car.__init__(self, Config.car_speed, (0, -1), *args)
        self.fuel_colour = self.fuel_full_colour
        self.more_smoke = 0
        self.initial_speed = self.speed

    def control(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in Config.left_buttons:
                self.requested_direction = (-self.speed, 0)
            elif event.key in Config.right_buttons:
                self.requested_direction = (self.speed, 0)
            elif event.key in Config.up_buttons:
                self.requested_direction = (0, -self.speed)
            elif event.key in Config.down_buttons:
                self.requested_direction = (0, self.speed)
            elif event.key in Config.smoke_buttons:
                if self.more_smoke == 0:
                    self.more_smoke = 3

    def collide(self, other, rebound):
        if isinstance(other, Computer) or isinstance(other, Rock):
            self.game.player_collided(self, other)
            self.image = Config.objects["bang"]
            self.angle = 0

    def update_fuel(self, n):
        if self.fuel > 0:
            if self.fuel > self.fuel_empty:
                self.fuel = max(0, self.fuel - n)
                if self.fuel <= self.fuel_empty:
                    self.fuel_colour = self.fuel_empty_colour
                    self.update_direction()
                    self.game.player_fuel_low(self)
            else:
                self.fuel = max(0, self.fuel - n)
                self.speed = int(float(self.fuel) / self.fuel_empty * self.initial_speed)

            if self.fuel == 0:
                self.game.player_stopped(self)

    def update_direction(self):
        self.direction = sign(self.direction[0]) * self.speed, sign(self.direction[1]) * self.speed

    def update(self):
        self.update_fuel(1)
        if self.more_smoke and self.fuel > self.fuel_empty:
            if self.game.make_smoke(self.position, self.direction):
                self.update_fuel(Config.smoke_penalty)
                self.more_smoke -= 1
        Car.update(self)

class DemoPlayer(Player):

    """
    A computer-controlled version of the player game object, with simple flag
    seeking behaviour. Instead of using the Computer class, we re-use most of
    the Player class, mostly for the fuel, score and crashing behaviour,
    overriding only the control method (there is no way to independently control
    the car) and augmenting the update method (for an alternative to control
    which works without events).
    """

    def __init__(self, *args):
        Player.__init__(self, *args)
        self.laziness = 8
        self.nearest_flag = None
        self.nearest_red_car = None

    def _get_distances(self, objects):
        distances = []
        for obj in objects:
            x, y = obj.position[0], obj.position[1]
            dx = x - self.position[0]
            dy = y - self.position[1]
            distances.append((math.sqrt(dx ** 2 + dy ** 2), obj))
        distances.sort()
        return distances

    def _retarget(self, old, new):
        if old is not None:
            old.targeted = 0
        new.targeted = 1
        return new

    def control(self, event):
        pass

    def update(self):

        """
        A complicated update method which attempts to make the demo player
        moderately intelligent, looking for the nearest flag whilst avoiding the
        nearest car.
        """

        if not random.randint(0, self.laziness):

            # Get the flag distances and objects.

            distances = self._get_distances(self.game.flags)
            distance, nearest_flag = distances[0]
            destination = nearest_flag.position
            self.nearest_flag = self._retarget(self.nearest_flag, nearest_flag)

            # Get the car distances and objects.

            distances = self._get_distances(self.game.red_cars)
            red_car_distance, nearest_red_car = distances[0]
            non_destination = nearest_red_car.position
            self.nearest_red_car = self._retarget(self.nearest_red_car, nearest_red_car)

            # Work out if the nearest car is in range.

            if red_car_distance < Config.object_size[0] * 5:
                if self.more_smoke == 0:
                    self.more_smoke = 3
                red_car_in_range = 1
            else:
                red_car_in_range = 0

            # Work out preferred and non-preferred directions.

            dir_x = sign(destination[0] - self.position[0])
            dir_y = sign(destination[1] - self.position[1])
            non_dir_x = sign(non_destination[0] - self.position[0])
            non_dir_y = sign(non_destination[1] - self.position[1])

            # Vertical motion...

            if self.direction[0] == 0:

                # Evasive action, reversing vertical direction of motion.

                if non_dir_y == sign(self.direction[1]) and red_car_in_range and -1 <= self.position[0] - non_destination[0] <= 1:
                    self.requested_direction = (0, -non_dir_y * self.speed)

                # Request horizontal motion in the direction of the flag.

                elif dir_y == sign(self.direction[1]):
                    if dir_x > 0:
                        self.requested_direction = (self.speed, 0)
                    elif dir_x < 0:
                        self.requested_direction = (-self.speed, 0)

            # Horizontal motion...

            elif self.direction[1] == 0:

                # Evasive action, reversing horizontal direction of motion.

                if non_dir_x == sign(self.direction[0]) and red_car_in_range and -1 <= self.position[1] - non_destination[1] <= 1:
                    self.requested_direction = (-non_dir_x * self.speed, 0)

                # Request vertical motion in the direction of the flag.

                elif dir_x == sign(self.direction[0]):
                    if dir_y > 0:
                        self.requested_direction = (0, self.speed)
                    elif dir_y < 0:
                        self.requested_direction = (0, -self.speed)

        Player.update(self)

class Computer(Car):

    """
    A computer-controlled version of the car game object, with simple player
    seeking behaviour.
    """

    radar_colour = (255, 0, 0)

    def __init__(self, direction, *args):
        Car.__init__(self, Config.car_speed + Config.computer_speed_advantage, direction, *args)
        self.immobile = 0
        self.delay = 50
        self.rebound_direction = None
        self.smoked = 0
        self.laziness = 5

    def update(self):
        if self.delay > 0:
            self.delay -= 1
            if self.rebound_direction is not None:
                if self.smoked:
                    self.angle += self.angle_step
                if self.delay == 0:
                    self.direction = self.rebound_direction
                    self.new_angle = self._get_angle(self.direction)
                    self._set_angle_step(self.new_angle)
                    self.position = self.position[0] + self.direction[0], self.position[1] + self.direction[1]
                    self.rebound_direction = None
                    self.smoked = 0
        elif self.immobile:
            pass
        else:
            Car.update(self)

    def control(self):
        if self.delay > 0 or random.randint(0, self.laziness):
            return

        dir_x = sign(self.game.player.position[0] - self.position[0])
        dir_y = sign(self.game.player.position[1] - self.position[1])

        if self.direction[0] == 0:
            if dir_y != sign(self.direction[1]):
                if dir_x > 0:
                    self.requested_direction = (self.speed, 0)
                else:
                    self.requested_direction = (-self.speed, 0)
        elif self.direction[1] == 0:
            if dir_x != sign(self.direction[0]):
                if dir_y > 0:
                    self.requested_direction = (0, self.speed)
                else:
                    self.requested_direction = (0, -self.speed)

    def collide(self, other, rebound):
        if isinstance(other, Flag):
            return
        if self.delay == 0:
            self.delay = 50
            self.rebound_direction = rebound[0] * abs(self.direction[0]), rebound[1] * abs(self.direction[1])
            self.requested_direction = None
            self.smoked = isinstance(other, Smoke) or isinstance(other, Rock)
            if self.smoked and self.angle_step == 0:
                self.angle_step = sign(self.direction[0] + self.direction[1]) * 15

class Flag(Object):

    "A flag game object which awards points to players who collect it."

    radar_colour = (255, 255, 0)

    def __init__(self, flag_type, *args):
        Object.__init__(self, *args)
        self.flag_type = flag_type
        self.timer = None

    def collide(self, other, rebound):
        if self.timer is not None:
            return
        if isinstance(other, Player):
            self.timer = 50
            self.game.flag_collected(self)

    def update(self):
        if self.timer is not None:
            self.timer -= 1
            if self.timer == 0:
                self.game.remove_flag(self)

class Smoke(Object):

    "A smoke game object which exists for a short period of time."

    def __init__(self, *args):
        Object.__init__(self, *args)
        self.remaining = 50

    def update(self):
        if self.remaining > 0:
            self.remaining -= 1
        else:
            self.game.remove_smoke(self)

class Rock(Object):

    "A rock game object whose only purpose is to participate in collisions."

    pass

# Concrete game classes.

class Game(GameEngine):

    "The actual game involving a real player."

    player_class = Player

    def handle_events(self, in_game):
        for event in pygame.event.get():
            if quit_requested(event):
                return QUIT_GAME
            elif coin_inserted(event):
                Config.credits += 1
            elif music_ended(event):
                if in_game:
                    self.switch_music()
                else:
                    return END_SEQUENCE
            elif snapshot_requested(event):
                save_screen(self.screen)
            elif in_game and not self.bang:
                self.player.control(event)
        return None

    def mainloop(self):

        """
        Monitor game events and return control to the caller when requested or
        when the current game is finished.
        """

        screen = self.screen

        self.start_level()
        intro = 1

        # Main game loop.

        while self.info.lives > 0:
            self.show()
            pygame.display.flip()
            set_next_screen(0)

            pygame.event.clear()
            self.start_life()

            # Set up the screen.

            self.info.update(self.red_cars + self.radar_flags + [self.player])
            self.update()
            pygame.display.flip()

            # Intro loop.

            if intro and not Config.skip_intros:
                self.music = "intro_theme"
                play_music(self.music)

                # Repeat until the music is finished.

                while 1:
                    Config.clock.tick(Config.framerate)
                    status = self.handle_events(0)
                    if status is not None:
                        stop_music()
                        if status == END_SEQUENCE:
                            break
                        self.info.end_game()
                        return status

                intro = 0
            else:
                pygame.time.delay(1000)

            self.music = "main_theme"
            play_music(self.music)

            # Repeat until a definitive outcome.

            while not self.bang and not self.complete and not self.stopped:
                Config.clock.tick(Config.framerate)
                status = self.handle_events(1)
                if status is not None:
                    self.info.end_game()
                    stop_music()
                    return status

                if not self.draining_fuel:
                    if not self.bang:
                        self.player.update()
                        for red_car in self.red_cars:
                            red_car.control()
                            red_car.update()
                        for smoke in self.smoke:
                            smoke.update()
                        for flag in self.flags:
                            flag.update()
                        self.info.update(self.red_cars + self.radar_flags + [self.player])
                        self.collisions()
                    self.update()
                else:
                    self.draining_fuel = self.info.drain_fuel()
                    if not self.draining_fuel:
                        self.player.fuel = self.draining_fuel_level

                pygame.display.flip()

            # Show the outcome.

            stop_music()

            # Test for fatal outcomes.

            if self.bang or self.stopped:
                self.end_life()

            # It is technically possible to lose a life whilst getting the last
            # flag.

            if self.complete:

                # Repeat until the fuel is drained.

                while self.info.drain_fuel():
                    Config.clock.tick(Config.framerate)
                    status = self.handle_events(0)
                    if status is not None:
                        if status != END_SEQUENCE:
                            self.info.end_game()
                            return status
                    pygame.display.flip()

                self.next_level()
                self.start_level()

                # Interlude.

                if self.info.is_challenging_level() and not Config.skip_intros:
                    challenging = Challenging(self.ncars, len(self.rocks), self.screen, self.info)
                    pygame.display.flip()

                    # Enter the interlude.

                    status = challenging.mainloop()
                    if status is not None:
                        stop_music()
                        if status != END_SEQUENCE:
                            self.info.end_game()
                            return status

            pygame.time.delay(2000)

        self.info.end_game()
        stop_music()
        return GAME_OVER

class Demo(GameEngine):

    "The demo/attract mode."

    player_class = DemoPlayer

    def handle_events(self, in_game):
        for event in pygame.event.get():
            if quit_requested(event):
                return QUIT_PRESENTATION
            elif reset_requested(event):
                return RESET_DISPLAY
            elif help_requested(event):
                return SHOW_HELP
            elif coin_inserted(event):
                Config.credits += 1
                return SHOW_START
            elif snapshot_requested(event):
                save_screen(self.screen)
            elif in_game and not self.bang:
                self.player.control(event)
        return None

    def mainloop(self):

        """
        Monitor game events and return control to the caller when requested or
        when the demo is finished.
        """

        screen = self.screen

        self.start_level()

        # Main demo activity - only one "life" is available.

        demo_timer = 0

        self.show()
        pygame.display.flip()
        set_next_screen(0)

        pygame.event.clear()
        self.start_life()

        # Set up the screen.

        self.info.update(self.red_cars + self.radar_flags + [self.player])
        self.update()
        pygame.display.flip()

        # Repeat until a definitive outcome.

        while not self.bang and not self.complete and not self.stopped and demo_timer < Config.demo_timer_limit:
            demo_timer += 1

            Config.clock.tick(Config.framerate)
            status = self.handle_events(1)
            if status is not None:
                self.info.end_game()
                return status

            if not self.draining_fuel:
                if not self.bang:
                    self.player.update()
                    for red_car in self.red_cars:
                        red_car.control()
                        red_car.update()
                    for smoke in self.smoke:
                        smoke.update()
                    for flag in self.flags:
                        flag.update()
                    self.info.update(self.red_cars + self.radar_flags + [self.player])
                    self.collisions()
                self.update()
            else:
                self.draining_fuel = self.info.drain_fuel()
                if not self.draining_fuel:
                    self.player.fuel = self.draining_fuel_level

            pygame.display.flip()

        pygame.time.delay(1000)

        return SHOW_TITLES

# Main program and associated functions.

def mainloop(screen, new_volume=None):

    """
    Run the game with the given 'screen', setting the 'new_volume' if
    specified. Return whether the game has been quit.
    """

    init(screen)
    if Config.have_audio:
        volume = pygame.mixer.music.get_volume()

    try:
        pygame.key.set_repeat(Config.repeat_delay, Config.repeat_interval)
        if Config.have_audio and new_volume is not None:
            pygame.mixer.music.set_volume(new_volume)

        info = Info(screen)
        titles = Titles(screen, info)
        instructions = Instructions(screen, info)
        start = Start(screen, info)
        game_over = GameOver(screen, info)
        high_score = HighScore(screen, info)

        # According to the system state, acquire a handler and invoke its
        # mainloop.

        handler = titles
        while 1:
            status = handler.mainloop()
            if status == QUIT_PRESENTATION:
                return 1
            elif status == RESET_DISPLAY:
                return 0
            elif status == SHOW_HELP:
                handler = Help(screen)
            elif status == START_GAME:
                handler = Game(screen, info)
            elif status == START_DEMO:
                handler = Demo(screen, info)
            elif status == QUIT_GAME:
                Config.credits = 0
                handler = titles
            elif status == END_GAME:
                if Config.credits > 0:
                    handler = start
                else:
                    handler = titles
            elif status == GAME_OVER:
                if info.new_hi_score:
                    handler = high_score
                    info.new_hi_score = 0 # Necessary to make the handler go away
                else:
                    handler = game_over
            elif status == SHOW_TITLES:
                handler = titles
            elif status == SHOW_START:
                handler = start
            elif status == SHOW_INSTRUCTIONS:
                handler = instructions

    finally:
        if Config.have_audio:
            pygame.mixer.music.set_volume(volume)

def main():
    pygame.init()

    Config.have_audio = not ("--no-audio" in sys.argv)
    if Config.have_audio:
        try:
            pygame.mixer.init()
        except pygame.error:
            Config.have_audio = 0

    if "--fullscreen" in sys.argv:
        set_fullscreen()
    else:
        set_window()

    if "--halfsize" in sys.argv or "--small" in sys.argv:
        set_small_screen()
    elif "--medium" in sys.argv:
        set_medium_screen()

    Config.sound = Config.have_audio and not ("--no-sound" in sys.argv)
    if not Config.sound:
        volume = 0
    else:
        volume = None

    Config.skip_intros = ("--no-intros" in sys.argv)

    Config.clock = pygame.time.Clock()

    while 1:
        screen = pygame.display.set_mode(Config.screen_size, Config.screen_flags)
        if mainloop(screen, volume):
            break

if __name__ == "__main__":
    main()

# vim: tabstop=4 expandtab shiftwidth=4
