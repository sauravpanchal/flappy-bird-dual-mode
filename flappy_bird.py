import pygame, neat, os, random

from pygame.constants import *  

pygame.font.init()
pygame.display.set_caption("Flappy Bird")
icon = pygame.image.load("images/redbird-upflap.png")
pygame.display.set_icon(icon)

# setting up variables
WIN_WIDTH = 500
WIN_HEIGHT = 800
GEN = 0
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("images","redbird-upflap.png"))),
            pygame.transform.scale2x(pygame.image.load(os.path.join("images","redbird-midflap.png"))),
            pygame.transform.scale2x(pygame.image.load(os.path.join("images","redbird-downflap.png")))
            ]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("images","pipe-red.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("images","base-edit.jpg")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("images","background-night.png")))
START_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "message.png")))
GAMEOVER_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "gameover.png")))
# setting up fonts
STAT_FONT = pygame.font.SysFont("comicsnas", 50)
OTHER_FONT = pygame.font.SysFont("comicsnas", 25)

class Bird:
    IMGS = BIRD_IMGS # img list object
    MAX_ROTATION = 25 # for tilting the bird +25 or -25 degree
    ROT_VEL = 20 # number times to rotate the image per frame every time we move bird
    ANIMATION_TIME = 5 # control flappy bird's flapping (image shuffle) 

    def __init__(self, x, y):
        self.x = x # x coordinate bird
        self.y = y # y coordinate bird
        self.tilt = 0 # initializing bird's tilting (will start with no tilt)
        self.tick_count = 0 # tracks jumps while bird moves in frame
        self.vel = 0 # initializing velocity
        self.height = self.y # setting height corresponding to y-coord
        self.img_count = 0 # initilizing image count (tracks image for shuffling)
        self.img = self.IMGS[0] # starting with first image of bird

    # will flap-up the bird
    def jump(self):
        # self.move()
        if self.tick_count < 5:
            self.height = self.y
        else:
            self.height = self.height - self.y
        self.vel = -10.5 # for flapping bird upwards
        self.tick_count = 0 # resetting jump counter to 0 for frame
        # self.height = self.y # after jump it'll update the height of bird (assigns y-coord)

    # invoked in every single frame to move our bird
    def move(self):
        self.tick_count += 1 # records the numbr of times we moved bird since the last jump

        # sets displacement (tells how much we are moving up or moving down)
        # e.g: -10.5 * 1 + 1.5 * (1) ** 2 
        # = -10.5 + 1.5 
        # = -9
        # similarly, ... -7, -5, -3, -1
        d = self.vel * self.tick_count + 1.5*self.tick_count ** 2 

        if d >= 16: # terminal velocity
            d = 16

        if d < 0: # move up little bit
            d -= 2
        elif d < -5:
            d = -2

        self.y += d # updates y-coord smoothly (whether it's upward or downward)

        # tilting the bird based on it's jump. (tilt down if it falls and vice-versa)
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL
        # self.jump()

    def draw(self, win):
        self.img_count += 1 

        # displaying imgage based on image counter
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0] # wings-down
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1] # leveled-wings
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2] # wings-up
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1] # leveled-wings
        elif self.img_count < self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0] # wings-down
            self.img_count = 0 # image counter reset

        # to avoid flapping of wings while falling
        if self.tilt <= -80:
            self.img = self.IMGS[1] # as it'll be falling so, displaying bird image with leveled-wings
            self.img_count = self.ANIMATION_TIME*2

        # rotating image
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)

        # rendering to the window
        win.blit(rotated_image, new_rect.topleft) # win.blit(source, destination)

    # helpful for getting mask of bird
    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        # initializing pipe variable
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        # top pipe should be flipped first before rendering to window.
        # transform module of pygame helps you to do such operations on surface
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True) # flip(surface, xbool, ybool)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False # bird passed the pipe or not
        self.set_height() # invoking randomized set_height() function

    # creates random height of top & bottom pipes
    def set_height(self):
        self.height = random.randrange(50, 450) # randrange(start, stop, step) - [start, stop]
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    # moves pipe
    def move(self):
        self.x -= self.VEL

    # draws top & bottom pipe
    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    # check for pixel perfect collision - bool function
    def collide(self, bird):
        bird_mask = bird.get_mask() # gets bird's mask
        top_mask = pygame.mask.from_surface(self.PIPE_TOP) # gets top pipes mask
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM) # gets bottom pipes mask

        # setting up the offset
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # collision check variable
        t_point = bird_mask.overlap(top_mask, top_offset)
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)

        # collision check logic
        if t_point or b_point:
            return True
        return False

