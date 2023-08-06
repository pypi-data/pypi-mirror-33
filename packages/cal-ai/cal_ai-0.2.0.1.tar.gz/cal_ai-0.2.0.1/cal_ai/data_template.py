#!/usr/bin/python
# -*- coding: utf-8 -*-
from enum import Enum
import logging
from string import Template

cral_logger = logging.getLogger('UrlTemplate')
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
cral_logger.addHandler(handler)


class DataType(Enum):
    REQUEST_COUNT = 1
    ERROR_COUNT = 2
    CAL_STATUS_1 = 3
    CAL_STATUS_2 = 4
    REQUEST_DURATION = 5
    CPU = 6
    MEMORY_USAGE = 7
    JVM = 8
    GC_COUNT = 9


def request_count_template():
    return Template("https://engineering.paypalcorp.com/sherlock/pp.tsdb/q?start=$start_time&end=$end_time&m=sum%3Appappmon.requestCount.STATE.60s%7Bpool%3D$pool_name%2Ccolo%3D$column_name%2Chost%3D$host_name%7D&o=&format=$output_type&useTopoCache=$use_cache")


def error_count_template():
    return Template("https://engineering.paypalcorp.com/sherlock/pp.tsdb/q?start=$start_time&end=$end_time&m=sum%3Appappmon.requestCount.STATE.60s%7Bpool%3D$pool_name%2Cstatus%3D1%7C2%2Ccolo%3D$column_name%2Chost%3D$host_name%7D&o=&format=$output_type&useTopoCache=$use_cache")


def cal_status_1_template():
    return Template("https://engineering.paypalcorp.com/sherlock/pp.tsdb/q?start=$start_time&end=$end_time&m=sum%3Appappmon.requestCount.STATE.60s%7Bpool%3D$pool_name%2Cstatus%3D1%2Ccolo%3D$column_name%2Chost%3D$host_name%7D&o=&format=$output_type&useTopoCache=$use_cache")


def cal_status_2_template():
    return Template("https://engineering.paypalcorp.com/sherlock/pp.tsdb/q?start=$start_time&end=$end_time&m=sum%3Appappmon.requestCount.STATE.60s%7Bpool%3D$pool_name%2Cstatus%3D2%2Ccolo%3D$column_name%2Chost%3D$host_name%7D&o=&format=$output_type&useTopoCache=$use_cache")


def request_duration_template():
    return Template("https://engineering.paypalcorp.com/sherlock/pp.tsdb/q?start=$start_time&end=$end_time&m=sum%3Appappmon.requestDuration.STATE.60s%7Bpool%3D$pool_name%2Ccolo%3D$column_name%2Chost%3D$host_name%7D&o=&format=$output_type&useTopoCache=$use_cache")


def cpu_template():
    return Template("https://engineering.paypalcorp.com/sherlock/pp.tsdb/q?start=$start_time&end=$end_time&m=avg%3Appsysmon.appcpu.usedperc.STATE.60s%7Bapp%3D$pool_name%2Ccolo%3D$column_name%2Chost%3D$host_name%7D&o=&format=$output_type&useTopoCache=$use_cache")


def memory_usage_template():
    return Template("https://engineering.paypalcorp.com/sherlock/pp.tsdb/q?start=$start_time&end=$end_time&m=avg%3Appsysmon.appmemr.used_perc.STATE.60s%7Bapp%3D$pool_name%2Ccolo%3D$column_name%2Chost%3D$host_name%7D&o=&format=$output_type&useTopoCache=$use_cache")


def jvm_template():
    return Template("https://engineering.paypalcorp.com/sherlock/pp.tsdb/q?start=$start_time&end=$end_time&m=avg%3Appsysmon.jvmm.heapfree_kb.STATE.60s%7Bapp%3D$pool_name%2Ccolo%3D$column_name%2Chost%3D$host_name%7D&o=&format=$output_type&useTopoCache=$use_cache")


def gc_count_template():
    return Template("https://engineering.paypalcorp.com/sherlock/pp.tsdb/q?start=$start_time&end=$end_time&m=sum%3Appsysmon.jvmm.gccountPerSec.STATE.60s%7Bapp%3D$pool_name%2Ccolo%3D$column_name%2Chost%3D$host_name%7D&o=&format=$output_type&useTopoCache=$use_cache")


switcher = {
    DataType.REQUEST_COUNT: request_count_template(),
    DataType.ERROR_COUNT: error_count_template(),
    DataType.CAL_STATUS_1: cal_status_1_template(),
    DataType.CAL_STATUS_2: cal_status_2_template(),
    DataType.REQUEST_DURATION: request_duration_template(),
    DataType.CPU: cpu_template(),
    DataType.MEMORY_USAGE: memory_usage_template(),
    DataType.JVM: jvm_template(),
    DataType.GC_COUNT: gc_count_template()
}

class UrlTemplate(object):
    @staticmethod
    def get_template_by_data_type(type):
        return switcher.get(type)

    @staticmethod
    def render(type, start_time, end_time, pool_name, column_name, host_name, output_type, use_cache):
        template = UrlTemplate.get_template_by_data_type(type)
        if template is not None:
            return template.substitute(start_time = start_time, end_time = end_time, pool_name = pool_name, column_name = column_name, host_name = host_name, output_type = output_type, use_cache = str(use_cache).lower())
        print("Get template return None, please make sure the type is correct! It must be one of data_template.data_type")
        return None


if __name__ == '__main__':
    for _type in DataType:
        print(_type.name)
        print(_type.value)
        # print(_type.name, UrlTemplate.render(_type, 1530082680, 1530086520, "risktxncomputeserv", "dcg13", "dcg13risktxncomputeserv7498", "json", True))
