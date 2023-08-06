#!/usr/bin/python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import time
from .cal_crawler import CalCrawler


class PlotUtil(object):
    @staticmethod
    def plot_show(datas):
        fig = plt.figure(figsize=(15, 8))
        pic_num = len(datas)
        base_value = pic_num * 100 + 10 + pic_num
        for data_type, data_list in datas.items():
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
    def plot_host(host_name, start_time_str, end_time_str=None, time_str_format="%Y-%m-%d %H:%M:%S"):
        start_time = PlotUtil.date_str_to_timestamp(start_time_str, time_str_format)

        if end_time_str is None:
            end_time = int(time.time())
        else:
            end_time = PlotUtil.date_str_to_timestamp(end_time_str, time_str_format)
        result = CalCrawler.crawl_data(host_name, start_time, end_time)
        plot_datas = {}
        for data_type, data_list in result.items():
            if len(data_list) > 0 and 'DataPoints' in data_list[0] and len(data_list[0]['DataPoints']) > 0:
                plot_datas[data_type] = data_list[0]['DataPoints']
        PlotUtil.plot_show(plot_datas)

    @staticmethod
    def date_str_to_timestamp(date_str, format):
        return int(time.mktime(datetime.datetime.strptime(date_str, format).timetuple()))


if __name__ == "__main__":
    PlotUtil.plot_host("dcg12risktxncomputeserv6950", "2018-07-09 10:12:12", "2018-07-10 10:12:12")



