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

"""A board representation and implementation."""

import operator
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from functools import lru_cache
from io import StringIO
from typing import Any, Iterator, List, Optional, Tuple, Union

from ._core import Piece, Side, Square, Type  # pylint: disable=unused-import
from ._util import ALL_SQUARES, validate_fen_board


class Board(metaclass=ABCMeta):
    """An abstract base class for a chess board implementation.  A chess board
    is immutable and need implement only :meth:`get`, :meth:`put` and
    :meth:`__init__`.  :meth:`__init__` must take no positional arguments and -
    without any arguments - create an initial chess board.

    All other methods are already implemented.
    """

    def __init__(self):
        self._hash = None

    @classmethod
    def from_fen(cls, fen: str) -> 'Board':
        """Generate a :class:`Board` from the board portion of a
        Forsyth-Edwards Notation string.

        :param fen: First part of Forsyth-Edwards Notation
        :return: A board.
        :raise ValueError: Input is invalid.
        """
        board = cls()
        fen = fen.split()[0]
        chunks = fen.split('/')
        files = 'abcdefgh'

        if not validate_fen_board(fen):
            raise ValueError('{} is not a valid notation'.format(fen))

        # From white to black
        for rank, chunk in zip(range(1, 9), reversed(chunks)):
            file_position = 0
            for char in chunk:
                if char.isnumeric():
                    for _ in range(int(char)):
                        board = board.put(
                            '{}{}'.format(files[file_position], rank),
                            None)
                        file_position += 1
                else:
                    piece = Piece.from_str(char)
                    board = board.put(
                        '{}{}'.format(files[file_position], rank),
                        piece)
                    file_position += 1

        return board

    @abstractmethod
    def get(self, square: str) -> Optional[Piece]:
        """Return piece at *square*.  Return :const:`None` if no piece exists
        at square.

        :param square: Square in algebraic notation.
        :return: Piece at square.
        """

    @abstractmethod
    def put(self, square: str, piece: Optional[Piece]) -> 'Board':
        """Put *piece* on *square*.  Override any existing pieces.  Return a
        new board.

        :param square: Square in algebraic notation.
        :param piece: Piece to be placed on square.
        :return: A new board.
        """

    def pretty(self) -> str:
        """
        >>> print(DictBoard().pretty())
          A B C D E F G H
        8 r n b q k b n r
        7 p p p p p p p p
        6 . . . . . . . .
        5 . . . . . . . .
        4 . . . . . . . .
        3 . . . . . . . .
        2 P P P P P P P P
        1 R N B Q K B N R

        :return: A pretty representation of the board.
        """
        result = StringIO()
        result.write('  A B C D E F G H\n')
        for rank in reversed(list(zip(*[iter(ALL_SQUARES)] * 8))):
            row = [rank[0][1]]
            for square in rank:
                piece = self.get(square)
                if not piece:
                    piece = '.'
                else:
                    piece = str(piece)
                row.append(piece)
            result.write(' '.join(row))
            result.write('\n')
        return result.getvalue().rstrip()

    def all_pieces(self) -> Iterator[Tuple[Square, Optional[Piece]]]:
        """Yield all squares and their respective pieces, from a1 to h8.
        Increment files before ranks.

        Comparable to :func:`enumerate`, except for squares and pieces.

        :return: All squares and their respective pieces.
        """
        return ((square, self.get(square)) for square in ALL_SQUARES)

    def __getitem__(self, key: str) -> Optional[Piece]:
        return self.get(key)

    def __eq__(self, other: Any) -> bool:
        for square in ALL_SQUARES:
            try:
                if self.get(square) != other.get(square):
                    return False
            except:  # pylint: disable=bare-except
                return False
        return True

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        # First divide up in chunks of 8.
        chunks = [
            [self.get('{}{}'.format(file_, rank)) for file_ in 'abcdefgh']
            for rank in reversed(range(1, 9))]
        new_chunks = []

        for chunk in chunks:
            new_chunk = []
            counter = 0
            # Just add each piece to *new_chunk*, unless it's an empty square.
            # Increment *counter* if the square is empty.  Add the value of
            # counter to *new_chunk* when the loop hits a piece, or if it hits
            # the end.
            for piece in chunk:
                if piece:
                    if counter:
                        new_chunk.append(str(counter))
                        counter = 0
                    new_chunk.append(
                        piece.type.value.upper()
                        if piece.side is Side.WHITE
                        else piece.type.value)
                else:
                    counter += 1
            if counter:
                new_chunk.append(str(counter))

            # Join the chunks into a single string and append them to
            # *new_chunks*.
            new_chunks.append(''.join(new_chunk))

        # Join the chunks with '/'.
        return '/'.join(new_chunks)

    def __hash__(self):
        if self._hash is not None:
            return self._hash
        result = 0
        for i, (_, piece) in enumerate(self.all_pieces()):
            result += (i + 1) * hash(piece)
        self._hash = result
        return self._hash


