# -*- coding: utf-8 -*-
from .utils.parse_utils import args
from .v3_0.file import FileDispatch as File


class UploadCommands(object):
    @args("--dir", dest="dir", default="/", help="valid dir")
    @args("--file", dest="files", required=True, nargs="+", help="")
    def file(self, auth, dir, files):
        """upload file"""
        File.upload(auth, dir, files)
