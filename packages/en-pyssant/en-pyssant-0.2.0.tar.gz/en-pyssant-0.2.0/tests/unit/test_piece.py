# -*- coding: utf-8 -*-
#
# Copyright (C) 2018  Carmen Bianca Bakker <carmen@carmenbianca.eu>
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

"""Unit tests for Piece."""

from en_pyssant import Piece, Side, Type


def test_from_str_all_types():
    """:meth:`Piece.from_str` can interpret all types."""
    for type_ in Type:
        piece = Piece.from_str(type_.value)
        assert piece.type == type_


def test_from_str_white():
    """A capital letter is white."""
    piece = Piece.from_str('P')
    assert piece.side == Side.WHITE


def test_from_str_black():
    """A lower-case letter is black."""
    piece = Piece.from_str('p')
    assert piece.side == Side.BLACK


def test_from_str_interpret_self():
    """The output of :meth:`Piece.__str__` can be fed straight into
    :meth:`Piece.from_str` and result in the same object.
    """
    for type_ in Type:
        for side in Side:
            piece = Piece(type_, side)
            assert Piece.from_str(str(piece)) == piece
