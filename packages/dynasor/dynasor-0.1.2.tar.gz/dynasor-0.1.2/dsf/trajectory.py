
# Copyright (C) 2011 Mattias Slabanja <slabanja@chalmers.se>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

__all__ = ['get_itraj', 'iwindow']

import logging
import sys

from collections import deque
from itertools import islice
from os.path import isfile

from .trajectory_reader import available_readers

logger = logging.getLogger('dynasor')


def get_itraj(filename: str, step: int=1, max_frames: int=0,
              readers=available_readers):
    """Return a dynasor-style trajectory iterator

    Simple wrapper for the trajectory_reader-classes.

    Parameters
    ----------
    filename : str
        name of input file
    step : int
        step to access (1 by default = every single frame); must be > 0.
    max_frames : int
        maximum number of frames to read (0 by default = no limit);
        must be >= 0.

    Returns
    -------
    Each iterator step consists of a dictionary.


    .. code-block:: python

        {
         'index' : trajectory frame index (1, 2, 3, ...),
         'box'   : simulation box as 3 row vectors (nm),
         'N'     : number of atoms,
         'x'     : particle positions as 3xN array (nm),
         'v'     : (*) particle velocities as 3xN array (nm/ps),
         'time'  : (*) simulation time (ps),
        }

    ``(*)`` may not be available, depends on reader and trajectory file format.
    """

    assert step > 0
    assert max_frames >= 0
    if max_frames == 0:
        max_frames = sys.maxint
    elif step > 1:
        max_frames = max_frames * step

    if not isfile(filename):
        raise IOError('File {} does not exist'.format(filename))

    for reader in readers:
        # Simply pick the first reader that seems to work
        if reader.available():
            reader_name = reader.__name__
            try:
                logger.debug('Trying trajectory_reader %s' % reader_name)
                return islice(reader(filename), 0, max_frames, step)
            except Exception:
                logger.debug('Trying trajectory_reader {}'
                             ' failed to open file {}'
                             .format(reader_name, filename))

    raise IOError('Failed to open trajectory file {}'.format(filename))


def consume(iterator, n):
    """ Advance the iterator by n steps. If n is none, consume entirely. """
    # From the python.org
    if n is None:
        deque(iterator, maxlen=0)
    else:
        next(islice(iterator, n, n), None)


class iwindow:
    """Sliding window iterator.

    Returns consecutive windows (a windows is represented as a list
    of objects), created from an input iterator.

    Parameters
    ----------
    width : int
        length of window
    stride : int
        distance between the start of two consecutive window frames
    element_processor : function
        enables processing each non-discarded object; useful if ``stride >
        width`` and ``map_item`` is expensive (as compared to directly passing
        ``map(fun, itraj)`` as ``itraj``); if ``stride < width``, you could as
        well directly pass ``map(fun, itraj)``.
    """

    def __init__(self, itraj, width=2, stride=1, element_processor=None):

        self._raw_it = itraj
        if element_processor:
            self._it = map(element_processor, self._raw_it)
        else:
            self._it = self._raw_it
        assert(stride >= 1)
        assert(width >= 1)
        self.width = width
        self.stride = stride
        self._window = None

    def __iter__(self):
        return self

    def next(self):
        """ Returns next element in sequence. """
        if self._window is None:
            self._window = deque(islice(self._it, self.width), self.width)
        else:
            if self.stride >= self.width:
                self._window.clear()
                consume(self._raw_it, self.stride - self.width)
            else:
                for _ in range(min((self.stride, len(self._window)))):
                    self._window.popleft()
            for f in islice(self._it, min((self.stride, self.width))):
                self._window.append(f)

        if len(self._window) == 0:
            raise StopIteration

        return list(self._window)
