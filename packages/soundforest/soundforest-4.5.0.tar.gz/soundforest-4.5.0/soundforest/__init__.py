# coding=utf-8
"""Soundforest audio tree management tools

Audio file tree processing classes

"""

import os
import sys
import unicodedata


__version__ = '4.5.0'


class SoundforestError(Exception):
    pass


class TreeError(Exception):
    pass


def normalized(path, normalization='NFC'):
    """
    Return given path value as normalized unicode string on OS/X,
    on other platform return the original string as unicode
    """
    if sys.platform != 'darwin':
        return type(path) == str and path or str(path, 'utf-8')
    if not isinstance(path, str):
        path = str(path, 'utf-8')
    return unicodedata.normalize(normalization, path)


class path_string(str):
    def __new__(self, path):
        return str.__new__(self, normalized(path))

    @property
    def exists(self):
        if os.path.isdir(self) or os.path.isfile(self):
            return True
        return False

    @property
    def isdir(self):
        return os.path.isdir(self)

    @property
    def isfile(self):
        return os.path.isfile(self)

    @property
    def no_ext(self):
        return os.path.splitext(self)[0]

    @property
    def directory(self):
        return os.path.dirname(self)

    @property
    def filename(self):
        return os.path.basename(self)

    @property
    def extension(self):
        return os.path.splitext(self)[1][1:]

    def relative_path(self, path):
        """Return relative path

        Return item's relative path.
        """
        if path[:len(self)] != self:
            raise ValueError('{} path is not relative to {}'.format(path, self))
        return path[len(self):].lstrip('/')


class CommandPathCache(list):

    """
    Class to represent commands on user's search path.
    """
    def __init__(self):
        self.paths = None
        self.update()

    def update(self):
        """
        Updates the commands available on user's PATH
        """
        self.paths = []
        del self[0:len(self)]

        for path in os.getenv('PATH').split(os.pathsep):
            if not self.paths.count(path):
                self.paths.append(path)

        for path in self.paths:
            if not os.path.isdir(path):
                continue

            for cmd in [os.path.join(path, f) for f in os.listdir(path)]:
                if os.path.isdir(cmd) or not os.access(cmd, os.X_OK):
                    continue

                self.append(cmd)

    def versions(self, name):
        """
        Returns all commands with given name on path, ordered by PATH search
        order.
        """
        if not len(self):
            self.update()

        return [cmd for cmd in self if os.path.basename(cmd) == name]

    def which(self, name):
        """
        Return first matching path to command given with name, or None if
        command is not on path
        """
        versions = self.versions(name)
        if versions:
            return versions[0]
        else:
            return None
