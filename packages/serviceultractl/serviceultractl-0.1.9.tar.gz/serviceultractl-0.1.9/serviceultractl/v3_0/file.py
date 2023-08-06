# -*- coding: utf-8 -*-
from .file_ch import File as File_ch
from .file_en import File as File_en
from .file_json import File as File_json
from .base.file import File as File_base


class FileDispatch(object):
    @staticmethod
    def list(auth, path, format_json):
        if format_json:
            File_json.list(auth, path)
        else:
            if auth.language == "en":
                File_en.list(auth, path)
            else:
                File_ch.list(auth, path)

    @staticmethod
    def upload(auth, dir, files):
        File_base._upload(auth, dir, files)

    @staticmethod
    def download(auth, path):
        File_base._download(auth, path)

    @staticmethod
    def delete_batch(auth, paths):
        File_base._delete_batch(auth, paths)

    @staticmethod
    def move_batch(auth, paths, newdir):
        File_base._move_batch(auth, paths, newdir)

    @staticmethod
    def copy_batch(auth, paths, newdir):
        File_base._copy_batch(auth, paths, newdir)

    @staticmethod
    def rename(auth, path, newpath):
        File_base._rename(auth, path, newpath)
