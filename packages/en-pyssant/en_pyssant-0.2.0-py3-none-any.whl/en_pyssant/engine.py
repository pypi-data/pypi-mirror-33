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

"""Various chess engines."""

import logging
import operator
import os
import pickle
import random
import sys
import time
from abc import ABCMeta, abstractmethod
from inspect import isabstract
from math import log, sqrt
from multiprocessing import Event, Lock, Pool, RLock
from typing import BinaryIO, List, Optional, Sequence

from pkg_resources import resource_stream

from . import rules
from ._core import HistoryRecord, Move, Side
from ._position import Position

LOGGER = logging.getLogger(__name__)

_CPUS = os.cpu_count()
_PROCESSES = _CPUS
_MAX_DEPTH = 10
_SIMULATIONS_PER_ROUND = _PROCESSES * 2


class Engine(metaclass=ABCMeta):
    """Abstract base class for engine implementations.

    :ivar _stop: An event that is set when thinking should stop.
    :vartype _stop: :class:`Event`
    :ivar _stopped: An event that is set when the engine is not thinking.
    :vartype _stopped: :class:`Event`
    :ivar _state_lock: A lock for the internal state.
    :vartype _state_lock: :class:`RLock`
    :ivar _no_one_wants_state: An event that is set when nobody else wants
        access to the internal state.  The thinking function interrupts
        thinking until this is set.
    :vartype _no_one_wants_state: :class:`Event`
    :ivar _thinking_lock: A lock that prevents multiple threads from thinking.
    :vartype _thinking_lock: :class:`Lock`
    """
    # pylint: disable=too-many-instance-attributes

    @abstractmethod
    def __init__(
            self,
            position: Position = None,
            history: Sequence[HistoryRecord] = None,
            ruleset=None,
            **kwargs):
        """:param position: Chess position.
        :param history: History of plays.
        :param ruleset: Game ruleset.
        """
        if position is None:
            position = Position()
        if history is None:
            history = tuple()
        if ruleset is None:
            ruleset = rules

        self._position = position
        self._history = tuple(history)
        self._ruleset = ruleset

        self._stop = Event()
        self._stopped = Event()
        self._stopped.set()

        self._state_lock = RLock()
        self._no_one_wants_state = Event()
        self._no_one_wants_state.set()

        self._thinking_lock = Lock()

    @abstractmethod
    def think_for(self, seconds: float) -> bool:
        """Perform analysis of the board for an estimated maximum of *seconds*.
        It is perfectly permissible that this function blocks for a lower
        amount of time, or goes slightly over.

        If *seconds* is 0, block forever until :meth:`stop_thinking` is called.

        This method always returns :const:`True` after it has finished
        thinking, whether prematurely stopped or not.  However, if it is called
        while it is already thinking, then it will return :const:`False`.

        :param seconds: Amount of seconds to process.
        :result: Whether the function was successfully able to start.
        """

    def stop_thinking(self, blocking: bool = True) -> None:
        """Stop the loop in :meth:`think_for`.

        :param blocking: Wait until the loop is well and truly stopped.
        """
        self._stop.set()
        if blocking:
            self._stopped.wait()

    def is_thinking(self) -> bool:
        """:return: Whether the engine is currently thinking."""
        return not self._stopped.is_set()

    @abstractmethod
    def best_move(self) -> Move:
        """Return the move that the engine thinks is best.  This probably
        requires some processing in advance with :meth:`think_for`.  Thinking
        will not be stopped by calling this method.

        :return: The best move.
        """

    def do_move(
            self,
            move: Move,
            force: bool = False,
            want_state: bool = False) -> Position:
        """Change the engine's internal state after performing *move*.

        This function does not cause the engine to stop thinking.

        *want_state* is ignored if an exception is raised.

        Return the resulting position.

        :param move: Move to perform on position.
        :param force: Whether to perform the move without any verification.
        :param want_state: A flag to keep :attr:`_no_one_wants_state` cleared
            and :attr:`_state_lock` locked.  This is primarily useful for
            extending this method.
        :result: The resulting position.
        :raise ValueError: *move* is invalid.
        """
        self._no_one_wants_state.clear()
        try:
            self._state_lock.acquire()
            position, record = self._ruleset.do_move_with_history(
                self._position, move, force=force)
            self._position = position
            self._history += (record,)
            return self._position
        finally:
            if not want_state or any(sys.exc_info()):
                self._state_lock.release()
                self._no_one_wants_state.set()

    @property
    def position(self) -> Position:
        """Current position."""
        return self._position

    @property
    def history(self) -> Sequence[HistoryRecord]:
        """Current history."""
        return self._history

    @property
    def ruleset(self):
        """The ruleset.  This is not editable."""
        return self._ruleset

    def _start_thinking(self) -> bool:
        """Only allow one thread to think at a time."""
        with self._thinking_lock:
            if self.is_thinking():
                return False
            self._stopped.clear()
        return True


