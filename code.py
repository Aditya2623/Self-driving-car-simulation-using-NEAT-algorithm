import pygame
import os
import math
import sys
import neat
import time
pygame.init()

red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
black = pygame.Color(0, 0, 0)


SCREEN_WIDTH = 1244
SCREEN_HEIGHT = 1016
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

TRACK = pygame.image.load('/Users/CAR game/Assets/track.png')
current_generation = 0

font = pygame.font.Font('freesansbold.ttf', 32)
 

def draw_signal(color, position):
    x, y = position
    rect_height = 10
    rect_width = 140
    rect_x = x - rect_width // 2
    rect_y = y - rect_height // 2
    pygame.draw.rect(SCREEN, color, pygame.Rect(rect_x, rect_y, rect_width, rect_height))

def generate_signal_position():
    x = 1010
    y = 450
    return x, y

class Car(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = pygame.image.load("/Users/CAR game/Assets/car.png")
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(490, 820))
        self.vel_vector = pygame.math.Vector2(0.8, 0)
        self.angle = 0
        self.rotation_vel = 5
        self.direction = 0
        self.alive = True
        self.radars = []
        self.temp=10

    def update(self):
        self.radars.clear()
        self.drive()
        self.rotate()
        for radar_angle in (-60, -30, 0, 30, 60):
            self.radar(radar_angle)
        
        
        self.collision()
        self.data()

    def drive(self):
        self.rect.center += self.vel_vector * self.temp
        self.temp=10

    def collision(self):
        length = 40
        self.collision_point_right = [int(self.rect.center[0] + math.cos(math.radians(self.angle + 18)) * length),
                                 int(self.rect.center[1] - math.sin(math.radians(self.angle + 18)) * length)]
        self.collision_point_left = [int(self.rect.center[0] + math.cos(math.radians(self.angle - 18)) * length),
                                int(self.rect.center[1] - math.sin(math.radians(self.angle - 18)) * length)]
        
        # Die on Collision
        if SCREEN.get_at(self.collision_point_right) == pygame.Color(2, 105, 31, 255) \
                or SCREEN.get_at(self.collision_point_left) == pygame.Color(2, 105, 31, 255):
            self.alive = False

        # Draw Collision Points
        pygame.draw.circle(SCREEN, (0, 255, 255, 0), self.collision_point_right, 4)
        pygame.draw.circle(SCREEN, (0, 255, 255, 0), self.collision_point_left, 4)
   
        

    def rotate(self):
        if self.direction == 1:
            self.angle -= self.rotation_vel
            self.vel_vector.rotate_ip(self.rotation_vel)
        if self.direction == -1:
            self.angle += self.rotation_vel
            self.vel_vector.rotate_ip(-self.rotation_vel)

        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 0.1)
        self.rect = self.image.get_rect(center=self.rect.center)
    
    def check_signal(self,x,y):
        
        if SCREEN.get_at((x,y))==pygame.Color(255, 0, 0):
         self.temp=0
        
    def radar(self, radar_angle):
     length = 0
     x = int(self.rect.center[0])
     y = int(self.rect.center[1])
        
     
     while not SCREEN.get_at((x, y)) == pygame.Color(2, 105, 31, 255) and length < 200 :
        length += 1
        x = int(self.rect.center[0] + math.cos(math.radians(self.angle + radar_angle)) * length)
        y = int(self.rect.center[1] - math.sin(math.radians(self.angle + radar_angle)) * length)
        self.check_signal(x,y)
    # Draw Radar
     pygame.draw.line(SCREEN, (255, 255, 255, 255), self.rect.center, (x, y), 3)
     pygame.draw.circle(SCREEN, (0, 255, 0, 0), (x, y), 3)

     dist = int(math.sqrt(math.pow(self.rect.center[0] - x, 2)
                         + math.pow(self.rect.center[1] - y, 2)))

     self.radars.append([radar_angle, dist])
   
    def data(self):
        input = [0, 0, 0, 0, 0]
        for i, radar in enumerate(self.radars):
            input[i] = int(radar[1])
            
        return input
    


def remove(index):
    cars.pop(index)
    ge.pop(index)
    nets.pop(index)

def genome(genomes,config):
    for genome_id, genome in genomes:
        cars.append(pygame.sprite.GroupSingle(Car()))
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0
    

def eval_genomes(genomes, config):
    global cars, ge, nets

    cars = []
    ge = []
    nets = []
    
    global current_generation
    current_generation += 1
    genome(genomes,config)
    
   

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        SCREEN.blit(TRACK, (0, 0))
        left, middle, right = pygame.mouse.get_pressed()
     
        
        # Generate random signal position
        signal_position = generate_signal_position()
        if (left):
            

        # Draw red signal
            draw_signal(red, signal_position)
            pygame.display.update()
            
        else:

        # Draw green signal
            draw_signal(green, signal_position)
            pygame.display.update()
           

        if len(cars) == 0:
            break

        for i, car in enumerate(cars):
            ge[i].fitness += 1
            if not car.sprite.alive:
                remove(i)

        for i, car in enumerate(cars):
            output = nets[i].activate(car.sprite.data())
            if output[0] > 0.7:
                car.sprite.direction = 1
            if output[1] > 0.7:
                car.sprite.direction = -1
            if output[0] <= 0.7 and output[1] <= 0.7:
                car.sprite.direction = 0
        text = font.render("Generation:"+str(current_generation), True,(0,0,0))
        

        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH // 2,  SCREEN_HEIGHT// 2)
        
        SCREEN.blit(text, textRect)

        # Update
        for car in cars:
            car.draw(SCREEN)
            car.update()
        pygame.display.update()



def run(config_path):
    global pop
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    pop = neat.Population(config)
    
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    pop.run(eval_genomes, 50)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)