# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2018  Carmen Bianca Bakker <carmen@carmenbianca.eu>
# Copyright (C) 2017  Stefan Bakker <s.bakker777@gmail.com>
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

"""Core functionality of En Pyssant.

Safe to assume that all submodules depend on this module.
"""

import re
from collections import namedtuple
from enum import Enum
from functools import lru_cache
from typing import FrozenSet, Sequence, Tuple, Union

SAN_END_PATTERN = re.compile(
    r'[+#]?[?!]*$')
SAN_PATTERN = re.compile(
    r'([PNBRQK])?([a-h])?([1-8])?x?-?([a-h][1-8])([QRBN])?', re.IGNORECASE)

EMPTY_FROZENSET = frozenset()


def stripped_san(san: str) -> str:
    """Remove superfluous symbols from *san*."""
    return re.sub(SAN_END_PATTERN, '', san)


class Type(Enum):
    """Type of piece."""
    KING = 'k'
    QUEEN = 'q'
    ROOK = 'r'
    BISHOP = 'b'
    KNIGHT = 'n'
    PAWN = 'p'


class Side(Enum):
    """Colours corresponding to sides."""
    WHITE = 1
    BLACK = 0


class Piece(namedtuple('Piece', ['type', 'side'])):
    """A chess piece.  This object is immutable.

    >>> white_rook = Piece(Type.ROOK, Side.WHITE)
    >>> white_rook.side = Side.BLACK
    Traceback (most recent call last):
        ...
    AttributeError: can't set attribute
    """
    __slots__ = ()

    # Cache this.  The object is immutable and there are only 2 * 6 possible
    # permutations of this object.  Powers of 2 are more efficient for
    # lru_cache so use 2**4.
    @lru_cache(maxsize=16)
    def __new__(cls, type: Type, side: Side):
        """:param type: Type of piece.
        :param side: Side to which the piece belongs.
        """
        return super().__new__(cls, type, side)

    @classmethod
    def from_str(cls, char: str) -> 'Piece':
        """Create a piece from *char*.  *char* must be a single letter as found
        in :class:`Type`.  Lower case means that the piece is black, and upper
        case means that the piece is white.

        :param char: String representation of piece.
        :return: A piece.
        """
        return cls(
            Type(char.lower()),
            Side.WHITE if char.isupper() else Side.BLACK)

    def __str__(self):
        if self.side is Side.WHITE:
            return self.type.value.upper()
        return self.type.value.lower()


