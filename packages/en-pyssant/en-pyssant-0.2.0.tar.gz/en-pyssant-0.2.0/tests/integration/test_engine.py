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

"""Integrated tests for the chess engine implementations."""

# pylint: disable=no-self-use,invalid-name,redefined-outer-name,not-callable

import gc
import os
import sys
import time
from queue import Queue
from threading import Thread

import pytest

from en_pyssant import Game, Move, Position, rules
from en_pyssant.engine import MCTSEngine
from en_pyssant.engine import ParallelEngine as ParEngine
from en_pyssant.engine import RandomEngine, _all_engine_classes

_CI = bool(os.environ.get('CI'))
_PYPY = sys.implementation.name == 'pypy'

_TINY_SLEEP = 0.1

_NO_RANDOM = _all_engine_classes()
_NO_RANDOM.remove(RandomEngine)
_PARALLEL = []
for engine_ in _all_engine_classes():
    if issubclass(engine_, ParEngine):
        _PARALLEL.append(engine_)


@pytest.fixture(params=_all_engine_classes())
def Engine(request):
    """Yield the available Engine classes."""
    yield request.param
    gc.collect()


@pytest.fixture(params=_NO_RANDOM)
def EngineNoRandom(request):
    """Yield the available Engine classes, without RandomEngine."""
    yield request.param
    gc.collect()


@pytest.fixture(params=_PARALLEL)
def ParallelEngine(request):
    """Yield the available ParallelEngine classes."""
    yield request.param
    gc.collect()


@pytest.fixture
def engine(Engine):
    """Return a default engine."""
    return Engine()


@pytest.mark.xfail(
    _CI or _PYPY,
    reason='performance is not predictable in CI, and really slow in PyPy')
def test_think_for_less_than(engine):
    """:meth:`Engine.think_for` takes less than the passed amount of seconds.
    """
    # pylint: disable=unused-argument
    seconds = 0.5
    start = time.perf_counter()
    engine.think_for(seconds)
    end = time.perf_counter()
    assert end - start < seconds + 0.2


def test_think_for_twice(engine):
    """If :meth:`Engine.think_for` is called for a second time, it returns
    :const:`False`.
    """
    thread_one = Thread(target=engine.think_for, args=(0,))
    thread_one.start()
    queue = Queue()
    thread_two = Thread(target=lambda: queue.put(engine.think_for(0)))
    thread_two.start()
    thread_two.join()
    assert not queue.get()
    engine.stop_thinking()
    thread_one.join()


def test_think_for_once(engine):
    """If :meth:`Engine.think_for` is called once, it returns :const:`True`."""
    assert engine.think_for(0.1)


def test_stop_thinking(engine):
    """:meth:`Engine.stop_thinking` stops an infinite thinking loop."""
    thread = Thread(target=engine.think_for, args=(0,))
    thread.start()
    engine.stop_thinking()
    thread.join()


@pytest.mark.xfail(_CI, reason='performance is not predictable in CI')
def test_stop_thinking_not_blocking(engine):
    """When timing is stopped without blocking, almost no time should pass."""
    thread = Thread(target=engine.think_for, args=(0,))
    thread.start()
    start = time.perf_counter()
    engine.stop_thinking(blocking=False)
    assert time.perf_counter() - start < 0.01
    thread.join()


def test_stop_thinking_never_thought(engine):
    """:meth:`Engine.stop_thinking` can be called without ever having thought.
    """
    engine.stop_thinking()


def test_is_thinking(engine):
    """After starting the engine's thinking, check whether
    :meth:`Engine.is_thinking` returns the correct value.
    """
    thread = Thread(target=engine.think_for, args=(0,))
    thread.start()
    time.sleep(_TINY_SLEEP)
    assert engine.is_thinking()
    engine.stop_thinking()
    thread.join()


def test_change_processes_during_thinking(ParallelEngine):
    """Able to change the amount of processes used by a ParallelEngine during
    thinking execution.
    """
    engine = ParallelEngine(processes=2)
    thread = Thread(target=engine.think_for, args=(0,))
    thread.start()
    time.sleep(_TINY_SLEEP)
    assert engine.processes == 2
    engine.processes = 1
    assert engine.processes == 1
    engine.stop_thinking()
    thread.join()


def test_can_think_zero_processes(ParallelEngine):
    """A ParallelEngine is also able to think with zero processes."""
    engine = ParallelEngine(processes=0)
    engine.think_for(_TINY_SLEEP)
    assert engine.processes == 0


@pytest.mark.xfail(
    _CI or _PYPY,
    reason='performance is not predictable in CI, and really slow in PyPy')
def test_fools_mate(EngineNoRandom):
    """One move from Fool's Mate, return the correct finishing move."""
    game = Game()
    game.do_move('f3')
    game.do_move('e5')
    game.do_move('g4')
    engine = EngineNoRandom(game.position, game.history, game.ruleset)
    engine.think_for(5)
    best_move = engine.best_move()
    assert best_move.san(game.position, game.ruleset) == 'Qh4#'
    # Expect no exception.
    game.do_move(best_move)


def test_best_move_without_thinking(engine):
    """Always return a best move, even if the engine hasn't thought yet."""
    move = engine.best_move()
    assert isinstance(move, Move)
    # Expect no exception.
    rules.do_move(Position(), move)


def test_best_move_stale_position(Engine):
    """Return None as best move if there is no possible move."""
    game = Game()
    game.do_move('f3')
    game.do_move('e5')
    game.do_move('g4')
    game.do_move('Qh4')
    engine = Engine(game.position, game.history, game.ruleset)
    engine.think_for(_TINY_SLEEP)
    best_move = engine.best_move()
    assert best_move is None


def test_do_move(engine):
    """Can perform move on engine without errors."""
    engine.think_for(_TINY_SLEEP)
    position = engine.do_move('a3')
    assert position == engine.position
    new_position, new_record = rules.do_move_with_history(Position(), 'a3')
    assert engine.position == new_position
    assert engine.history[-1] == new_record
    engine.think_for(_TINY_SLEEP)


def test_do_move_illegal(engine):
    """:meth:`Engine.do_move` raises a ValueError when move is illegal, but
    thinking is not interrupted.
    """
    thread = Thread(target=engine.think_for, args=(0,))
    thread.start()
    time.sleep(_TINY_SLEEP)
    with pytest.raises(ValueError):
        engine.do_move('a6')
    assert engine.is_thinking()
    engine.stop_thinking()
    thread.join()


def test_do_move_does_not_interrupt_thinking(ParallelEngine):
    """Keep thinking after performing move."""
    engine = ParallelEngine()
    thread = Thread(target=engine.think_for, args=(0,))
    thread.start()
    time.sleep(_TINY_SLEEP)
    engine.do_move('a3')
    time.sleep(_TINY_SLEEP)
    engine.do_move('a6')
    time.sleep(_TINY_SLEEP)
    engine.stop_thinking()
    thread.join()


def test_load_precomputed():
    """The root node has been visited and has children if a precomputed state
    is loaded.
    """
    engine = MCTSEngine()
    engine.load_precomputed()
    # pylint: disable=protected-access
    assert engine._root.visits > 0
    assert engine._root.children


def test_load_precomputed_during_init():
    """load_precomputed can be passed as parameter to __init__."""
    engine = MCTSEngine(load_precomputed=True)
    # pylint: disable=protected-access
    assert engine._root.visits > 0
    assert engine._root.children
