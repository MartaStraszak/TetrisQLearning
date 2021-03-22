import numpy as np
import pygame, sys, random
from pygame.locals import *
from boardClass import *
from gameControl import *
from drawGame import *
# from GameStateForBen import BenState



    

fps=30
windowWidth = 500
windowHeight = 600
fpsClock = pygame.time.Clock()

keyFuse = 0.2
dropSpeed = 0.25

pygame.init()

screen = pygame.display.set_mode((windowWidth, windowHeight))
pygame.display.set_caption('Tetris')
drawer = GameDrawer(screen)
game = GameState('Human',logging=True)
stepCounter = 0
buttonDelay = {'keyLeft' : 0, 'keyRight' : 0 }
while True:
    stepCounter += 1.0/fps

    screen.fill((204,204,255))
    for key in buttonDelay:
        if buttonDelay[key] > 0:
            buttonDelay[key] += 1.0/fps
        if buttonDelay[key]>= keyFuse:
            buttonDelay[key]=0
    

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                game.movePiece((0,-1))
                buttonDelay['keyLeft']=1.0/fps
            if event.key == pygame.K_RIGHT:
                game.movePiece((0,1))
                buttonDelay['keyRight']=1.0/fps
            if event.key == pygame.K_UP:
                game.rotatePiece()
            if event.key == pygame.K_DOWN:
                game.movePiece((1,0))
            if event.key == pygame.K_SPACE:
                game.hardDrop()
                
    keys = pygame.key.get_pressed()  #checking pressed keys
    # if stepCounter % pressedButtonSpeed == 0:
    if buttonDelay['keyLeft']==0 and keys[pygame.K_LEFT] :
        game.movePiece((0,-1))
    if buttonDelay['keyRight']==0 and keys[pygame.K_RIGHT]:
        game.movePiece((0,1))
    if keys[pygame.K_DOWN]:
        game.movePiece((1,0))
            
            
    if stepCounter >= dropSpeed:      
        game.performStep()
        stepCounter = 0.0
    drawer.drawGame(game)
    pygame.display.update()
    fpsClock.tick(fps)