class Direction(Enum):
    """General four directions."""
    # (file, rank)
    UP = (0, 1)  # pylint: disable=invalid-name
    DOWN = (0, -1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class Square(str):
    """A wrapper class around :class:`str` that handles only chess squares.

    >>> Square('a1')
    'a1'
    >>> Square('')
    Traceback (most recent call last):
        ...
    ValueError: '' is not a valid square
    >>> Square('a9')
    Traceback (most recent call last):
        ...
    ValueError: 'a9' is not a valid square
    """

    @lru_cache(maxsize=64)
    def __new__(cls, string: str):
        error = False
        if len(string) != 2:
            error = True
        elif not 'a' <= string[0] <= 'h' or not '1' <= string[1] <= '8':
            error = True
        if error:
            raise ValueError('{} is not a valid square'.format(repr(string)))
        square = super().__new__(cls, string)
        return square

    @property
    def rank(self) -> int:
        """The rank (or row) of the square."""
        return int(self[1])

    @property
    def file(self) -> str:
        """The file (or column) of the square."""
        return self[0]

    @property
    def colour(self) -> Side:
        """Colour of the square."""
        return Side.WHITE if (ord(self.file) + self.rank) % 2 else Side.BLACK

    def goto(self, direction: Union[Direction, Tuple[int, int]]) -> 'Square':
        """:param direction: Direction to go to.
        :return: One square in the given direction.
        :raise IndexError: Destination out of bounds.
        """
        return self.traverse((direction,))

    def up(self) -> 'Square':  # pylint: disable=invalid-name
        """:return: One square up.
        :raise IndexError: Cannot go up.
        """
        return self.goto(Direction.UP.value)

    def down(self) -> 'Square':
        """:return: One square down.
        :raise IndexError: Cannot go down.
        """
        return self.goto(Direction.DOWN.value)

    def left(self) -> 'Square':
        """:return: One square to the left.
        :raise IndexError: Cannot go left.
        """
        return self.goto(Direction.LEFT.value)

    def right(self) -> 'Square':
        """:return: One square to the right.
        :raise IndexError: Cannot go right.
        """
        return self.goto(Direction.RIGHT.value)

    def traverse(
            self,
            path: Sequence[Union[Direction, Tuple[int, int]]]) -> 'Square':
        """:param path: Sequence of directions to follow.  Must be hashable.
        :return: The square at the end of the path.
        :raise IndexError: Path goes out of bounds.
        """
        destination = self.in_bounds(path)
        if destination:
            return destination
        raise IndexError('Cannot traverse {!r} from {!r}'.format(path, self))

    def in_bounds(
            self,
            path: Sequence[Union[Direction, Tuple[int, int]]]) -> Union[
                'Square', bool]:
        """Traverse with *path*.  Return the destination if it is inside the
        bounds of a chess board.  Else, return :const:`False`.

        .. NOTE::
            A sequence of (int, int) tuples is more performant than a sequence
            of :class:`Direction` objects.  To get such a tuple, just do
            ``direction.value``.

        :param path: Path to traverse to destination.  Must be hashable.
        :return: Destination square or :const:`False`
        """
        return _in_bounds(self, path)


@lru_cache(maxsize=2**32)
def _in_bounds(
        square: Square,
        path: Sequence[Union[Direction, Tuple[int, int]]]) -> Union[
            Square, bool]:
    balance = (0, 0)  # Total offset from origin.
    for direction in path:
        offset = getattr(direction, 'value', direction)
        balance = tuple(map(sum, zip(balance, offset)))
    file_ = chr(ord(square.file) + balance[0])
    rank = square.rank + balance[1]
    if 'a' <= file_ <= 'h' and rank in range(1, 9):
        return square.__class__('{}{}'.format(file_, rank))
    return False


class MoveFlag(Enum):
    """Flags associated with a move."""
    NON_CAPTURE = 0
    STANDARD_CAPTURE = 1
    EN_PASSANT_CAPTURE = 2
    PAWN_PUSH = 3
    QUEENSIDE_CASTLING = 4
    KINGSIDE_CASTLING = 5
    PROMOTION = 6


class Move(namedtuple(
        'Move',
        ['origin', 'destination', 'piece', 'captured', 'promotion', 'flags'])):
    """A move on the chess board.

    Under normal circumstances, you only need to provide *origin*,
    *destination* and possibly *promotion* when using a Move object to
    interface with the rest of the API.  The rest is metadata, as it were.
    """
    __slots__ = ()

    # pylint: disable=too-many-arguments
    def __new__(
            cls,
            origin: Square,
            destination: Square,
            piece: Piece = None,
            captured: Piece = None,
            promotion: Type = None,
            flags: FrozenSet[MoveFlag] = None):
        """:param origin: Square from which the piece has moved.
        :param destination: Square to which the piece has moved.
        :param piece: The piece that has moved.
        :param captured: If a capture move: Piece that has been captured.
        :param promotion: The piece type that the pawn has been promoted to.
        :param flags: Flags associated with move.
        """
        origin = Square(origin)
        destination = Square(destination)
        if flags is None:
            flags = EMPTY_FROZENSET
        else:
            # TODO: Verify whether there is a performance penalty here.
            flags = frozenset(flags)
        return super().__new__(
            cls, origin, destination, piece, captured, promotion, flags)

    def expand(self, position, ruleset) -> 'Move':
        """Given a move that contains only *origin* and *destination*, return a
        new, fully descriptive move that contains all fields.

        Promotion moves that do not already specify which piece to promoto to
        will default to queen promotions.

        :param position: Chess position before the move is performed.
        :type position: :class:`Position`
        :param ruleset: Game ruleset.
        :return: A fully expanded move.
        :raise ValueError: Move is invalid.
        """
        promotion = self.promotion
        if not promotion:
            promotion = Type.QUEEN

        for move in ruleset.moves(position):
            if (self.origin == move.origin
                    and self.destination == move.destination):
                # If we're dealing with a promotion, only return the promotion
                # that matches the promotion target.
                if MoveFlag.PROMOTION in move.flags:
                    if promotion is move.promotion:
                        return move
                else:
                    return move
        raise ValueError('{} is not a valid move'.format(repr(self)))

    def san(self, position, ruleset) -> str:
        """Return the Standard Algebraic Notation of a move.

        :param position: Chess position _before_ the move is performed.
        :type position: :class:`Position`
        :param ruleset: Game ruleset.
        :return: Standard Algebraic Notation.
        """
        result = ''

        if MoveFlag.KINGSIDE_CASTLING in self.flags:
            result = 'O-O'
        elif MoveFlag.QUEENSIDE_CASTLING in self.flags:
            result = 'O-O-O'
        else:
            if self.piece.type != Type.PAWN:
                disambiguator = self._disambiguate_san(position, ruleset)
                # TODO: Make following line nicer.
                piece = self.piece.type.value.upper()
                result += '{}{}'.format(piece, disambiguator)
            if self.captured:
                if self.piece.type is Type.PAWN:
                    result += self.origin.file
                result += 'x'
            result += self.destination
            if MoveFlag.PROMOTION in self.flags:
                result += self.promotion.value.upper()

        new_position = ruleset.do_move(position, self)
        if ruleset.is_check(new_position):
            if ruleset.is_stale(new_position):
                result += '#'
            else:
                result += '+'

        return result

    @classmethod
    def from_san(
            cls,
            san: str,
            position,
            ruleset,
            strict: bool = False) -> 'Move':
        """Return a :class:`Move` object from a Standard Algebraic Notation
        string.

        :param san: Standard Algebraic Notation.
        :param position: Chess position _before_ the move is performed.
        :type position: :class:`Position`
        :param ruleset: Game ruleset.
        :param strict: Only accept the strictest possible notation as valid.
        :return: A move.
        :raise ValueError: *san* is invalid.
        """
        if not strict:
            san = stripped_san(san)
        match = SAN_PATTERN.match(san)
        castling = 'O-O' in san
        if not match:
            if not castling:
                raise ValueError('{!r} is not a valid notation'.format(san))
        else:
            piece, file, rank, destination, promotion = match.groups()

        # Compare properties of *san* with legal moves.  This is a lot less
        # error-prone than re-implementing all the rules of chess heuristically
        # for this function.
        for move in ruleset.moves(position):
            # This check is here for performance:  Don't bother with all the
            # logic below if we have a castling SAN, but *move* is not a
            # castling move.
            if castling and not any(
                    flag in move.flags for flag in (
                        MoveFlag.KINGSIDE_CASTLING,
                        MoveFlag.QUEENSIDE_CASTLING)):
                continue
            if strict or castling:
                # Just generate the SAN for the move.  This works on the
                # assumption that generated SANs are always strict.
                #
                # For castling, we could technically manually create the move,
                # but this solution requires a lot less coding effort.
                #
                # Note that this is not very performant.
                move_san = move.san(position, ruleset)
                if not strict:
                    move_san = stripped_san(move_san)
                if move_san == san:
                    return move
                continue
            # pylint: disable=too-many-boolean-expressions
            if (
                    move.destination != destination
                    or (file and move.origin.file != file)
                    or (rank and str(move.origin.rank) != rank)
                    or (piece and move.piece.type != Type(piece.lower()))
                    or (promotion
                        and move.promotion != Type(promotion.lower()))
                    or (not piece and move.piece.type != Type.PAWN)):
                continue
            # Edge case.
            if not promotion and move.promotion:
                break
            return move

        raise ValueError('{!r} is not a valid move'.format(san))

    def _disambiguate_san(
            self,
            position,
            ruleset) -> str:
        """Find the *origin* coordinates (either file or rank or both) that
        might be necessary to disambiguate a SAN move.

        If the rank is enough to disambiguate by, use solely the rank.  If the
        file is enough to disambiguate by, use solely the file.  Else, use
        both.
        """
        file = ''
        rank = ''
        for move in ruleset.moves(position):
            if (move.piece == self.piece
                    and move.destination == self.destination
                    and move != self):
                if move.origin.file == self.origin.file:
                    rank = str(self.origin.rank)
                elif move.origin.rank == self.origin.rank:
                    file = self.origin.file
        return '{}{}'.format(file, rank)


class HistoryRecord(namedtuple('HistoryRecord', ['position', 'move'])):
    """A history record.  This object is immutable.

    You may put these in a list to keep track of a game's history.
    """
    __slots__ = ()

    def __new__(cls, position, move: Move):
        """:param position: Position before *move* is executed.
        :type position: :class:`Position`
        :param move: Move chosen by the player.
        """
        return super().__new__(cls, position, move)


class Gameover(Enum):
    """How a game has ended.  There is no value for 'game has not ended'."""
    CHECKMATE = 1
    STALEMATE = 2
    FIFTY_MOVE = 3
    INSUFFICIENT_MATERIAL = 4
    THREEFOLD_REPETITION = 5
