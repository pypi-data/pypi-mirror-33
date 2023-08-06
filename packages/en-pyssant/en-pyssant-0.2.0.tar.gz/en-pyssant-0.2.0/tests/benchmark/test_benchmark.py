# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2018  Carmen Bianca Bakker <carmen@carmenbianca.eu>
#
# This file is part of En Pyssant, available from its original location:
# <https://gitlab.com/carmenbianca/en-pyssant>.
#
# En Pyssant is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# En Pyssant is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with En Pyssant.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0+

"""Benchmark suite for En Pyssant."""

# pylint: disable=invalid-name,redefined-outer-name

import os
import sys
from multiprocessing import Pool

import pytest

from en_pyssant import Move, Piece, Side, Type, rules
from en_pyssant._util import ALL_SQUARES
from en_pyssant.rules import attacked, moves

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '../../util')))

# A little construct that makes the linter and isort happy.
try:
    from single_game import play_game
except ImportError:
    raise

GAME_COUNT = 10
CPU_COUNT = os.cpu_count()
CORES = [1]
for n in range(2, GAME_COUNT + 1, 2):
    if n > CPU_COUNT + 2:
        break
    CORES.append(n)


@pytest.fixture(params=CORES)
def process_count(request):
    """Yield some amounts of cores to test for."""
    yield request.param


@pytest.mark.benchmark(group='board_read')
def test_read_all_board(benchmark, board):
    """Benchmark how long it takes to read all squares on the board."""
    squares = ALL_SQUARES

    def read_all(board):
        """Read all squares on the board."""
        return [board[square] for square in squares]

    benchmark(read_all, board)


@pytest.mark.benchmark(group='board_read_1000')
def test_read_board_thousand_times(benchmark, board):
    """Benchmark how long it takes to read all squares on the board a thousand
    times.

    This should probably hit caching of the Board.get function, if caching is
    used.
    """
    squares = ALL_SQUARES

    def read_all(board):
        """Read all squares on the board."""
        for _ in range(1000):
            for square in squares:
                board.get(square)

    benchmark(read_all, board)


@pytest.mark.benchmark(group='board_write')
def test_clear_board(benchmark, board):
    """Benchmark how long it takes to clear all squares on the board."""
    squares = ALL_SQUARES

    def clear(board):
        """Clear the board."""
        for square in squares:
            board = board.put(square, None)
        return board

    benchmark(clear, board)


@pytest.mark.benchmark(group='board_write')
def test_fill_board(benchmark, board):
    """Benchmark how long it takes to fill the board with pawns."""
    squares = ALL_SQUARES
    pawn = Piece(Type.PAWN, Side.WHITE)

    def fill(board):
        """Fill the board."""
        for square in squares:
            board = board.put(square, pawn)
        return board

    benchmark(fill, board)


@pytest.mark.benchmark(group='board_init')
def test_board_init(benchmark, Board):
    """Benchmark the performance of Board.__init__."""
    benchmark(Board)


@pytest.mark.benchmark(group='moves')
def test_moves(benchmark, position_multi_board):
    """Benchmark :func:`moves` on the default position."""
    def all_moves(position_multi_board):
        """Exhaust the generator."""
        return list(moves(position_multi_board))
    benchmark(all_moves, position_multi_board)


@pytest.mark.benchmark(group='attacked')
def test_attacked(benchmark, position_multi_board):
    """Benchmark :func:`attacked` on the default position."""
    benchmark(attacked, position_multi_board, Side.WHITE, 'd4')


@pytest.mark.benchmark(group='san')
def test_san(benchmark, san_position_multi_board):
    """Benchmark :meth:`Move.san`."""
    move = Move('c2', 'c7')
    move = move.expand(san_position_multi_board, rules)
    benchmark(Move.san, move, san_position_multi_board, rules)


@pytest.mark.benchmark(group='from_san')
def test_from_san(benchmark, san_position_multi_board):
    """Benchmark :meth:`Move.from_san`."""
    san = 'Rxc7+'
    benchmark(Move.from_san, san, san_position_multi_board, rules)


@pytest.mark.benchmark(group='play_game')
def test_play_game(benchmark, Board, process_count):
    """Benchmark how long it takes to run a complete game GAME_COUNT times,
    sharing the load between multiple processes.
    """
    warmup_rounds = 5 if sys.implementation.name == 'pypy' else 1
    rounds = 20

    def inner_single(board_cls, count, _):
        """Play the game *count* times."""
        for _ in range(count):
            play_game(board_cls)

    def inner(board_cls, count, pool):
        """Play the game *count* times, shared across *pool*."""
        results = [
            pool.apply_async(play_game, (board_cls,)) for _ in range(count)]
        for result in results:
            result.get()

    if process_count == 1:
        pool = None
        func = inner_single
    else:
        pool = Pool(processes=process_count)
        func = inner

    benchmark.pedantic(
        func, (Board, GAME_COUNT, pool), rounds=rounds,
        warmup_rounds=warmup_rounds)

    if pool is not None:
        pool.close()
