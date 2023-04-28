from typing import Any
import pygame
from pygame.locals import *
import random


pygame.init()
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()


# game variables
screen_width = 854
screen_height = 936
screen = pygame.display.set_mode((screen_width, screen_height))
run = True
fps = 60
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500  # miliseconds
last_pipe = pygame.time.get_ticks()-pipe_frequency
score = 0
pass_pipe = False
font = pygame.font.SysFont('Bauhaus 93', 60)
white = (255, 255, 255)
# assets
bg = pygame.image.load('img/bg.png')
ground = pygame.image.load('img/ground.png')
button_img=pygame.image.load('img/restart.png')
ground_scroll = 0
ground_scroll_speed = 4


def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def reset_game():
    pipe_group.empty()
    flappy.rect.x=100
    flappy.rect.y=int(screen_height/2)
    score=0
    return score

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'img/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):
        if (flying == True):
            # gravity physics
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        # flapping mechanism
        if (pygame.mouse.get_pressed()[0] == 1 and self.clicked == False):
            self.clicked = True
            self.vel = -10
        if (pygame.mouse.get_pressed()[0] == 0):
            self.clicked = False

        if game_over == False:
            # flapping animation
            self.counter += 1
            flap_cooldown = 5
            if (self.counter > flap_cooldown):
                self.counter = 0
                self.index += 1

                if (self.index == len(self.images)):
                    self.index = 0
            self.image = self.images[self.index]

            # flapping rotation
            self.image = pygame.transform.rotate(
                self.images[self.index], self.vel*-3)
        else:
            # game over rotation
            self.image = pygame.transform.rotate(self.images[self.index], -90)


class Pipes(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe.png')

        self.rect = self.image.get_rect()
        # position == 1 => top pipe
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y-int(pipe_gap/2)]
        # position == -1 => bottom pipe
        elif position == -1:
            self.rect.topleft = [x, y+int(pipe_gap/2)]

    def update(self):
        if (game_over == False):
            self.rect.x -= ground_scroll_speed
        if (self.rect.right < 0):
            self.kill()

class Button():
    def __init__(self,x,y,image):
        self.image=image
        self.rect=self.image.get_rect()
        self.rect.topleft=(x,y)

    def draw(self):
        action=False
        pos=pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0]==1:
                action=True 
        screen.blit(self.image, (self.rect.x,self.rect.y))

        return action
    

bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()
flappy = Bird(100, int(screen_height/2))
bird_group.add(flappy)
button= Button( screen_width//2-38,screen_height//2-50,button_img)

# game loop
while run:
    # scrolling ground
    clock.tick(fps)
    screen.blit(bg, (0, 0))
    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)

    screen.blit(ground, (ground_scroll, 768))
    if (len(pipe_group) > 0):
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
                and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                pass_pipe = False
                score += 1

    draw_text(str(score), font, white, int(screen_width/2), 20)

    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True

    # checking game over
    if (flappy.rect.bottom >= 768):
        game_over = True
        flying = False

    # ground scroll
    if game_over == False and flying == True:
        time_now = pygame.time.get_ticks()
        pipe_height = random.randint(-100, +100)
        if time_now - last_pipe > pipe_frequency:
            btm_pipe = Pipes(screen_width, int(
                screen_height/2)-10+pipe_height, -1)
            top_pipe = Pipes(screen_width, int(
                screen_height/2)-10+pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now
        ground_scroll -= ground_scroll_speed
        pipe_group.update()
        if (abs(ground_scroll) > 35):
            ground_scroll = 0

    if game_over==True:
       if button.draw():
           game_over=False
           score=reset_game()   
    # exit loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if (event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False):
            flying = True

    pygame.display.update()
# end game
pygame.quit()
