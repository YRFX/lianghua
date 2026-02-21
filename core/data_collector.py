# -*- coding: utf-8 -*-
# 模块1：行情数据采集层 - 仅负责：实盘实时采集/回测历史采集，无其他逻辑
import traceback

# import tushare as ts
import pandas as pd
import threading
import time
from config.settings import  BASE_CONFIG, REAL_TIME_DATA, MIN1_DATA
from utils.common_utils import print_info, print_error
import akshare as ak

# Tushare Token 配置【必填，替换成你的】
# ts.set_token("10119dd85c4a960217364adfaa05ed4f6351cb514e54e0a1c18232da")
# pro = ts.pro_api()

# def collect_history_data(start_date: str, end_date: str, freq: str = "1min"):
#     """回测专用：采集股票历史1分钟K线数据"""
#     try:
#         df = pro.stk_mins(ts_code=BASE_CONFIG["target_stock"], start_date=start_date, end_date=end_date, freq=freq)
#         df = df.sort_values("trade_time").reset_index(drop=True)
#         df.to_csv(f"{BASE_CONFIG['data_save_path']}{BASE_CONFIG['target_stock']}_{freq}_{start_date}_{end_date}.csv", index=False)
#         print_info(f"历史数据采集完成：{BASE_CONFIG['target_stock']} {start_date}-{end_date}")
#         return df
#     except Exception as e:
#         traceback.print_exc()
#         print_error(f"历史数据采集失败: {str(e)}")
#         return None
#
def collect_history_data(target_code:str,start_date: str, end_date: str, min_freq: str = "1"):
    """回测专用：采集股票历史1分钟K线数据"""
    try:
        df = ak.stock_zh_a_hist_min_em(symbol=target_code, start_date=start_date , end_date=end_date, period=min_freq)
        # df.to_csv(f"{BASE_CONFIG['data_save_path']}{BASE_CONFIG['target_stock']}_{min_freq}_{start_date}_{end_date}.csv", index=False)
        print_info(f"历史数据采集完成：{BASE_CONFIG['target_stock']} {start_date}-{end_date}")
        return df
    except Exception as e:
        traceback.print_exc()
        # print_error(f"历史数据采集失败: {str(e)}")
        return None

def collect_real_time_data(target_code):
    """实盘专用：独立线程实时采集1分钟K线+分时数据，不阻塞主程序"""
    # global REAL_TIME_DATA, MIN1_DATA
    # while True:
    try:
        df = ak.stock_zh_a_minute(target_code)
        df=df.sort_values(by="day")
        # MIN1_DATA = pro.bar(ts_code=BASE_CONFIG["target_stock"], freq="1min", count=1)
        # time.sleep(60)  # 严格匹配1分钟K线更新频率
        return df
    except Exception as e:
        print_error(f"实时数据采集异常，重试中: {str(e)}")
        time.sleep(3)
            # continue

def load_data(mode: str = "real"):
    """数据加载统一入口：切换实盘/回测"""
    if mode == "backtest":
        return collect_history_data("2026-02-13 09:00:00", "2026-02-13 19:00:00")
    elif mode == "real":
        # 启动实时采集守护线程
        t = threading.Thread(target=collect_real_time_data)
        t.daemon = True
        t.start()
        time.sleep(2)  # 等待线程初始化数据
        return MIN1_DATA
    else:
        print_error("数据加载模式错误，仅支持 real / backtest")
        return None

if __name__ == '__main__':
    # load_data("backtest")
    df = collect_real_time_data("sh603086")
    print(df)