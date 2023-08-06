#!/usr/bin/python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import time
from .cal_crawler import CalCrawler
from .common_utils import CommonUtils
from .healthy_checker import MachineInfo


class CalPlot(object):
    @staticmethod
    def __plot(history_data):
        fig = plt.figure(figsize=(25, 25))
        sub_fig_num = len(history_data)
        base_value = sub_fig_num * 100 + 10 + sub_fig_num
        display_order = [MachineInfo.TPM, MachineInfo.TRANS_TIME, MachineInfo.CPU_USAGE, MachineInfo.MEMORY_USAGE,
                         MachineInfo.EPM, MachineInfo.JVM, MachineInfo.GC_COUNT, MachineInfo.CAL_STATUS_1,
                         MachineInfo.CAL_STATUS_2]
        for machine_info_type in display_order[::-1]:
            if machine_info_type in history_data:
                data_list = history_data[machine_info_type]
                ax = fig.add_subplot(base_value)
                base_value -= 1
                x, y = zip(*data_list)
                x = [datetime.datetime.fromtimestamp(ts) for ts in x]
                ax.plot(x, y)
                ax.set_title(machine_info_type.name)
                plt.subplots_adjust(hspace=0.3)
                plt.autoscale()
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
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



