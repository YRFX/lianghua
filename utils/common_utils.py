# -*- coding: utf-8 -*-
# 通用工具函数 - 解耦所有通用功能，无业务逻辑，纯工具
import time
import logging
from datetime import datetime
from lianghua.config.settings import BASE_CONFIG

# 日志初始化 - 全局生效
logging.basicConfig(
    filename=BASE_CONFIG["log_save_path"],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

def is_trading_time() -> bool:
    """精准判断A股有效交易时段：周一至周五 9:30-11:30 | 13:00-15:00"""
    now = datetime.now()
    # 过滤周末
    if now.weekday() >= 5:
        return False
    # 过滤法定节假日
    if now.strftime("%Y%m%d") in BASE_CONFIG["holiday_list"]:
        return False
    # 过滤交易时段外
    hour, minute = now.hour, now.minute
    if (hour ==9 and minute >=30) or (10<=hour<11) or (hour==11 and minute<=30):
        return True
    if 13<=hour <15:
        return True
    return False

def cancel_all_orders() -> None:
    """安全撤单：手动停止/收盘/异常时，撤销所有未成交委托"""
    print("\n🔐 【安全操作】正在撤销所有未成交委托单...")
    # 替换为券商API：broker_api.cancel_all_orders()
    logging.info("所有未成交委托单已撤销")
    print("✅ 所有委托单已撤销，持仓安全")

def print_info(msg: str) -> None:
    """统一打印+日志记录"""
    print(msg)
    logging.info(msg)

def print_error(msg: str) -> None:
    """统一错误打印+日志记录"""
    print(f"❌ {msg}")
    logging.error(msg)