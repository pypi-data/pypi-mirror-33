#!/usr/bin/python
# -*- coding: utf-8 -*

# file_size.py file is part of slpkg.

# Copyright 2014-2018 Dimitris Zlatanidis <d.zlatanidis@gmail.com>
# All rights reserved.

# Slpkg is a user-friendly package manager for Slackware installations

# https://gitlab.com/dslackw/slpkg

# Slpkg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import os
import urllib2


class FileSize(object):
    """Check local or remote file size
    """
    def __init__(self, registry):
        self.registry = registry

    def server(self):
        """Returns the size of remote files
        """
        try:
            tar = urllib2.urlopen(self.registry)
            meta = tar.info()
            return int(meta.getheaders("Content-Length")[0])
        except (urllib2.URLError, IndexError):
            return " "

    def local(self):
        """Returns the size of local files
        """
        return os.path.getsize(self.registry)
