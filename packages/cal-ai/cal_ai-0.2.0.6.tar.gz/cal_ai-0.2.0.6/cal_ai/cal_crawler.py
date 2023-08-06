#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import logging
from enum import Enum
import requests, json
from threading import Thread
from .data_template import UrlTemplate, DataType
from .common_utils import CommonUtils


class MachineInfo(Enum):
    TPM = 1
    EPM = 2
    CAL_STATUS_1 = 3
    CAL_STATUS_2 = 4
    TRANS_TIME = 5
    CPU_USAGE = 6
    MEMORY_USAGE = 7
    JVM = 8
    GC_COUNT = 9


class CalCrawler(object):
    @staticmethod
    def get_all_traffic_host(pool_name, sample_width=3600, sample_count=5, output_type="json", use_cache=True,
                             max_wait_second=300):
        thread_list = []
        host_list = []
        current_timestamp = int(time.time())
        for i in range(sample_count):
            data_url = UrlTemplate.render(DataType.REQUEST_COUNT, current_timestamp - sample_width * i - 60,
                                          current_timestamp - sample_width * i, pool_name, "*", "*",
                                          output_type, use_cache)
            thread = Thread(target=CalCrawler.__crawl_hostname, args=[data_url, host_list])
            thread.daemon = True
            thread.start()
            thread_list.append(thread)

        for thread in thread_list:
            thread.join(max_wait_second)

        return list(set(host_list))

    @staticmethod
    def __crawl_hostname(data_url, host_list, retry=5):
        for i in range(retry):
            try:
                response = requests.get(data_url)
                data = json.loads(response.content)
                try:
                    host_list.extend([record["Tags"]["host"] for record in data])
                except KeyError:
                    print("Key error load %s" % data_url)
                    print("data %s" % data)
                if i > 0:
                    logging.warn("Get good result for %s through %d retry after IOException." % (str(data_url), i))
                break
            except IOError:
                # Retry when IO Error Happen
                if i == retry - 1:
                    logging.error("Curl data failed after %d time retry, url %s" % (i, data_url))


    @staticmethod
    def __crawl(data_url, data_type, current_part_num, history_data, retry=5):
        start_time = time.time()
        logging.debug("%s thread start at time: %s" % (data_type, CommonUtils.timestamp_to_data_str(start_time)))
        logging.debug(data_url)

        for i in range(retry):
            try:
                response = requests.get(data_url)
                data = json.loads(response.content)
                history_data[data_type][current_part_num] = data
                if i > 0:
                    logging.warn("Get good result for %s through %d retry after IOException." % (str(data_type), i))
                break
            except IOError:
                # Retry when IO Error Happen
                if i == retry - 1:
                    logging.error("Curl data type %s failed after %d time retry, url %s" % (data_type, i, data_url))
            time.sleep(3)

        finish_time = time.time()
        logging.debug("%s thread finished at time: %s, total take %s second" % (data_type, CommonUtils.timestamp_to_data_str(finish_time), str(finish_time - start_time)))

    @staticmethod
    def __merge_history_data(history_data):
        merged_history_data = {}
        for data_type in DataType:
            data_type_dict = history_data[data_type]
            if not data_type_dict:
                logging.warn("Data crawl for type %s is None" % data_type.name)
            elif len(data_type_dict) != max(data_type_dict.keys()):
                logging.error("Crawl data part missing for type %s, collected parts: %s" % (data_type.name, str(data_type.keys())))
            else:
                merged_history_data[data_type] = []
                for i in range(1, len(data_type_dict) + 1):
                    logging.info("start merge %d for type %s" % (i, data_type.name))
                    if data_type_dict[i]:
                        if not merged_history_data[data_type]:
                            merged_history_data[data_type] = data_type_dict[i]
                        else:
                            merged_history_data[data_type][0]['DataPoints'].extend(data_type_dict[i][0]['DataPoints'])
        return merged_history_data

    @staticmethod
    def crawl_data(host_name, start_time, end_time, column_name=None, pool_name="risktxncomputeserv", output_type="json"
                   , use_cache=True, max_wait_second=300):
        if column_name is None:
            column_name = CommonUtils.get_column_name_from_host_name(host_name)
            logging.debug("Get column name %s from host %s" % (column_name, host_name))

        thread_list = []
        history_data = {}
        for data_type in DataType:
            history_data[data_type] = {}
            current_part_num = 1
            current_time = start_time
            while current_time + 24 * 60 * 60 < end_time:
                CalCrawler.__new_crawl_thread(data_type, current_time, current_time + 24 * 60 * 60, pool_name,
                                              column_name, host_name, output_type, use_cache, current_part_num,
                                              thread_list, history_data)
                current_time += 24 * 60 * 60
                current_part_num += 1
            CalCrawler.__new_crawl_thread(data_type, current_time, end_time, pool_name, column_name, host_name,
                                          output_type, use_cache, current_part_num, thread_list, history_data)
        for thread in thread_list:
            thread.join(max_wait_second)

        return CalCrawler.__convert_to_machine_info_history(CalCrawler.__merge_history_data(history_data))

    @staticmethod
    def __new_crawl_thread(data_type, start_time, end_time, pool_name, column_name, host_name, output_type, use_cache,
                           current_part_num, thread_list, history_data):
        data_url = UrlTemplate.render(data_type, start_time, end_time, pool_name, column_name, host_name, output_type, use_cache)
        thread = Thread(target=CalCrawler.__crawl, args=[data_url, data_type, current_part_num, history_data])
        thread.daemon = True
        thread.start()
        thread_list.append(thread)

    @staticmethod
    def __convert_to_machine_info_history(history_data):
        machine_status = {}
        if DataType.REQUEST_COUNT in history_data:
            machine_status[MachineInfo.TPM] = history_data[DataType.REQUEST_COUNT]
        if DataType.REQUEST_COUNT in history_data and DataType.REQUEST_DURATION in history_data:
            request_count_list = history_data.get(DataType.REQUEST_COUNT)
            duration_data_list = history_data.get(DataType.REQUEST_DURATION)
            if len(request_count_list) > 0 and len(duration_data_list) > 0:
                request_count_list = request_count_list[0]["DataPoints"]
                duration_data_list = duration_data_list[0]["DataPoints"]
                if len(request_count_list) == len(duration_data_list):
                    machine_status[MachineInfo.TRANS_TIME] = history_data.get(DataType.REQUEST_DURATION)
                    machine_status[MachineInfo.TRANS_TIME][0]['DataPoints'] = [[request_count_list[i][0], duration_data_list[i][1] / request_count_list[i][1]] for i in range(len(request_count_list))]
                else:
                    logging.error("Warning: request count list is %d while duration time list is %d" % (len(request_count_list), len(duration_data_list)))
            else:
                logging.warn("Either request count %d or duration count %d is None." % (len(request_count_list), len(duration_data_list)))
        if DataType.ERROR_COUNT in history_data:
            machine_status[MachineInfo.EPM] = history_data[DataType.ERROR_COUNT]
        if DataType.CAL_STATUS_1 in history_data:
            machine_status[MachineInfo.CAL_STATUS_1] = history_data[DataType.CAL_STATUS_1]
        if DataType.CAL_STATUS_2 in history_data:
            machine_status[MachineInfo.CAL_STATUS_2] = history_data[DataType.CAL_STATUS_2]
        if DataType.CPU in history_data:
            machine_status[MachineInfo.CPU_USAGE] = history_data[DataType.CPU]
        if DataType.MEMORY_USAGE in history_data:
            machine_status[MachineInfo.MEMORY_USAGE] = history_data[DataType.MEMORY_USAGE]
        if DataType.ERROR_COUNT in history_data:
            machine_status[MachineInfo.EPM] = history_data[DataType.ERROR_COUNT]
        if DataType.JVM in history_data:
            machine_status[MachineInfo.JVM] = history_data[DataType.JVM]
        if DataType.GC_COUNT in history_data:
            machine_status[MachineInfo.GC_COUNT] = history_data[DataType.GC_COUNT]
        return machine_status


if __name__ == "__main__":
    print(len(CalCrawler.get_all_traffic_host("risktxncomputeserv")))
    result = CalCrawler.crawl_data("dcg13risktxncomputeserv6056", 1530979200, 1531324800)
    for key, value in result.items():
        print(key, value)


