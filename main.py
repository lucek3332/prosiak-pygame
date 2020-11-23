import pygame
from pygame import mixer
from math import hypot
import random
import pandas as pd


pygame.init()

# FPS
FPS = 60
fpsClock = pygame.time.Clock()

# Uploaded images
background = pygame.image.load("images/background.png")
icon = pygame.image.load("images/icon.png")
pig_img = pygame.image.load("images/pig.png")
pig50_img = pygame.image.load("images/pig50.png")
pig100_img = pygame.image.load("images/pig100.png")
elephant_img = pygame.image.load("images/elephant.png")
elephant50_img = pygame.image.load("images/elephant50.png")
elephant100_img = pygame.image.load("images/elephant100.png")
cow_img = pygame.image.load("images/cow.png")
cow50_img = pygame.image.load("images/cow50.png")
cow100_img = pygame.image.load("images/cow100.png")
apple_img = pygame.image.load("images/apple.png")
wolf_img = pygame.image.load("images/wolf.png")

# Uploaded images of character avatars
pig_icon = pygame.image.load("images/pig_icon.png")
elephant_icon = pygame.image.load("images/elephant_icon.png")
cow_icon = pygame.image.load("images/cow_icon.png")

# Uploaded sounds / music
pig_sound = mixer.Sound("sounds/pig.wav")
elephant_sound = mixer.Sound("sounds/elephant.wav")
cow_sound = mixer.Sound("sounds/cow.wav")
apple_chew = mixer.Sound("sounds/apple.wav")
mixer.music.load("sounds/music.wav")
mixer.music.play(-1)

# General settings
screen_width = 998
screen_height = 590
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Prosiak vs Jabłka")
pygame.display.set_icon(icon)
status_game = "menu"  # menu, ranking, player, char_select, play or over

# Database - best scores
best_scores = pd.read_csv("database/scores.csv")


class Button:
    """
    Class for handling buttons in game.
    """
    # Class attributes
    button_font = pygame.font.Font("fonts/Bangers-Regular.ttf", 32)

    def __init__(self, width, height, color, string, x, y):
        """
        Init the Button instance.
        :param width: int
        :param height: int
        :param color: tuple
        :param string: string
        :param x: int
        :param y: int
        """
        self.width = width
        self.height = height
        self.color = color
        self.string = string
        self.x = x
        self.y = y

    def draw(self, win):
        """
        Method for drawing the button with rectangular background.
        :param win: pygame Surface instance
        :return: None
        """
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        win.blit(self.button_font.render("{}".format(self.string), True, (255, 255, 255)),
                 (round(self.x + self.width / 2 - len(self.string) * 7), round(self.y + self.height / 2 - 16)))

    def on_button(self, pos):
        """
        Method for checking the mouse position relative to the button.
        :param pos: tuple
        :return: boolean
        """
        if self.x <= pos[0] <= self.x + self.width:
            if self.y <= pos[1] <= self.y + self.height:
                return True
        return False


class Avatar:
    """
    Class for handling avatars of characters.
    """
    # Class attributes
    color = (217, 28, 22)
    width = 220
    height = 220
    font = pygame.font.Font("fonts/Bangers-Regular.ttf", 32)
    avatars = []

    def __init__(self, character, x, y, icon):
        """
        Init the Avatar instance.
        :param character: string, character name
        :param x: int
        :param y: int
        :param icon: pygame Surface instance, image of character
        """
        self.character = character
        self.x = x
        self.y = y
        self.icon = icon
        Avatar.avatars.append(self)

    def draw(self, win):
        """
        Method for drawing the avatar on the screen with rectangular background.
        :param win: pygame Surface instance
        :return: None
        """
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        win.blit(self.icon, (round(self.x + self.width / 2 - 64), round(self.y + 20)))
        win.blit(self.font.render("{}".format(self.character.name), True, (255, 255, 255)),
                 (round(self.x + self.width / 2 - len(self.character.name) * 7),
                  round(self.y + self.height / 2 + 60)))

    def on_avatar(self, pos):
        """
        Method for checking mouse position relative to the avatar.
        :param pos: tuple
        :return: boolean
        """
        if self.x <= pos[0] <= self.x + self.width:
            if self.y <= pos[1] <= self.y + self.height:
                return True
        return False


class InputString:
    """
    Class for handling the input from the user.
    """

    def __init__(self):
        """
        Init the InputString instance.
        """
        self.string = ""

    def add_letter(self, char):
        """
        Method for adding specific letter.
        :param char: string
        :return: None
        """
        self.string += char

    def remove_letter(self):
        """
        Method for removing last letter.
        :return: None
        """
        if len(self.string) >= 1:
            self.string = self.string[:-1]
        else:
            self.reset()

    def reset(self):
        """
        Method for resetting the input string.
        :return: None
        """
        self.string = ""

    def get_string(self):
        """
        Method for getting the input string.
        :return: string
        """
        return self.string


