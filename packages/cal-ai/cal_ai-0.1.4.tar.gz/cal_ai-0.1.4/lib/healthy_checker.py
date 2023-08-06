#!/usr/bin/python
# -*- coding: utf-8 -*-
from enum import Enum
import logging
from string import Template
from datetime import datetime
from lib.data_template import DataType

abnormal_wave_template = Template("Abnormal high $machine_info: start from $start_time to $end_time, "
                                  "and highest value is $max_value at time $max_time")

checker_logger = logging.getLogger('HealthyChecker')
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
checker_logger.addHandler(handler)


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


healthy_threshold = {
    MachineInfo.TPM: 100,
    MachineInfo.EPM: 1,
    MachineInfo.CAL_STATUS_1: 1,
    MachineInfo.CAL_STATUS_2: 1,
    MachineInfo.TRANS_TIME: 500,
    MachineInfo.CPU_USAGE: 20,
    MachineInfo.MEMORY_USAGE: 50,
    MachineInfo.JVM: 1,
    MachineInfo.GC_COUNT: 1
}


class HealthyChecker(object):
    @staticmethod
    def abnormal_check_data(cal_data):
        return {
            MachineInfo.TPM: HealthyChecker._abnormal_check_tpm(cal_data),
            MachineInfo.EPM: HealthyChecker._abnormal_check_epm(cal_data),
            MachineInfo.CAL_STATUS_1: HealthyChecker._abnormal_check_cal_status_1(cal_data),
            MachineInfo.CAL_STATUS_2: HealthyChecker._abnormal_check_cal_status_2(cal_data),
            MachineInfo.TRANS_TIME: HealthyChecker._abnormal_check_trans_time(cal_data),
            MachineInfo.CPU_USAGE: HealthyChecker._abnormal_check_cpu_usage(cal_data),
            MachineInfo.MEMORY_USAGE: HealthyChecker._abnormal_check_memory_usage(cal_data),
            MachineInfo.JVM: HealthyChecker._abnormal_check_jvm(cal_data),
            MachineInfo.GC_COUNT: HealthyChecker._abnormal_check_gc_count(cal_data)}

    @staticmethod
    def assessment_on_result(abnormal_result):
        assessments = []
        for machine_info in MachineInfo:
            if machine_info in abnormal_result:
                abnormal_behaviours = abnormal_result.get(machine_info)
                for abnormal_behaviour in abnormal_behaviours:
                    assessments.append(abnormal_wave_template.substitute(machine_info=machine_info.name,
                                                                         start_time=HealthyChecker.convert_unix_time(abnormal_behaviour[0]),
                                                                         end_time=HealthyChecker.convert_unix_time(abnormal_behaviour[1]),
                                                                         max_time=HealthyChecker.convert_unix_time(abnormal_behaviour[2]),
                                                                         max_value=abnormal_behaviour[3]))
        if len(assessments) == 0:
            return "Check status assessment: Healthy!"
        else:
            return "Check status assessment: Abnormal behaviour identified.\nDetails:" + "\n".join(assessments)

    @staticmethod
    def convert_unix_time(ts):
        current_date = datetime.fromtimestamp(ts)
        return current_date.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _abnormal_wave_detect(machine_info_type, data_list, merge_wave_interval=600):
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
    def _basic_abnormal_check(cal_data, data_type, check_type):
        checker_logger.debug("Check %s on data type %s, data list:%s" % (check_type, data_type, cal_data))
        data_list = cal_data.get(data_type)
        if data_list is None:
            checker_logger.error("Can not found data type %s in %s" % (data_type, cal_data))
            return []
        if len(data_list) == 0:
            return []
        data_count_list = data_list[0]["DataPoints"]
        return HealthyChecker._abnormal_wave_detect(check_type, data_count_list)

    @staticmethod
    def _abnormal_check_tpm(cal_data):
        return HealthyChecker._basic_abnormal_check(cal_data, DataType.REQUEST_COUNT, MachineInfo.TPM)

    @staticmethod
    def _abnormal_check_epm(cal_data):
        return HealthyChecker._basic_abnormal_check(cal_data, DataType.ERROR_COUNT, MachineInfo.EPM)

    @staticmethod
    def _abnormal_check_cal_status_1(cal_data):
        return HealthyChecker._basic_abnormal_check(cal_data, DataType.CAL_STATUS_1, MachineInfo.CAL_STATUS_1)

    @staticmethod
    def _abnormal_check_cal_status_2(cal_data):
        return HealthyChecker._basic_abnormal_check(cal_data, DataType.CAL_STATUS_2, MachineInfo.CAL_STATUS_2)

    @staticmethod
    def _abnormal_check_trans_time(cal_data):
        data_list = cal_data.get(DataType.REQUEST_COUNT)
        duration_data_list = cal_data.get(DataType.REQUEST_DURATION)
        if len(data_list) == 0 or len(duration_data_list) == 0:
            return []
        data_list = data_list[0]["DataPoints"]
        duration_data_list = duration_data_list[0]["DataPoints"]
        if len(data_list) != len(duration_data_list):
            checker_logger.debug("Warning: request count list is %d while duration time list is %d" % (
            len(data_list), len(duration_data_list)))
            return []
        avg_duration = [[data_list[i][0], duration_data_list[i][1] / data_list[i][1]] for i in range(len(data_list))]

        return HealthyChecker._abnormal_wave_detect(MachineInfo.TRANS_TIME, avg_duration)

    @staticmethod
    def _abnormal_check_cpu_usage(cal_data):
        return HealthyChecker._basic_abnormal_check(cal_data, DataType.CPU, MachineInfo.CPU_USAGE)

    @staticmethod
    def _abnormal_check_memory_usage(cal_data):
        return HealthyChecker._basic_abnormal_check(cal_data, DataType.MEMORY_USAGE, MachineInfo.MEMORY_USAGE)

    @staticmethod
    def _abnormal_check_jvm(cal_data):
        return HealthyChecker._basic_abnormal_check(cal_data, DataType.JVM, MachineInfo.JVM)

    @staticmethod
    def _abnormal_check_gc_count(cal_data):
        return HealthyChecker._basic_abnormal_check(cal_data, DataType.GC_COUNT, MachineInfo.GC_COUNT)


