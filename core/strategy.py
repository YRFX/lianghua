# -*- coding: utf-8 -*-
# 模块3：策略层 - 仅负责：生成买卖信号，无风控、无执行，纯策略逻辑
import pandas as pd
from config.settings import BASE_CONFIG, STRATEGY_CONFIG


def gen_boll_signal(df):
    """主策略：布林带+RSI+量能 震荡做T（80%信号来源，胜率最高）"""
    signals = []
    if df.empty:
        return signals

    latest = df.iloc[-1]
    t_quantity = int(BASE_CONFIG["base_position"] * STRATEGY_CONFIG["t_position_ratio"])

    # 正T：先买后卖 - 下轨超卖放量买
    if (latest["close"] <= latest["boll_lower"]) and (latest["rsi6"] <= 30) and (latest["vol_ratio"] > 1):
        signals.append({
            "ts_code": BASE_CONFIG["target_stock"],
            "datetime": latest["datetime"],
            "signal_type": "BUY_THEN_SELL",
            "direction": "BUY",
            "price": latest["close"],
            "quantity": t_quantity,
            "trigger": "BOLL下轨+RSI超卖+放量企稳"
        })
    # 正T平仓：中轨超买缩量卖
    elif (latest["close"] >= latest["boll_mid"]) and (latest["rsi6"] >= 60) and (latest["vol_ratio"] < 1):
        signals.append({
            "ts_code": BASE_CONFIG["target_stock"],
            "datetime": latest["datetime"],
            "signal_type": "BUY_THEN_SELL",
            "direction": "SELL",
            "price": latest["close"],
            "quantity": t_quantity,
            "trigger": "BOLL中轨+RSI超买+缩量滞涨"
        })

    # 反T：先卖后买 - 上轨超买缩量卖
    if (latest["close"] >= latest["boll_upper"]) and (latest["rsi6"] >= 70) and (latest["vol_ratio"] < 1):
        signals.append({
            "ts_code": BASE_CONFIG["target_stock"],
            "datetime": latest["datetime"],
            "signal_type": "SELL_THEN_BUY",
            "direction": "SELL",
            "price": latest["close"],
            "quantity": t_quantity,
            "trigger": "BOLL上轨+RSI超买+缩量滞涨"
        })
    # 反T平仓：中轨超卖放量买
    elif (latest["close"] <= latest["boll_mid"]) and (latest["rsi6"] <= 40) and (latest["vol_ratio"] > 1):
        signals.append({
            "ts_code": BASE_CONFIG["target_stock"],
            "datetime": latest["datetime"],
            "signal_type": "SELL_THEN_BUY",
            "direction": "BUY",
            "price": latest["close"],
            "quantity": t_quantity,
            "trigger": "BOLL中轨+RSI超卖+放量企稳"
        })
    return signals


def gen_ma_bias_signal(df):
    """辅策略：均线+乖离率 趋势做T（15%信号补充）"""
    signals = []
    if df.empty:
        return signals

    latest = df.iloc[-1]
    t_quantity = int(BASE_CONFIG["base_position"] * STRATEGY_CONFIG["t_position_ratio"])

    if latest["close"] < latest["ma10"] and latest["bias6"] <= -1.5:
        signals.append({
            "ts_code": BASE_CONFIG["target_stock"],
            "datetime": latest["datetime"],
            "signal_type": "BUY_THEN_SELL",
            "direction": "BUY",
            "price": latest["close"],
            "quantity": t_quantity,
            "trigger": "MA10跌破+BIAS超卖"
        })
    elif latest["close"] > latest["ma10"] and latest["bias6"] >= 1.5:
        signals.append({
            "ts_code": BASE_CONFIG["target_stock"],
            "datetime": latest["datetime"],
            "signal_type": "SELL_THEN_BUY",
            "direction": "SELL",
            "price": latest["close"],
            "quantity": t_quantity,
            "trigger": "MA10突破+BIAS超买"
        })
    return signals


def gen_all_signals(df):
    """信号统一入口：主策略优先，无信号则用辅策略"""
    boll_signals = gen_boll_signal(df)
    return boll_signals if len(boll_signals) > 0 else gen_ma_bias_signal(df)