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

"""A module implementing all the rules of chess."""

import logging
import sys
from collections import Counter
from typing import Iterator, Optional, Sequence, Tuple, Union

from ._core import (Direction, Gameover, HistoryRecord, Move, MoveFlag, Piece,
                    Side, Square, Type, _in_bounds)
from ._position import Castling, CastlingSide, Position
from ._util import ALL_SQUARES, opponent

LOGGER = logging.getLogger(__name__)

# Reduce attribute lookup time by moving these names into the global namespace.

# Direction
_UP = Direction.UP
_DOWN = Direction.DOWN
_LEFT = Direction.LEFT
_RIGHT = Direction.RIGHT

# Type
_KING = Type.KING
_QUEEN = Type.QUEEN
_ROOK = Type.ROOK
_BISHOP = Type.BISHOP
_KNIGHT = Type.KNIGHT
_PAWN = Type.PAWN

# Side
_WHITE = Side.WHITE
_BLACK = Side.BLACK

# MoveFlag
_NON_CAPTURE = MoveFlag.NON_CAPTURE
_STANDARD_CAPTURE = MoveFlag.STANDARD_CAPTURE
_EN_PASSANT_CAPTURE = MoveFlag.EN_PASSANT_CAPTURE
_PAWN_PUSH = MoveFlag.PAWN_PUSH
_QUEENSIDE_CASTLING = MoveFlag.QUEENSIDE_CASTLING
_KINGSIDE_CASTLING = MoveFlag.KINGSIDE_CASTLING
_PROMOTION = MoveFlag.PROMOTION

# Instead of creating these sets in every function, already have them generated
# as constants.
_NON_CAPTURE_SET = frozenset({_NON_CAPTURE})
_STANDARD_CAPTURE_SET = frozenset({_STANDARD_CAPTURE})
_EN_PASSANT_CAPTURE_SET = frozenset({_EN_PASSANT_CAPTURE})
_PAWN_PUSH_SET = frozenset({_PAWN_PUSH})
_QUEENSIDE_CASTLING_SET = frozenset({_QUEENSIDE_CASTLING})
_KINGSIDE_CASTLING_SET = frozenset({_KINGSIDE_CASTLING})
_PROMOTION_SET = frozenset({_PROMOTION})

_NON_CAPTURE_PROMOTION_SET = _NON_CAPTURE_SET | _PROMOTION_SET
_NON_CAPTURE_PAWN_PUSH_SET = _NON_CAPTURE_SET | _PAWN_PUSH_SET
_NON_CAPTURE_KINGSIDE_CASTLING_SET = _NON_CAPTURE_SET | _KINGSIDE_CASTLING_SET
_NON_CAPTURE_QUEENSIDE_CASTLING_SET = (
    _NON_CAPTURE_SET | _QUEENSIDE_CASTLING_SET)
_STANDARD_CAPTURE_PROMOTION_SET = _STANDARD_CAPTURE_SET | _PROMOTION_SET

# pylint: disable=invalid-name
_DirectionPath = Sequence[Direction]
_TupleOfTwoDirectionPaths = Tuple[_DirectionPath, _DirectionPath]
_TupleOfTwoTuplesOf = Tuple[
    _TupleOfTwoDirectionPaths, _TupleOfTwoDirectionPaths]

_PAWN_PATHS = {  # type: Dict[Side, _TupleOfTwoTuplesOf]
    _WHITE: (
        # Advancing paths
        (
            (_UP.value,),
            (_UP.value, _UP.value),
        ),
        # Capturing paths
        (
            (_UP.value, _RIGHT.value),
            (_UP.value, _LEFT.value),
        ),
    ),
    _BLACK: (
        # Adancing paths
        (
            (_DOWN.value,),
            (_DOWN.value, _DOWN.value),
        ),
        # Capturing paths
        (
            (_DOWN.value, _RIGHT.value),
            (_DOWN.value, _LEFT.value),
        ),
    ),
}

