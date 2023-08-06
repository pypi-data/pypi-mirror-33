..
  Copyright (C) 2017-2018  Carmen Bianca Bakker <carmen@carmenbianca.eu>

  This file is part of En Pyssant, available from its original location:
  <https://gitlab.com/carmenbianca/en-pyssant>.

  This work is licensed under the Creative Commons Attribution-ShareAlike
  4.0 International License. To view a copy of this license, visit
  <http://creativecommons.org/licenses/by-sa/4.0/>.

  SPDX-License-Identifier: CC-BY-SA-4.0


==========
En Pyssant
==========

En Pyssant is a chess implementation and engine.

- Free software: GNU General Public License version 3 or later

- Documentation: `<https://carmenbianca.gitlab.io/en-pyssant>`_

- Source code: `<https://gitlab.com/carmenbianca/en-pyssant>`_

- PyPI: `<https://pypi.python.org/pypi/en-pyssant>`_

- Python: 3.4+


.. IMPORTANT::
   This project is still a heavy work in progress and will break backwards
   compatibility with every release before 1.0.


Background
==========

En Pyssant is a hobby project to implement a complete chess implementation and
engine in Python with a simple, straightforward API.  The public API is thusly
documented and implemented that it should be relatively simple to swap out
individual components with different implementations.

The focus is on keeping the API clean and flexible.  This may come at the cost
of performance, but if performance were the primary goal, perhaps it mightn't
have been a good idea to use Python in the first place.

The goal is to keep the project thoroughly tested with unit and integration
tests.  More of the latter than the former.


Install
=======

Installing En Pyssant should be a simple matter of executing the following
command::

  pip3 install --user en-pyssant


Usage
=====

Longum iter est per praecepta, breve et efficax per exempla---It’s a long way by
the rules, but short and efficient with examples.

First, import everything::

  >>> import threading
  >>> import time
  >>> from en_pyssant import *
  >>> from en_pyssant.engine import *
  >>> from en_pyssant.rules import *
  >>> # Technically you should never star-import, but it makes
  >>> # the examples easier.

En Pyssant has a few core data types::

  >>> white_pawn = Piece(Type.PAWN, Side.WHITE)
  >>> white_pawn
  Piece(type=<Type.PAWN: 'p'>, side=<Side.WHITE: 1>)
  >>> a1 = Square('a1')
  >>> a1.up().up()
  'a3'

You can easily create a starting board, or import any other board layout from
partial `Forsyth-Edwards Notation (FEN)
<https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation>`_::

  >>> board = DictBoard()
  >>> board
  rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR
  >>> DictBoard.from_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR')
  rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR
  >>> board[a1]
  Piece(type=<Type.ROOK: 'r'>, side=<Side.WHITE: 1>)
  >>> print(board['a3'])
  None
  >>> board.put('a3', white_pawn)
  rnbqkbnr/pppppppp/8/8/8/P7/PPPPPPPP/RNBQKBNR

You can also easily create a chess position in the same way, which is a complete
state of the chess game (i.e., the board and some extra information).  Find
below the diverse ways of creating the starting position::

  >>> position = Position()
  >>> position
  rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
  >>> Position(
  ...     board=DictBoard(),
  ...     side_to_play=Side.WHITE,
  ...     castling=Castling(
  ...         CastlingSide(True, True),
  ...         CastlingSide(True, True)),
  ...     en_passant_target=None,
  ...     half_move_clock=0,
  ...     move_count=1)
  ...
  rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
  >>> Position.from_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
  rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
  >>> position.move_count
  1

If Forsyth-Edwards Notation is too terse, you can easily get some pretty output
instead::

  >>> print(board.pretty())
    A B C D E F G H
  8 r n b q k b n r
  7 p p p p p p p p
  6 . . . . . . . .
  5 . . . . . . . .
  4 . . . . . . . .
  3 . . . . . . . .
  2 P P P P P P P P
  1 R N B Q K B N R
  >>> print(position.pretty())
    A B C D E F G H
  8 r n b q k b n r
  7 p p p p p p p p
  6 . . . . . . . .
  5 . . . . . . . .
  4 . . . . . . . .
  3 . . . . . . . .
  2 P P P P P P P P
  1 R N B Q K B N R
  <BLANKLINE>
  FEN: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1

