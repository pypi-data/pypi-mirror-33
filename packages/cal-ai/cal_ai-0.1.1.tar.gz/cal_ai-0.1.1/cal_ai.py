from lib.ai_monitor import AIMonitor
from lib.cal_crawler import CalCrawler
from lib.plot_util import PlotUtil


__version__ = "0.1.1"


def plot_host(host_name, start_time_str, end_time_str=None, time_str_format="%Y-%m-%d %H:%M:%S"):
    PlotUtil.plot_host(host_name, start_time_str, end_time_str, time_str_format)


def onebox_evaluate(box_list, last_x_hours, pool_name):
    AIMonitor.onebox_evaluate(box_list, last_x_hours, pool_name)

def crawl_data(host_name, start_time, end_time, column_name=None, pool_name="risktxncomputeserv", output_type="json", use_cache=True):
    return CalCrawler.crawl_data(host_name, start_time, end_time, column_name, pool_name, output_type, use_cache)