_PIECE_PATHS = {  # type: Dict[Type, Set[_DirectionPath]]
    _KNIGHT: frozenset({
        (_UP.value, _UP.value, _RIGHT.value),
        (_UP.value, _UP.value, _LEFT.value),
        (_UP.value, _RIGHT.value, _RIGHT.value),
        (_UP.value, _LEFT.value, _LEFT.value),
        (_DOWN.value, _RIGHT.value, _RIGHT.value),
        (_DOWN.value, _LEFT.value, _LEFT.value),
        (_DOWN.value, _DOWN.value, _RIGHT.value),
        (_DOWN.value, _DOWN.value, _LEFT.value),
    }),
    _BISHOP: frozenset({
        (_UP.value, _RIGHT.value),
        (_UP.value, _LEFT.value),
        (_DOWN.value, _RIGHT.value),
        (_DOWN.value, _LEFT.value),
    }),
    _ROOK: frozenset({
        (_UP.value,),
        (_RIGHT.value,),
        (_LEFT.value,),
        (_DOWN.value,),
    }),
}
_PIECE_PATHS[_QUEEN] = _PIECE_PATHS[_BISHOP].union(_PIECE_PATHS[_ROOK])
_PIECE_PATHS[_KING] = _PIECE_PATHS[_QUEEN]

_TO_CHECK = {  # type: Dict[Type, Set[Type]]
    _KNIGHT: frozenset({_KNIGHT}),
    _BISHOP: frozenset({_BISHOP, _QUEEN, _KING}),
    _ROOK: frozenset({_ROOK, _QUEEN, _KING}),
}


def attacked(position: Position, side: Side, square: Square) -> bool:
    """ Is *square* in check by *side*?

    .. NOTE::
        Pawns that can be struck through an en passant move are also identified
        as being in check by this function.

    .. NOTE::
        Just because *square* might be in check, it does *NOT* mean that the
        square can be legally captured.  The piece attacking *square* might be
        pinned, for instance.  Or more mundanely, the square is held by a piece
        that is friendly to the attacker.

    :param position: Chess position.
    :param side: Attacking side.
    :param square: Square that is under attack or not.
    :return: Whether *square* is in check by *side*.
    """
    # pylint: disable=too-many-branches

    # Implementation detail:
    # Draw rays from *square* and check whether a piece from *side* is struck,
    # and whether that piece can strike back using the same ray.
    #
    # This is more performant than checking all the plausible moves, filtering
    # for attack moves, and checking whether your square is a destination in
    # one of those moves.

    square = Square(square)
    other_side = opponent(side)
    # En passant
    if position.en_passant_target and side is position.side_to_play:
        if side is _WHITE and square is position.en_passant_target.down():
            return True
        elif side is _BLACK and square is position.en_passant_target.up():
            return True

    # Pawn
    pawn_paths = _PAWN_PATHS[
        other_side][1]  # type: Iterable[_DirectionPath]
    pawn_piece = Piece(_PAWN, side)
    for path in pawn_paths:
        target = _in_bounds(square, path)
        if not target:
            continue
        if position.board.get(target) is pawn_piece:
            return True

    # Pretend our square is a knight, a bishop or a rook.  If an identical
    # piece (or a queen or a king) is in our path, then our square is in check.
    for type_, targets in _TO_CHECK.items():
        for path in _PIECE_PATHS[type_]:
            first_traverse = True
            current = square
            while True:
                current = _in_bounds(current, path)
                if not current:
                    break

                target = position.board.get(current)
                if target:
                    # If piece is friendly, stop checking in this direction
                    if target.side is other_side:
                        break
                    if not first_traverse and target.type is _KING:
                        break
                    if target.type in targets:
                        return True
                    else:
                        break

                first_traverse = False
                if type_ is _KNIGHT:
                    break

    return False


