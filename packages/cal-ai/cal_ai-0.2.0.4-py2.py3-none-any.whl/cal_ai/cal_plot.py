#!/usr/bin/python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import time
from .cal_crawler import CalCrawler
from .common_utils import CommonUtils


class CalPlot(object):
    @staticmethod
    def __plot(history_data):
        fig = plt.figure(figsize=(15, 8))
        sub_fig_num = len(history_data)
        base_value = sub_fig_num * 100 + 10 + sub_fig_num
        for data_type, data_list in history_data.items():
            ax = fig.add_subplot(base_value)
            base_value -= 1
            x, y = zip(*data_list)
            x = [datetime.datetime.fromtimestamp(ts) for ts in x]
            ax.plot(x, y)
            ax.set_title(data_type.name)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y %H:%M'))
        plt.gca().xaxis.set_major_locator(mdates.HourLocator())
        plt.gcf().autofmt_xdate()
        plt.show()

    @staticmethod
    def show_instance_history(host_name, start_time_str, end_time_str=None, time_str_format="%Y-%m-%d %H:%M:%S"):
        if end_time_str is None:
            end_time = int(time.time())
        else:
            end_time = CommonUtils.date_str_to_timestamp(end_time_str, time_str_format)
        start_time = CommonUtils.date_str_to_timestamp(start_time_str, time_str_format)

        result = CalCrawler.crawl_data(host_name, start_time, end_time)
        history_data = {}
        for data_type, data_list in result.items():
            if len(data_list) > 0 and 'DataPoints' in data_list[0] and len(data_list[0]['DataPoints']) > 0:
                history_data[data_type] = data_list[0]['DataPoints']
        CalPlot.__plot(history_data)


if __name__ == "__main__":
    CalPlot.show_instance_history("dcg12risktxncomputeserv6950", "2018-07-09 10:12:12", "2018-07-10 10:12:12")



