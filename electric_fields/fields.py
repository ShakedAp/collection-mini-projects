import math
import pygame

class Particle:

    POSITIVE_COLOR = (0, 0, 255)
    NEGATIVE_COLOR = (255, 0, 0)

    def __init__(self, x, y, charge) -> None:
        self.x = x
        self.y = y
        self.charge = charge

    # Drawing functions
    def draw(self, surface):
        if self.charge > 0:
            pygame.draw.circle(surface, Particle.POSITIVE_COLOR, (self.x, self.y), OFFSET/3)
        else:
            pygame.draw.circle(surface, Particle.NEGATIVE_COLOR, (self.x, self.y), OFFSET/3)


class Point:

    COLOR = (0, 0, 0)

    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
        self.field = 0
        self.angle = 0

        self.cos = 0
        self.sin = 0
    
    def calc_field(self, particles):
        # 1px = 1meter
        field_x, field_y = 0, 0

        for p in particles:
            dx = abs(self.x - p.x)
            dy = abs(self.y - p.y)
            c = math.sqrt(dx**2 + dy**2) # hypotenuse

            if dx == 0 and dy == 0:
                self.field = 0
                self.angle = 0
                return
            

            field_x += math.copysign(1, self.x - p.x) * (9 * 10**9 * p.charge * dx) / (c**3) # cos = dx/c
            field_y += math.copysign(1, p.y - self.y) * (9 * 10**9 * p.charge * dy) / (c**3) # sin = dy/c
        
        self.field = round(math.sqrt(field_x**2 + field_y**2), 3)
        self.angle = math.atan2(field_y, field_x) + math.pi/2


    # Drawing functions
    def draw(self, surface):
        pygame.draw.circle(surface, Point.COLOR, (self.x, self.y), OFFSET / 16)
        
        if self.field != 0:
            length = OFFSET / 2
            pygame.draw.line(screen, Point.COLOR, (self.x, self.y),
            (self.x + length * math.sin(self.angle), self.y + length * math.cos(self.angle)), width=1)



def update_screen(_particles, _points):
    screen.fill(background_colour)
    for p in _points:
        p.calc_field(particles)
        p.draw(screen)
    for p in _particles:
        p.draw(screen)
    pygame.display.update()

def generate_points():
    _points = []
    for i in range(WIDTH // OFFSET + 1):
        for j in range(HEIGHT // OFFSET + 1):
            _points.append(Point(i * OFFSET, j*OFFSET))
    return _points

def reset():
    global points, particles, OFFSET
    OFFSET = 16
    particles = []
    points = generate_points()
    update_screen(particles, points)

WIDTH, HEIGHT = 800, 450
OFFSET = 16
background_colour = (255, 255, 255)

# MAIN
if __name__ == "__main__":
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption('Electric Fields')
    screen.fill(background_colour)

    points, particles = [], []
    points = generate_points()

    for p in points:
        p.draw(screen)

    pygame.display.flip()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.size
                if WIDTH < 600: WIDTH = 600
                if WIDTH < 400: WIDTH = 400
                reset()
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button < 4:
                x, y = pygame.mouse.get_pos()
                x = round(x/OFFSET) * OFFSET
                y = round(y/OFFSET) * OFFSET

                if event.button == 1:
                    particles.append(Particle(x, y, 1))
                elif event.button == 3:
                    particles.append(Particle(x, y, -1))
                update_screen(particles, points)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    OFFSET += 1
                    points = generate_points()
                    particles = []
                    update_screen(particles, points)
                if event.button == 5:
                    OFFSET -= 1
                    particles = []
                    points = generate_points()
                    update_screen(particles, points)
                
                if OFFSET < 15: OFFSET = 15
                if OFFSET > 300: OFFSET = 300
                

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                reset()