def all_board_classes() -> List[Board]:
    """Return a list of all defined board classes, excluding the base class."""
    result = []
    for key, value in globals().items():
        if key.endswith('Board') and key != 'Board':
            result.append(value)
    return sorted(result, key=operator.attrgetter('__name__'))


@lru_cache(maxsize=64)
def algebraic_to_index(square: Union[Square, str]) -> int:
    """Convert the square in algebraic notation to the corresponding index
    in our internal representation.

    :param square: Algebraic notation square.
    :return: Index on board.
    :raise ValueError: Input is invalid.

    >>> algebraic_to_index('a1')
    0
    >>> algebraic_to_index('h8')
    63
    >>> algebraic_to_index('9a')
    Traceback (most recent call last):
        ...
    ValueError: '9a' is not a valid square
    """
    square = Square(square)

    rank = square.rank - 1
    file_ = ord(square.file) - 97

    return rank * 8 + (file_)


ALGEBRAIC_TO_INDEX_MAP = dict()
for _square in ALL_SQUARES:
    ALGEBRAIC_TO_INDEX_MAP[_square] = algebraic_to_index(_square)

_BitBoardTup = namedtuple(
    '_BitBoardTup',
    [
        'kings', 'queens', 'rooks', 'bishops', 'knights', 'pawns', 'whites',
        'blacks'])

# Board looks reversed!  This is normal.  Most chess board implementations use
# a1 as index 0.
_INITIAL_STRINGBOARD = (
    'RNBQKBNR'  # 0-7,   a1-h1
    'PPPPPPPP'  # 8-15,  a2-h2
    '        '  # 16-23, a3-h3
    '        '  # 24-31, a4-h4
    '        '  # 32-39, a5-h5
    '        '  # 40-47, a6-h6
    'pppppppp'  # 48-55, a7-h7
    'rnbqkbnr'  # 56-63, a8-h8
)

_INITIAL_BYTESBOARD = _INITIAL_STRINGBOARD.encode('ascii')

_INITIAL_DICTBOARD = dict()
_INITIAL_LISTBOARD = list()
_INITIAL_KINGS = 0
_INITIAL_QUEENS = 0
_INITIAL_ROOKS = 0
_INITIAL_BISHOPS = 0
_INITIAL_KNIGHTS = 0
_INITIAL_PAWNS = 0
_INITIAL_WHITES = 0
_INITIAL_BLACKS = 0

for _char, _square in zip(_INITIAL_STRINGBOARD, ALL_SQUARES):
    if _char == ' ':
        _piece = None
    else:
        _piece = Piece.from_str(_char)
    _INITIAL_DICTBOARD[_square] = _piece
    _INITIAL_LISTBOARD.append(_piece)
    if not _piece:
        continue
    _bit = 1 << ALGEBRAIC_TO_INDEX_MAP[_square]
    if _piece.type is Type.KING:
        _INITIAL_KINGS = _INITIAL_KINGS | _bit
    elif _piece.type is Type.QUEEN:
        _INITIAL_QUEENS = _INITIAL_QUEENS | _bit
    elif _piece.type is Type.ROOK:
        _INITIAL_ROOKS = _INITIAL_ROOKS | _bit
    elif _piece.type is Type.BISHOP:
        _INITIAL_BISHOPS = _INITIAL_BISHOPS | _bit
    elif _piece.type is Type.KNIGHT:
        _INITIAL_KNIGHTS = _INITIAL_KNIGHTS | _bit
    elif _piece.type is Type.PAWN:
        _INITIAL_PAWNS = _INITIAL_PAWNS | _bit

    if _piece.side is Side.WHITE:
        _INITIAL_WHITES = _INITIAL_WHITES | _bit
    else:
        _INITIAL_BLACKS = _INITIAL_BLACKS | _bit

_INITIAL_TUPLEBOARD = tuple(_INITIAL_LISTBOARD)
_INITIAL_BITBOARD = _BitBoardTup(
    _INITIAL_KINGS, _INITIAL_QUEENS, _INITIAL_ROOKS, _INITIAL_BISHOPS,
    _INITIAL_KNIGHTS, _INITIAL_PAWNS, _INITIAL_WHITES, _INITIAL_BLACKS)