def moves_single(
        position: Position,
        square: Union[Square, str]) -> Iterator[Move]:
    """Yield all legal moves for *position* from *square*.  See :func:`moves`
    for a full description of what constitutes a legal move.

    :param position: Chess position.
    :param square: Square from which to calculate moves.
    :return: All legal moves from *square*.
    """
    square = Square(square)
    other_side = opponent(position.side_to_play)

    for move in _all_moves_single(position, square):
        new_position = _perform_move(position, move)
        # Move results in check?
        if is_check(new_position, position.side_to_play):
            continue

        kingside = _KINGSIDE_CASTLING in move.flags
        queenside = _QUEENSIDE_CASTLING in move.flags
        # Castling
        if kingside or queenside:
            current = move.origin
            direction = _RIGHT if kingside else _LEFT
            while current != move.destination:
                # King has to cross through square that is in check to castle.
                if attacked(position, other_side, current):
                    break
                current = current.goto(direction.value)
            # All clear
            else:
                yield move
        else:
            yield move


def moves(position: Position) -> Iterator[Move]:
    """Yield all legal moves for *position*.  This includes:

    - Regular moves and captures.

    - En passant captures.

    - Pawn promotions (each promotion yields its own move).

    - Castling.

    Moves that result in check are not legal.

    The rules of chess can be found here:

    `<https://en.wikipedia.org/wiki/Rules_of_chess#Gameplay>`_

    It is currently not possible to enable, disable or change certain rules.

    .. IMPORTANT::
        *position* is assumed to be correct.  If the position is impossible,
        the behaviour of this function is undefined.

    :param position: Chess position.
    :return: All legal moves.
    """
    return (
        move for square, piece in position.board.all_pieces()
        # Small optimalisation
        if piece is not None
        and piece.side is position.side_to_play
        for move in moves_single(position, square))


def do_move(
        position: Position,
        move: Union[Move, str],
        force: bool = False) -> Position:
    """Perform *move* on *position* and return the resulting position.

    *move* need only contain the *origin*, *destination* and (possibly)
    *promotion* fields.  It can also be a SAN string.

    If the *promotion* field is not specified, :func:`do_move` will default to
    queen promotion.

    If *force* is specified, *move* needs all the correct fields filled out.
    *force* disables any move verification and will lead to unspecified
    behaviour if an invalid move is provided.  Typically you might obtain valid
    moves from :func:`moves`.

    >>> do_move(Position(), Move(origin='a2', destination='a4'))
    rnbqkbnr/pppppppp/8/8/P7/8/1PPPPPPP/RNBQKBNR b KQkq a3 0 1

    :param position: Chess position to perform a move on.
    :param move: Move to be executed.
    :param force: Whether to perform the move without any verification.
    :return: The position that results from performing *move*.
    :raise ValueError: *move* is invalid.
    """
    return do_move_with_history(position, move, force)[0]


def do_move_with_history(
        position: Position,
        move: Union[Move, str],
        force: bool = False) -> Tuple[Position, HistoryRecord]:
    """Exactly as :func:`do_move`, except instead of returning the resulting
    position, return a tuple of the resulting position and the history
    record to reach that position.

    :param position: Chess position to perform a move on.
    :param move: Move to be executed.
    :param force: Whether to perform the move without any verification.
    :return: The position that results from performing *move*, and the
             corresponding history record.
    :raise ValueError: *move* is invalid.
    """
    if isinstance(move, str):
        move = Move.from_san(move, position, sys.modules[__name__])
    elif not force:
        move = move.expand(position, sys.modules[__name__])

    return (_perform_move(position, move), HistoryRecord(position, move))


def is_check(position: Position, side: Side = None) -> bool:
    """Return whether *side*'s king is in check.

    If *side* is not specified, it defaults to the side to play.

    :param position: Chess position.
    :param side: Side to check for check.
    :return: Whether *side*'s king is in check.
    """
    if side is None:
        side = position.side_to_play
    king_piece = Piece(_KING, side)
    for square, piece in position.board.all_pieces():
        if piece is king_piece:
            return attacked(position, opponent(side), square)
    LOGGER.warning('no king in %s', position)
    return False


def is_stale(position: Position) -> bool:
    """Return whether there are no possible moves left.

    :param position: Chess position.
    :return: Whether the position is stale.
    """
    try:
        next(moves(position))
        return False
    except StopIteration:
        return True


def is_checkmate(position: Position) -> bool:
    """Return whether *position* is in checkmate.

    :param position: Chess position.
    :return: Whether the position is in checkmate.
    """
    return is_check(position) and is_stale(position)


