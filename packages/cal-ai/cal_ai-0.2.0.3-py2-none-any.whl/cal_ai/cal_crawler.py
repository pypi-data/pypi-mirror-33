#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import logging
import urllib, json
from threading import Thread
from .data_template import UrlTemplate, DataType
from .common_utils import CommonUtils


class CalCrawler(object):
    @staticmethod
    def __crawl(data_url, data_type, current_part_num, history_data, retry=5):
        start_time = time.time()
        logging.debug("%s thread start at time: %s" % (data_type, CommonUtils.timestamp_to_data_str(start_time)))
        logging.debug(data_url)

        for i in range(retry):
            try:
                response = urllib.urlopen(data_url)
                data = json.loads(response.read())
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
    def crawl_data(host_name, start_time, end_time, column_name=None, pool_name="risktxncomputeserv", output_type="json", use_cache=True, max_wait_second=300):
        if column_name is None:
            column_name = CommonUtils.get_column_name_from_host_name(host_name)
            logging.debug("Get column name %s from host %s" % (column_name, host_name))

        thread_list = []
        history_data = {}
        for data_type in DataType:
            history_data[data_type] = {}
            current_part_num = 1
            while start_time + 24 * 60 * 60 < end_time:
                CalCrawler.__new_crawl_thread(data_type, start_time, start_time + 24 * 60 * 60, pool_name, column_name,
                                         host_name, output_type, use_cache, current_part_num, thread_list, history_data)
                start_time += 24 * 60 * 60
                current_part_num += 1
            CalCrawler.__new_crawl_thread(data_type, start_time, end_time, pool_name, column_name, host_name, output_type,
                                          use_cache, current_part_num, thread_list, history_data)
        for thread in thread_list:
            thread.join(max_wait_second)

        return CalCrawler.__merge_history_data(history_data)

    @staticmethod
    def __new_crawl_thread(data_type, start_time, end_time, pool_name, column_name, host_name, output_type, use_cache,
                           current_part_num, thread_list, history_data):
        data_url = UrlTemplate.render(data_type, start_time, end_time, pool_name, column_name, host_name, output_type, use_cache)
        thread = Thread(target=CalCrawler.__crawl, args=[data_url, data_type, current_part_num, history_data])
        thread.daemon = True
        thread.start()
        thread_list.append(thread)


if __name__ == "__main__":
    host_name = "dcg13risktxncomputeserv6056"
    result = CalCrawler.crawl_data(host_name, 1530979200, 1531324800)
    for key, value in result.items():
        print(key, value)