class BitBoard(Board):
    """A bitboard representation."""

    def __init__(self, **kwargs):
        super().__init__()
        self._board = kwargs.get('_board', _INITIAL_BITBOARD)

    def get(self, square: str) -> Optional[Piece]:
        bit = 1 << ALGEBRAIC_TO_INDEX_MAP[square]
        side = None
        type_ = None
        if bit & self._board.whites:
            side = Side.WHITE
        elif bit & self._board.blacks:
            side = Side.BLACK
        else:
            return None

        if bit & self._board.kings:
            type_ = Type.KING
        elif bit & self._board.queens:
            type_ = Type.QUEEN
        elif bit & self._board.rooks:
            type_ = Type.ROOK
        elif bit & self._board.bishops:
            type_ = Type.BISHOP
        elif bit & self._board.knights:
            type_ = Type.KNIGHT
        elif bit & self._board.pawns:
            type_ = Type.PAWN

        return Piece(type_, side)

    def put(self, square: str, piece: Optional[Piece]) -> 'BitBoard':
        index = ALGEBRAIC_TO_INDEX_MAP[square]
        bit = 1 << index

        # Pop bit at index.
        mask = ~bit
        kings = self._board.kings & mask
        queens = self._board.queens & mask
        rooks = self._board.rooks & mask
        bishops = self._board.bishops & mask
        knights = self._board.knights & mask
        pawns = self._board.pawns & mask
        whites = self._board.whites & mask
        blacks = self._board.blacks & mask

        if piece is not None:
            if piece.type is Type.KING:
                kings = kings | bit
            elif piece.type is Type.QUEEN:
                queens = queens | bit
            elif piece.type is Type.ROOK:
                rooks = rooks | bit
            elif piece.type is Type.BISHOP:
                bishops = bishops | bit
            elif piece.type is Type.KNIGHT:
                knights = knights | bit
            elif piece.type is Type.PAWN:
                pawns = pawns | bit

            if piece.side is Side.WHITE:
                whites = whites | bit
            elif piece.side is Side.BLACK:
                blacks = blacks | bit

        return self.__class__(_board=_BitBoardTup(
            kings, queens, rooks, bishops, knights, pawns, whites, blacks))


class BytesBoard(Board):
    """A simple bytes-based board representation."""

    def __init__(self, **kwargs):
        super().__init__()
        self._board = kwargs.get('_board', _INITIAL_BYTESBOARD)

    def get(self, square: str) -> Optional[Piece]:
        i = self._board[ALGEBRAIC_TO_INDEX_MAP[square]]
        letter = bytes((i,))
        if letter == b' ':
            return None
        rtype = Type(letter.lower().decode('ascii'))
        rside = Side.WHITE if letter.isupper() else Side.BLACK
        return Piece(rtype, rside)

    def put(self, square: str, piece: Optional[Piece]) -> 'BytesBoard':
        if piece is None:
            letter = b' '
        else:
            letter = str(piece).encode('ascii')
        index = ALGEBRAIC_TO_INDEX_MAP[square]
        return self.__class__(_board=b''.join([
            self._board[:index],
            letter,
            self._board[index + 1:]
        ]))


class DictBoard(Board):
    """A simple dictionary-based board representation."""

    def __init__(self, **kwargs):
        super().__init__()
        self._board = kwargs.get('_board', _INITIAL_DICTBOARD)

    def get(self, square: str) -> Optional[Piece]:
        return self._board[square]

    def put(self, square: str, piece: Optional[Piece]) -> 'DictBoard':
        # Shallow copy.  This is acceptable, because all values in it are
        # immutable.
        new_dict = self._board.copy()
        new_dict[Square(square)] = piece
        return self.__class__(_board=new_dict)


class ListBoard(Board):
    """A simple list-based board representation."""

    def __init__(self, **kwargs):
        super().__init__()
        self._board = kwargs.get('_board', _INITIAL_LISTBOARD)

    def get(self, square: str) -> Optional[Piece]:
        return self._board[ALGEBRAIC_TO_INDEX_MAP[square]]

    def put(self, square: str, piece: Optional[Piece]) -> 'DictBoard':
        # Shallow copy.  This is acceptable, because all values in it are
        # immutable.
        new_list = self._board[:]
        new_list[ALGEBRAIC_TO_INDEX_MAP[square]] = piece
        return self.__class__(_board=new_list)


class StringBoard(Board):
    """A simple string-based board representation."""

    def __init__(self, **kwargs):
        super().__init__()
        self._board = kwargs.get('_board', _INITIAL_STRINGBOARD)

    def get(self, square: str) -> Optional[Piece]:
        letter = self._board[ALGEBRAIC_TO_INDEX_MAP[square]]
        if letter == ' ':
            return None
        return Piece.from_str(letter)

    def put(self, square: str, piece: Optional[Piece]) -> 'StringBoard':
        if piece is None:
            letter = ' '
        else:
            letter = str(piece)
        index = ALGEBRAIC_TO_INDEX_MAP[square]
        return self.__class__(_board='{}{}{}'.format(
            self._board[:index],
            letter,
            self._board[index + 1:]
        ))


class TupleBoard(Board):
    """A tuple-based board representation."""

    def __init__(self, **kwargs):
        super().__init__()
        self._board = kwargs.get('_board', _INITIAL_TUPLEBOARD)

    def get(self, square: str) -> Optional[Piece]:
        return self._board[ALGEBRAIC_TO_INDEX_MAP[square]]

    def put(self, square: str, piece: Optional[Piece]) -> 'DictBoard':
        # Shallow copy.  This is acceptable, because all values in it are
        # immutable.
        index = ALGEBRAIC_TO_INDEX_MAP[square]
        new_tuple = self._board[:index] + (piece,) + self._board[index + 1:]
        return self.__class__(_board=new_tuple)
