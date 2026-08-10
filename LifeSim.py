import pygame
import random
import time
from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import numpy as np

screen = pygame.display.set_mode((1600,900), pygame.RESIZABLE)
width = screen.get_width()
height = screen.get_height()

pygame.init()
pygame.font.init()
#Text
txtFont = pygame.font.SysFont('Comic Sans MS', 20)

isRunning = True

#camera
CamSensitivity = 1000
CamOffsets = pygame.Vector2(0,0)
CamZoom = 0.7

#params
mapSize = 400 / 0.7

drawName = False
drawLine = False
drawStat = False

tickRate = 1/100

entityCount = [10,50,100]
entityMoveSpeed = [11,9,0]
entitySightRange = [400,300,0]
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

    @abstractmethod
    def update(self, otherAnimals):
        pass
        

    def searchForTarget(self, otherAnimals):
        target = []
        for other in otherAnimals:
            if other == self: continue
            distance = self.position.distance_to(other.position)
            if distance < self.sightrange:
                target.append(other)
                if drawLine: pygame.draw.line(screen, "white", render(self.position), render(other.position))
        target.sort(key=lambda other: self.position.distance_to(other.position))
        return target


class Animal(Entity):
    def __init__(self, position, movementSpeed, sightrange, color, size):
            super().__init__(position, movementSpeed, sightrange, color, size)
            #abstract variable
            self.freakyRate = 0

            self.satiation = 1
            self.hungerRate = 0
            self.foodSource = []

            self.fearSource = []

            #Const
            self.freaky = random.uniform(0,100)
            self.hunger = 33 + random.uniform(0,50)

    def update(self, otherAnimals):
        #updateHunger / Freaky
        if self.freaky < 100:
            self.freaky += self.freakyRate
        if self.hunger > 0:
            self.hunger -= self.hungerRate
        elif self.hunger <= 0:
            if self in entityArray: entityArray.remove(self)

        #border
        distance_to_center = pygame.Vector2.distance_to(self.position, pygame.Vector2(width/2, height/2))
        if distance_to_center > mapSize:
            normalize_to_center = pygame.Vector2.normalize(self.position - pygame.Vector2(width/2, height/2))
            self.position -= (distance_to_center - mapSize) * normalize_to_center

        #position
        self.doAction(self.searchForTarget(otherAnimals), self.decideIgnored())

    def doAction(self, target, ignored):
        main_target = "none"
        #if the main_target is ignore then go find the next target
        for obj in target:
            relevant = obj.name in self.foodSource or obj.name == self.name or obj.name in self.fearSource
            if not relevant: continue
            if obj.name in self.foodSource and "food" in ignored: continue
            if obj.name == self.name and "sex" in ignored: continue
            main_target = obj
            break

        if main_target == "none": return
        #Animal specific action
        normalize_to_target = pygame.Vector2(0,0)
        deltaVector = self.position - main_target.position
        if deltaVector.length() != 0: 
            normalize_to_target = pygame.Vector2.normalize(deltaVector)

        #flee
        if main_target.name in self.fearSource:
            self.position += self.movementSpeed * normalize_to_target
        #Approach
        elif main_target.name in self.foodSource or main_target.name  == self.name:
            self.position -= self.movementSpeed * normalize_to_target
    
        #Food and Reproduction
        if self.position.distance_to(main_target.position) < self.size:
            if main_target.name in self.foodSource:
                #Food and consumption
                self.hunger = 100 * self.satiation
                if main_target in entityArray: entityArray.remove(main_target)
            elif main_target.name == self.name:
                #reproduce
                if self.freaky >= 100:
                    self.freaky = 0
                    self.hunger = min(self.hunger, 33)
                    entityArray.append(type(self)(self.position.copy(), self.movementSpeed, self.sightrange, self.color, self.size))

    def decideIgnored(self):
        ignored_action = []
        if self.hunger > 60: ignored_action.append("food")
        if self.freaky < 100: ignored_action.append("sex")
        return list(set(ignored_action))

#Animal
class Fox(Animal):
    def __init__(self, position, movementSpeed, sightrange, color, size):
        super().__init__(position, movementSpeed, sightrange, color, size)

        #Const
        self.name = "fox"
        self.satiation = 0.7
        self.freakyRate = 0.2
        self.hungerRate = 0.5
        self.foodSource = ["sheep"]
        self.fearSource = []


class Sheep(Animal):
    def __init__(self, position, movementSpeed, sightrange, color, size):
        super().__init__(position, movementSpeed, sightrange, color, size)

        #Const
        self.name = "sheep"
        self.satiation = 0.2
        self.freakyRate = 1
        self.hungerRate = 0.5
        self.foodSource = ["tree"]
        self.fearSource = ["fox"]
        
#Tree
class Tree(Entity):
    def __init__(self, position, movementSpeed, sightrange, color, size):
        super().__init__(position, movementSpeed, sightrange, color, size)
        self.spawnProgress = random.uniform(0,100)

        #Const
        self.name = "tree"
        self.spawnRadius = 100
        self.spawnRate = 4

    def update(self, otherAnimals):
        #updateHunger / Freaky
        if self.spawnProgress < 100:
            self.spawnProgress += self.spawnRate

            if self.spawnProgress >= 100:
                self.spawnProgress = 0
                entityArray.append(type(self)((self.position + pygame.Vector2(random.uniform(-self.spawnRadius, self.spawnRadius), random.uniform(-self.spawnRadius, self.spawnRadius))), self.movementSpeed, self.sightrange, self.color, self.size))

        #border
        distance_to_center = pygame.Vector2.distance_to(self.position, pygame.Vector2(width/2, height/2))
        if distance_to_center > mapSize:
            if self in entityArray: entityArray.remove(self)

            
#Creating an array that contain all of the animals
entityArray:list[Entity] = []

for i in range (len(entityType)):
    for j in range(entityCount[i]):
            #Init value for each particle
            pos = pygame.Vector2((width / 2) + random.uniform(-mapSize, mapSize),(height / 2) + random.uniform(-mapSize, mapSize))
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

#Modified data to match the camera
def render(base):
    return pygame.Vector2(width / 2,height / 2) + ((pygame.Vector2(width / 2,height / 2) - (base - CamOffsets)) * CamZoom)

#Main Loop
while isRunning:
    screen.fill("white")
    pygame.draw.circle(screen, "lime", render(pygame.Vector2(width/2, height/2)), mapSize * CamZoom * 1.1)

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
        if drawName:
            txtFont = pygame.font.SysFont('Comic Sans MS', max(20 * int(CamZoom), 16))
            text = txtFont.render(str(i.name), True, "white")
            screen.blit(text, render(i.position))

        #Stats
        if drawStat == True:
            if isinstance(i, Animal):
                text2 = txtFont.render(str(round(i.hunger, 2)), True, "white")
                screen.blit(text2, render(i.position - pygame.Vector2(0,20)))
                text3 = txtFont.render(str(round(i.freaky, 2)), True, "white")
                screen.blit(text3, render(i.position - pygame.Vector2(0,40)))
            if isinstance(i, Tree):
                text4 = txtFont.render(str(round(i.spawnProgress, 2)), True, "white")
                screen.blit(text4, render(i.position - pygame.Vector2(0,20)))
    pygame.display.flip()

    #Quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False

    plt.pause(tickRate)


pygame.quit