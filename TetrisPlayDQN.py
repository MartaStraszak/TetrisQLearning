import numpy as np
import pygame, sys
from pygame.locals import *
from gameControl import *
from drawGame import *
import tensorflow as tf
from tensorflow import keras
import os.path
from gameControlForAgent import *

TETROMINOS = ['I','J','L','O','S','Z','T']
W = 10
H = 24
BOARD_CUT = 3
FEATURES_H = H-BOARD_CUT
MODEL_FILE = 'DQN-allT-model-c8-d1-BEST'


class BoardValueApproximator:
    def __init__(self):
        assert(os.path.exists(MODEL_FILE))
        self.model = keras.models.load_model(MODEL_FILE)
        self.model.summary()

    def applySeveral(self, boards):
        y = (self.model)(boards)
        nBoards = y.shape[0]
        return np.reshape(y, (nBoards,))


def generateBoardsActions(board, piece):
    actions = validActions(board, piece)
    boards = []
    for a in actions:
        b, _= boardAfterAction(board, piece, a)
        b = np.reshape(b[BOARD_CUT:], (FEATURES_H,W,1))
        boards.append(b)
    boards = np.array(boards)
    return actions, boards


def greedyTransition(bva, actions, boards):
    qvals = bva.applySeveral(boards)
    bestIdx = np.argmax(qvals) 
    a = actions[bestIdx]
    return a

def getAction(bva, board, piece):
    actions, boards = generateBoardsActions(board, piece)
    return greedyTransition(bva, actions, boards)

def getBoardFromGameState(gameState):
    board = np.zeros((H,W))
    for i in range(H):
        for j in range(W):
            board[i][j] = int(not gameState.gameBoard.grid[i][j].empty)
    return board

def main():
    physical_devices = tf.config.experimental.list_physical_devices('GPU')
    assert len(physical_devices) > 0, "Not enough GPU hardware devices available"
    config = tf.config.experimental.set_memory_growth(physical_devices[0], True)
    fps=180
    windowWidth = 500
    windowHeight = 600
    fpsClock = pygame.time.Clock()
    keyFuse = 0.2
    dropSpeed = 0.05
    pygame.init()
    screen = pygame.display.set_mode((windowWidth, windowHeight))
    pygame.display.set_caption('Tetris')
    drawer = GameDrawer(screen)
    game = GameState('Human')
    stepCounter = 0
    boardValApprox = BoardValueApproximator()
    while True:
        stepCounter += 1.0/fps
        screen.fill((204,204,255))
        if game.isGameOver():
            print('Final Score '+str(game.score))
            game = GameState('Human')

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        if stepCounter >= dropSpeed:  
            if game.currentPiecePos == (0,4):
                currBoard = getBoardFromGameState(game)
                currPieceType = game.currentPiece.type
                action = getAction(boardValApprox, currBoard, currPieceType)
                shift,rot = action
                for i in range(rot):
                    game.rotatePiece()
                game.movePiece((0,shift))
            game.performStep()
            stepCounter = 0.0
        drawer.drawGame(game)
        pygame.display.update()
        fpsClock.tick(fps)



if __name__ == "__main__":
    main()