import pygame, neat, os, random

pygame.font.init()
pygame.display.set_caption("God Mode - Flappy Bird")
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
        self.vel = -10.5 # for flapping bird upwards
        self.tick_count = 0 # resetting jump counter to 0 for frame
        self.height = self.y # after jump it'll update the height of bird (assigns y-coord)

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

        self.y += d # updates y-coord smoothly (whether it's upward or downward)

        # tilting the bird based on it's jump. (tilt down if it falls and vice-versa)
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

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
        # pygame.draw.line(win, (0,0,255), (self.x, 0), (int(self.PIPE_TOP), self.bottom))
        # pygame.display.flip()

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
def draw_window(win, birds, pipes, base, score, gen, alive, avgfitness, bestfitness):
    win.blit(BG_IMG, (0,0))
    for pipe in pipes:
        pipe.draw(win)
        # pygame.draw.line(win, (0,0,255), (0,0), (pipe.x+(pipe.PIPE_TOP.get_width())/2, pipe.height))
        # pygame.draw.line(win, (0,0,255), (0,0), (pipe.x+(pipe.PIPE_BOTTOM.get_width())/2, pipe.height+pipe.GAP))


    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255)) # 1 is for anti-aliasing (255,255,255) is the colour
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    text = STAT_FONT.render("Gen: " + str(gen), 1, (255,255,255)) # 1 is for anti-aliasing (255,255,255) is the colour
    win.blit(text, (10, 50))

    text = STAT_FONT.render("Alive: " + str(alive), 1, (255,255,255)) # 1 is for anti-aliasing (255,255,255) is the colour
    win.blit(text, (10, 10))
    
    text = OTHER_FONT.render("Avg Fitness: " + str(avgfitness), 1, (255,255,255)) # 1 is for anti-aliasing (255,255,255) is the colour
    win.blit(text, (10, 90))
    
    text = OTHER_FONT.render("Best Fitness: " + str(bestfitness), 1, (255,255,255)) # 1 is for anti-aliasing (255,255,255) is the colour
    win.blit(text, (10, 110))

    base.draw(win)

    for bird in birds:
        bird.draw(win)
        pygame.draw.line(win, (0, 100, 0), (bird.x+30, bird.y+30), (pipe.x+(pipe.PIPE_TOP.get_width())/2, pipe.height), 3)
        pygame.draw.line(win, (0, 100, 0), (bird.x+30, bird.y+30), (pipe.x+(pipe.PIPE_BOTTOM.get_width())/2, pipe.height+pipe.GAP), 3)
    pygame.display.update()

def main(genomes, config): # fitness function need 2 arguments - genomes and config file object
    # bird = Bird(230, 350)
    global GEN
    GEN += 1
    nets = []
    ge = []
    birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)
    # create base object
    base = Base(730)
    # create pipes list
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT)) # setting up pygame window object
    clock = pygame.time.Clock()
    score = 0
    alive = 100
    fit = list()
    avgfitness = 0
    bestfitness = 0

    run = True
    while run:
        clock.tick(30) # 30 tick every seconds so frame doesn't move fast.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and  birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else: # no birds left so quit the game
            run = False
            break
        
        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1
            fit.insert(x, ge[x].fitness)

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                bird.jump()

        add_pipe = False
        rem = []
        # loops for each pipe in pipes list
        for pipe in pipes:
            for x, bird in enumerate(birds):
                # collision check
                if pipe.collide(bird):
                    # print("hi")
                    ge[x].fitness -= 1
                    fit.insert(x, ge[x].fitness)
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                    alive -= 1

                # checks whether bird has passed the pipe or not ?
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
            
            if pipe.x + pipe.PIPE_TOP.get_width() < 0: # whether pipe is completely off the screen or not ?
                rem.append(pipe) # add it to rem list
            avgfitness = round(sum(fit)/len(fit), 2)
            bestfitness = round(max(fit), 2)
            pipe.move() # moves pipe 

        # will append new pipe in pipes list
        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))

        # removes pipes which are off the screen
        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            # check whether bird hits the floor or shoots into the sky
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
                alive -= 1

        base.move()
        draw_window(win, birds, pipes, base, score, GEN, alive, avgfitness, bestfitness)

def run(config_path):
    # import pickle
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
            neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True)) # prints various information about each generation in console
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50) # 50 here is generations (here main is fitness function it calls main function 50 times.)
    return

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir,  "config-feedforward.txt")
    run(config_path)
    # win.blit(GAMEOVER_IMG, (63, 150))
    pygame.display.update()