Boards and positions are immutable data containers.  Whenever you would normally
change the state of a position, you simply create a new one and discard the old
one.  Though typically you let En Pyssant create the new position for you by
performing moves upon the board::

  >>> move = Move('a2', 'a3')
  >>> new_position = do_move(position, move)
  >>> new_position
  rnbqkbnr/pppppppp/8/8/8/P7/1PPPPPPP/RNBQKBNR b KQkq - 0 1
  >>> print(new_position.board.pretty())
    A B C D E F G H
  8 r n b q k b n r
  7 p p p p p p p p
  6 . . . . . . . .
  5 . . . . . . . .
  4 . . . . . . . .
  3 P . . . . . . .
  2 . P P P P P P P
  1 R N B Q K B N R

You can also use `Standard Algebraic Notation
<https://en.wikipedia.org/wiki/Algebraic_notation_(chess)>`_ to do moves.  You
are allowed to be a little creative in creating your SAN strings.  The parser is
fairly tolerant and permissive::

  >>> san = 'a3'  # or 'Pa3', or 'a2a3', or 'Pa2-a3'
  >>> assert new_position == do_move(position, san)

You can easily obtain a list of all moves or perform other game logic upon the
position.  There are 20 legal moves at the start of any chess game::

  >>> assert len(list(moves(position))) == 20
  >>> is_check(position)
  False
  >>> is_checkmate(position)
  False

You are also provided with a simple wrapper that keeps track of the current
position and the history of the game for you.  Below a simple game of `Fool's
Mate <https://en.wikipedia.org/wiki/Fool%27s_mate>`_::

  >>> game = Game()
  >>> game.position
  rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
  >>> game.do_move('f3')
  rnbqkbnr/pppppppp/8/8/8/5P2/PPPPP1PP/RNBQKBNR b KQkq - 0 1
  >>> game.do_move('e5')
  rnbqkbnr/pppp1ppp/8/4p3/8/5P2/PPPPP1PP/RNBQKBNR w KQkq e6 0 2
  >>> game.do_move('g4')
  rnbqkbnr/pppp1ppp/8/4p3/6P1/5P2/PPPPP2P/RNBQKBNR b KQkq g3 0 2
  >>> game.do_move('Qh4#')
  rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3
  >>> print(game.position.board.pretty())
    A B C D E F G H
  8 r n b . k b n r
  7 p p p p . p p p
  6 . . . . . . . .
  5 . . . . p . . .
  4 . . . . . . P q
  3 . . . . . P . .
  2 P P P P P . . P
  1 R N B Q K B N R
  >>> game.is_gameover()
  <Gameover.CHECKMATE: 1>
  >>> game.winner()
  <Side.BLACK: 0>
  >>> assert len(game.history) == 4

You can also export (and import) the game as `Portable Game Notation
<https://en.wikipedia.org/wiki/Portable_Game_Notation>`_::

  >>> pgn = game.pgn()
  >>> print(pgn)
  [Result "0-1"]
  <BLANKLINE>
  1. f3 e5 2. g4 Qh4# 0-1
  >>> new_game = Game.from_pgn(pgn)
  >>> new_game.winner()
  <Side.BLACK: 0>

The simplest way to play a complete game of chess::

  >>> game = Game()
  >>> while not game.is_gameover():
  ...     new_position = game.do_move(next(game.moves()))
  ...
  >>> assert game.is_gameover()

The most interesting thing, however, is to let the computer play for you.  Below
a simple example of utilising the engine::

  >>> engine = MCTSEngine()
  >>> # Let the engine do its thinking magic for a few seconds.
  >>> engine.think_for(3)
  True
  >>> engine.is_thinking()  # Thinking has just finished.
  False
  >>> best_move = engine.best_move()
  >>> position = engine.do_move(best_move)
  >>> assert position == engine.position
  >>>
  >>> # You can also let the engine think in a subthread.
  >>> thread = threading.Thread(target=engine.think_for, args=(0,))
  >>> thread.start()
  >>> time.sleep(0.2)
  >>> # The engine is now thinking infinitely in another thread.
  >>> engine.is_thinking()
  True
  >>> # You can query the object while the engine is calculating.
  >>> new_best_move = engine.best_move()
  >>> assert best_move != new_best_move
  >>> _ = engine.do_move(new_best_move)
  >>> engine.is_thinking()
  True
  >>> # Cannot think again while thinking.
  >>> engine.think_for(0)
  False
  >>> engine.stop_thinking()
  >>> thread.join()


