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
            header["name"] = u"名称"
            header["path"] = u"路径"
            header["size"] = u"大小(kB)"
            header["type"] = u"类型"
            header["date"] = u"创建时间"
            files_info = []
            files = data.get("result", [])
            for file in files:
                file["size"] = round(file.get("size", 0)/1024.0, 2)
                file_info = [file.get(key, "") for key in header]
                files_info.append(file_info)
            print_table(header.values(), files_info, auth.encoding)
        except Exception as e:
            raise