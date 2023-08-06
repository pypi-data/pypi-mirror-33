# -*- coding: utf-8 -*-
import time
import datetime
from prettytable import PrettyTable, FRAME, ALL, NONE
import sys
import tarfile


def get_item_bins(item_list, bin_num_max=1):
    assert item_list and isinstance(item_list, list)
    item_bin_list = []
    bin_num = min(len(item_list), bin_num_max)
    for _ in range(0, bin_num):
        item_bin_list.append([])
    for index in range(len(item_list)):
        item_bin_index = index % bin_num
        item_bin_list[item_bin_index].append(item_list[index])
    return item_bin_list


def utc2local(utc_st):
    """UTC时间转本地时间（+8:00）"""
    now_stamp = time.time()
    local_time = datetime.datetime.fromtimestamp(now_stamp)
    utc_time = datetime.datetime.utcfromtimestamp(now_stamp)
    offset = local_time - utc_time
    local_st = utc_st + offset
    return local_st


def local2utc(local_st):
    """本地时间转UTC时间（-8:00）"""
    time_struct = time.mktime(local_st.timetuple())
    utc_st = datetime.datetime.utcfromtimestamp(time_struct)
    return utc_st


def print_table(header, data_list, encoding):
    try:
        # print sys.stdout.encoding
        x = PrettyTable(list(header), border=False, encoding=encoding)
        # x = PrettyTable(list(header), border=False, encoding=sys.stdout.encoding)
        x.padding_width = 1
        x.hrules = ALL
        for data in data_list:
            x.add_row(list(data))
        print x
    except Exception as e:
        print e.message


def timestamp_to_datetime(int_time):
    timeStamp = int(str(int_time)[:10])
    timeArray = time.localtime(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime


def obj_replace_time_field(oobj, field_name_list):
    assert isinstance(oobj, dict)
    for field_name in field_name_list:
        oobj_time = oobj.get(field_name, None)
        if oobj_time and (isinstance(oobj_time, int) or isinstance(oobj_time, long) or oobj_time.isdigit()):
            oobj_datetime = timestamp_to_datetime(oobj_time)
            oobj[field_name] = oobj_datetime
    return oobj


def status_format(lifecycle, lifecycle_conf, status_summary, status_summary_conf, running_status, running_status_conf, type=None):
    assert isinstance(lifecycle_conf, dict)
    assert isinstance(status_summary_conf, dict)
    assert isinstance(running_status_conf, dict)
    if type == "task":
        status = status_format_task(lifecycle, lifecycle_conf, running_status, running_status_conf)
        return status
    if type == "application":
        status = status_format_app(status_summary, status_summary_conf, running_status, running_status_conf)
        return status
    _lifecycle = lifecycle_conf.get(lifecycle, "")
    _status_summary = status_summary_conf.get(status_summary, "")
    _running_status = running_status_conf.get(running_status, "")
    if lifecycle == "running":
        if status_summary == "failed_deployed":
            status = _status_summary
        else:
            status = u"{}[{}]".format(_status_summary, _running_status)
    else:
        status = _lifecycle
    return status


def status_format_app(status_summary, status_summary_conf, running_status, running_status_conf):
    assert isinstance(status_summary_conf, dict)
    assert isinstance(running_status_conf, dict)
    _status_summary = status_summary_conf.get(status_summary, "")
    _running_status = running_status_conf.get(running_status, "")
    if status_summary == "successfully_deployed":
        status = u"{}[{}]".format(_status_summary, _running_status)
    else:
        status = _status_summary
    return status


def status_format_task(lifecycle, lifecycle_conf, running_status, running_status_conf):
    assert isinstance(lifecycle_conf, dict)
    assert isinstance(running_status_conf, dict)
    _lifecycle = lifecycle_conf.get(lifecycle, "")
    _running_status = running_status_conf.get(running_status, "")
    if lifecycle == "scheduling":
        status = u"{}[{}]".format(_lifecycle, _running_status)
    else:
        status = _lifecycle
    return status


def extract(tar_path, target_path):
    try:
        tar = tarfile.open(tar_path, "r")
        tar.extractall(target_path)
        tar.close()
    except Exception, e:
        raise Exception, e





