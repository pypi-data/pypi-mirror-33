#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import logging
import pytz
from datetime import datetime


class CommonUtils(object):
    @staticmethod
    def get_current_pst_timestamp():
        utc_date = datetime.now(tz=pytz.utc)
        pst_date = utc_date.astimezone(pytz.timezone('US/Pacific'))
        return int(time.mktime(pst_date.timetuple()))

    @staticmethod
    def date_str_to_timestamp(date_str, format="%Y-%m-%d %H:%M:%S"):
        return int(time.mktime(datetime.strptime(date_str, format).timetuple()))

    @staticmethod
    def timestamp_to_data_str(ts, format="%Y-%m-%d %H:%M:%S"):
        current_date = datetime.fromtimestamp(ts)
        return current_date.strftime(format)

    @staticmethod
    def get_column_name_from_host_name(host_name):
        dcg_list = ["dcg01", "dcg02", "dcg11", "dcg12", "dcg13"]
        for dcg in dcg_list:
            if host_name.startswith(dcg):
                return dcg
        if host_name.startswith("slc"):
            if host_name.endswith("a"):
                return "slca"
            elif host_name.endswith("b"):
                return "slcb"
        logging.warn("host %s can not be identitied, class it to phx" % host_name)
        return "phx"


if __name__ == '__main__':
    print("Current time: %s" % CommonUtils.timestamp_to_data_str(int(time.time())))
    print("Current PST time: %s" % CommonUtils.timestamp_to_data_str(CommonUtils.get_current_pst_timestamp()))
    __host_name = "dcg13risktxncomputeserv6056"
    print("Pool name for %s is %s" % (__host_name, CommonUtils.get_column_name_from_host_name(__host_name)))


