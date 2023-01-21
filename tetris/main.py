import pygame
from constants import (
    DISPLAY_HEIGHT,
    DISPLAY_WIDTH,
    BLACK
)
from board import MainBoard
from controller import GameKeyInput
from clock import GameClock
import sys


pygame.init()

gameDisplay = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.set_caption('Tetris')
clock = pygame.time.Clock()


def gameLoop(key: GameKeyInput, gameClock: GameClock, display):

    blockSize = 20
    boardColNum = 10
    boardRowNum = 20
    boardLineWidth = 10
    blockLineWidth = 1
    scoreBoardWidth = blockSize * (boardColNum//2)
    boardPosX = DISPLAY_WIDTH * 0.3
    boardPosY = DISPLAY_HEIGHT * 0.15

    mainBoard = MainBoard(
        blockSize,
        boardPosX,
        boardPosY,
        boardColNum,
        boardRowNum,
        boardLineWidth,
        blockLineWidth,
        scoreBoardWidth,
        **{
            "game": pygame,
            "clock": gameClock,
            "display": display,
            "key": key
        }
    )

    xChange = 0

    gameExit = False

    while not gameExit:  # Stay in this loop unless the game is quit

        for event in pygame.event.get():
            # Looks for quitting event in every iteration (Meaning closing the game window)
            if event.type == pygame.QUIT:
                gameExit = True

            if event.type == pygame.KEYDOWN:  # Keyboard keys press events
                if event.key == pygame.K_LEFT:
                    xChange += -1
                if event.key == pygame.K_RIGHT:
                    xChange += 1
                if event.key == pygame.K_DOWN:
                    key.down.status = 'pressed'
                if event.key == pygame.K_UP:
                    if key.rotate.status == 'idle':
                        key.rotate.trig = True
                        key.rotate.status = 'pressed'
                if event.key == pygame.K_LCTRL:
                    if key.cRotate.status == 'idle':
                        key.cRotate.trig = True
                        key.cRotate.status = 'pressed'
                if event.key == pygame.K_p:
                    if key.pause.status == 'idle':
                        key.pause.trig = True
                        key.pause.status = 'pressed'
                if event.key == pygame.K_r:
                    if key.restart.status == 'idle':
                        key.restart.trig = True
                        key.restart.status = 'pressed'
                if event.key == pygame.K_RETURN:
                    key.enter.status = 'pressed'

            if event.type == pygame.KEYUP:  # Keyboard keys release events
                if event.key == pygame.K_LEFT:
                    xChange += 1
                if event.key == pygame.K_RIGHT:
                    xChange += -1
                if event.key == pygame.K_DOWN:
                    key.down.status = 'released'
                if event.key == pygame.K_UP:
                    key.rotate.status = 'idle'
                if event.key == pygame.K_LCTRL:
                    key.cRotate.status = 'idle'
                if event.key == pygame.K_p:
                    key.pause.status = 'idle'
                if event.key == pygame.K_r:
                    key.restart.status = 'idle'
                if event.key == pygame.K_RETURN:
                    key.enter.status = 'idle'

            if xChange > 0:
                key.xNav.status = 'right'
            elif xChange < 0:
                key.xNav.status = 'left'
            else:
                key.xNav.status = 'idle'

        # Whole screen is painted black in every iteration before any other drawings occur
        gameDisplay.fill(BLACK)

        mainBoard.gameAction()  # Apply all the game actions here
        mainBoard.draw()  # Draw the new board after game the new game actions
        gameClock.update()  # Increment the frame tick

        pygame.display.update()  # Pygame display update
        clock.tick(60)  # Pygame clock tick function(60 fps)


# Main program
key = GameKeyInput()
gameClock = GameClock()
gameLoop(key, gameClock, gameDisplay)
pygame.quit()
sys.exit()