def is_stalemate(position: Position) -> bool:
    """Return whether *position* is in stalemate.

    :param position: Chess position.
    :return: Whether the position is in stalemate.
    """
    return is_stale(position) and not is_check(position)


def is_fifty_move(position: Position) -> bool:
    """There have been fifty moves without a pawn advance or without a capture.

    :param position: Chess position.
    :return: Whether the fifty-move rule has been initiated.
    """
    return position.half_move_clock >= 50


def is_insufficient_material(position: Position) -> bool:
    """There are not enough pieces left on the board for either player to win.

    That is:

    - K v. k

    - K + N v. k

    - K + B v. k + b where all bishops are on the same colour, any number of
      bishops on both sides

    There are more situations where this rule might apply, but those situations
    are not accounted for here.

    :param position: Chess position.
    :return: Whether there is insufficient material.
    """
    amount = 0
    bishop_colours = []
    knight_present = False

    for square, piece in position.board.all_pieces():
        if piece:
            amount += 1
            if piece.type in (_QUEEN, _ROOK):
                return False
            elif piece.type is _BISHOP:
                bishop_colours.append(square.colour)
            elif piece.type is _KNIGHT:
                knight_present = True

    # K v. k
    if amount == 2:
        return True
    # K + N v. k
    elif amount == 3 and knight_present:
        return True
    # K + B v. k + b
    elif not knight_present and len(set(bishop_colours)) == 1:
        return True
    return False


def is_threefold_repetition(history: Sequence[HistoryRecord] = None) -> bool:
    """The same position has been played three times.

    If *history* is not specified, return :const:`False`.

    :param history: History of plays.
    :return: Whether the threefold repetition rule has been initiated.
    """
    if history is None:
        return False
    counter = Counter([(p.board, p.side_to_play, p.castling,
                        p.en_passant_target)
                       for p in (record.position for record in history)])
    if not counter:
        return False
    return counter.most_common(1)[0][1] >= 3


def is_draw(
        position: Position,
        history: Sequence[HistoryRecord] = None) -> Union[Gameover, bool]:
    """Return whether *position* is in draw.

    :param position: Chess position.
    :param history: History of plays.
    :return: Whether and how the position is in draw.
    """
    if is_stalemate(position):
        return Gameover.STALEMATE
    elif is_fifty_move(position):
        return Gameover.FIFTY_MOVE
    elif is_insufficient_material(position):
        return Gameover.INSUFFICIENT_MATERIAL
    elif is_threefold_repetition(history):
        return Gameover.THREEFOLD_REPETITION
    return False


def is_gameover(
        position: Position,
        history: Sequence[HistoryRecord] = None) -> Union[Gameover, bool]:
    """Return whether *position* is game-over.

    :param position: Chess position.
    :param history: History of plays.
    :return: Whether and how the position is game-over.
    """

    if is_checkmate(position):
        return Gameover.CHECKMATE
    return is_draw(position, history)


def winner(position: Position) -> Optional[Side]:
    """Return the winner of *position*.

    If there is no winner, return :const:`None`.

    :param position: Chess position.
    :return: The winner.
    """
    if is_checkmate(position):
        return opponent(position.side_to_play)
    return None


def loser(position: Position) -> Optional[Side]:
    """Return the loser of *position*.

    If there is no loser, return :const:`None`.

    :param position: Chess position.
    :return: The loser.
    """
    result = winner(position)
    if result is not None:
        return opponent(result)
    return None


def _replace_castling(
        castling: Castling,
        castling_side: CastlingSide,
        side: Side) -> Castling:
    """Create and return a new Castling object from *castling* where
    *castling[side]* is replaced by *castling_side*.
    """
    if side is _WHITE:
        return Castling(castling_side, castling.black)
    return Castling(castling.white, castling_side)


