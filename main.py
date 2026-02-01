import pygame
from pygame import mixer
from fighter import Fighter
from PIL import Image
import random
import glob

def load_gif_frames(path):
    pil_gif = Image.open(path)
    frames = []
    try:
        while True:
            frame = pil_gif.convert("RGBA")
            pygame_image = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode).convert_alpha()
            scaled_frame = pygame.transform.scale(pygame_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            frames.append(scaled_frame)
            pil_gif.seek(pil_gif.tell() + 1)
    except EOFError:
        pass
    return frames

mixer.init()
pygame.init()

#create game window
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("MultiPlayer Battle Arena")

welcome_bg = pygame.image.load("assets/images/background/welcomeimage/welcome_bg.jpg").convert()
welcome_bg = pygame.transform.scale(welcome_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

mode_bg = pygame.image.load("assets/images/background/welcomeimage/mode_bg.jpg").convert()
mode_bg = pygame.transform.scale(mode_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

CHARACTERS = {
    "warrior": {
        "name": "Warrior",
        "path": "assets/images/characters/warrior/Sprites/warrior.png",
        "data": [162, 4, [72, 56]],
        "steps": [10, 8, 1, 7, 7, 3, 7]
    },
    "wizard": {
        "name": "Wizard",
        "path": "assets/images/characters/wizard/Sprites/wizard.png",
        "data": [250, 3, [112, 107]],
        "steps": [8, 8, 1, 8, 8, 3, 7]
    }
    # Add more characters here
}

# Randomly select a GIF background
background_gif_files = glob.glob("assets/images/background/*.gif")
selected_gif = random.choice(background_gif_files)
bg_frames = load_gif_frames(selected_gif)
bg_frame_index = 0
bg_last_update = pygame.time.get_ticks()

#set framerate
clock = pygame.time.Clock()
FPS = 60

#define colours
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

#define game variables
intro_count = 3
last_count_update = pygame.time.get_ticks()
score = [0, 0]#player scores. [P1, P2]
round_over = False
ROUND_OVER_COOLDOWN = 2000

#load music and sounds
pygame.mixer.music.load("assets/audio/music.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1, 0.0, 5000)
sword_fx = pygame.mixer.Sound("assets/audio/sword.wav")
sword_fx.set_volume(0.5)
magic_fx = pygame.mixer.Sound("assets/audio/magic.wav")
magic_fx.set_volume(0.75)

# load character spritesheets
character_sheets = {}
for name, info in CHARACTERS.items():
    character_sheets[name] = pygame.image.load(info["path"]).convert_alpha()

#load vicory image
victory_img = pygame.image.load("assets/images/icons/victory.png").convert_alpha()

#define font
count_font = pygame.font.Font("assets/fonts/turok.ttf", 80)
score_font = pygame.font.Font("assets/fonts/turok.ttf", 30)

#function for drawing text
def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))

#function for drawing background
def draw_animated_bg():
    global bg_frame_index, bg_last_update
    animation_speed = 100  # milliseconds per frame

    if pygame.time.get_ticks() - bg_last_update > animation_speed:
        bg_frame_index = (bg_frame_index + 1) % len(bg_frames)
        bg_last_update = pygame.time.get_ticks()

    screen.blit(bg_frames[bg_frame_index], (0, 0))

#function for drawing fighter health bars
def draw_health_bar(health, x, y):
  ratio = health / 100
  pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 404, 34))
  pygame.draw.rect(screen, RED, (x, y, 400, 30))
  pygame.draw.rect(screen, YELLOW, (x, y, 400 * ratio, 30))


