# -*- coding: utf-8 -*-
from .utils.parse_utils import args
from .v3_0.file import FileDispatch as File


class CopyCommands(object):
    @args("--path", dest="paths", nargs="+", required=True, help="full path of file")
    @args("--newdir", dest="newdir", required=True, help="valid dir")
    def file(self, auth, paths, newdir):
        """copy files"""
        File.copy_batch(auth, paths, newdir)

