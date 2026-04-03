"""
股票数据工具
使用 akshare 获取股票数据
"""

import akshare as ak
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from .base import BaseTool


class StockDataTool(BaseTool):
    """股票数据工具"""
    name = "stock_data"
    description = "获取股票数据（历史行情、基本信息、财务数据）"
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行股票数据查询
        
        Args:
            stock_code: 股票代码（如 '002202'）
            data_type: 数据类型 ('history'=历史行情, 'info'=基本信息, 'finance'=财务数据)
            start_date: 开始日期（格式：'2024-01-01'）
            end_date: 结束日期（格式：'2024-12-31'）
            period: 周期 ('daily'=日线, 'weekly'=周线, 'monthly'=月线)
        
        Returns:
            股票数据字典
        """
        stock_code = kwargs.get('stock_code')
        data_type = kwargs.get('data_type', 'history')
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')
        period = kwargs.get('period', 'daily')
        
        if not stock_code:
            return {"error": "缺少股票代码参数"}
        
        try:
            # 添加市场前缀
            if stock_code.startswith('6'):
                full_code = f"sh{stock_code}"
            elif stock_code.startswith('0') or stock_code.startswith('3'):
                full_code = f"sz{stock_code}"
            else:
                full_code = stock_code
            
            result = {}
            
            if data_type == 'history':
                # 获取历史行情
                if not start_date:
                    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
                if not end_date:
                    end_date = datetime.now().strftime('%Y%m%d')
                
                try:
                    # 尝试使用 akshare 的股票历史行情接口
                    df = ak.stock_zh_a_hist(
                        symbol=stock_code,
                        period=period,
                        start_date=start_date,
                        end_date=end_date,
                        adjust="qfq"
                    )
                    
                    if not df.empty:
                        # 转换为字典列表
                        records = df.to_dict('records')
                        result = {
                            "stock_code": stock_code,
                            "data_type": "history",
                            "period": period,
                            "start_date": start_date,
                            "end_date": end_date,
                            "data_count": len(records),
                            "data": records[:100],  # 限制返回数量
                            "latest_price": df.iloc[-1]['收盘'] if '收盘' in df.columns else None,
                            "latest_date": df.iloc[-1]['日期'] if '日期' in df.columns else None
                        }
                    else:
                        result = {"error": "未获取到历史数据"}
                        
                except Exception as e:
                    # 备用方法：获取实时行情
                    try:
                        df = ak.stock_zh_a_spot_em()
                        stock_data = df[df['代码'] == stock_code]
                        if not stock_data.empty:
                            result = {
                                "stock_code": stock_code,
                                "data_type": "realtime",
                                "data": stock_data.iloc[0].to_dict()
                            }
                        else:
                            result = {"error": f"未找到股票 {stock_code}"}
                    except:
                        result = {"error": f"获取数据失败: {str(e)}"}
            
            elif data_type == 'info':
                # 获取基本信息
                try:
                    # 获取股票基本信息
                    df = ak.stock_individual_info_em(symbol=full_code)
                    if not df.empty:
                        info_dict = {}
                        for _, row in df.iterrows():
                            info_dict[row['item']] = row['value']
                        
                        result = {
                            "stock_code": stock_code,
                            "data_type": "info",
                            "info": info_dict
                        }
                    else:
                        result = {"error": "未获取到基本信息"}
                except Exception as e:
                    result = {"error": f"获取基本信息失败: {str(e)}"}
            
            elif data_type == 'finance':
                # 获取财务数据
                try:
                    # 获取资产负债表
                    df_balance = ak.stock_balance_sheet_by_report_em(symbol=full_code)
                    # 获取利润表
                    df_income = ak.stock_profit_sheet_by_report_em(symbol=full_code)
                    # 获取现金流量表
                    df_cash = ak.stock_cash_flow_sheet_by_report_em(symbol=full_code)
                    
                    result = {
                        "stock_code": stock_code,
                        "data_type": "finance",
                        "balance_sheet": df_balance.to_dict('records') if not df_balance.empty else [],
                        "income_statement": df_income.to_dict('records') if not df_income.empty else [],
                        "cash_flow": df_cash.to_dict('records') if not df_cash.empty else []
                    }
                except Exception as e:
                    result = {"error": f"获取财务数据失败: {str(e)}"}
            
            else:
                result = {"error": f"不支持的数据类型: {data_type}"}
            
            return result
            
        except Exception as e:
            return {"error": f"工具执行异常: {str(e)}"}
    
    def get_permission_level(self) -> int:
        """权限等级：数据查询为低权限"""
        return 1