class ScoreClass:
    """
    Class for handling the game score.
    """
    # Class attributes
    font = pygame.font.Font("fonts/Bangers-Regular.ttf", 32)

    def __init__(self, x, y, value):
        """
        Init the ScoreClass instance.
        :param x: int
        :param y: int
        :param value: int
        """
        self.x = x
        self.y = y
        self.value = value

    def draw(self, win):
        """
        Method for drawing the score.
        :param win: pygame Surface instance
        :return: None
        """
        self.isCorrect()
        win.blit(self.font.render("Score: {}".format(self.value), True, (255, 255, 255)), (self.x, self.y))

    def isCorrect(self):
        """
        Setting the score to 0, if the score was negative.
        :return: None
        """
        if self.value < 0:
            self.value = 0


class Character:
    """
    Class for handling main character.
    """

    def __init__(self, width, height, img, img50, img100, icon, x, y, vel, name, sound, collision_dist):
        """
        Init the Character instance.
        :param width: int
        :param height: int
        :param img: pygame Surface instance, small image of character
        :param img50: pygame Surface instance, bigger image of character
        :param img100: pygame Surface instance, the biggest image of character
        :param icon: pygame Surface instance, avatar of character
        :param x: int
        :param y: int
        :param vel: int, velocity of character
        :param name: string
        :param sound: pygame Sound object
        :param collision_dist: int, distance for hitbox
        """
        self.width = width
        self.height = height
        self.img = img
        self.img50 = img50
        self.img100 = img100
        self.icon = icon
        self.display = self.img
        self.x = x
        self.y = y
        self.vel = vel
        self.status = "small"
        self.name = name
        self.sound = sound
        self.collision_dist = collision_dist

    def draw(self, win, score):
        """
        Method for drawing the character on the screen during gameplay.
        :param win: pygame Surface instance
        :param score: int
        :return: None
        """
        # Boundaries of character movement
        if self.x < 0:
            self.x = 0
        if self.x >= 930:
            self.x = 930
        if self.y < 0:
            self.y = 0
        if self.y >= 530:
            self.y = 530
        # Checking which image should be used (small, bigger, the biggest)
        self.get_bigger(score)
        win.blit(self.display, (self.x, self.y))

    def get_bigger(self, score):
        """
        Setting attributes for correct values depending on the score value.
        :param score: int
        :return: None
        """
        # Small character
        if score < 50:
            self.status = "small"
            self.vel = 4
            self.collision_dist = 40
            self.display = self.img
        # Bigger character
        if score >= 50 and self.status == "small":
            self.status = "big"
            self.vel -= 1
            self.collision_dist += 15
            self.display = self.img50
        # The biggest character
        elif score >= 100 and self.status == "big":
            self.status = "very big"
            self.vel -= 1
            self.collision_dist += 10
            self.display = self.img100

    def isCollision(self, obj):
        """
        Detecting collision of the character with other object.
        :param obj: Enemy or StaticObjects instance
        :return: boolean
        """
        distance = hypot((self.x - obj.x), (self.y - obj.y))
        if distance <= self.collision_dist:
            return True
        return False

    def superpower(self):
        """
        Using superpower by the character.
        Turning the moving direction of the wolves.
        :return: None
        """
        self.sound.play()
        for e in Enemy.enemies:
            e.direction_y = -e.direction_y
            e.delta_x = -e.delta_x


class Enemy:
    """
    Class for handling wolf.
    """
    # Class attributes
    enemies = []
    count = 0

    def __init__(self, width, height, img, x, y, delta_x, delta_y, direction_y):
        """
        Init the Enemy instance.
        Appending the wolf to wolves list.
        :param width: int
        :param height: int
        :param img: pygame Surface instance, image of wolf
        :param x: int
        :param y: int
        :param delta_x: int, horizontal velocity
        :param delta_y: int, vertical velocity
        :param direction_y: int, direction of vertical movement
        """
        self.width = width
        self.height = height
        self.img = img
        self.x = x
        self.y = y
        self.delta_x = delta_x
        self.delta_y = delta_y
        self.direction_y = direction_y
        Enemy.enemies.append(self)
        Enemy.count += 1

    def draw(self, win):
        """
        Method for drawing the wolf on the screen.
        :param win: pygame Surface instance
        :return: None
        """
        # Enemy movement boundaries
        if self.x < 0:
            self.x = 0
            self.delta_x = 3
            self.y += self.direction_y * self.delta_y
        if self.x >= 930:
            self.x = 930
            self.delta_x = -3
            self.y += self.direction_y * self.delta_y
        if self.y < 0:
            self.y = 0
            self.direction_y = 1
        if self.y >= 530:
            self.y = 530
            self.direction_y = -1
        self.x += self.delta_x
        win.blit(self.img, (self.x, self.y))


