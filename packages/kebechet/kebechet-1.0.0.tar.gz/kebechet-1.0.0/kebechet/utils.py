#!/usr/bin/env python3
# Kebechet
# Copyright(C) 2018 Fridolin Pokorny
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Just some utility methods."""


import os
from contextlib import contextmanager


@contextmanager
def cwd(path: str):
    """Change working directory in a push-pop manner with context manager."""
    previous_dir = os.getcwd()
    try:
        os.chdir(path)
        yield previous_dir
    finally:
        os.chdir(previous_dir)
