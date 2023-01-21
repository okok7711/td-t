from constants import (
    STARTING_LEVEL,
    BLACK,
    BORDER_COLOR,
    WHITE,
    blockColors,
    DARK_GRAY,
    LIGHT_GRAY,
    TEXT_COLOR,
    ROW,
    pieceDefs,
    COL,
    NUM_COLOR,
    SINE_ANI_PERIOD,
    CLEAR_ANI_PERIOD,
    baseLinePoints,
    fontGAMEOVER,
    fontPAUSE,
    fontSB,
    fontSmall,
    fontTitle,
    fontVersion,
    pieceNames,
    levelSpeeds
)
from block import MovingPiece

import math
import random


class MainBoard:

    def __init__(self, blockSize, xPos, yPos, colNum, rowNum, boardLineWidth, blockLineWidth, scoreBoardWidth, **kwargs):

        # Size and position initiations
        self.blockSize = blockSize
        self.xPos = xPos
        self.yPos = yPos
        self.colNum = colNum
        self.rowNum = rowNum
        self.boardLineWidth = boardLineWidth
        self.blockLineWidth = blockLineWidth
        self.scoreBoardWidth = scoreBoardWidth

        self.game = kwargs.pop("game")
        self.clock = kwargs.pop("clock")
        self.display = kwargs.pop("display")
        self.key = kwargs.pop("key")

        # Matrix that contains all the existing blocks in the game board, except the moving piece
        self.blockMat = [['empty'] * colNum for i in range(rowNum)]

        self.piece = MovingPiece(
            colNum, rowNum, 'uncreated', self.key, self.clock)

        self.lineClearStatus = 'idle'  # 'clearRunning' 'clearFin'
        self.clearedLines = [-1, -1, -1, -1]

        self.gameStatus = 'firstStart'  # 'running' 'gameOver'
        self.gamePause = False
        self.nextPieces = ['I', 'I']

        self.score = 0
        self.level = STARTING_LEVEL
        self.lines = 0

    def restart(self):
        self.blockMat = [['empty'] * self.colNum for i in range(self.rowNum)]

        self.piece = MovingPiece(
            self.colNum, self.rowNum, 'uncreated', self.key, self.clock)

        self.lineClearStatus = 'idle'
        self.clearedLines = [-1, -1, -1, -1]
        self.clock.fall.preFrame = self.clock.frameTick
        self.generateNextTwoPieces()
        self.gameStatus = 'running'
        self.gamePause = False

        self.score = 0
        self.level = STARTING_LEVEL
        self.lines = 0

        self.clock.restart()

    def erase_BLOCK(self, xRef, yRef, row, col):
        self.game.draw.rect(self.display, BLACK, [
            xRef+(col*self.blockSize), yRef+(row*self.blockSize), self.blockSize, self.blockSize], 0)

    def draw_BLOCK(self, xRef, yRef, row, col, color):
        self.game.draw.rect(self.display, BLACK, [xRef+(col*self.blockSize), yRef+(
            row*self.blockSize), self.blockSize, self.blockLineWidth], 0)
        self.game.draw.rect(self.display, BLACK, [xRef+(col*self.blockSize)+self.blockSize -
                                                  self.blockLineWidth, yRef+(row*self.blockSize), self.blockLineWidth, self.blockSize], 0)
        self.game.draw.rect(self.display, BLACK, [xRef+(col*self.blockSize), yRef+(
            row*self.blockSize), self.blockLineWidth, self.blockSize], 0)
        self.game.draw.rect(self.display, BLACK, [xRef+(col*self.blockSize), yRef+(
            row*self.blockSize)+self.blockSize-self.blockLineWidth, self.blockSize, self.blockLineWidth], 0)

        self.game.draw.rect(self.display, color, [xRef+(col*self.blockSize)+self.blockLineWidth, yRef+(
            row*self.blockSize)+self.blockLineWidth, self.blockSize-(2*self.blockLineWidth), self.blockSize-(2*self.blockLineWidth)], 0)

    def draw_GAMEBOARD_BORDER(self):
        self.game.draw.rect(self.display, BORDER_COLOR, [self.xPos-self.boardLineWidth-self.blockLineWidth, self.yPos-self.boardLineWidth -
                                                         self.blockLineWidth, (self.blockSize*self.colNum)+(2*self.boardLineWidth)+(2*self.blockLineWidth), self.boardLineWidth], 0)
        self.game.draw.rect(self.display, BORDER_COLOR, [self.xPos+(self.blockSize*self.colNum)+self.blockLineWidth, self.yPos-self.boardLineWidth -
                                                         self.blockLineWidth, self.boardLineWidth, (self.blockSize*self.rowNum)+(2*self.boardLineWidth)+(2*self.blockLineWidth)], 0)
        self.game.draw.rect(self.display, BORDER_COLOR, [self.xPos-self.boardLineWidth-self.blockLineWidth, self.yPos-self.boardLineWidth -
                                                         self.blockLineWidth, self.boardLineWidth, (self.blockSize*self.rowNum)+(2*self.boardLineWidth)+(2*self.blockLineWidth)], 0)
        self.game.draw.rect(self.display, BORDER_COLOR, [self.xPos-self.boardLineWidth-self.blockLineWidth, self.yPos+(
            self.blockSize*self.rowNum)+self.blockLineWidth, (self.blockSize*self.colNum)+(2*self.boardLineWidth)+(2*self.blockLineWidth), self.boardLineWidth], 0)

    def draw_GAMEBOARD_CONTENT(self):

        if self.gameStatus == 'firstStart':

            titleText = fontTitle.render('TETRIS', False, WHITE)
            self.display.blit(titleText, (self.xPos++1.55 *
                                          self.blockSize, self.yPos+8*self.blockSize))

            versionText = fontVersion.render('v 1.0', False, WHITE)
            self.display.blit(versionText, (self.xPos++7.2 *
                                            self.blockSize, self.yPos+11.5*self.blockSize))

        else:

            for row in range(0, self.rowNum):
                for col in range(0, self.colNum):
                    if self.blockMat[row][col] == 'empty':
                        self.erase_BLOCK(self.xPos, self.yPos, row, col)
                    else:
                        self.draw_BLOCK(self.xPos, self.yPos, row,
                                        col, blockColors[self.blockMat[row][col]])

            if self.piece.status == 'moving':
                for i in range(0, 4):
                    self.draw_BLOCK(
                        self.xPos, self.yPos, self.piece.blocks[i].currentPos.row, self.piece.blocks[i].currentPos.col, blockColors[self.piece.type])

            if self.gamePause == True:
                self.game.draw.rect(self.display, DARK_GRAY, [
                    self.xPos+1*self.blockSize, self.yPos+8*self.blockSize, 8*self.blockSize, 4*self.blockSize], 0)
                pauseText = fontPAUSE.render('PAUSE', False, BLACK)
                self.display.blit(
                    pauseText, (self.xPos++1.65*self.blockSize, self.yPos+8*self.blockSize))

            if self.gameStatus == 'gameOver':
                self.game.draw.rect(self.display, LIGHT_GRAY, [
                    self.xPos+1*self.blockSize, self.yPos+8*self.blockSize, 8*self.blockSize, 8*self.blockSize], 0)
                gameOverText0 = fontGAMEOVER.render('GAME', False, BLACK)
                self.display.blit(
                    gameOverText0, (self.xPos++2.2*self.blockSize, self.yPos+8*self.blockSize))
                gameOverText1 = fontGAMEOVER.render('OVER', False, BLACK)
                self.display.blit(
                    gameOverText1, (self.xPos++2.35*self.blockSize, self.yPos+12*self.blockSize))

    def draw_SCOREBOARD_BORDER(self):
        self.game.draw.rect(self.display, BORDER_COLOR, [self.xPos+(self.blockSize*self.colNum)+self.blockLineWidth, self.yPos -
                                                         self.boardLineWidth-self.blockLineWidth, self.scoreBoardWidth+self.boardLineWidth, self.boardLineWidth], 0)
        self.game.draw.rect(self.display, BORDER_COLOR, [self.xPos+(self.blockSize*self.colNum)+self.boardLineWidth+self.blockLineWidth+self.scoreBoardWidth, self.yPos -
                                                         self.boardLineWidth-self.blockLineWidth, self.boardLineWidth, (self.blockSize*self.rowNum)+(2*self.boardLineWidth)+(2*self.blockLineWidth)], 0)
        self.game.draw.rect(self.display, BORDER_COLOR, [self.xPos+(self.blockSize*self.colNum)+self.blockLineWidth, self.yPos+(
            self.blockSize*self.rowNum)+self.blockLineWidth, self.scoreBoardWidth+self.boardLineWidth, self.boardLineWidth], 0)

    def draw_SCOREBOARD_CONTENT(self):

        xPosRef = self.xPos+(self.blockSize*self.colNum) + \
            self.boardLineWidth+self.blockLineWidth
        yPosRef = self.yPos
        yLastBlock = self.yPos+(self.blockSize*self.rowNum)

        if self.gameStatus == 'running':
            nextPieceText = fontSB.render('next:', False, TEXT_COLOR)
            self.display.blit(
                nextPieceText, (xPosRef+self.blockSize, self.yPos))

            blocks = [[0, 0], [0, 0], [0, 0], [0, 0]]
            origin = [0, 0]
            for i in range(0, 4):
                blocks[i][ROW] = origin[ROW] + \
                    pieceDefs[self.nextPieces[1]][i][ROW]
                blocks[i][COL] = origin[COL] + \
                    pieceDefs[self.nextPieces[1]][i][COL]

                if self.nextPieces[1] == 'O':
                    self.draw_BLOCK(xPosRef+0.5*self.blockSize, yPosRef+2.25*self.blockSize,
                                    blocks[i][ROW], blocks[i][COL], blockColors[self.nextPieces[1]])
                elif self.nextPieces[1] == 'I':
                    self.draw_BLOCK(xPosRef+0.5*self.blockSize, yPosRef+1.65*self.blockSize,
                                    blocks[i][ROW], blocks[i][COL], blockColors[self.nextPieces[1]])
                else:
                    self.draw_BLOCK(xPosRef+1*self.blockSize, yPosRef+2.25*self.blockSize,
                                    blocks[i][ROW], blocks[i][COL], blockColors[self.nextPieces[1]])

            if self.gamePause == False:
                pauseText = fontSmall.render('P -> pause', False, WHITE)
                self.display.blit(
                    pauseText, (xPosRef+1*self.blockSize, yLastBlock-15*self.blockSize))
            else:
                unpauseText = fontSmall.render(
                    'P -> unpause', False, self.whiteSineAnimation())
                self.display.blit(
                    unpauseText, (xPosRef+1*self.blockSize, yLastBlock-15*self.blockSize))

            restartText = fontSmall.render('R -> restart', False, WHITE)
            self.display.blit(
                restartText, (xPosRef+1*self.blockSize, yLastBlock-14*self.blockSize))

        else:

            yBlockRef = 0.3
            text0 = fontSB.render('press', False, self.whiteSineAnimation())
            self.display.blit(text0, (xPosRef+self.blockSize,
                                      self.yPos+yBlockRef*self.blockSize))
            text1 = fontSB.render('enter', False, self.whiteSineAnimation())
            self.display.blit(text1, (xPosRef+self.blockSize,
                                      self.yPos+(yBlockRef+1.5)*self.blockSize))
            text2 = fontSB.render('to', False, self.whiteSineAnimation())
            self.display.blit(text2, (xPosRef+self.blockSize,
                                      self.yPos+(yBlockRef+3)*self.blockSize))
            if self.gameStatus == 'firstStart':
                text3 = fontSB.render(
                    'start', False, self.whiteSineAnimation())
                self.display.blit(text3, (xPosRef+self.blockSize,
                                          self.yPos+(yBlockRef+4.5)*self.blockSize))
            else:
                text3 = fontSB.render(
                    'restart', False, self.whiteSineAnimation())
                self.display.blit(text3, (xPosRef+self.blockSize,
                                          self.yPos+(yBlockRef+4.5)*self.blockSize))

        self.game.draw.rect(self.display, BORDER_COLOR, [
            xPosRef, yLastBlock-12.5*self.blockSize, self.scoreBoardWidth, self.boardLineWidth], 0)

        scoreText = fontSB.render('score:', False, TEXT_COLOR)
        self.display.blit(scoreText, (xPosRef+self.blockSize,
                                      yLastBlock-12*self.blockSize))
        scoreNumText = fontSB.render(str(self.score), False, NUM_COLOR)
        self.display.blit(scoreNumText, (xPosRef+self.blockSize,
                                         yLastBlock-10*self.blockSize))

        levelText = fontSB.render('level:', False, TEXT_COLOR)
        self.display.blit(levelText, (xPosRef+self.blockSize,
                                      yLastBlock-8*self.blockSize))
        levelNumText = fontSB.render(str(self.level), False, NUM_COLOR)
        self.display.blit(levelNumText, (xPosRef+self.blockSize,
                                         yLastBlock-6*self.blockSize))

        linesText = fontSB.render('lines:', False, TEXT_COLOR)
        self.display.blit(linesText, (xPosRef+self.blockSize,
                                      yLastBlock-4*self.blockSize))
        linesNumText = fontSB.render(str(self.lines), False, NUM_COLOR)
        self.display.blit(linesNumText, (xPosRef+self.blockSize,
                                         yLastBlock-2*self.blockSize))

    # All the screen drawings occurs in this function, called at each game loop iteration
    def draw(self):

        self.draw_GAMEBOARD_BORDER()
        self.draw_SCOREBOARD_BORDER()

        self.draw_GAMEBOARD_CONTENT()
        self.draw_SCOREBOARD_CONTENT()

    def whiteSineAnimation(self):

        sine = math.floor(
            255 * math.fabs(math.sin(2*math.pi*(self.clock.frameTick/(SINE_ANI_PERIOD*2)))))
        #sine = 127 + math.floor(127 * math.sin(2*math.pi*(self.clock.frameTick/SINE_ANI_PERIOD)))
        sineEffect = [sine, sine, sine]
        return sineEffect

    def lineClearAnimation(self):

        clearAniStage = math.floor(
            (self.clock.frameTick - self.clock.clearAniStart)/CLEAR_ANI_PERIOD)
        halfCol = math.floor(self.colNum/2)
        if clearAniStage < halfCol:
            for i in range(0, 4):
                if self.clearedLines[i] >= 0:
                    self.blockMat[self.clearedLines[i]][(
                        halfCol)+clearAniStage] = 'empty'
                    self.blockMat[self.clearedLines[i]][(
                        halfCol-1)-clearAniStage] = 'empty'
        else:
            self.lineClearStatus = 'cleared'

    def dropFreeBlocks(self):  # Drops down the floating blocks after line clears occur

        for cLIndex in range(0, 4):
            if self.clearedLines[cLIndex] >= 0:
                for rowIndex in range(self.clearedLines[cLIndex], 0, -1):
                    for colIndex in range(0, self.colNum):
                        self.blockMat[rowIndex +
                                      cLIndex][colIndex] = self.blockMat[rowIndex+cLIndex-1][colIndex]

                for colIndex in range(0, self.colNum):
                    self.blockMat[0][colIndex] = 'empty'

    # Returns index list(length of 4) of cleared lines(-1 if not assigned as cleared line)
    def getCompleteLines(self):

        clearedLines = [-1, -1, -1, -1]
        cLIndex = -1
        rowIndex = self.rowNum - 1

        while rowIndex >= 0:
            for colIndex in range(0, self.colNum):
                if self.blockMat[rowIndex][colIndex] == 'empty':
                    rowIndex = rowIndex - 1
                    break
                if colIndex == self.colNum - 1:
                    cLIndex = cLIndex + 1
                    clearedLines[cLIndex] = rowIndex
                    rowIndex = rowIndex - 1

        if cLIndex >= 0:
            self.clock.clearAniStart = self.clock.frameTick
            self.lineClearStatus = 'clearRunning'
        else:
            self.prepareNextSpawn()

        return clearedLines

    def prepareNextSpawn(self):
        self.generateNextPiece()
        self.lineClearStatus = 'idle'
        self.piece.status = 'uncreated'

    def generateNextTwoPieces(self):
        self.nextPieces[0] = pieceNames[random.randint(0, 6)]
        self.nextPieces[1] = pieceNames[random.randint(0, 6)]
        self.piece.type = self.nextPieces[0]

    def generateNextPiece(self):
        self.nextPieces[0] = self.nextPieces[1]
        self.nextPieces[1] = pieceNames[random.randint(0, 6)]
        self.piece.type = self.nextPieces[0]

    def checkAndApplyGameOver(self):
        if self.piece.gameOverCondition == True:
            self.gameStatus = 'gameOver'
            for i in range(0, 4):
                if self.piece.blocks[i].currentPos.row >= 0 and self.piece.blocks[i].currentPos.col >= 0:
                    self.blockMat[self.piece.blocks[i].currentPos.row][self.piece.blocks[i].currentPos.col] = self.piece.type

    def updateScores(self):

        clearedLinesNum = 0
        for i in range(0, 4):
            if self.clearedLines[i] > -1:
                clearedLinesNum = clearedLinesNum + 1

        self.score = self.score + \
            (self.level+1) * \
            baseLinePoints[clearedLinesNum] + self.piece.dropScore
        if self.score > 999999:
            self.score = 999999
        self.lines = self.lines + clearedLinesNum
        self.level = STARTING_LEVEL + math.floor(self.lines/10)
        if self.level > 99:
            self.level = 99

    def updateSpeed(self):

        if self.level < 29:
            self.clock.fall.framePeriod = levelSpeeds[self.level]
        else:
            self.clock.fall.framePeriod = 1

        if self.clock.fall.framePeriod < 4:
            self.clock.fall.framePeriod = self.clock.move.framePeriod

    # All the game events and mechanics are placed in this function, called at each game loop iteration
    def gameAction(self):

        if self.gameStatus == 'firstStart':
            if self.key.enter.status == 'pressed':
                self.restart()

        elif self.gameStatus == 'running':

            if self.key.restart.trig == True:
                self.restart()
                self.key.restart.trig = False

            if self.gamePause == False:

                self.piece.move(self.blockMat)
                self.checkAndApplyGameOver()

                if self.key.pause.trig == True:
                    self.clock.pause()
                    self.gamePause = True
                    self.key.pause.trig = False

                if self.gameStatus != 'gameOver':
                    if self.piece.status == 'moving':
                        if self.key.rotate.trig == True:
                            self.piece.rotate('CW')
                            self.key.rotate.trig = False

                        if self.key.cRotate.trig == True:
                            self.piece.rotate('cCW')
                            self.key.cRotate.trig = False

                    elif self.piece.status == 'collided':
                        if self.lineClearStatus == 'idle':
                            for i in range(0, 4):
                                self.blockMat[self.piece.blocks[i].currentPos.row][self.piece.blocks[i].currentPos.col] = self.piece.type
                            self.clearedLines = self.getCompleteLines()
                            self.updateScores()
                            self.updateSpeed()
                        elif self.lineClearStatus == 'clearRunning':
                            self.lineClearAnimation()
                        else:  # 'clearFin'
                            self.dropFreeBlocks()
                            self.prepareNextSpawn()

            else:  # self.gamePause = False
                if self.key.pause.trig == True:
                    self.clock.unpause()
                    self.gamePause = False
                    self.key.pause.trig = False

        else:  # 'gameOver'
            if self.key.enter.status == 'pressed':
                self.restart()