def _perform_move(position: Position, move: Move) -> Position:
    """Perform a move on *position* and return the resulting position.

    .. IMPORTANT::
        *move* has to be a *COMPLETELY VALID* :class:`~en_pyssant.Move` object
        for this to work.  If the move's flags are incorrect or if the move is
        illegal, there is no saying what this function will do.

    >>> _perform_move(
    ...     Position(),
    ...     Move(
    ...         'a2', 'a3', Piece(Type.PAWN, Side.WHITE),
    ...         flags=frozenset({MoveFlag.NON_CAPTURE})))
    ...
    rnbqkbnr/pppppppp/8/8/8/P7/1PPPPPPP/RNBQKBNR b KQkq - 0 1

    :param position: Chess position.
    :param move: Move to be executed.
    :return: The resulting position.
    """
    # pylint: disable=too-many-branches
    # Do the move on the board
    board = position.board.put(move.destination, move.piece)
    board = board.put(move.origin, None)

    side = position.side_to_play
    castling = position.castling
    en_passant_target = None
    half_move_clock = position.half_move_clock
    move_count = position.move_count

    # En passant
    if _EN_PASSANT_CAPTURE in move.flags:
        if side is _WHITE:
            target = move.destination.down()
        else:
            target = move.destination.up()
        board = board.put(target, None)

    # Promotion
    elif _PROMOTION in move.flags:
        board = board.put(move.destination, Piece(move.promotion, side))

    # Set en passant target behind advancing pawn if the pawn pushed
    elif _PAWN_PUSH in move.flags:
        if side is _WHITE:
            en_passant_target = move.destination.down()
        else:
            en_passant_target = move.destination.up()

    # King
    if move.piece.type is _KING:
        if _KINGSIDE_CASTLING in move.flags:
            rook_square = move.destination.right()
            rook_destination = move.destination.left()
            board = board.put(rook_destination, board.get(rook_square))
            board = board.put(rook_square, None)
        elif _QUEENSIDE_CASTLING in move.flags:
            rook_square = move.destination.left().left()
            rook_destination = move.destination.right()
            board = board.put(rook_destination, board.get(rook_square))
            board = board.put(rook_square, None)

        # Turn off castling
        castling = _replace_castling(
            castling, CastlingSide(False, False), side)

    # Rook
    elif move.piece.type is _ROOK:
        if move.origin.file == 'h' and castling[side].kingside:
            queenside = castling[side].queenside
            castling = _replace_castling(
                castling, CastlingSide(False, queenside), side)
        elif move.origin.file == 'a' and castling[side].queenside:
            kingside = castling[side].kingside
            castling = _replace_castling(
                castling, CastlingSide(kingside, False), side)

    # Has pawn moved or has a piece been captured
    if (move.piece.type is _PAWN
            or any(
                flag in move.flags for flag in
                (_STANDARD_CAPTURE, _EN_PASSANT_CAPTURE))):
        half_move_clock = 0
    else:
        half_move_clock += 1

    # Increase move count
    if side is _BLACK:
        move_count += 1

    return Position(
        board, opponent(side), castling, en_passant_target, half_move_clock,
        move_count)


