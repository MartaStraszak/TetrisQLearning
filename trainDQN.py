import random
import numpy as np
import os
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.regularizers import l2
import matplotlib.pyplot as plt
import copy
import os.path
import logging
from gameControlForAgent import *

logging.basicConfig(filename='app4.log', filemode='w', format='%(message)s')

TETROMINOS = ['I','J','L','O','S','Z','T']
W = 10  # width of Tetris board
H = 24  # height
BOARD_CUT = 3   # cut 3 rows from above that does not influence agent learning
FEATURES_H = H-BOARD_CUT 
MODEL_FILE = 'DQN-allT-model-c4-d1-doSmieci'



class State:
    def __init__(self, board, piece):
        self.board = np.copy(board)
        self.piece = piece
    

def getStartingState():
    board = np.zeros((H, W), dtype = int)
    piece = random.choice(TETROMINOS)
    return State(board, piece)

def transition(state, action):
    newBoard, reward = boardAfterAction(state.board, state.piece, action)
    newPiece = random.choice(TETROMINOS)
    isFinal = boardTerminal(newBoard)
    return (State(newBoard, newPiece), reward, isFinal)

def getBoardFromStateAction(state, action):
    ns, r, isFinal = transition(state, action)
    return ns.board

def getAvailableActions(state):
    return validActions(state.board, state.piece)


class BoardValueApproximator:
    def __init__(self):
        if os.path.exists(MODEL_FILE):
            print("wczytuje")
            self.model = keras.models.load_model(MODEL_FILE)
        else:
            self.model = keras.Sequential()
            self.model.add(layers.Conv2D(4, (3, 3), activation='relu', input_shape=(FEATURES_H, W, 1)))
            self.model.add(layers.Flatten())
            self.model.add(layers.Dense(1))
            optimizer = keras.optimizers.Adam(learning_rate=0.00025, clipnorm=1.0)
            self.model.compile(optimizer=optimizer, loss=tf.keras.losses.MeanSquaredError())
        self.optimizer = self.model.optimizer
        self.model.summary()

    def applySeveral(self, boards): #boards maja miec wymiar liczba przykladow x 240
        y = (self.model)(boards)
        nBoards = y.shape[0]
        return np.reshape(y, (nBoards,))

    def printMaxWgtInLayer(self):
        cnt=0
        for l in self.model.layers:
            maxes = []
            for wb in l.get_weights():
                maxes.append(np.max(np.abs(wb)))
            print("Max wgt, bias in layer %d:  %s" %(cnt, maxes))
            logging.warning("Max wgt, bias in layer %d:  %s" %(cnt, maxes))
            cnt+=1

    def saveModel(self):
        self.model.save(MODEL_FILE)
        
    def drawNeurons(self):
        wgts, biases = self.model.layers[0].get_weights()
        wgts = wgts.T
        neuronsNo = wgts.shape[0]
        gridDim=int(np.sqrt(neuronsNo)+0.9999999)
        fig = plt.figure(figsize=(gridDim,gridDim))
        for n in range(neuronsNo):
            neuron = wgts[n][0]
            neuron = (neuron - neuron.min())/(neuron.max() - neuron.min())
            sub1 = plt.subplot(gridDim, gridDim, n+1)
            sub1.set_xticks(())
            sub1.set_yticks(())
            sub1.imshow(neuron, cmap='gray')
        fig.tight_layout(pad=0.1)
        plt.savefig('neuron-conv.png')
        plt.close(fig) 


def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

def drawRewards(listOfRewards, plotName):
    movingAverageReward = moving_average(np.array(listOfRewards),10)
    fig, (ax1, ax2) = plt.subplots(2, 1)
    ax1.plot(listOfRewards, '.-')
    ax1.set_ylabel(plotName)

    ax2.plot(movingAverageReward, '.-')
    ax2.set_ylabel('last 10 MA from ' + plotName)

    plt.savefig(MODEL_FILE+'/' + plotName+ '.png')
    plt.close(fig) 


def generateBoardsActions(state):
    actions = getAvailableActions(state)
    boards = []
    for a in actions:
        b, _= boardAfterAction(state.board, state.piece, a)
        b = np.reshape(b[BOARD_CUT:], (FEATURES_H,W,1))
        boards.append(b)
    boards = np.array(boards)
    return actions, boards


def epsGreedyTransition(eps, bva, s, actions, boards):
    if random.random() < eps:
        a = random.choice(actions)
    else:
        qvals = bva.applySeveral(boards)
        bestIdx = np.argmax(qvals) 
        a = actions[bestIdx]
    ns, r, isFinal = transition(s, a)
    return a, ns, r, isFinal


def trainOneStep(bva, bs, ys):
    huber = tf.keras.losses.Huber()
    bs = np.reshape(bs, (-1, FEATURES_H, W, 1))
    ys = np.reshape(ys, (-1,1))

    with tf.GradientTape() as tape:
        predictions = bva.model(bs)
        loss = huber(ys, predictions)

    grads = tape.gradient(loss, bva.model.trainable_variables)
    bva.optimizer.apply_gradients(zip(grads, bva.model.trainable_variables))


