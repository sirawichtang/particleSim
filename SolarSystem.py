import pygame
import time

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((1600,900), pygame.RESIZABLE)
width = screen.get_width()
width_center = width / 2
height = screen.get_height()
height_center = height / 2
isRunning = True

timeScale = 0.005
velocityScale = ((330000 / ((1 / 35.14) * width_center))**0.5) / 29.8
gravitationalConst = 1

drawTrail = False

#Camera
CamSensitivity = 1000

CamZoom = 1
CamOffsets = pygame.Vector2(0,0)
dt = 0
astronomicalObject_initial = [
["Sun", pygame.Vector2(width_center,height_center), pygame.Vector2(0,0), 330000, 4, "Red"],
["Mercury", pygame.Vector2(width_center + ((0.39 / 35.14) * width_center) ,height_center), pygame.Vector2(0,47.9 * velocityScale), 0.0553, 2, "Gray"],
["Venus", pygame.Vector2(width_center + ((0.72 / 35.14) * width_center) ,height_center), pygame.Vector2(0,35.0 * velocityScale), 0.815, 2, "Gray"],
["Earth", pygame.Vector2(width_center + ((1 / 35.14) * width_center) ,height_center), pygame.Vector2(0,29.8 * velocityScale), 1, 2, "Green"],
["Mars", pygame.Vector2(width_center + ((1.52 / 35.14) * width_center) ,height_center), pygame.Vector2(0,24.1 * velocityScale), 0.1075, 2, "Orange"],
["Jupiter", pygame.Vector2(width_center + ((5.2 / 35.14) * width_center) ,height_center), pygame.Vector2(0,13.1 * velocityScale), 317.8, 3, "Gray"],
["Saturn", pygame.Vector2(width_center + ((9.5 / 35.14) * width_center) ,height_center), pygame.Vector2(0,9.7 * velocityScale), 95.2, 3, "Gray"],
["Venus", pygame.Vector2(width_center + ((19.2 / 35.14) * width_center) ,height_center), pygame.Vector2(0,6.8 * velocityScale), 14.6, 2, "blue"],
["Neptune", pygame.Vector2(width_center + ((30.1 / 35.14) * width_center) ,height_center), pygame.Vector2(0,5.4 * velocityScale), 17.2, 2, "blue"],
["halley's comet", pygame.Vector2(width_center + ((35.14 / 35.14) * width_center) ,height_center), pygame.Vector2(0,0.91 * velocityScale), 0.000000000037, 2, "white"]
]

class astronomicalObject:
    name : str
    position : pygame.Vector2
    velocity : pygame.Vector2
    mass : float
    size : float
    color : str

    def __init__(self, name, position, velocity, mass, size, color):
        self.name = name
        self.position = position
        self.velocity = velocity
        self.mass = mass
        self.size = size
        self.color = color

    def updateVelocity(self, otherObject):
        dist_to_otherObject = pygame.Vector2.distance_to(self.position, otherObject.position)
        normal_vector_to_otherObject = pygame.Vector2.normalize(otherObject.position - self.position)
        self.velocity += ((otherObject.mass * gravitationalConst) / (dist_to_otherObject **2)) * normal_vector_to_otherObject * timeScale

    def updatePosition(self): self.position += self.velocity * timeScale

astronomicalObject_Array: list[astronomicalObject] = [astronomicalObject(*i) for i in astronomicalObject_initial]

def render(base):
    return pygame.Vector2(width_center,height_center) + ((pygame.Vector2(width_center,height_center) - (base - CamOffsets)) * CamZoom)

while isRunning:
    startTime = time.time()
    #iterate through objects
    if drawTrail == False: screen.fill("Black")
    for main_obj in astronomicalObject_Array:
        for secondary_obj in astronomicalObject_Array:
            if secondary_obj == main_obj: continue
            main_obj.updateVelocity(secondary_obj)
        main_obj.updatePosition()

        #Draw
        pygame.draw.circle(screen, main_obj.color, render(main_obj.position), main_obj.size * CamZoom)
        txtfont = pygame.font.SysFont('Comic Sans MS', int(max(5 * CamZoom, 10)))
        text = txtfont.render(main_obj.name, False, "white")
        if drawTrail == False: screen.blit(text, render(main_obj.position))

    timetxtfont = pygame.font.SysFont('Comic Sans MS', 20)
    timetext = timetxtfont.render("Timescale: " + str(round(timeScale, 4)), False, "white")
    screen.blit(timetext, pygame.Vector2(10,10))

    pygame.display.flip()

    #Camera
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        CamOffsets.y += dt * CamSensitivity / CamZoom
    if keys[pygame.K_s]:
        CamOffsets.y -= dt * CamSensitivity / CamZoom
    if keys[pygame.K_a]:
        CamOffsets.x += dt * CamSensitivity / CamZoom
    if keys[pygame.K_d]:
        CamOffsets.x -= dt * CamSensitivity / CamZoom
    
    if keys[pygame.K_q]:
        CamZoom += dt
    if keys[pygame.K_e]:
        CamZoom -= dt

    #Time scale
    if keys[pygame.K_z] and timeScale < 0.02:
        timeScale = timeScale + (timeScale * dt)
    if keys[pygame.K_x] and timeScale > 0.0005:
        timeScale = timeScale - (timeScale * dt)

    
    #Quit
    for Event in pygame.event.get():
        if Event.type == pygame.QUIT:
            isRunning = False

    dt = time.time() - startTime
pygame.quit()