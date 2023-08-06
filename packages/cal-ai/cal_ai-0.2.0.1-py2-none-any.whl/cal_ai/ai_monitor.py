#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import logging
from datetime import datetime
from pytz import timezone
import pytz
from .cal_crawler import CalCrawler
from .healthy_checker import HealthyChecker


ai_logger = logging.getLogger('AI_Monitor')
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
ai_logger.addHandler(handler)


class AIMonitor(object):
    @staticmethod
    def get_current_pst_timestamp():
        utc_date = datetime.now(tz=pytz.utc)
        pst_date = utc_date.astimezone(timezone('US/Pacific'))
        return int(time.mktime(pst_date.timetuple()))

    @staticmethod
    def abnormal_check_last_24hour(host_name):
        current_timestamp = int(time.time())
        last_24_hour_timestamp = current_timestamp - 24 * 60 * 60
        AIMonitor.monitor_live_box(host_name, last_24_hour_timestamp, current_timestamp)

    @staticmethod
    def monitor_live_box(host_name, start_time, end_time, pool_name="riskunifiedcomputeserv"):
        cal_log_data = CalCrawler.crawl_data(host_name, start_time, end_time, pool_name=pool_name)
        check_result = HealthyChecker.abnormal_check_data(cal_log_data)
        print("%s [%s - %s] %s\n\n" % (host_name, HealthyChecker.convert_unix_time(start_time), HealthyChecker.convert_unix_time(end_time), HealthyChecker.assessment_on_result(check_result)))

    @staticmethod
    def abnormal_check_last_7day(host_name):
        current_timestamp = int(time.time())
        for i in range(7):
            end = current_timestamp - i * 24 * 60 * 60
            start = current_timestamp - (i + 1) * 24 * 60 * 60
            AIMonitor.monitor_live_box(host_name, start, end)

    @staticmethod
    def onebox_evaluate(box_list, last_x_hours, pool_name):
        current_timestamp = int(time.time())
        last_x_hours_timestamp = current_timestamp - last_x_hours * 60 * 60
        for host_name in box_list:
            AIMonitor.monitor_live_box(host_name, last_x_hours_timestamp, current_timestamp, pool_name)


if __name__ == "__main__":
    # bad_box = ["slcrisktxncomputeserv2132a", "slcrisktxncomputeserv3750b"]
    # onebox_list = ["dcg11risktxncomputeserv5579", "dcg11risktxncomputeserv6924", "dcg12risktxncomputeserv1111", "dcg12risktxncomputeserv9937", "dcg13risktxncomputeserv3716", "dcg13risktxncomputeserv9779"]
    AIMonitor.onebox_evaluate(["dcg12riskunifiedcomputeserv2040"], 18)