Maintainer
==========

Carmen Bianca Bakker <carmen@carmenbianca.eu>.


Contribute
==========

Any merge requests or suggestions are welcome at
`<https://gitlab.com/carmenbianca/en-pyssant>`_ or via e-mail to one of the
maintainers.

Starting local development is very simple.  Just execute the following
commands::

  git clone git@gitlab.com:carmenbianca/en-pyssant.git
  cd en-pyssant/
  python3 -mvenv venv
  source venv/bin/activate
  make develop

You need to run ``make develop`` at least once to set up the virtualenv.

Next, run ``make help`` to see the available interactions.

When submitting a merge request, please make sure that all the tests pass.  If
possible, also provide additional tests to accompany the changed functionality.
Always add a change log entry, and make sure to add yourself to AUTHORS.rst.

You are required to add a copyright notice to the files you have changed.  It is
assumed that you license the changes in your merge request under the licence
specified in the header of those files.  If not, please be specific.  See
`<https://reuse.software/>`_ for more information on licensing.


Licence
=======

GNU General Public License version 3 or later.


..
  Copyright (C) 2017-2018  Carmen Bianca Bakker <carmen@carmenbianca.eu>

  This file is part of En Pyssant, available from its original location:
  <https://gitlab.com/carmenbianca/en-pyssant>.

  This work is licensed under the Creative Commons Attribution-ShareAlike
  4.0 International License. To view a copy of this license, visit
  <http://creativecommons.org/licenses/by-sa/4.0/>.

  SPDX-License-Identifier: CC-BY-SA-4.0

==========
Change log
==========

This change log follows the `Keep a Changelog <http://keepachangelog.com/>`_
spec.  Every release contains the following sections:

- *Added* for new features.

- *Changed* for changes in existing functionality.

- *Deprecated* for soon-to-be removed features.

- *Removed* for now removed features.

- *Fixed* for any bug fixes.

- *Security* in case of vulnerabilities.

The versions follow `semantic versioning <https://semver.org>`_.


0.2.0 (2018-07-04)
==================

Added
-----

- ``moves_single`` now complements ``moves`` as a function that generates all
  legal moves for a single origin square.

- ``BitBoard`` and ``TupleBoard`` added.

- Added ``Piece.from_str``.

- Added ``do_move_with_history``, which returns a ``(Position, HistoryRecord)``
  tuple.

- ``ParallelEngine`` (base class) and ``MCTSEngine`` added.  There is now a
  fully functional engine that isn't ``RandomEngine``.

- Added more methods to ``Engine``.

Changed
-------

- ``CastlingAvailability`` has been replaced with ``CastlingSide``.  Positions
  now no longer contain a dictionary of ``CastlingAvailability`` objects, but a
  ``Castling`` object.  For example:

  ``castling = {Side.WHITE: CastlingAvailability(True, True), Side.BLACK:
  CastlingAvailability(True, True)``

  is now

  ``castling = Castling(CastlingSide(True, True), CastlingSide(True, True))``

  In effect, this makes ``Position`` objects hashable and entirely immutable.

  The new ``Castling`` class still permits key lookup.  So
  ``castling[Side.WHITE].kingside`` remains valid.

- ``Square.in_bounds`` and ``Square.goto`` now also accept ``(int, int)`` tuples
  in lieue of ``Direction`` objects.  This is more performant because tuples
  hash quicker.

- ``Board.all_pieces`` now starts at a1 and goes to h8.

- Changed some code around to be more
  ``threading``/``multiprocessing``-friendly.

- Changed the public interface of ``Engine``.  Specifically:

  + ``Engine.__init__`` now takes a position, history and ruleset instead of a
    game.

  + ``Engine.think_for`` returns True.  If another thread is already thinking,
    it returns False and does not begin thinking.

  + ``Engine.stop_thinking`` takes an additional ``blocking`` keyword argument.


0.1.7 (2018-04-02)
==================

Changed
-------

- Re-release to fix the documentation.  No changes in the codebase.


0.1.5 (2018-03-13)
==================

- First release.

- Contains almost all functionality except the chess engine itself.  You can
  play chess, basically.  Just not against a hyper-intelligent computer.