class ParallelEngine(Engine, metaclass=ABCMeta):
    """Abstract base class for engines that do parallel execution with the
    :mod:`multiprocessing` module.

    :ivar _pool: A pool of processes.
    :vartype _pool: :class:`Pool` or :const:`None`
    :ivar _pool_lock: A lock for access to the pool.
    :vartype _pool_lock: :class:`Lock`
    """

    @abstractmethod
    def __init__(
            self,
            position: Position = None,
            history: Sequence[HistoryRecord] = None,
            ruleset=None,
            processes: int = None,
            **kwargs):
        """:param position: Chess position.
        :param history: History of plays.
        :param ruleset: Game ruleset.
        :param processes: Amount of processes to spawn.  Defaults to the amount
            of cores.  If equal to 0, do not spawn any processes.
        """
        super().__init__(position, history, ruleset)

        self._pool_lock = Lock()
        self._pool = None
        if processes is None:
            processes = _PROCESSES
        self.__processes = processes
        self._replace_pool(self.__processes)

    @property
    def processes(self) -> int:
        """The amount of processes spawned by this engine.  This can be changed
        on-the-fly.
        """
        return self.__processes

    @processes.setter
    def processes(self, value: int):
        self._replace_pool(value)

    def _replace_pool(self, processes):
        with self._pool_lock:
            if self._pool:
                self._pool.close()
                self._pool.join()
            if processes == 0:
                self._pool = None
            else:
                self._pool = Pool(processes=processes)
            self.__processes = processes

    def __del__(self):
        if self._pool:
            self._pool.terminate()
            self._pool.join()


def _all_engine_classes() -> List[Engine]:
    """Return a list of all defined engine classes, excluding the base classes.
    """
    result = []
    for key, value in globals().items():
        if key.endswith('Engine') and not isabstract(value):
            result.append(value)
    return sorted(result, key=operator.attrgetter('__name__'))


def _random_move(position: Position, ruleset, rng=random) -> Optional[Move]:
    """Get a random move from *position*."""
    moves = list(ruleset.moves(position))
    if moves:
        return rng.choice(moves)
    return None


class _Node:
    """A node in the Monte Carlo tree."""

    # pylint: disable=too-many-instance-attributes,too-many-arguments
    # pylint: disable=too-few-public-methods
    def __init__(
            self,
            move: Move,
            position: Position,
            history: Sequence[HistoryRecord],
            ruleset,
            parent: '_Node' = None):
        self.move = move
        self.position = position
        self.history = history
        self.parent = parent

        self.children = []
        self.untried_moves = []
        self.untried_moves = list(ruleset.moves(self.position))

        self.visits = 0
        self.wins = 0


def _ucb1(node: _Node):
    """Select a node to explore from a node's children."""
    return sorted(
        node.children,
        key=lambda c: (
            c.wins / c.visits + sqrt(2 * log(node.visits) / c.visits)))[-1]


def _play_complete_game(
        position: Position,
        history: Sequence[HistoryRecord]) -> Optional[Side]:
    """Play a complete game and return the winner.

    The function name is a moderate lie.  It only plays _MAX_DEPTH moves.
    """
    # TODO: Pass ruleset as argument.
    start_length = len(history)
    while (
            not rules.is_fifty_move(position)
            and not rules.is_threefold_repetition(history)
            and not rules.is_insufficient_material(position)):
        if len(history) > start_length + _MAX_DEPTH:
            return None
        moves = list(rules.moves(position))
        if not moves:
            break
        move = random.choice(moves)
        history = history + (HistoryRecord(position, move),)
        position = rules.do_move(position, move, force=True)
    return rules.winner(position)


