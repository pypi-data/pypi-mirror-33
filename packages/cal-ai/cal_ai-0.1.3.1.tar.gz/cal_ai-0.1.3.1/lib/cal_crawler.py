#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, time
import logging
import urllib, json
from threading import Thread
from lib.data_template import UrlTemplate, DataType

reload(sys)
sys.setdefaultencoding('utf-8')


MAX_TIME_WAIT = 300
cral_logger = logging.getLogger('CAL_CRAWLER')
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
cral_logger.addHandler(handler)


def crawl(url, data_type, result, retry=5):
    start_time = time.time()
    cral_logger.debug("%s thread start at time: %s" % (data_type, str(start_time)))
    cral_logger.debug(url)

    for i in range(retry):
        try:
            response = urllib.urlopen(url)
            data = json.loads(response.read())
            result[data_type] = data
            if i > 0:
                cral_logger.warn("Get good result for %s through %d retry after IOException." % (str(data_type), i))
            break
        except IOError:
            # Retry when IO Error Happen
            if i == retry - 1:
                cral_logger.error("Curl data type %s failed after %d time retry, url %s" % (data_type, i, url))
        time.sleep(3)

    finish_time = time.time()
    cral_logger.debug("%s thread finished at time: %s, total take %s second" % (data_type, str(finish_time), str(finish_time - start_time)))


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
    cral_logger.warn("host %s can not be identitied, class it to phx" % host_name)
    return "phx"


class CalCrawler(object):
    @staticmethod
    def crawl_data(host_name, start_time, end_time, column_name=None, pool_name="risktxncomputeserv", output_type="json", use_cache=True):
        if column_name is None:
            column_name = get_column_name_from_host_name(host_name)
            cral_logger.debug("Get column name %s from host %s" % (column_name, host_name))

        thread_list = []
        result = {}
        for data_type in DataType:
            url = UrlTemplate.render(data_type, start_time, end_time, pool_name, column_name, host_name, output_type, use_cache)
            thread = Thread(target=crawl, args=[url, data_type, result])
            thread.daemon = True
            thread.start()
            thread_list.append(thread)
        for thread in thread_list:
            thread.join(MAX_TIME_WAIT)
        return result


if __name__ == "__main__":
    host_name = "dcg13risktxncomputeserv6056"
    result = CalCrawler.crawl_data(host_name, 1530082680, 1530086520)
    for key, value in result.items():
        print(key, value)