def play(bva, movesNo):
    s = getStartingState()
    rewardPerGame = 0.0
    gainedRewardsPerGame = []
    for m in range(movesNo):
        actions, boards = generateBoardsActions(s)
        a, ns, r, isFinal = epsGreedyTransition(0.0, bva, s, actions, boards)
        rewardPerGame += r
        if isFinal:
            s = getStartingState()
            gainedRewardsPerGame.append(rewardPerGame)
            rewardPerGame = 0.0
        else:
            s = ns
    gainedRewardsPerGame.append(rewardPerGame)
    gainedRewardsPerGame = np.array(gainedRewardsPerGame)
    gamesNo = len(gainedRewardsPerGame)
    averageRewardPerGame = np.mean(gainedRewardsPerGame)
    stdRewardPerGame = np.std(gainedRewardsPerGame)
    totalReward = np.sum(gainedRewardsPerGame)
    print("greedyRewardsPerGAme =", gainedRewardsPerGame )
    return totalReward, gamesNo, averageRewardPerGame, stdRewardPerGame


def main():
    # physical_devices = tf.config.experimental.list_physical_devices('GPU')
    # assert len(physical_devices) > 0, "Not enough GPU hardware devices available"
    # config = tf.config.experimental.set_memory_growth(physical_devices[0], True)

    # pr = cProfile.Profile()
    # pr.enable()
    EPS = 0.1
    BATCH_SIZE = 32
    MEMORY_SIZE = 40000
    MIN_TRAINING_SIZE = 3000
    UPDATE_TARGET = 5000
    OVERSIZE = 1000
    GAMMA = 0.99
    
    boardValueTarget = BoardValueApproximator() 
    boardValueRunning = BoardValueApproximator() 
    
    memory = []
    isFinal = True
    totReward = 0.0
    bestGreedy = 0.0

    allTotalRewards = []
    allAverageGreedyRewards = []
    allTotalGreedyRewards = []

    for t in range(2**40):
        if isFinal:
            s = getStartingState()
            nactions, nboards = generateBoardsActions(s)
        else:
            s = ns
        eps = EPS
        actions, boards = nactions, nboards
        a, ns, r, isFinal = epsGreedyTransition(eps, boardValueRunning, s, actions, boards)
        totReward += r
        if isFinal:
            nboards = None
        else:
            nactions, nboards = generateBoardsActions(ns)
        nb = np.copy(ns.board[BOARD_CUT:])
        memory.append(copy.deepcopy((nb, r, isFinal, nboards)))

        if len(memory) >= MIN_TRAINING_SIZE:
            indices = np.random.randint(len(memory), size=BATCH_SIZE)
            bs = []
            ys = []
            for i in indices:
                mnb, mr, misFinal, mboards = memory[i]
                if misFinal:
                    y = r
                else:
                    mqvals = boardValueTarget.applySeveral(mboards)
                    y = r+GAMMA*np.max(mqvals)
                bs.append(np.copy(mnb))
                ys.append(y)
            bs = np.array(bs)
            ys = np.array(ys)
            trainOneStep(boardValueRunning, bs, ys)

        if t % 1000 == 999:
            print("Step: %d, reward: %f"%(t,totReward))
            allTotalRewards.append(totReward)
            totReward = 0.0
            drawRewards(allTotalRewards, "totalRewards")

        if t % UPDATE_TARGET == 0:
            print("Update Target Model")
            boardValueTarget.model.set_weights(boardValueRunning.model.get_weights())
            boardValueTarget.saveModel()
            boardValueTarget.printMaxWgtInLayer()
            boardValueTarget.drawNeurons()
            totalGreedyReward, greedyGamesNo, averageRewardPerGreedyGame, stdRewardPerGreedyGame = play(boardValueRunning, 1000)
            if totalGreedyReward > bestGreedy:
                print("Updating best model")
                bestGreedy = totalGreedyReward
                boardValueTarget.model.save(MODEL_FILE+"-BEST")
            print("totalGreedyReward = %.2f, greedyGamesNo = %d, averageRewardPerGreedyGame = %.2f, stdRewardPerGreedyGame = %.2f" %(totalGreedyReward, greedyGamesNo, averageRewardPerGreedyGame, stdRewardPerGreedyGame ))
            allAverageGreedyRewards.append(averageRewardPerGreedyGame)
            allTotalGreedyRewards.append(totalGreedyReward)
            drawRewards(allAverageGreedyRewards, "AverageGreedyRewards")
            drawRewards(allTotalGreedyRewards, "TotalGreedyRewards")

        if len(memory) >= MEMORY_SIZE + OVERSIZE:
            toDel = len(memory) - MEMORY_SIZE
            memory = memory[toDel:]


if __name__ == "__main__":
    main()