import pygame
import random

pygame.init
pygame.font.init()
txtFont = pygame.font.SysFont('Comic Sans MS', 20)
screen = pygame.display.set_mode((1000,1000))
clock = pygame.time.Clock()
isRunning = True

#Cam
CamSensitivity = 1000
CamOffsets = pygame.Vector2(0,0)
CamZoom = 0.9

#Environment
typeCount = [50,50,50,50]
typeColor = ["red", "green", "blue", "yellow"]
typeSize = [5,5,5,5]
particleCount = sum(typeCount)

#particles Properties
particlesDrag = 0.8
maxVelocity = -1 # -1 is unlimit
maxAcceleration = 1000 # -1 is unlimit
colisionForce = 2

#interaction
particle_interaction = [
                        [500,500,500,500], # particle 0's interaction with    itself  / #1        / #2
                        [500,500,500,500], # particle 1's interaction with    #0      / itself    / #2
                        [500,500,500,500], # particle 2's interaction with    #0      / #1        / itself
                        [500,500,500,500]  
                        ]

def reRoll():
    for i in range(4):
        for j in range(4):
            k = random.random()
            if k < 0.33:
                particle_interaction[i][j] = random.uniform(-1000,0)
            elif 0.33 <= k < 0.66:
                particle_interaction[i][j] = 0
            else:
                particle_interaction[i][j] = random.uniform(0,1000)
            
    print(particle_interaction)


#time
timeScale = 0.1
dt = 0

class Particles:
        
        position:pygame.Vector2
        velocity:pygame.Vector2
        acceleration:pygame.Vector2
        color:str
        size:float
        ID:int

        def __init__(self, position, velocity, acceleration, color, size, ID):
            self.position = position
            self.velocity = velocity
            self.acceleration = acceleration
            self.color = color
            self.size = size
            self.ID = ID

        def updateVel(self, otherParticlesArr):
            self.velocity *= particlesDrag ** timeScale

            #gravity + colision
            for i in range(particleCount):
                otherParticles = otherParticlesArr[i]
                partDist = pygame.Vector2.distance_to(self.position, otherParticles.position)
                if self is otherParticles : continue
                gravConst = particle_interaction[self.ID][otherParticles.ID]
                
                if partDist == 0: continue
                self.acceleration += ((gravConst / partDist) * pygame.Vector2.normalize(otherParticles.position - self.position))
                #"collision"
                self.acceleration -= ((1 / (partDist / self.size)**colisionForce) * pygame.Vector2.normalize(otherParticles.position - self.position))
            
            #max acceleration
            if self.acceleration.magnitude() > maxAcceleration and maxAcceleration != -1:
                self.acceleration = maxAcceleration * pygame.Vector2.normalize(self.acceleration)
            self.velocity += self.acceleration * timeScale
            self.acceleration *= 0

            #max vel
            if self.velocity.magnitude() > maxVelocity and maxVelocity != -1:
                self.velocity = maxVelocity * pygame.Vector2.normalize(self.velocity)

            
        
        def updatePos(self):
            self.position += self.velocity * timeScale

            #offscreen
            #self.position.x = self.position.x % screen.get_width()
            #self.position.y = self.position.y % screen.get_width()
            if self.position.x < 20:
                self.position.x = 20
                self.velocity.x *= -1
            if self.position.x > screen.get_width() - 20:
                self.position.x = screen.get_width() - 20
                self.velocity.x *= -1
            if self.position.y < 20:
                self.position.y = 20
                self.velocity.y *= -1
            if self.position.y > screen.get_height() - 20:
                self.position.y = screen.get_height() - 20
                self.velocity.y *= -1


#Creating an array that contain a particles
particlesArr:list[Particles] = []
for i in range (len(typeCount)):
    for j in range(typeCount[i]):
            #Init value for each particle
            pos = pygame.Vector2(random.uniform(0,1000),random.uniform(0,1000))
            vel = pygame.Vector2(0,0)
            acc = pygame.Vector2(0,0)
            col = typeColor[i]
            siz = typeSize[i]
            #create a new list entry
            particlesArr.append(Particles(pos, vel, acc, col, siz, i))
    
#camera math
def project(position:pygame.Vector2):
    return (((position - CamOffsets) - (500, 500)) * CamZoom + (500, 500))

while isRunning:
    screen.fill("black")

    #Debug
    keys = pygame.key.get_pressed()
    if keys[pygame.K_t] and particlesDrag > 0.1:
        particlesDrag -= 0.01
    if keys[pygame.K_y]:
        particlesDrag += 0.01
    if keys[pygame.K_r]:
        reRoll()
    
    text_surface = txtFont.render("Drag : " + str(round(particlesDrag, 10)), False, "white")
    screen.blit(text_surface, (0,0))
    
    #camera
    if keys[pygame.K_w]:
        CamOffsets.y -= dt * CamSensitivity
    if keys[pygame.K_s]:
        CamOffsets.y += dt * CamSensitivity
    if keys[pygame.K_a]:
        CamOffsets.x -= dt * CamSensitivity
    if keys[pygame.K_d]:
        CamOffsets.x += dt * CamSensitivity

    if keys[pygame.K_e]:
        CamZoom += dt
    if keys[pygame.K_q]:
        CamZoom -= dt

    #X to exit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False

    #update particles
    for i in range(particleCount):
        particles = particlesArr[i]
        particles.updateVel(particlesArr)
    for i in range(particleCount):
        particles = particlesArr[i]
        particles.updatePos()

        pygame.draw.circle(screen, particles.color, project(particles.position), particles.size * CamZoom)


    pygame.draw.lines(screen, "white", True, [project(pygame.Vector2(0, 0)), project(pygame.Vector2(0, 1000)), project(pygame.Vector2(1000, 1000)), project(pygame.Vector2(1000, 0))], 1)
    pygame.display.flip()
    clock.tick(60)
    dt = clock.tick(60) / 1000

pygame.quit