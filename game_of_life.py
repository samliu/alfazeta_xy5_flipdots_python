"""game_of_life.py

https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life
"""
from xy5_controller import XY5Driver

import time
import numpy as np
import scipy

class GameOfLife(object):
    REFRESH_INTERVAL = 0.5  # Seconds.
    STARTING_DENSITY = 0.3

    def __init__(self, starting_grid=None):
        self.__reset_state(starting_grid)

        self.kernel = np.ones((3,3), dtype=np.int8)
        self.kernel[1][1] = 0

        self.driver = XY5Driver()

    def __reset_state(self, starting_grid=None):
        if starting_grid is None:
            # Random 10% of cells flipped on.
            starting_grid = np.random.rand(14, 28) < self.STARTING_DENSITY
            starting_grid = starting_grid.astype(np.int8)
        assert(starting_grid.shape == (14,28))
        assert(starting_grid.dtype == np.int8)
        self.state = starting_grid

    def update_state(self):
        conv_state = scipy.signal.convolve2d(
            self.state, self.kernel, mode="same", boundary="wrap"
        )
        temp_state = np.zeros((14,28), dtype=np.int8)

        # If # neighbors aren't in [2,3] then the cell is dead.
        temp_state[(conv_state < 2) | (conv_state > 3)] = 0

        # If # neighbors are in [2, 3] AND the cell is already alive, then it
        # stays alive.
        temp_state[
            ((conv_state == 2) | (conv_state == 3)) & (self.state == 1)
        ] = 1

        # If you're a dead cell but you have 3 neighbors, you become alive. In
        # the last update step, we already kept live cells with 3 neighbors
        # alive, so this update is really only about the dead cells.
        temp_state[conv_state == 3] = 1
        self.state = temp_state

        # Draw to the XY5.
        time.sleep(self.REFRESH_INTERVAL)
        self.driver.paint_14x28(self.state)

    def loop(self, max_steps):
        while True:
            for i in range(0, max_steps):
                self.update_state()
            self.__reset_state()


if __name__ == "__main__":
    game_of_life = GameOfLife()
    game_of_life.loop(max_steps=100)

