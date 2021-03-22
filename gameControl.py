import numpy as np
import pygame, sys, random
from pygame.locals import *
from boardClass import *

class GameState:
    def __init__(self, playerType='Human',logging=False):
        self.playerType = playerType
        self.width = 10
        self.height = 24
        self.gameBoard = Board(self.height,self.width)
        self.currentPiece = Tetromino('RANDOM')
        self.currentPiecePos = (0,4)
        self.nextPiece = Tetromino('RANDOM')
        self.score = 0
        self.gameRunning = True
        self.logging = logging
        self.dataMemory=[]
        self.actionLog='HumanTraining.txt'
        
    def isWithinBoard(self,x,y):
        if x<0 or y<0 or x>=self.height or y>=self.width:
            return False
        return True
        
    def movePiece(self, direction):
        '''direction is (dx,dy) -- returns whether movement was successful'''
        newX, newY = self.currentPiecePos[0]+direction[0], self.currentPiecePos[1]+direction[1]
        boxLen = self.currentPiece.boundaryLen
        for x in range(boxLen):
            for y in range(boxLen):
                if not self.currentPiece.block[x][y]:
                    continue
                if not self.isWithinBoard(newX+x,newY+y) or (not self.gameBoard.grid[newX+x][newY+y].empty):
                    return False
        self.currentPiecePos = newX, newY
        return True
        
    def rotatePiece(self):
        '''returns whether rotation was successful'''
        curX, curY = self.currentPiecePos[0], self.currentPiecePos[1]
        boxLen = self.currentPiece.boundaryLen
        self.currentPiece.rotate(1)
        for x in range(boxLen):
            for y in range(boxLen):
                if not self.currentPiece.block[x][y]:
                    continue
                if not self.isWithinBoard(curX+x,curY+y) or (not self.gameBoard.grid[curX+x][curY+y].empty):
                    self.currentPiece.rotate(3)
                    return False
        return True
        
    def reduceFullLine(self):
        '''finds a full line and removes it
        the part on top of it drops one unit down
        returns true if line found'''
        for x in range(self.height):
            fullLine=True
            for y in range(self.width):
                if self.gameBoard.grid[x][y].empty:
                    fullLine=False
            if fullLine:
                self.gameBoard.removeLine(x)
                return True
        return False
        
    def isGameOver(self):
        for y in range(self.width):
            if not self.gameBoard.grid[3][y].empty:
                return True
        return False
        
        
        
    def reduceLines(self):
        '''reduce lines until not possible
        return the number of lines reduced'''
        num = 0
        while self.reduceFullLine():
            num+=1
        return num
        
        
    def handlePieceDrop(self):
        '''returns whether game is over or not'''
        # if self.logging:
        #     self.addTrainingSample()
        curX, curY = self.currentPiecePos[0], self.currentPiecePos[1]
        boxLen = self.currentPiece.boundaryLen
        for x in range(boxLen):
            for y in range(boxLen):
                if self.currentPiece.block[x][y]:
                    self.gameBoard.grid[curX+x][curY+y]=Brick(self.currentPiece.color)
        self.currentPiece = Tetromino(self.nextPiece.type,self.nextPiece.rotation)
        self.currentPiecePos = (0,4)
        self.nextPiece = Tetromino('RANDOM')
        linesReduced = self.reduceLines()
        self.score += linesReduced
        
        if self.isGameOver():
            self.gameRunning = False
            return False
        return True
        
    def performStep(self):
        if not self.gameRunning:
            return
        if not self.movePiece((1,0)):
            self.handlePieceDrop()
            
    def hardDrop(self):
        if not self.gameRunning:
            return
        while True:
            if not self.movePiece((1,0)):
                self.handlePieceDrop()
                break
                
    # def addTrainingSample(self):
    #     currBoard = BenState(gameState = self)
    #     currPieceType = self.currentPiece.type
    #     currShift = self.currentPiecePos[1]-4
    #     currRot = self.currentPiece.rotation
    #     self.dataMemory.append((currBoard,currPieceType,currShift,currRot))
    #     if len(self.dataMemory)>10:
    #         self.dumpDataToFile()
                
    # def dumpDataToFile(self):
    #     f = open(self.actionLog,'a')
    #     for boardState,pieceType,shift,rot in self.dataMemory:
    #         f.write(boardState.stateToStr()+' '+pieceType+' '+str(shift)+' '+str(rot)+'\n')
    #     f.close()
    #     self.dataMemory=[]
