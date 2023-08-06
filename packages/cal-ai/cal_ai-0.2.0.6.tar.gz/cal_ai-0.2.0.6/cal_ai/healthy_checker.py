#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from string import Template
from .common_utils import CommonUtils
from .cal_crawler import MachineInfo


abnormal_wave_template = Template("Abnormal high $machine_info: From $start_time to $end_time, Max $max_value at $max_time")

healthy_threshold = {
    MachineInfo.TPM: 500,
    MachineInfo.EPM: 2,
    MachineInfo.CAL_STATUS_1: 2,
    MachineInfo.CAL_STATUS_2: 2,
    MachineInfo.TRANS_TIME: 800,
    MachineInfo.CPU_USAGE: 50,
    MachineInfo.MEMORY_USAGE: 55,
    MachineInfo.JVM: 1,
    MachineInfo.GC_COUNT: 1
}


class HealthyChecker(object):
    @staticmethod
    def abnormal_check(machine_info_status):
        return {machine_info_type: HealthyChecker._basic_abnormal_check(machine_info_type, data_list) for machine_info_type, data_list in machine_info_status.items()}

    @staticmethod
    def result_analysis(abnormal_result):
        assessments = []
        for machine_info in MachineInfo:
            if machine_info in abnormal_result:
                abnormal_behaviours = abnormal_result.get(machine_info)
                for abnormal_behaviour in abnormal_behaviours:
                    assessments.append(abnormal_wave_template.substitute(machine_info=machine_info.name,
                                                                         start_time=CommonUtils.timestamp_to_data_str(abnormal_behaviour[0]),
                                                                         end_time=CommonUtils.timestamp_to_data_str(abnormal_behaviour[1]),
                                                                         max_time=CommonUtils.timestamp_to_data_str(abnormal_behaviour[2]),
                                                                         max_value=abnormal_behaviour[3]))
        if len(assessments) == 0:
            return "Healthy!"
        else:
            return "Abnormal behaviour identified.\nDetails:\n\t" + "\n\t".join(assessments)

    @staticmethod
    def _abnormal_wave_detect(machine_info_type, data_list, merge_wave_interval=1800):
        abnormal_wave_list = []
        start_time = end_time = max_time = 0
        max_value = -1
        for timestamp, count in data_list:
            if count > healthy_threshold.get(machine_info_type):
                if start_time == 0:
                    start_time = timestamp
                if count > max_value:
                    max_value = count
                    max_time = timestamp
            else:
                if start_time != 0:
                    end_time = timestamp
                    wave = (start_time, end_time, max_time, max_value)
                    HealthyChecker.__append_merge(abnormal_wave_list, wave, merge_wave_interval)
                    start_time = 0
                    max_value = -1

        return abnormal_wave_list

    @staticmethod
    def __append_merge(full_list, element, merge_wave_interval):
        if len(full_list) == 0:
            full_list.append(element)
        else:
            last_element = full_list[-1]
            if element[0] - last_element[1] < merge_wave_interval:
                max_time, max_value = (element[2], element[3]) if element[3] > last_element[3] else (last_element[2], last_element[3])
                new_element =  (last_element[0], element[1], max_time, max_value)
                full_list[-1] = new_element
            else:
                full_list.append(element)

    @staticmethod
    def _basic_abnormal_check(machine_info_type, data_list):
        logging.debug("Check machine info %s, data list:%s" % (machine_info_type, data_list))
        if data_list is None or len(data_list) == 0:
            logging.error("Data list is null or empty for type: %s" % (machine_info_type))
            return []
        data_count_list = data_list[0]["DataPoints"]
        return HealthyChecker._abnormal_wave_detect(machine_info_type, data_count_list)
