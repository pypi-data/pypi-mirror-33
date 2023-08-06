# -*- coding: utf-8 -*-
import os


def get_ttyclient_uri():
    ttyclient_uri = os.getenv("ADMINISTRATION_ENV_TTYCLIENT_URI", "http://su.huayun.com/resserverpub/bin/bin.tar")
    return ttyclient_uri

