# -*- coding: utf-8 -*-
# ==============================================
# A股自动做T量化系统 - 唯一启动文件
# 运行方式：python main.py
# 所有配置在 config/settings.py 修改，无需改此文件
# ==============================================
import time
import sys
from datetime import datetime

# 导入所有模块
from core.data_collector import load_data
from core.data_processor import preprocess_data
from core.strategy import gen_all_signals
from core.risk_control import risk_control
from core.trade_executor import trade_executor
from core.analysis import gen_review_report
from utils.common_utils import is_trading_time, cancel_all_orders, print_info
from config.settings import BASE_CONFIG


def run_full_pipeline():
    """封装完整业务链路：采集 → 预处理 → 策略 → 风控 → 执行"""
    raw_data = load_data(mode="real")
    processed_data = preprocess_data(raw_data)
    raw_signals = gen_all_signals(processed_data)
    valid_signals, invalid_signals = risk_control(raw_signals, processed_data)
    trade_results = trade_executor(valid_signals)
    return trade_results, invalid_signals


if __name__ == "__main__":
    # 初始化变量
    total_trade_results = []
    total_invalid_signals = []

    # 启动信息
    print("=" * 80)
    print("🚀 A股日内自动做T量化系统 - 已启动")
    print(
        f"📌 标的：{BASE_CONFIG['target_stock']} | 底仓：{BASE_CONFIG['base_position']}股 | 成本：{BASE_CONFIG['base_hold_cost']}元")
    print(f"📌 可用资金：{BASE_CONFIG['current_cash']}元 | 交易模式：{BASE_CONFIG['trade_mode']}")
    print(f"📌 运行规则：仅交易时段9:30-11:30/13:00-15:00运行，Ctrl+C 安全停止")
    print("=" * 80 + "\n")

    try:
        # 核心可控循环
        while True:
            now = datetime.now()
            if is_trading_time():
                trade_res, invalid_sig = run_full_pipeline()
                total_trade_results.extend(trade_res)
                total_invalid_signals.extend(invalid_sig)
                time.sleep(60)  # 每分钟执行一次
            else:
                print_info(f"⏰ 非交易时段：{now.strftime('%Y-%m-%d %H:%M:%S')}，系统休眠中...")
                time.sleep(300)  # 5分钟检测一次

                # 收盘后自动复盘+退出
                if now.hour >= 15 and now.minute >= 5:
                    print_info("\n🔔 今日交易收盘，开始复盘归档...")
                    gen_review_report(total_trade_results, total_invalid_signals)
                    print_info("\n✅ 系统运行结束，复盘完成，安全退出！")
                    break

    # 手动安全停止
    except KeyboardInterrupt:
        print_info("\n⚠️ 检测到手动停止指令，执行安全退出流程...")
        cancel_all_orders()
        gen_review_report(total_trade_results, total_invalid_signals)
        print_info("\n✅ 系统已安全停止，持仓无风险！")
        sys.exit(0)

    # 异常兜底处理
    except Exception as e:
        print_info(f"\n❌ 系统运行异常：{str(e)}")
        cancel_all_orders()
        print_info("✅ 紧急撤单完成，日志已记录，程序退出！")
        sys.exit(1)