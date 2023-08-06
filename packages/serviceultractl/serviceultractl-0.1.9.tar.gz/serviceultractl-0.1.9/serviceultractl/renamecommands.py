# -*- coding: utf-8 -*-
from .utils.parse_utils import args
from .v3_0.file import FileDispatch as File


class RenameCommands(object):
    @args("--path", dest="path", required=True, help="full path of file")
    @args("--newpath", dest="newpath", required=True, help="full path of renamed file")
    def file(self, auth, path, newpath):
        """copy files"""
        File.rename(auth, path, newpath)

