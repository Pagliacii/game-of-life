#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2021 Pagliacii
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Author:             Pagliacii
# Last Modified By:   Pagliacii
# Created Date:       2021-08-01 17:51:14
# Last Modified Date: 2021-08-01 23:51:05

import sys
import time

from collections import Counter
from pathlib import Path


class Game:
    def __init__(self, row: int = 64, column: int = 64, fps: int = 30) -> None:
        self._row: int = row
        self._column: int = column
        self._delta: int = 10 ** 9 // fps
        # The empty frame
        self._frame = self._empty_frame()

    def _empty_frame(self) -> list[list[bool]]:
        return [[False for _ in range(self._column)] for _ in range(self._row)]

    def _draw(self) -> None:
        """Draws the current game board, '*' for alive, ' ' for dead"""
        self._erase()
        for row in self._frame:
            for cell in row:
                sys.stdout.write("*" if cell else " ")
            sys.stdout.write("\n")
            sys.stdout.flush()

    def _erase(self) -> None:
        """Erases the existed board"""
        for _ in range(self._row):
            self._erase_one_row()
            # Go to the end of previous row
            sys.stdout.write("\033[A")
            sys.stdout.flush()
        sys.stdout.write("\r")
        sys.stdout.flush()

    def _erase_one_row(self) -> None:
        """Erases one row on the board"""
        sys.stdout.write("\033[2K")
        sys.stdout.flush()

    def set_first_frame(self, frame: str) -> None:
        """Setups the first frame based on the random number"""
        for i, row in enumerate(frame.splitlines()):
            for j, column in enumerate(row):
                self._frame[i][j] = int(column) == 1

    def _gen_next_frame(self) -> None:
        """Generates the next frame based on the rules"""
        # Every cell interacts with its eight neighbours
        neighbours = [
            (-1, -1),  # Top-left corner
            (-1, 0),  # Top
            (-1, 1),  # Top-right corner
            (0, -1),  # Left
            # (0, 0)
            (0, 1),  # Right
            (1, -1),  # Bottom-left corner
            (1, 0),  # Bottom
            (1, 1),  # Bottom-right corner
        ]
        next_frame = self._empty_frame()
        for row in range(self._row):
            for column in range(self._column):
                alive = self._frame[row][column]
                # Detects all neighbours status
                neighbours_status = Counter(
                    [
                        self._frame[(row + r) % self._row][(column + c) % self._column]
                        for (r, c) in neighbours
                    ]
                )
                lives = neighbours_status[True]
                if alive:
                    # The current cell is alive.
                    if lives < 2:
                        # 1. Any live cell with fewer than two live neighbours dies,
                        #    as if by underpopulation.
                        next_frame[row][column] = False
                    elif lives == 2 or lives == 3:
                        # 2. Any live cell with two or three live neighbours lives
                        #    on to the next generation
                        next_frame[row][column] = True
                    else:
                        # 3. Any live cell with more than three live neighbours dies,
                        #    as if by overpopulation.
                        next_frame[row][column] = False
                else:
                    # The current cell is dead.
                    if lives == 3:
                        # 4. Any dead cell with exactly three live neighbours becomes
                        #    a live cell, as if by reproduction.
                        next_frame[row][column] = True
        self._frame = next_frame

    def run(self) -> None:
        """Starts the game"""
        tic: int = 0
        while True:
            try:
                toc = time.perf_counter_ns()
                if tic == 0:
                    # When the game first starts
                    tic = time.perf_counter_ns()
                elif toc - tic < self._delta:
                    # It isn't time to refresh
                    continue
                # Draws the current board
                self._draw()
                # Prepares next board
                self._gen_next_frame()
                tic = time.perf_counter_ns()
            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "\N{Cross Mark} \033[31mExpected a file to specify the first frame.\033[0m"
        )
        print(f"Usage: {sys.argv[0]} <filename> [fps=6]")
        sys.exit(1)
    if len(sys.argv) == 2:
        init_frame = Path(sys.argv[-1]).read_text()
        fps = 6
    else:
        init_frame = Path(sys.argv[1]).read_text()
        fps = int(sys.argv[2])

    row = len(init_frame.splitlines())
    column = len(init_frame.splitlines()[0])
    game = Game(row=row, column=column, fps=fps)
    game.set_first_frame(init_frame)
    game.run()
