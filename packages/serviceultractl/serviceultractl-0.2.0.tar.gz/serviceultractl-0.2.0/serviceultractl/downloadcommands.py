# -*- coding: utf-8 -*-
from .utils.parse_utils import args
from .v3_0.file import FileDispatch as File


class DownloadCommands(object):
    @args("--path", dest="path", required=True, help="full path of file")
    def file(self, auth, path):
        """download file"""
        File.download(auth, path)
