import pygame
import sys
import random
import json
from pygame.locals import *

# initialize Pygame
pygame.init()

#stats
score = 0
high_score = 0
has_moved = False
game_state = 1

# set up window

w_width = 800
w_height = 600

screen = pygame.display.set_mode((w_width, w_height))
pygame.display.set_caption('Flappy Dodo')
font = pygame.font.Font("font/BaiJamjuree-Bold.ttf", 60)
clock = pygame.time.Clock()
fps = 60

# sounds 

jump_sfx = pygame.mixer.Sound("sfx/jump.wav")
score_sfx = pygame.mixer.Sound("sfx/score.wav")
die_sfx = pygame.mixer.Sound("sfx/die.mp3")

# images

bg_img = pygame.image.load("assets/dodoflappybg.png")
ground_img = pygame.image.load("assets/ground.png")
dodo_img = pygame.image.load("assets/dodojump1.png")
pipe_down_img = pygame.image.load("assets/pipe_down.png")
pipe_up_img = pygame.image.load("assets/pipe_up.png")
pipe_down_img = pygame.transform.scale(pipe_down_img, (200, 450))
pipe_up_img = pygame.transform.scale(pipe_up_img, (200, 450))
bg_img = pygame.transform.scale(bg_img, (w_width, w_height))

# moving bg
bg_scroll_speed = 1
# moving ground
ground_scroll_speed = 2


def load_high_score():
    try:
        with open("highscore.json", "r") as f:
            data = json.load(f)
            return int(data.get("high_score", 0))
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return 0


def save_high_score(high_score):
    with open("highscore.json", "w") as f:
        json.dump({"high_score": high_score}, f)


def update_high_score(score, high_score):
    if score > high_score:
        high_score = score
        save_high_score(high_score)
    return high_score


# dodo player

class dodo_player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0


    def jump(self):
        self.velocity = -10


    def update(self):
        self.velocity += 0.75
        self.y += self.velocity


    def draw(self):
        screen.blit(dodo_img, (self.x, self.y))
    

# pipe class
class Pipe:
    def __init__(self, x, height, gap, velocity):
        self.x = x
        self.height = height
        self.gap = gap
        self.velocity = velocity
        self.scored = False

    def update(self):
        self.x -= self.velocity

    def draw(self):
        # spride top pipe
        screen.blit(pipe_down_img, (self.x, 0 - pipe_down_img.get_height() + self.height))

        # spride bottom pipe
        screen.blit(pipe_up_img, (self.x, self.height + self.gap))

def scoreboard():
    show_score = font.render(str(score), True, (255, 255, 255))
    score_rect = show_score.get_rect(center=(w_width//2, 64))
    screen.blit(show_score, score_rect)
    hs_text = font.render(f"Best: {high_score}", True, (255, 255, 255))
    screen.blit(hs_text, (10,10))



def game():
    global game_state
    global score
    global has_moved
    global high_score

    bg_x_pos = 0
    ground_x_pos = 0
    high_score = load_high_score()

    dodo = dodo_player(168, 300)
    pipes = [Pipe(600, random.randint(30, 250), 220, 2.4)]

    while game_state != 0:
        # gameplay
        while game_state == 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    has_moved = True
                    if event.key == pygame.K_SPACE:
                        pygame.mixer.Sound.play(jump_sfx)
                        dodo.jump()


                    
            if has_moved == True:
                        dodo.update()

                        dodo_rect = pygame.Rect(dodo.x, dodo.y, dodo_img.get_width(), dodo_img.get_height())

                        for pipe in pipes:
                            pipe_width = pipe_up_img.get_width()
                            pipe_top_height = pipe.height
                            pipe_gap = pipe.gap
                            pipe_bottom_y = pipe_top_height + pipe_gap
                            pipe_padding_x = 12
                            pipe_padding_y = 10

                            pipe_top_rect = pygame.Rect(
                                pipe.x + pipe_padding_x,
                                0,
                                pipe_width - (pipe_padding_x * 2),
                                pipe_top_height - pipe_padding_y
                            )
                            pipe_bottom_rect = pygame.Rect(
                                pipe.x + pipe_padding_x,
                                pipe_bottom_y + pipe_padding_y,
                                pipe_width - (pipe_padding_x * 2),
                                w_height - pipe_bottom_y
                            )

                            if dodo_rect.colliderect(pipe_top_rect) or dodo_rect.colliderect(pipe_bottom_rect):
                                high_score = update_high_score(score, high_score)
                                dodo = dodo_player(168, 300)
                                pipes = [Pipe(600, random.randint(30, 250), 220, 2.4)]
                                score = 0
                                has_moved = False
                                pygame.mixer.Sound.play(die_sfx)

                        if dodo.y < -64 or dodo.y > 536:
                            high_score = update_high_score(score, high_score)
                            dodo = dodo_player(168, 300)
                            pipes = [Pipe(600, random.randint(30, 250), 220, 2.4)]
                            score = 0
                            has_moved = False
                            pygame.mixer.Sound.play(die_sfx)

                        for pipe in pipes:
                            pipe.update()

                        if pipes[0].x < -pipe_up_img.get_width():
                            pipes.pop(0)
                            pipes.append(Pipe(400, random.randint(30, 280), 220, 2.4))


                        for pipe in pipes:
                            if not pipe.scored and pipe.x + pipe_up_img.get_width() < dodo.x:
                                score += 1
                                high_score = update_high_score(score, high_score)
                                pygame.mixer.Sound.play(score_sfx)
                                pipe.scored = True

            bg_x_pos -= bg_scroll_speed
            ground_x_pos -= ground_scroll_speed

            if bg_x_pos <= -w_width:
                bg_x_pos = 0

            if ground_x_pos <= -w_width:
                ground_x_pos = 0


            screen.blit(bg_img, (bg_x_pos, 0))
            screen.blit(bg_img, (bg_x_pos + w_width, 0))
            screen.blit(ground_img, (ground_x_pos, 536))
            screen.blit(ground_img, (ground_x_pos + w_width, 536))

            for pipe in pipes:
                pipe.draw()

            dodo.draw()
            scoreboard()

            pygame.display.flip()
            clock.tick(fps)

game()
                
    
                   