def _all_moves_single(position: Position, square: Square) -> Iterator[Move]:
    """Yield all plausible moves from a given square.  See :func:`_all_moves`
    for the definition of "plausible moves".

    >>> moves = sorted(list(_all_moves_single(Position(), Square('a2'))))
    >>> for move, destination in zip(moves, ['a3', 'a4']):
    ...     assert move.origin == 'a2'
    ...     assert move.destination == destination
    ...     assert MoveFlag.NON_CAPTURE in move.flags
    ...     if destination == 'a4':
    ...         assert MoveFlag.PAWN_PUSH in move.flags
    ...

    :param position: Chess position.
    :param square: Square from which to calculate moves.
    :return: All plausible moves from *square*.
    """
    # Maybe split this up because this is huge.
    # pylint: disable=too-many-branches,too-many-locals,too-many-statements
    board = position.board
    piece = board.get(square)
    side = position.side_to_play
    other_side = opponent(side)

    # Square is empty or belongs to other side.
    if not piece or piece.side != side:
        return

    # Pawn
    if piece.type is _PAWN:
        base_rank = 2 if side is _WHITE else 7
        promotion_rank = 8 if side is _WHITE else 1
        # Pawn hasn't yet moved
        if square.rank == base_rank:
            advance_paths = _PAWN_PATHS[
                side][0]  # type: Iterable[_DirectionPath]
        else:
            advance_paths = (
                _PAWN_PATHS[side][0][0],)  # type: Iterable[_DirectionPath]

        # Advance
        for path, push in zip(advance_paths, (0, 1)):
            destination = square.traverse(path)
            # Destination square is occupied
            if board.get(destination):
                break
            # Promotion
            if destination.rank == promotion_rank:
                flags = _NON_CAPTURE_PROMOTION_SET
                for promotion_target in (_KNIGHT, _BISHOP, _ROOK, _QUEEN):
                    yield Move(
                        square, destination, piece, promotion=promotion_target,
                        flags=flags)
            # Regular advance
            else:
                flags = _NON_CAPTURE_SET
                if push:
                    flags = _NON_CAPTURE_PAWN_PUSH_SET
                yield Move(square, destination, piece, flags=flags)

        # Capture
        for path in _PAWN_PATHS[side][1]:
            destination = _in_bounds(square, path)
            if not destination:
                continue
            target = board.get(destination)
            # Target is enemy
            if target and target.side is other_side:
                flags = _STANDARD_CAPTURE_SET
                # Promotion
                if destination.rank == promotion_rank:
                    flags = _STANDARD_CAPTURE_PROMOTION_SET
                    for promotion_target in (_KNIGHT, _BISHOP, _ROOK, _QUEEN):
                        yield Move(
                            square, destination, piece, target,
                            promotion_target, flags)
                # Regular capture
                else:
                    yield Move(square, destination, piece, target, flags=flags)
            # En passant
            if destination == position.en_passant_target:
                captured_pawn = (
                    destination.down() if side is _WHITE else destination.up())
                captured_pawn = board.get(captured_pawn)
                flags = _EN_PASSANT_CAPTURE_SET
                yield Move(square, destination, piece, captured_pawn,
                           flags=flags)

    # All other pieces
    else:
        for path in _PIECE_PATHS[piece.type]:
            current = square

            while True:
                current = _in_bounds(current, path)
                if not current:
                    break
                target = board.get(current)
                # Reached another piece
                if target:
                    # Piece is enemy
                    if target.side is other_side:
                        flags = _STANDARD_CAPTURE_SET
                        yield Move(square, current, piece, target, flags=flags)
                    # Further path is blocked
                    break
                # Unobstructed move
                else:
                    flags = _NON_CAPTURE_SET
                    yield Move(square, current, piece, flags=flags)

                # Kings and knights cannot 'string' moves together in one
                # direction, as it were.
                if piece.type in (_KING, _KNIGHT):
                    break

    # Castling
    if piece.type is _KING:
        # Kingside
        if position.castling[side].kingside:
            destination = square.traverse((_RIGHT.value, _RIGHT.value))
            current = square
            while current != destination:
                current = current.right()
                if board.get(current):
                    break
            # Squares are clear
            else:
                flags = _NON_CAPTURE_KINGSIDE_CASTLING_SET
                yield Move(square, destination, piece, flags=flags)
        # Queenside
        if position.castling[side].queenside:
            destination = square.traverse((_LEFT.value, _LEFT.value))
            current = square
            while current != destination:
                current = current.left()
                if board.get(current):
                    break
            # Squares are clear
            else:
                flags = _NON_CAPTURE_QUEENSIDE_CASTLING_SET
                yield Move(square, destination, piece, flags=flags)


def _all_moves(position: Position) -> Iterator[Move]:
    """Yield all plausible moves.  This function performs very few checks.  It
    only returns all possible squares each piece might move to.

    In summary:

    - The resulting moves are allowed to result in check/checkmate.

    - Pawn capturing moves are as normal, including en passant moves.

    - Striking friendly pieces is not allowed.

    - Castling is allowed even if the king crosses over or lands in a square
      that is in check.

    - Castling is not allowed if the king or rook had already moved (see the
      castling flags in *position*).

    >>> len(list(_all_moves(Position())))
    20

    :param position: Chess position.
    :return: All plausible moves.
    """
    return (
        move for square in ALL_SQUARES
        for move in _all_moves_single(position, square))
