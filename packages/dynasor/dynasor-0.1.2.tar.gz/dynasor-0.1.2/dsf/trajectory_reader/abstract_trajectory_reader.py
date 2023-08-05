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

from abc import abstractmethod, ABCMeta


class abstract_trajectory_reader:
    __metaclass__ = ABCMeta

    """Provides a way to iterate through a molecular dynamics (MD) trajectory
    file.

    Each frame/time-step is returned as a trajectory_frame.
    """

    @classmethod
    @abstractmethod
    def available(cls):
        """ Returns True if this reader available on a particular system. """
        pass

    @abstractmethod
    def __iter__(self):
        """ Iterates through the trajectory file, frame by frame. """
        pass

    @abstractmethod
    def __next__(self):
        """ Gets next trajectory frame. """
        pass

    @abstractmethod
    def close(self):
        """ Closes down, release resources etc. """
        pass