class MCTSEngine(ParallelEngine):
    """An Engine implementation that uses Monte Carlo Tree Search."""

    def __init__(
            self,
            position: Position = None,
            history: Sequence[HistoryRecord] = None,
            ruleset=None,
            processes: int = None,
            **kwargs):
        super().__init__(position, history, ruleset, processes)

        load_precomputed = kwargs.get('load_precomputed', False)

        self._root = None
        if (
                load_precomputed
                and self._position == Position()
                and not self._history
                and self._ruleset is rules):
            try:
                self.load_precomputed()
            except FileNotFoundError:
                LOGGER.debug('no mcts.pickle found, continuing without')
        if not self._root:
            self._root = _Node(
                None, self._position, self._history, self._ruleset)

    def think_for(self, seconds: float) -> bool:
        if not self._start_thinking():
            return False

        start = time.perf_counter()
        end = start + seconds
        infinity = seconds == 0

        try:
            while (
                    (infinity or time.perf_counter() < end)
                    and not self._stop.is_set()):
                self._mcts_round()
        finally:
            self._stop.clear()
            self._stopped.set()
        return True

    def best_move(self) -> Move:
        self._no_one_wants_state.clear()
        try:
            with self._state_lock:
                if not self._root.children:
                    best_move = _random_move(self._position, self._ruleset)
                else:
                    best_node = sorted(
                        self._root.children,
                        key=operator.attrgetter('wins'))[-1]
                    best_move = best_node.move
        finally:
            self._no_one_wants_state.set()
        return best_move

    def do_move(
            self,
            move: Move,
            force: bool = False,
            want_state: bool = False) -> Position:
        result = super().do_move(move, force=force, want_state=True)
        try:
            # self._state_lock is already acquired, so no need to acquire it
            # here.
            nodes = list(filter(
                lambda c: c.position == self._position,
                self._root.children))
            if nodes:
                node = nodes[0]
                node.parent = None
            else:
                performed_move = self._history[-1].move
                node = _Node(
                    performed_move, result, self._history, self._ruleset)
            self._root = node
        finally:
            if not want_state or any(sys.exc_info()):
                self._state_lock.release()
                self._no_one_wants_state.set()
        return result

    def load_precomputed(self, source: BinaryIO = None) -> None:
        """Load a precomputed state from *source*.  If *source* is None, load
        from pickle included with the distribution.

        :param source: A binary stream of a pickled :class:`_Node`.
        :raise FileNotFoundError: There was no included pickle.
        """
        if source is None:
            source = resource_stream(__name__, 'mcts.pickle')
        try:
            with self._state_lock:
                start = time.perf_counter()
                self._root = pickle.load(source)
                LOGGER.debug(
                    'loaded pickled node in %f seconds',
                    time.perf_counter() - start)
                self._position = self._root.position
                self._history = self._root.history
        finally:
            source.close()

    def _select(self, formula=None) -> _Node:
        """Start from the root and select nodes using *formula*.  If we reach a
        node that does not have all children, or if it is a terminal node,
        return that node.
        """
        if formula is None:
            formula = _ucb1
        with self._state_lock:
            selected = self._root

            while (
                    not selected.untried_moves
                    and selected.children):
                selected = formula(selected)
            return selected

    def _expand(self, node: _Node) -> _Node:
        """Given *node*, randomly choose one of the possible moves that has not
        already been made into a child of *node*.

        If *node* has already expanded all nodes, return it.
        """
        with self._state_lock:
            if node.untried_moves:
                move = random.choice(node.untried_moves)
                node.untried_moves.remove(move)
                record = HistoryRecord(node.position, move)
                position = self._ruleset.do_move(
                    node.position, move, force=True)
                result = _Node(
                    move, position, node.history + (record,),
                    self._ruleset, node)
                node.children.append(result)
                return result
            return node

    def _simulate(self, node: _Node) -> List[Side]:
        """Do some random games to completion on *node*.  Then return the
        winners.
        """
        with self._state_lock:
            with self._pool_lock:
                if self._pool:
                    winners = self._pool.starmap(
                        _play_complete_game,
                        [
                            (node.position, node.history)
                        ] * _SIMULATIONS_PER_ROUND,
                        _SIMULATIONS_PER_ROUND // self.processes)
                else:
                    winners = [
                        _play_complete_game(node.position, node.history)
                        for _ in range(_SIMULATIONS_PER_ROUND)]
        return winners

    # pylint: disable=no-self-use
    def _backpropogate(self, node: _Node, winner: Side) -> None:
        """Propogate the results up the tree.  All wins are counted for the
        player who has just moved.
        """
        with self._state_lock:
            while node is not None:
                node.visits += 1
                if winner is None:
                    node.wins += 0.5
                elif winner is not node.position.side_to_play:
                    node.wins += 1

                node = node.parent

    def _mcts_round(self) -> None:
        """Do an entire round of MCTS."""
        self._no_one_wants_state.wait()
        with self._state_lock:
            node = self._select()
            node = self._expand(node)
            # LOGGER.debug(
            #     ' '.join(
            #         '{}{}'.format(
            #             record.move.origin,
            #             record.move.destination)
            #     for record in node.history))
            # LOGGER.debug(self._root.visits)
            # LOGGER.debug(self._root.wins)
            winners = self._simulate(node)
            for winner in winners:
                self._backpropogate(node, winner)


class RandomEngine(Engine):
    """An Engine implementation that returns random moves.  The purpose of this
    engine is solely to prototype.
    """

    def __init__(
            self,
            position: Position = None,
            history: Sequence[HistoryRecord] = None,
            ruleset=None,
            **kwargs):
        super().__init__(position, history, ruleset)
        self._random = random.SystemRandom()

    def think_for(self, seconds: float) -> bool:
        if not self._start_thinking():
            return False

        try:
            if seconds == 0:
                self._stop.wait()
            else:
                time.sleep(seconds)
        finally:
            self._stopped.set()
            self._stop.clear()
        return True

    def best_move(self) -> Move:
        return _random_move(self._position, self._ruleset, rng=self._random)
