import numpy as np
import pygame, sys, random
from pygame.locals import *

class Brick:
    def __init__(self, color=None):
        self.color = color
        if color == None:
            self.empty = True
        else:
            self.empty = False
            
    def __str__(self):
        if self.empty:
            return 'O'
        else:
            return 'X'
    
            
class Board:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.grid = np.array([[Brick()]*self.width for i in range(self.height)])
        
    def __str__(self):
        picture = ''
        for i in range(self.height):
            for j in range(self.width):
                picture += str(self.grid[i][j])
            picture += '\n'
        return picture
        
    def removeLine(self,x):
        for i in range(x):
            self.grid[x-i]=self.grid[x-i-1]
        self.grid[0]=[Brick()]*self.width
        

class Tetromino:
    boxSize = 20
    def __init__(self, type, rotation=0):
        if type == 'RANDOM':
            self.type = random.choice(['I','J','L','O','S','Z','T'])
            self.rotation = 0
        else:
            self.type = type
            self.rotation = rotation
            
        self.boundaryLen = 3
    
        if self.type == 'I':
            self.boundaryLen = 4
            self.block = np.array([[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]])
            self.color = (0,255,255)
        
        elif self.type == 'J':
            self.block = np.array([[1,0,0],[1,1,1],[0,0,0]])
            self.color = (0,0,255)
            
        elif self.type == 'L':
            self.block = np.array([[0,0,1],[1,1,1],[0,0,0]])
            self.color = (255,128,0)
        
        elif self.type == 'O':
            self.boundaryLen = 2
            self.block = np.array([[1,1],[1,1]])
            self.color = (255,255,0)
        
        elif self.type == 'S':
            self.block = np.array([[0,1,1],[1,1,0],[0,0,0]])
            self.color = (0,204,0)
        
        elif self.type == 'T':
            self.block = np.array([[0,1,0],[1,1,1],[0,0,0]])
            self.color = (153,51,255)
        
        elif self.type == 'Z':
            self.block = np.array([[1,1,0],[0,1,1],[0,0,0]])
            self.color = (255,0,0)
        
        self.rotate(self.rotation)
        
            
    def rotate(self,rotation):
        self.rotation = (self.rotation+rotation)%4
        for n in range(rotation%4):
            currentBlock = np.copy(self.block)
            for i in range(self.boundaryLen):
                for j in range(self.boundaryLen):
                    self.block[j][self.boundaryLen-1-i] = currentBlock[i][j]
        
    def __str__(self):
        return str(self.block)
        
    
