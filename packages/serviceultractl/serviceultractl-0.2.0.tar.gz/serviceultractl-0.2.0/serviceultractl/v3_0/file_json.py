# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from .base.file import File as File_base


class File(object):
    @staticmethod
    def list(auth, path):
        try:
            data = File_base._list(auth, path)
            files = data.get("result", [])
            print json.dumps(dict(files=files), indent=4, ensure_ascii=False)
        except Exception as e:
            raise