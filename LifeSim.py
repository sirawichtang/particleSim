import pygame
import random
import time
from abc import ABC, abstractmethod

screen = pygame.display.set_mode((1600,900), pygame.RESIZABLE)
width = screen.get_width()
height = screen.get_height()

pygame.init()
pygame.font.init()
#Text
txtFont = pygame.font.SysFont('Comic Sans MS', 20)

isRunning = True

tickRate = 1/100

mapSize = 800 / 0.7

#camera
CamSensitivity = 1000
CamOffsets = pygame.Vector2(0,0)
CamZoom = 1

entityCount = [10,10,10]
entityMoveSpeed = [1,1,0]
entitySightRange = [200,200,0]
entityColor = ["red", "white", "dark green"]
entitySize = [8,6,10]
entityType = ["fox", "sheep", "tree"]

totalAnimal = sum(entityCount)


class Entity:
    position:pygame.Vector2
    movementSpeed:int
    sightrange:int
    color:str
    size:int
    target:list
    name:str

    def __init__(self, position, movementSpeed, sightrange, color, size):
        self.position = position
        self.movementSpeed = movementSpeed
        self.sightrange = sightrange
        self.color = color
        self.size = size

        self.name = "undefined"


    def update(self, otherAnimals):
        distance_to_center = pygame.Vector2.distance_to(self.position, pygame.Vector2(width/2, height/2))
        if distance_to_center > mapSize:
            normalize_to_center = pygame.Vector2.normalize(self.position - pygame.Vector2(width/2, height/2))
            self.position -= (distance_to_center - mapSize) * normalize_to_center
        

    def searchForTarget(self, otherAnimals):
        target = []
        for other in otherAnimals:
            if other == self: continue
            distance = self.position.distance_to(other.position)
            if distance < self.sightrange:
                target.append(other)
                pygame.draw.line(screen, "white", render(self.position), render(other.position))
        target.sort(key=lambda other: self.position.distance_to(other.position))
        return target


class Animal(Entity):
    def __init__(self, position, movementSpeed, sightrange, color, size):
            super().__init__(position, movementSpeed, sightrange, color, size)

            self.freaky = 0
            self.hunger = 100
            self.freakyRate = None
            self.hungerRate = None

    def update(self, otherAnimals):
        #border
        distance_to_center = pygame.Vector2.distance_to(self.position, pygame.Vector2(width/2, height/2))
        if distance_to_center > mapSize:
            normalize_to_center = pygame.Vector2.normalize(self.position - pygame.Vector2(width/2, height/2))
            self.position -= (distance_to_center - mapSize) * normalize_to_center

        #position
        self.decideAction(self.searchForTarget(otherAnimals), self.decideIgnored())

    @abstractmethod
    def decideAction(self, target):
        pass


    def decideIgnored(self):
        ignored_action = []
        if self.hunger > 50: ignored_action.append("food")
        if self.freaky < 100: ignored_action.append("sex")
        return set(ignored_action)

#Animal
class Fox(Animal):
    def __init__(self, position, movementSpeed, sightrange, color, size):
        super().__init__(position, movementSpeed, sightrange, color, size)
        self.name = "fox"

        self.freakyRate = 0.1
        self.hungerRate = 0.1

    def decideAction(self, target, ignored):
        main_target = "none"
        for obj in target:
            if obj.name == "sheep" and ignored.count("food") == 1: continue
            if obj.name == "fox" and ignored.count("sex") == 1: continue
            main_target = obj
            break

        if main_target == "none": return

        #Animal specific action
        #Approach
        if main_target.name == "sheep" or "fox":
            normalize_to_target = pygame.Vector2.normalize(self.position - main_target.position)
            self.position -= self.movementSpeed * normalize_to_target
        #flee


class Sheep(Animal):
    def __init__(self, position, movementSpeed, sightrange, color, size):
        super().__init__(position, movementSpeed, sightrange, color, size)
        self.name = "sheep"

        self.freakyRate = 0.1
        self.hungerRate = 0.1

    def decideAction(self, target, ignored):
        main_target = "none"
        for obj in target:
            if obj.name == "tree" and ignored == "food": continue
            if obj.name == "sheep" and ignored == "sex": continue
            main_target = obj
            break

        if main_target == "none": return

        #Animal specific action
        #Approach
        if main_target.name == "sheep" or "tree":
            normalize_to_target = pygame.Vector2.normalize(self.position - main_target.position)
            self.position -= self.movementSpeed * normalize_to_target
        #flee
        if main_target.name == "fox":
                normalize_to_target = pygame.Vector2.normalize(self.position - main_target.position)
                self.position += self.movementSpeed * normalize_to_target

        
#Static
class Tree(Entity): #tree is an animal now :3
    def __init__(self, position, movementSpeed, sightrange, color, size):
        super().__init__(position, movementSpeed, sightrange, color, size)
        self.name = "tree"
            

#Creating an array that contain all of the animals
entityArray:list[Entity] = []

for i in range (len(entityType)):
    for j in range(entityCount[i]):
            #Init value for each particle
            pos = pygame.Vector2(random.uniform(0,1000),random.uniform(0,1000))
            moveSpd = entityMoveSpeed[i]
            sightrge = entitySightRange[i]
            col = entityColor[i]
            siz = entitySize[i]
            #create a new list entry
            if entityType[i] == "fox":
                entityArray.append(Fox(pos, moveSpd, sightrge, col, siz))

            if entityType[i] == "sheep":
                entityArray.append(Sheep(pos, moveSpd, sightrge, col, siz))

            if entityType[i] == "tree":
                entityArray.append(Tree(pos, moveSpd, sightrge, col, siz))

def render(base):
    return pygame.Vector2(width / 2,height / 2) + ((pygame.Vector2(width / 2,height / 2) - (base - CamOffsets)) * CamZoom)

while isRunning:
    screen.fill("white")
    pygame.draw.circle(screen, "lime", render(pygame.Vector2(width/2, height/2)), mapSize * CamZoom)

    #Updating
    for i in entityArray:
        i.update(entityArray)

    #camera
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        CamOffsets.y += tickRate * CamSensitivity / CamZoom
    if keys[pygame.K_s]:
        CamOffsets.y -= tickRate * CamSensitivity / CamZoom
    if keys[pygame.K_a]:
        CamOffsets.x += tickRate * CamSensitivity / CamZoom
    if keys[pygame.K_d]:
        CamOffsets.x -= tickRate * CamSensitivity / CamZoom
    
    if keys[pygame.K_q]:
        CamZoom += tickRate
    if keys[pygame.K_e]:
        CamZoom -= tickRate
    
    #Rendering
    for i in entityArray:
        pygame.draw.circle(screen, i.color, render(i.position), i.size * CamZoom)
        text = txtFont.render(str(i.name), True, "white")
        screen.blit(text, render(i.position))
    pygame.display.flip()

    #Quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False

    time.sleep(tickRate)


print(entityArray)
pygame.quit