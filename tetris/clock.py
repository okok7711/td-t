from constants import (
    MOVE_PERIOD_INIT,
    levelSpeeds,
    STARTING_LEVEL
)


class GameClock:
    def __init__(self):
        # The main clock tick of the game, increments at each frame (1/60 secs, 60 fps)
        self.frameTick = 0
        self.pausedMoment = 0
        # Drop and move(right and left) timing object
        self.move = self.TimingType(MOVE_PERIOD_INIT)
        # Free fall timing object
        self.fall = self.TimingType(levelSpeeds[STARTING_LEVEL])
        self.clearAniStart = 0

    class TimingType:
        def __init__(self, framePeriod):
            self.preFrame = 0
            self.framePeriod = framePeriod

        def check(self, frameTick):
            if frameTick - self.preFrame > self.framePeriod - 1:
                self.preFrame = frameTick
                return True
            return False

    def pause(self):
        self.pausedMoment = self.frameTick

    def unpause(self):
        self.frameTick = self.pausedMoment

    def restart(self):
        self.frameTick = 0
        self.pausedMoment = 0
        self.move = self.TimingType(MOVE_PERIOD_INIT)
        self.fall = self.TimingType(levelSpeeds[STARTING_LEVEL])
        self.clearAniStart = 0

    def update(self):
        self.frameTick = self.frameTick + 1