class StaticObject:
    """
    Class for handling apple.
    """
    # Class attributes
    objects = []
    count = 0

    def __init__(self, width, height, img, x, y, sound):
        """
        Init the StaticObject instance.
        Appending the apple to apples list.
        :param width: int
        :param height: int
        :param img: pygame Surface instance
        :param x: int
        :param y: int
        :param sound: pygame Sound instance
        """
        self.width = width
        self.height = height
        self.img = img
        self.x = x
        self.y = y
        self.sound = sound
        StaticObject.objects.append(self)
        StaticObject.count += 1

    def draw(self, win):
        """
        Method for drawing apple on the screen.
        :param win: pygame Surface instace
        :return: None
        """
        win.blit(self.img, (self.x, self.y))


# Definitions of drawing functions
def draw_menu():
    """
    Function for drawing main menu.
    :return: None
    """
    # Background
    screen.fill((43, 117, 237))
    # Drawing buttons
    new_game_button.draw(screen)
    ranking_button.draw(screen)
    quit_button.draw(screen)
    # Update pygame window
    pygame.display.update()


def draw_ranking():
    """
    Function for drawing top 5 ranking.
    :return: None
    """
    # Background
    screen.fill((43, 117, 237))
    ranking_font = pygame.font.Font("fonts/Bangers-Regular.ttf", 32)
    # Drawing subsequent places in the ranking
    for indx, series in best_scores.iterrows():
        if indx == 0:
            ranking_font_color = (232, 176, 23)
        elif indx == 1:
            ranking_font_color = (184, 179, 174)
        elif indx == 2:
            ranking_font_color = (125, 86, 47)
        else:
            ranking_font_color = (255, 255, 255)
        screen.blit(ranking_font.render(str(indx + 1), True, ranking_font_color), (350, 100 + indx * 60))
        screen.blit(ranking_font.render(series.Name, True, ranking_font_color), (400, 100 + indx * 60))
        screen.blit(ranking_font.render(str(series.Score), True, ranking_font_color), (650, 100 + indx * 60))
    # Drawing buttons
    back_button.draw(screen)
    # Update pygame window
    pygame.display.update()


def draw_player_menu():
    """
    Function for drawing username.
    :return: None
    """
    # Background
    screen.fill((43, 117, 237))
    # Drawing buttons
    new_player_button = Button(200, 80, (217, 28, 22), player_name.get_string(), 400, 250)
    new_player_button.draw(screen)
    type_name_button.draw(screen)
    ok_button.draw(screen)
    # Update pygame window
    pygame.display.update()


def draw_char_select():
    """
    Function for drawing the character select menu.
    :return: None
    """
    # Background
    screen.fill((43, 117, 237))
    # Drawing avatars
    for av in Avatar.avatars:
        av.draw(screen)
    # Update pygame window
    pygame.display.update()


def draw_game_over():
    """
    Function for drawing game over menu.
    :return: None
    """
    game_over_font = pygame.font.Font("fonts/Bangers-Regular.ttf", 64)
    # Background
    screen.fill((43, 117, 237))
    # Info message
    screen.blit(game_over_font.render("GAME OVER", True, (255, 255, 255)), (400, 250))
    # Drawing buttons
    play_again_button.draw(screen)
    quit_button2.draw(screen)
    # Drawing score
    score.draw(screen)
    # Update pygame window
    pygame.display.update()


def draw_game_window():
    """
    Function for drawing gameplay window.
    :return: None
    """
    # Background
    screen.blit(background, (0, 0))
    # Drawing character
    main_char.draw(screen, score.value)
    # Drawing score
    score.draw(screen)
    # Drawing wolves
    for wolf in Enemy.enemies:
        wolf.draw(screen)
    # Drawing apples
    for apple in StaticObject.objects:
        apple.draw(screen)
    # Update pygame window
    pygame.display.update()


# Buttons
new_game_button = Button(200, 80, (217, 28, 22), "NEW GAME", 400, 150)
ranking_button = Button(200, 80, (217, 28, 22), "RANKING", 400, 250)
quit_button = Button(200, 80, (217, 28, 22), "QUIT", 400, 350)
play_again_button = Button(200, 80, (217, 28, 22), "PLAY AGAIN", 425, 350)
quit_button2 = Button(200, 80, (217, 28, 22), "QUIT", 425, 450)
type_name_button = Button(200, 60, (43, 117, 237), "TYPE YOUR NAME:", 420, 180)
ok_button = Button(200, 80, (217, 28, 22), "OK", 400, 350)
back_button = Button(200, 80, (217, 28, 22), "BACK", 400, 450)

