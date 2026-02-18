# -*- coding: utf-8 -*-
# 全局核心配置 - 所有可修改参数全部集中在这里，业务代码无硬编码
import pandas as pd

# ========== 基础配置 ==========
BASE_CONFIG = {
    "target_stock": "603086.SH",    # 做T标的股票代码
    "base_position": 1000,          # 底仓持股数量（固定不变）
    "base_hold_cost": 10.00,        # 底仓持仓成本价
    "current_cash": 100000.00,      # 可用资金(元)
    "data_save_path": "./data/",    # 历史数据存储路径
    "log_save_path": "../log/t_log.log",  # 交易日志存储路径
    "trade_mode": "semi_auto",      # 交易模式：semi_auto(推荐)/full_auto
    "market_risk_pct": 0.02,        # 大盘涨跌幅≥2%触发风控
    "avoid_end_trade": 1430,        # 14:30后只平仓不开新仓
    "holiday_list": ["20260101", "20260210", "20260405"]  # 法定节假日
}

# ========== 做T策略参数（最优参数，按需微调） ==========
STRATEGY_CONFIG = {
    "t_position_ratio": 0.5,    # 单次做T仓位 ≤ 底仓50%
    "min_profit_pct": 0.002,    # 最小盈利0.2%，覆盖手续费
    "boll_timeperiod": 20,      # BOLL周期
    "boll_nbdev": 2,            # BOLL标准差
    "rsi_timeperiod": 6,        # RSI周期
    "bias_timeperiod": 6        # 乖离率周期
}

# ========== 风控参数（硬性规则，禁止随意修改） ==========
RISK_CONFIG = {
    "max_t_position_ratio": 0.8,    # 日内总做T仓位 ≤ 底仓80%
    "force_profit_pct": 0.0025,     # 强制止盈0.25%
    "force_loss_pct": 0.002,        # 强制止损0.2%
    "day_max_loss_pct": 0.01,       # 日内亏损≥1%，关闭当日做T
    "min_turnover": 0.03,           # 标的换手率≥3%才做T
    "min_amount": 3e8               # 标的成交额≥3亿才做T
}

# ========== 全局变量（初始化） ==========
REAL_TIME_DATA = pd.DataFrame()
MIN1_DATA = pd.DataFrame()