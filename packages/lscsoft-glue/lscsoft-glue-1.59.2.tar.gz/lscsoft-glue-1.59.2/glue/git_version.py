# This file is part of the Grid LSC User Environment (GLUE)
#
# GLUE is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

version = '1.59.2'

# git information
id = '06238141fefc6b6eeeee7a39b386fa5c9c2664e7'
date = '2018-06-19 16:26:40 +0000'
branch = 'glue-1-59-branch'
tag = 'glue-release-1.59.2'
author = 'Ryan Fisher <ryan.fisher@ligo.org>'
builder = 'Ryan Fisher <ryan.fisher@ligo.org>'
committer = 'Ryan Fisher <ryan.fisher@ligo.org>'
status = 'CLEAN: All modifications committed'
verbose_msg = """Branch: glue-1-59-branch
Tag: glue-release-1.59.2
Id: 06238141fefc6b6eeeee7a39b386fa5c9c2664e7

Builder: Ryan Fisher <ryan.fisher@ligo.org>
Build date: 2018-06-19 16:53:21 +0000
Repository status: CLEAN: All modifications committed"""

import warnings

class VersionMismatchError(ValueError):
    pass

def check_match(foreign_id, onmismatch="raise"):
    """
    If foreign_id != id, perform an action specified by the onmismatch
    kwarg. This can be useful for validating input files.

    onmismatch actions:
      "raise": raise a VersionMismatchError, stating both versions involved
      "warn": emit a warning, stating both versions involved
    """
    if onmismatch not in ("raise", "warn"):
        raise ValueError(onmismatch + " is an unrecognized value of onmismatch")
    if foreign_id == '06238141fefc6b6eeeee7a39b386fa5c9c2664e7':
        return
    msg = "Program id (06238141fefc6b6eeeee7a39b386fa5c9c2664e7 does not match given id (%s)." % foreign_id
    if onmismatch == "raise":
        raise VersionMismatchError(msg)

    # in the backtrace, show calling code
    warnings.warn(msg, UserWarning)


