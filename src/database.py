"""
贾维斯 SQLite 数据库模块
轻量级本地存储方案

功能：
- 分析历史记录
- 自选股管理
- 持仓跟踪
- 用户偏好设置
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import pandas as pd

# 数据库路径
DB_PATH = Path(__file__).parent.parent.parent / "data" / "jarvis.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


class JarvisDB:
    """贾维斯数据库管理器"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(DB_PATH)
        self._init_db()
    
    def _get_conn(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self):
        """初始化数据库表"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # 1. 分析历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT NOT NULL,
                stock_name TEXT,
                analysis_type TEXT,
                decision TEXT,
                confidence REAL,
                score REAL,
                report TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 2. 自选股表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT UNIQUE NOT NULL,
                stock_name TEXT,
                industry TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # 3. 持仓记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT NOT NULL,
                stock_name TEXT,
                position_date DATE,
                price REAL,
                quantity REAL,
                amount REAL,
                stop_loss REAL,
                target_price REAL,
                status TEXT DEFAULT 'open',
                closed_at TIMESTAMP,
                pnl REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 4. 用户偏好表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 5. 板块轮动记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sector_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sector_name TEXT NOT NULL,
                sector_type TEXT,
                change_percent REAL,
                turnover_rate REAL,
                position_ratio REAL,
                recommendation TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 6. 周期战法记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cycle_strategy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                high_sectors TEXT,
                low_sectors TEXT,
                money_flow TEXT,
                recommendation TEXT,
                analysis_summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print(f"✅ 数据库初始化完成: {self.db_path}")
    
    # ==================== 分析历史 ====================
    
    def save_analysis(self, stock_code: str, stock_name: str = None,
                      analysis_type: str = None, decision: str = None,
                      confidence: float = None, score: float = None,
                      report: str = None) -> int:
        """保存分析记录"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO analysis_history 
            (stock_code, stock_name, analysis_type, decision, confidence, score, report)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (stock_code, stock_name, analysis_type, decision, confidence, score, report))
        analysis_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return analysis_id
    
    def get_analysis_history(self, stock_code: str = None, 
                            limit: int = 10) -> List[Dict]:
        """获取分析历史"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        if stock_code:
            cursor.execute('''
                SELECT * FROM analysis_history 
                WHERE stock_code = ?
                ORDER BY created_at DESC LIMIT ?
            ''', (stock_code, limit))
        else:
            cursor.execute('''
                SELECT * FROM analysis_history 
                ORDER BY created_at DESC LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_recent_decisions(self, days: int = 7) -> List[Dict]:
        """获取最近N天的决策"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM analysis_history 
            WHERE created_at >= datetime('now', '-' || ? || ' days')
            ORDER BY created_at DESC
        ''', (days,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # ==================== 自选股 ====================
    
    def add_watchlist(self, stock_code: str, stock_name: str = None,
                      industry: str = None, notes: str = None) -> bool:
        """添加自选股"""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO watchlist (stock_code, stock_name, industry, notes)
                VALUES (?, ?, ?, ?)
            ''', (stock_code, stock_name, industry, notes))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # 已存在
            conn.close()
            return False
    
    def remove_watchlist(self, stock_code: str) -> bool:
        """移除自选股"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM watchlist WHERE stock_code = ?', (stock_code,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    def get_watchlist(self, status: str = 'active') -> List[Dict]:
        """获取自选股列表"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM watchlist 
            WHERE status = ?
            ORDER BY added_at DESC
        ''', (status,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def update_watchlist_notes(self, stock_code: str, notes: str) -> bool:
        """更新自选股备注"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE watchlist SET notes = ? WHERE stock_code = ?
        ''', (notes, stock_code))
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated
    
    # ==================== 持仓管理 ====================
    
    def add_position(self, stock_code: str, stock_name: str,
                     position_date: str, price: float, quantity: float,
                     stop_loss: float = None, target_price: float = None) -> int:
        """添加持仓"""
        conn = self._get_conn()
        cursor = conn.cursor()
        amount = price * quantity
        cursor.execute('''
            INSERT INTO portfolio 
            (stock_code, stock_name, position_date, price, quantity, amount, stop_loss, target_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (stock_code, stock_name, position_date, price, quantity, amount, stop_loss, target_price))
        position_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return position_id
    
    def close_position(self, position_id: int, close_price: float) -> bool:
        """平仓"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # 获取持仓成本
        cursor.execute('SELECT price, quantity FROM portfolio WHERE id = ?', (position_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False
        
        cost_price, quantity = row['price'], row['quantity']
        pnl = (close_price - cost_price) * quantity
        
        # 更新持仓状态
        cursor.execute('''
            UPDATE portfolio 
            SET status = 'closed', closed_at = CURRENT_TIMESTAMP, pnl = ?
            WHERE id = ?
        ''', (pnl, position_id))
        conn.commit()
        conn.close()
        return True
    
    def get_open_positions(self) -> List[Dict]:
        """获取当前持仓"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM portfolio 
            WHERE status = 'open'
            ORDER BY position_date DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_position_summary(self) -> Dict:
        """获取持仓汇总"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # 总持仓数
        cursor.execute("SELECT COUNT(*) as count FROM portfolio WHERE status = 'open'")
        open_count = cursor.fetchone()['count']
        
        # 总市值
        cursor.execute("SELECT SUM(amount) as total FROM portfolio WHERE status = 'open'")
        total_amount = cursor.fetchone()['total'] or 0
        
        # 已平仓盈亏
        cursor.execute("SELECT SUM(pnl) as total_pnl FROM portfolio WHERE status = 'closed'")
        total_pnl = cursor.fetchone()['total_pnl'] or 0
        
        conn.close()
        return {
            'open_count': open_count,
            'total_amount': total_amount,
            'total_pnl': total_pnl
        }
    
    # ==================== 用户偏好 ====================
    
    def set_preference(self, key: str, value) -> bool:
        """设置用户偏好"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, json.dumps(value) if isinstance(value, (dict, list)) else str(value)))
        conn.commit()
        conn.close()
        return True
    
    def get_preference(self, key: str, default=None):
        """获取用户偏好"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM user_preferences WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()
        if row:
            try:
                return json.loads(row['value'])
            except:
                return row['value']
        return default
    
    # ==================== 板块分析 ====================
    
    def save_sector_analysis(self, sector_name: str, sector_type: str,
                             change_percent: float, turnover_rate: float,
                             position_ratio: float = None,
                             recommendation: str = None, notes: str = None) -> int:
        """保存板块分析"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sector_analysis 
            (sector_name, sector_type, change_percent, turnover_rate, 
             position_ratio, recommendation, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (sector_name, sector_type, change_percent, turnover_rate,
              position_ratio, recommendation, notes))
        analysis_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return analysis_id
    
    def get_sector_analysis_history(self, days: int = 30) -> List[Dict]:
        """获取板块分析历史"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM sector_analysis 
            WHERE created_at >= datetime('now', '-' || ? || ' days')
            ORDER BY created_at DESC
        ''', (days,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # ==================== 周期战法 ====================
    
    def save_cycle_strategy(self, date: str, high_sectors: List[str],
                           low_sectors: List[str], money_flow: Dict,
                           recommendation: str, analysis_summary: str) -> int:
        """保存周期战法分析"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO cycle_strategy 
            (date, high_sectors, low_sectors, money_flow, recommendation, analysis_summary)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (date, json.dumps(high_sectors), json.dumps(low_sectors),
              json.dumps(money_flow), recommendation, analysis_summary))
        strategy_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return strategy_id
    
    def get_latest_cycle_strategy(self) -> Optional[Dict]:
        """获取最新周期战法分析"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM cycle_strategy 
            ORDER BY date DESC LIMIT 1
        ''')
        row = cursor.fetchone()
        conn.close()
        if row:
            result = dict(row)
            # 解析JSON字段
            result['high_sectors'] = json.loads(result['high_sectors'])
            result['low_sectors'] = json.loads(result['low_sectors'])
            result['money_flow'] = json.loads(result['money_flow'])
            return result
        return None
    
    def get_cycle_strategy_history(self, days: int = 30) -> List[Dict]:
        """获取周期战法历史"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM cycle_strategy 
            WHERE date >= date('now', '-' || ? || ' days')
            ORDER BY date DESC
        ''', (days,))
        rows = cursor.fetchall()
        conn.close()
        result = []
        for row in rows:
            r = dict(row)
            r['high_sectors'] = json.loads(r['high_sectors'])
            r['low_sectors'] = json.loads(r['low_sectors'])
            r['money_flow'] = json.loads(r['money_flow'])
            result.append(r)
        return result
    
    # ==================== 统计功能 ====================
    
    def get_statistics(self) -> Dict:
        """获取数据库统计"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        stats = {}
        
        # 分析记录数
        cursor.execute('SELECT COUNT(*) as count FROM analysis_history')
        stats['analysis_count'] = cursor.fetchone()['count']
        
        # 自选股数量
        cursor.execute("SELECT COUNT(*) as count FROM watchlist WHERE status = 'active'")
        stats['watchlist_count'] = cursor.fetchone()['count']
        
        # 当前持仓
        cursor.execute("SELECT COUNT(*) as count FROM portfolio WHERE status = 'open'")
        stats['open_positions'] = cursor.fetchone()['count']
        
        # 平仓盈亏
        cursor.execute("SELECT SUM(pnl) as total FROM portfolio WHERE status = 'closed'")
        stats['total_pnl'] = cursor.fetchone()['total'] or 0
        
        conn.close()
        return stats
    
    def export_to_json(self, filepath: str = None) -> str:
        """导出所有数据为JSON"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        data = {}
        
        # 导出所有表
        tables = ['analysis_history', 'watchlist', 'portfolio', 
                  'user_preferences', 'sector_analysis', 'cycle_strategy']
        
        for table in tables:
            cursor.execute(f'SELECT * FROM {table}')
            rows = cursor.fetchall()
            data[table] = [dict(row) for row in rows]
        
        conn.close()
        
        filepath = filepath or f'/root/.openclaw/workspace/data/jarvis_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath


# ==================== 便捷函数 ====================

# 全局数据库实例
_db_instance = None

def get_db() -> JarvisDB:
    """获取数据库实例（单例）"""
    global _db_instance
    if _db_instance is None:
        _db_instance = JarvisDB()
    return _db_instance


# ==================== 使用示例 ====================

if __name__ == "__main__":
    db = JarvisDB()
    
    # 保存分析记录
    db.save_analysis(
        stock_code="002202",
        stock_name="金风科技",
        analysis_type="周期战法",
        decision="观望",
        confidence=0.65,
        score=7.5,
        report="风电板块处于低位，建议等待止跌信号"
    )
    
    # 添加自选股
    db.add_watchlist("002202", "金风科技", "风电设备", "周期低位关注")
    
    # 添加持仓
    db.add_position(
        stock_code="002202",
        stock_name="金风科技",
        position_date="2026-04-02",
        price=24.0,
        quantity=1000,
        stop_loss=22.0,
        target_price=28.0
    )
    
    # 获取统计
    print("\n📊 数据库统计:")
    print(db.get_statistics())
    
    print("\n📈 自选股:")
    print(db.get_watchlist())
    
    print("\n💼 持仓:")
    print(db.get_open_positions())
