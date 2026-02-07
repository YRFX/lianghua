# -*- coding: utf-8 -*-
# 模块6：复盘分析层 - 仅负责：日志记录、绩效计算、复盘报告，无其他逻辑
import pandas as pd
from config.settings import BASE_CONFIG
from utils.common_utils import print_info


def record_trade_log(trade_results, invalid_signals):
    """完整日志记录：成交/过滤信号全部归档，可回溯审计"""
    for res in trade_results:
        print_info(f"【成交记录】{res}")
    for inv in invalid_signals:
        print_info(f"【过滤信号】{inv}")
    return "日志记录完成"


def calc_performance(trade_results):
    """绩效计算：核心指标-持仓成本降低幅度，做T的终极目标"""
    success_trades = [r for r in trade_results if r["status"] in ["success", "notify_success"]]
    if len(success_trades) == 0:
        return {
            "当日做T次数": 0, "胜率": 0.0, "平均单笔盈利": 0.0, "平均单笔亏损": 0.0,
            "总盈亏(元)": 0.0, "持仓成本降低幅度(%)": 0.0, "手续费成本(元)": 0.0
        }

    df = pd.DataFrame([r["signal"] for r in success_trades])
    df["trade_value"] = df["price"] * df["quantity"]
    df["profit"] = df["trade_value"].diff()
    total_profit = df["profit"].sum()
    total_hold_value = BASE_CONFIG["base_position"] * BASE_CONFIG["base_hold_cost"]
    cost_reduce_pct = (total_profit / total_hold_value) * 100
    fee_cost = len(df) * df["price"].mean() * df["quantity"].mean() * 0.0015

    return {
        "当日做T次数": len(df),
        "胜率": round(len(df[df["profit"] > 0]) / len(df), 4),
        "平均单笔盈利": round(df[df["profit"] > 0]["profit"].mean(), 2) if len(df[df["profit"] > 0]) > 0 else 0.0,
        "平均单笔亏损": round(df[df["profit"] < 0]["profit"].mean(), 2) if len(df[df["profit"] < 0]) > 0 else 0.0,
        "总盈亏(元)": round(total_profit, 2),
        "持仓成本降低幅度(%)": round(cost_reduce_pct, 4),
        "手续费成本(元)": round(fee_cost, 2)
    }


def gen_review_report(trade_results, invalid_signals):
    """复盘报告统一入口：生成可视化报告+优化建议"""
    record_trade_log(trade_results, invalid_signals)
    perf = calc_performance(trade_results)

    print("\n" + "=" * 60)
    print("📊 【A股日内做T - 当日复盘报告】")
    print("=" * 60)
    for k, v in perf.items():
        print(f"{k}: {v}")
    print("=" * 60)

    if perf["胜率"] < 0.6:
        print("💡 优化建议：调整布林带/RSI参数，增强信号有效性")
    if perf["手续费成本(元)"] > abs(perf["总盈亏(元)"]):
        print("💡 优化建议：减少做T次数，严控交易频率")
    if perf["持仓成本降低幅度(%)"] > 0:
        print(f"✅ 做T有效：底仓成本降低 {perf['持仓成本降低幅度(%)']}%")
    return perf