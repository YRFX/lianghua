# -*- coding: utf-8 -*-
# 模块5：交易执行层 - 仅负责：执行有效信号，半自动/全自动切换，无其他逻辑
import time
from config.settings import BASE_CONFIG
from utils.common_utils import print_info


def send_signal_notify(signal):
    """半自动模式【推荐】：控制台+日志推送买卖信号，手动下单，无风险"""
    notify_msg = f"\n✅ 【做T信号推送】{signal['datetime'].strftime('%Y-%m-%d %H:%M:%S')} | 标的：{signal['ts_code']} | 模式：{signal['signal_type']} | 方向：{signal['direction']} | 价格：{signal['price']:.2f} | 数量：{signal['quantity']}股 | 触发：{signal['trigger']}"
    print_info(notify_msg)
    return {"status": "notify_success", "signal": signal}


def send_order_to_broker(signal):
    """全自动模式：对接券商API自动下单，此处为模拟，替换API即可用"""
    try:
        order_params = {
            "code": signal["ts_code"],
            "direction": signal["direction"],
            "price": signal["price"],
            "quantity": signal["quantity"],
            "order_type": "limit"
        }
        # ========== 替换为你的券商API ==========
        # order_id = broker_api.place_order(**order_params)
        # time.sleep(1)
        # order_status = broker_api.query_order(order_id)
        # ======================================
        order_id = f"SIM_ORDER_{int(time.time())}"
        order_status = "filled"

        if order_status == "filled":
            print_info(f"委托成交：{order_id} | {signal}")
            return {"status": "success", "order_id": order_id, "signal": signal}
        else:
            print_info(f"委托未成交，已撤单：{order_id} | {signal}")
            return {"status": "failed", "reason": "未成交", "signal": signal}
    except Exception as e:
        print_info(f"下单异常: {str(e)} | {signal}")
        return {"status": "error", "reason": str(e), "signal": signal}


def trade_executor(valid_signals):
    """交易执行统一入口：根据配置的模式执行"""
    trade_results = []
    for sig in valid_signals:
        if BASE_CONFIG["trade_mode"] == "semi_auto":
            res = send_signal_notify(sig)
        else:
            res = send_order_to_broker(sig)
        trade_results.append(res)
    return trade_results