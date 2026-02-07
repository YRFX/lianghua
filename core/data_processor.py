# -*- coding: utf-8 -*-
# 模块2：数据预处理层 - 仅负责：清洗脏数据 + 计算技术指标，纯数据处理
import talib as ta
import pandas as pd
import numpy as np
from config.settings import STRATEGY_CONFIG
from utils.common_utils import print_error


def data_clean(raw_data):
    """数据清洗：去重、补值、剔除异常值、时间对齐，保证数据有效性"""
    if raw_data is None or raw_data.empty:
        return pd.DataFrame()

    df = raw_data.copy()
    price_cols = ["open", "close", "high", "low"]

    # 1. 去重+时间排序
    df = df.drop_duplicates(subset=["datetime"]).sort_values("datetime").reset_index(drop=True)
    # 2. 缺失值填充
    df[price_cols] = df[price_cols].fillna(method="ffill")
    df["vol"] = df["vol"].fillna(0)
    # 3. 剔除乌龙指（涨跌幅±5%以上）
    df["pct_chg"] = df["close"].pct_change() * 100
    df = df[(df["pct_chg"] > -5) & (df["pct_chg"] < 5)]
    # 4. 分钟级时间对齐
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.set_index("datetime").asfreq("1min").reset_index()
    df[price_cols] = df["price_cols"].fillna(method="ffill")

    return df


def calc_technical_indicators(clean_data):
    """技术指标计算：预计算所有做T所需指标，缓存使用，避免重复计算"""
    if clean_data.empty:
        return pd.DataFrame()

    df = clean_data.copy()
    close = df["close"].values
    high = df["high"].values
    low = df["low"].values
    vol = df["vol"].values

    # 核心震荡指标（做T信号源）
    df["boll_upper"], df["boll_mid"], df["boll_lower"] = ta.BBANDS(close, timeperiod=STRATEGY_CONFIG["boll_timeperiod"],
                                                                   nbdevup=STRATEGY_CONFIG["boll_nbdev"],
                                                                   nbdevdn=STRATEGY_CONFIG["boll_nbdev"])
    df["rsi6"] = ta.RSI(close, timeperiod=STRATEGY_CONFIG["rsi_timeperiod"])
    df["kdj_k"], df["kdj_d"], df["kdj_j"] = ta.STOCH(high, low, close, fastk_period=9, slowk_period=3, slowd_period=3)
    df["bias6"] = ta.BIAS(close, timeperiod=STRATEGY_CONFIG["bias_timeperiod"])

    # 辅助趋势指标
    df["ma5"] = ta.MA(close, timeperiod=5)
    df["ma10"] = ta.MA(close, timeperiod=10)
    df["macd"], df["macdsignal"], df["macdhist"] = ta.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)

    # 量能验证指标
    df["vol_ma5"] = ta.MA(vol, timeperiod=5)
    df["vol_ratio"] = df["vol"] / df["vol_ma5"]

    df = df.dropna().reset_index(drop=True)
    return df


def preprocess_data(raw_data):
    """预处理统一入口：清洗 → 指标计算"""
    clean_df = data_clean(raw_data)
    processed_df = calc_technical_indicators(clean_df)
    return processed_df