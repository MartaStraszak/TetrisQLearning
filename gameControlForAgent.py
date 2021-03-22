
import numpy as np
import random


TETROMINOS = ['I','J','L','O','S','Z','T']
W = 10
H = 24
BOARD_CUT = 3
FEATURES_H = H-BOARD_CUT



class Tetromino:
    def __init__(self, blockType=None, rotation=0):
        self.blockType = random.choice(TETROMINOS)
        self.rotation = rotation
        if blockType != None:
            self.blockType = blockType
        self.boundaryLen = 3
    
        if self.blockType == 'I':
            self.boundaryLen = 4
            self.block = np.array([[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]])
                
        elif self.blockType == 'J':
            self.block = np.array([[1,0,0],[1,1,1],[0,0,0]])
                
        elif self.blockType == 'L':
            self.block = np.array([[0,0,1],[1,1,1],[0,0,0]])
            
        elif self.blockType == 'O':
            self.boundaryLen = 2
            self.block = np.array([[1,1],[1,1]])
            
        elif self.blockType == 'S':
            self.block = np.array([[0,1,1],[1,1,0],[0,0,0]])
        
        elif self.blockType == 'T':
            self.block = np.array([[0,1,0],[1,1,1],[0,0,0]])
            
        elif self.blockType == 'Z':
            self.block = np.array([[1,1,0],[0,1,1],[0,0,0]])
        else:
            assert(0)

        self.rotate(self.rotation)
            
    def rotate(self,rotation):
        self.rotation = (self.rotation+rotation)%4
        for n in range(rotation%4):
            currentBlock = np.copy(self.block)
            for i in range(self.boundaryLen):
                for j in range(self.boundaryLen):
                    self.block[j][self.boundaryLen-1-i] = currentBlock[i][j]


def movePiece(board, block, boxLen, position, direction):
    '''direction is (dx,dy) -- returns whether movement is possibe'''
    newX, newY = position[0]+direction[0], position[1]+direction[1]  # pierwsze w pionie drugie w poziomie
    for x in range(boxLen):
        for y in range(boxLen):
            if not block[x][y]:
                continue
            if (newX+x<0 or newY+y<0 or newX+x>=H or newY+y>=W) or (board[newX+x][newY+y]):
                return False
    return True

def reduceFullLine(board):
    '''finds a full line and removes it
    the part on top of it drops one unit down
    returns true if line found'''
    for x in range(H):
        if np.all(board[x]):   # np.all returns True if all elements of a given array evaluate to True
            board[1:x+1] = board[:x]
            board[0]=np.zeros(W)
            return True
    return False


def boardTerminal(board):
    for j in range(W):
        if board[3][j]:
            return True
    return False


def piecePasteToBoard(board, block, boxLen, position):
    '''returns copy of a board with new piece and reward'''
    newBoard = np.copy(board)
    for x in range(boxLen):
        for y in range(boxLen):
            if block[x][y]:
                newBoard[position[0]+x][position[1]+y] = 1
    reward = 0.1
    while reduceFullLine(newBoard):
        reward += 1.0
    return newBoard, reward

def boardAfterAction(board, piece, action):
    move, rotation = action
    tet = Tetromino(piece, rotation)
    pieceBlock = tet.block
    boxLen = tet.boundaryLen
    currX, currY = (0,4)
    if movePiece(board, pieceBlock, boxLen, (0,4), (0, move)) == False:
        assert(0)
        return False 
    currY += move
    while movePiece(board, pieceBlock, boxLen, (currX, currY), (1,0)) != False:
        currX += 1
    return piecePasteToBoard(board, pieceBlock, boxLen, (currX, currY))

def validActions(board, pieceType):
    '''returns list of pairs (move, rotation)'''
    actions = []
    for shift in range(-7,8):
        for rot in range(4):
            pieceBlock = Tetromino(pieceType, rot).block
            boxLen = Tetromino(pieceType, rot).boundaryLen
            if movePiece(board, pieceBlock, boxLen, (0,4), (0,shift)):
                actions.append((shift, rot))
    return actions