def show_welcome_screen():
    welcome_running = True
    while welcome_running:
        screen.blit(welcome_bg, (0, 0))  # draw the background

        # Title text
        draw_text("Welcome to Brawler!", count_font, WHITE, SCREEN_WIDTH // 2 - 300, 100)

        # Let's Fight button
        fight_btn_rect = pygame.draw.rect(screen, (255, 50, 50), (SCREEN_WIDTH // 2 - 150, 300, 300, 80))
        draw_text("Let's Fight", score_font, WHITE, SCREEN_WIDTH // 2 - 70, 320)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if fight_btn_rect.collidepoint(pygame.mouse.get_pos()):
                    welcome_running = False  # Exit welcome screen

        pygame.display.update()

def show_menu():
    menu_running = True
    while menu_running:
        screen.blit(mode_bg, (0, 0))  # draw the background
        draw_text("Select Game Mode", count_font, WHITE, SCREEN_WIDTH // 2 - 250, 100)

        # Draw buttons
        single_rect = pygame.draw.rect(screen, (100, 100, 255), (SCREEN_WIDTH // 2 - 150, 200, 335, 60))
        multi_rect = pygame.draw.rect(screen, (100, 255, 100), (SCREEN_WIDTH // 2 - 150, 300, 335, 60))

        draw_text("1 Player (vs AI)", score_font, WHITE, SCREEN_WIDTH // 2 - 100, 215)
        draw_text("2 Player (Multiplayer)", score_font, WHITE, SCREEN_WIDTH // 2 - 120, 315)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if single_rect.collidepoint(mouse_pos):
                    return True  # Single player
                elif multi_rect.collidepoint(mouse_pos):
                    return False  # Multiplayer

        pygame.display.update()

def select_character(player_num):
    selected_index = 0
    character_keys = list(CHARACTERS.keys())
    selecting = True

    while selecting:
        screen.fill((30, 30, 30))
        draw_text(f"Player {player_num} - Select Your Character", count_font, WHITE, 150, 50)

        for i, key in enumerate(character_keys):
            color = (255, 255, 0) if i == selected_index else (100, 100, 100)
            draw_text(CHARACTERS[key]["name"], score_font, color, SCREEN_WIDTH // 2 - 80, 150 + i * 60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(character_keys)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(character_keys)
                elif event.key == pygame.K_RETURN:
                    selecting = False

        pygame.display.update()
        clock.tick(30)

    return character_keys[selected_index]


show_welcome_screen()
single_player_mode = show_menu()

# Character selection
fighter_1_name = select_character(1)
fighter_2_name = select_character(2 if not single_player_mode else "AI")

# Now create fighters using selected names
fighter_1_info = CHARACTERS[fighter_1_name]
fighter_2_info = CHARACTERS[fighter_2_name]

fighter_1 = Fighter(1, 200, 310, False, fighter_1_info["data"], character_sheets[fighter_1_name], fighter_1_info["steps"], sword_fx)
fighter_2 = Fighter(2, 700, 310, True, fighter_2_info["data"], character_sheets[fighter_2_name], fighter_2_info["steps"], magic_fx)


#game loop
run = True
while run:

  clock.tick(FPS)

  #draw background
  draw_animated_bg()


  #show player stats
  draw_health_bar(fighter_1.health, 20, 20)
  draw_health_bar(fighter_2.health, 580, 20)
  draw_text("P1: " + str(score[0]), score_font, RED, 20, 60)
  draw_text("P2: " + str(score[1]), score_font, RED, 580, 60)

  #update countdown
  if intro_count <= 0:
    #move fighters
    fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_2, round_over, single_player_mode)
    fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_1, round_over, single_player_mode)

  else:
    #display count timer
    # Let fighters fall to ground even during countdown
    fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_2, round_over, single_player_mode=False)
    fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_1, round_over, single_player_mode=False)

    # Display countdown text
    draw_text(str(intro_count), count_font, RED, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)

    if (pygame.time.get_ticks() - last_count_update) >= 1000:
        intro_count -= 1
        last_count_update = pygame.time.get_ticks()


  #update fighters
  fighter_1.update()
  fighter_2.update()

  #draw fighters
  fighter_1.draw(screen)
  fighter_2.draw(screen)

  #check for player defeat
  if round_over == False:
    if fighter_1.alive == False:
      score[1] += 1
      round_over = True
      round_over_time = pygame.time.get_ticks()
    elif fighter_2.alive == False:
      score[0] += 1
      round_over = True
      round_over_time = pygame.time.get_ticks()
  else:
    #display victory image
    screen.blit(victory_img, (360, 150))
    if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
      round_over = False
      intro_count = 3
      fighter_1 = Fighter(1, 200, 310, False, fighter_1_info["data"], character_sheets[fighter_1_name], fighter_1_info["steps"], sword_fx)
      fighter_2 = Fighter(2, 700, 310, True, fighter_2_info["data"], character_sheets[fighter_2_name], fighter_2_info["steps"], magic_fx)


  #event handler
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False


  #update display
  pygame.display.update()

#exit pygame
pygame.quit()