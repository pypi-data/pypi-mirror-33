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

from .lammpstrj_trajectory_reader import lammpstrj_trajectory_reader
from .molfile_trajectory_reader import molfile_trajectory_reader
from .xtc_trajectory_reader import xtc_trajectory_reader

available_readers = []

for reader in [lammpstrj_trajectory_reader,
               molfile_trajectory_reader,
               xtc_trajectory_reader]:
    if reader.available():
        available_readers.append(reader)
