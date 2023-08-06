# -*- coding: utf-8 -*-
import collections
from ..utils.common_utils import print_table, obj_replace_time_field, status_format
from .base.file import File as File_base


class File(object):
    @staticmethod
    def list(auth, path):
        try:
            data = File_base._list(auth, path)
            header = collections.OrderedDict()
            header["name"] = "Name"
            header["path"] = "Path"
            header["size"] = "Size(kB)"
            header["type"] = "Type"
            header["date"] = "Date"
            files_info = []
            files = data.get("result", [])
            for file in files:
                file["size"] = round(file.get("size", 0) / 1024.0, 1)
                file_info = [file.get(key, "") for key in header]
                files_info.append(file_info)
            print_table(header.values(), files_info, auth.encoding)
        except Exception as e:
            raise