# Characters
pig = Character(64, 64, pig_img, pig50_img, pig100_img, pig_icon, 400, 350, 4, "Pig", pig_sound, 40)
elephant = Character(64, 64, elephant_img, elephant50_img, elephant100_img, elephant_icon, 400, 350, 4, "Elephant",
                     elephant_sound, 40)
cow = Character(64, 64, cow_img, cow50_img, cow100_img, cow_icon, 400, 350, 4, "Cow", cow_sound, 40)

# Avatars
pig_avatar = Avatar(pig, 100, 100, pig_icon)
elephant_avatar = Avatar(elephant, 400, 100, elephant_icon)
cow_avatar = Avatar(cow, 700, 100, cow_icon)

# Player name
player_name = InputString()

# Main character
main_char = cow

# Enemies
wolf = Enemy(64, 64, wolf_img, random.randint(150, 900), random.randint(10, 100), 3, 40, 1)

# Static objects
num_of_apples = 5
for _ in range(num_of_apples):
    apple = StaticObject(64, 64, apple_img, random.randint(50, 900), random.randint(50, 520), apple_chew)

# Score
score = ScoreClass(10, 10, 0)

# Game loop
run = True

while run:

    # Menu
    if status_game == "menu":
        pos = pygame.mouse.get_pos()
        draw_menu()
        # Controls
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if new_game_button.on_button(pos):
                    status_game = "player"
                elif ranking_button.on_button(pos):
                    status_game = "ranking"
                elif quit_button.on_button(pos):
                    run = False

    # Ranking
    elif status_game == "ranking":
        draw_ranking()
        pos = pygame.mouse.get_pos()
        # Controls
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.on_button(pos):
                    status_game = "menu"

    # Player name
    elif status_game == "player":
        draw_player_menu()
        pos = pygame.mouse.get_pos()
        # Controls
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if ok_button.on_button(pos):
                    status_game = "char_select"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    player_name.remove_letter()
                elif event.key == 13 or event.key == pygame.K_KP_ENTER:
                    status_game = "char_select"
                elif event.unicode:
                    player_name.add_letter(event.unicode)

    # Character selection
    elif status_game == "char_select":
        pos = pygame.mouse.get_pos()
        draw_char_select()
        # Controls
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pig_avatar.on_avatar(pos):
                    main_char = pig
                    status_game = "play"
                elif elephant_avatar.on_avatar(pos):
                    main_char = elephant
                    status_game = "play"
                elif cow_avatar.on_avatar(pos):
                    main_char = cow
                    status_game = "play"

    # Game
    elif status_game == "play":
        # Pressed keys of keyboard
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            main_char.x -= main_char.vel
        if keys[pygame.K_RIGHT]:
            main_char.x += main_char.vel
        if keys[pygame.K_UP]:
            main_char.y -= main_char.vel
        if keys[pygame.K_DOWN]:
            main_char.y += main_char.vel

        # Controls
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    main_char.superpower()
                    score.value -= 1

        draw_game_window()

        # Collision with apples / new apple at random place
        for apple in StaticObject.objects:
            if main_char.isCollision(apple):
                apple.sound.play()
                StaticObject.objects.pop(StaticObject.objects.index(apple))
                score.value += 1
                new_apple = StaticObject(64, 64, apple_img, random.randint(50, 900), random.randint(50, 520), apple_chew)

        # Additional enemies
        if score.value >= (10 * Enemy.count):
            new_wolf = Enemy(64, 64, wolf_img, random.randint(150, 900), random.randint(10, 100), 3, 40, 1)

        # Game over - checking collision with wolves
        for wolf in Enemy.enemies:
            if main_char.isCollision(wolf):
                status_game = "over"
                # Saving scores
                new_score = pd.DataFrame({"Name": [player_name.get_string().capitalize()], "Score": [score.value]})
                best_scores = best_scores.append(new_score)
                best_scores = best_scores.sort_values(by="Score", ascending=False, ignore_index=True).head(5)
                best_scores.to_csv("database/scores.csv", index=False)
                # Resetting settings for new game
                Enemy.enemies.clear()
                Enemy.count = 0
                new_wolf = Enemy(64, 64, wolf_img, random.randint(150, 900), random.randint(10, 100), 3, 40, 1)
                main_char.x = 400
                main_char.y = 350
                break

        fpsClock.tick(FPS)

    # Game over view
    elif status_game == "over":
        # Controls
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if play_again_button.on_button(pos):
                    status_game = "menu"
                    score.value = 0
                elif quit_button2.on_button(pos):
                    run = False
            elif event.type == pygame.QUIT:
                run = False

        draw_game_over()