class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    # print(WIDTH)
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    # will move pipe element
    def move(self):
        self.x1 -=self.VEL
        self.x2 -= self.VEL

        # logic that checks if any image is completely of the window - updating x1 & x2
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    # will loop pipe images in continuous manner
    def draw(self, win):
        # renders two images of pipe at x1 & x2 coords
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

# will render all the elements as a whole
def draw_window(win, birds, pipes, base, score):
    win.blit(BG_IMG, (0,0))
    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255)) # 1 is for anti-aliasing (255,255,255) is the colour
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    base.draw(win)

    birds.draw(win)
    pygame.display.update()

def start(win):
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type==KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                quit()

            elif event.type==KEYDOWN and (event.key==K_SPACE or event.key == K_LEFT):
                print("Manual Mode")
                pygame.display.set_caption("Manual Mode - Flappy Bird")
                return
            elif event.type==KEYDOWN and (event.key == K_RIGHT):
                print("God Mode")
                os.system("flappy_bird_ai.py")
            else:
                win.fill((0,0,0))
                win.blit(START_IMG, (63, 150))
                text = OTHER_FONT.render("<<  Manual Mode | God Mode  >>", 1, (255,255,255)) # 1 is for anti-aliasing (255,255,255) is the colour
                win.blit(text, (115, 760))
                names = ["IU1941230085 - Nirmal Mudaliar",
                        "IU1941230093 - Saurav Panchal",
                        "IU1941230097 - Abhi Patel"]
                text = OTHER_FONT.render(names[0], 1, (255,255,255)) # 1 is for anti-aliasing (255,255,255) is the colour
                win.blit(text, ((WIN_WIDTH/2)-(WIN_WIDTH/2)/2, 10))
                text = OTHER_FONT.render(names[1], 1, (255,255,255)) # 1 is for anti-aliasing (255,255,255) is the colour
                win.blit(text, ((WIN_WIDTH/2)-(WIN_WIDTH/2)/2, 30))
                text = OTHER_FONT.render(names[2], 1, (255,255,255)) # 1 is for anti-aliasing (255,255,255) is the colour
                win.blit(text, ((WIN_WIDTH/2)-(WIN_WIDTH/2)/2+25, 50))
                pygame.display.set_caption("Flappy Bird")
                pygame.display.update()

def main(win):
    bird = Bird(230, 350)
    # create base object
    base = Base(730)
    # create pipes list
    pipes = [Pipe(600)]
    clock = pygame.time.Clock()
    score = 0

    run = True
    while run:
        clock.tick(30) # 30 tick every seconds so frame doesn't move fast.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                bird.jump()
                pygame.display.update()
                break
        bird.move()

        add_pipe = False
        rem = []
        for pipe in pipes:
            if pipe.collide(bird) or bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                win.blit(GAMEOVER_IMG, (63, 150))
                pygame.display.update()
                return

            if pipe.x + pipe.PIPE_TOP.get_width() < 0: # whether pipe is completely off the screen or not ?
                rem.append(pipe) # add it to rem list

            # checks whether bird has passed the pipe or not ?
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

            pipe.move() # moves pipe 
            
        # will append new pipe in pipes list
        if add_pipe:
            score += 1
            # for g in ge:
            #     g.fitness += 5
            pipes.append(Pipe(600))

        # removes pipes which are off the screen
        for r in rem:
            pipes.remove(r)

        base.move()
        draw_window(win, bird, pipes, base, score)
        
if __name__ == "__main__":
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    while True:
        start(win)
        main(win)