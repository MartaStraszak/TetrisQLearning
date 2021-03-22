import numpy as np
import pygame, sys, random
from pygame.locals import *
from gameControl import *

class GameDrawer:
    black = (0,0,0)
    
    def __init__(self, screen):
        self.screen = screen
        
    def drawGame(self, gameState):
        brickSize = 20
        offsetX = 50
        offsetY = 50
        self.drawBoard(gameState, brickSize, offsetX, offsetY)
        self.drawCurrentPiece(gameState, brickSize, offsetX, offsetY)
        self.drawNextPieceArea(gameState, brickSize)
        self.drawScore(gameState)
        
        
        
    def drawBoard(self,gameState, brickSize, offsetX, offsetY):
        boardWidth = 10
        boardHeight = 24
        frameThick=4
        frameColor = (0, 102, 204)
        
        pygame.draw.rect(self.screen, self.black, (offsetY, offsetX, (brickSize+1) * boardWidth + 3, (brickSize+1) * boardHeight + 3))
        frameY, frameX = offsetY - (frameThick)/2, offsetX - (frameThick)/2
        frameWidth, frameHeight = (brickSize+1) * boardWidth + frameThick + 2, (brickSize+1) * boardHeight + frameThick + 2
        pygame.draw.rect(self.screen, frameColor, (frameY, frameX, frameWidth, frameHeight),frameThick)
        
        for x in range(boardHeight):
            for y in range(boardWidth):
                if gameState.gameBoard.grid[x][y].empty:
                    continue
                dx = offsetX +2+ (brickSize+1)*x
                dy = offsetY +2+ (brickSize+1)*y
                brickColor = gameState.gameBoard.grid[x][y].color
                pygame.draw.rect(self.screen, brickColor, (dy, dx, brickSize, brickSize))
    
      
    def drawCurrentPiece(self, gameState, brickSize, offsetX, offsetY):            
        curX, curY = gameState.currentPiecePos[0], gameState.currentPiecePos[1]
        boxLen = gameState.currentPiece.boundaryLen
     
        for x in range(boxLen):
            for y in range(boxLen): 
                if gameState.currentPiece.block[x][y]:
                    dx = offsetX+2+(brickSize+1)*(curX+x)
                    dy = offsetY+2+(brickSize+1)*(curY+y)
                    pygame.draw.rect(self.screen, gameState.currentPiece.color, (dy, dx, brickSize, brickSize))
        
    def drawNextPieceArea(self, gameState, brickSize):   
        areaX, areaY = 70, 320
        frameThick=4
        frameColor = (0, 102, 204)
        areaHeight, areaWidth = (brickSize+1)*6, (brickSize+1)*6 
        pygame.draw.rect(self.screen, self.black, (areaY, areaX, areaWidth, areaHeight))
        frameY, frameX = areaY - (frameThick)/2, areaX - (frameThick)/2
        frameWidth, frameHeight = areaWidth + frameThick , areaHeight + frameThick 
        pygame.draw.rect(self.screen, frameColor, (frameY, frameX, frameWidth, frameHeight),frameThick)
        
        pos_x, pos_y = areaX+(brickSize+1), areaY+(brickSize+1)
        nextBoxLen = gameState.nextPiece.boundaryLen
        for x in range(nextBoxLen):
            for y in range(nextBoxLen): 
                if gameState.nextPiece.block[x][y]:
                    dx = pos_x+(brickSize+1)*(x)
                    dy = pos_y+(brickSize+1)*(y)
                    pygame.draw.rect(self.screen, gameState.nextPiece.color, (dy, dx, brickSize, brickSize))
                    
    

    def drawScore(self, gameState):
        # initialize font; must be called after 'pygame.init()' to avoid 'Font not Initialized' error
        myfont = pygame.font.SysFont("monospace", 30)
        # render text
        label = myfont.render("Score: "+str(gameState.score), 10, (0,0,0))
        self.screen.blit(label, (310, 300))