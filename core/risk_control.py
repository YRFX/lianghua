# -*- coding: utf-8 -*-
# 模块4：风控层 - 仅负责：校验信号合法性，一票否决制，优先级最高，无其他逻辑
from config.settings import BASE_CONFIG, STRATEGY_CONFIG, RISK_CONFIG


def check_stock_risk(signal, stock_data):
    """风控1：标的风控 - 过滤流动性差/涨跌停的股票"""
    latest = stock_data.iloc[-1]
    if latest["turn"] < RISK_CONFIG["min_turnover"]:
        return False, "换手率<3%，流动性不足"
    if latest["amount"] < RISK_CONFIG["min_amount"]:
        return False, "成交额<3亿，活跃度低"
    if abs(latest["pct_chg"]) >= 8:
        return False, "涨跌停附近，禁止交易"
    return True, "标的合规"


def check_signal_risk(signal):
    """风控2：信号风控 - 过滤无效/违规信号"""
    if signal["quantity"] % 100 != 0:
        return False, "非100股整数倍，A股交易规则违规"
    if signal["price"] * signal["quantity"] * STRATEGY_CONFIG["min_profit_pct"] < 1:
        return False, "价差不足0.2%，无盈利空间"
    return True, "信号合规"


def check_position_risk(signal, current_pos):
    """风控3：仓位风控 - 杜绝重仓，核心保命规则"""
    total_t_pos = sum([s["quantity"] for s in current_pos if s["signal_type"] in ["BUY_THEN_SELL", "SELL_THEN_BUY"]])
    if total_t_pos > BASE_CONFIG["base_position"] * RISK_CONFIG["max_t_position_ratio"]:
        return False, f"日内做T仓位超80%底仓，累计{total_t_pos}股"
    if signal["direction"] == "BUY" and (signal["price"] * signal["quantity"] > BASE_CONFIG["current_cash"]):
        return False, "可用资金不足，无法买入"
    return True, "仓位合规"


def check_time_risk(signal):
    """风控4：时间风控 - 尾盘禁止开新仓"""
    trade_time = signal["datetime"].hour * 100 + signal["datetime"].minute
    if trade_time >= BASE_CONFIG["avoid_end_trade"] and signal["direction"] == "BUY":
        return False, "尾盘风控：14:30后禁止开新仓"
    return True, "时间合规"


def check_market_risk(market_pct=0.01):
    """风控5：大盘风控 - 顺势而为，不逆势操作"""
    if market_pct <= -BASE_CONFIG["market_risk_pct"]:
        return False, "大盘大跌≥2%，禁止开多仓"
    if market_pct >= BASE_CONFIG["market_risk_pct"]:
        return False, "大盘大涨≥2%，禁止开空仓"
    return True, "大盘合规"


def risk_control(raw_signals, stock_data, current_pos=[]):
    """风控统一入口：所有规则全部通过，才生成有效信号"""
    valid_signals = []
    invalid_signals = []
    if not raw_signals or stock_data.empty:
        return valid_signals, invalid_signals

    for sig in raw_signals:
        chk1, msg1 = check_stock_risk(sig, stock_data)
        chk2, msg2 = check_signal_risk(sig)
        chk3, msg3 = check_position_risk(sig, current_pos)
        chk4, msg4 = check_time_risk(sig)
        chk5, msg5 = check_market_risk()

        if all([chk1, chk2, chk3, chk4, chk5]):
            valid_signals.append(sig)
        else:
            invalid_signals.append({"signal": sig, "reject_reason": [msg1, msg2, msg3, msg4, msg5]})
    return valid_signals, invalid_signals