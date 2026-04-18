#!/usr/bin/env python3
"""
Trading Journal - A cross-platform trading tracking application
Track your trades, P&L, and performance across markets (Stocks, Futures, Crypto)

Author: Jonah Tillman (adam-bot-dk)
License: MIT
"""

import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import List, Optional
from pathlib import Path


@dataclass
class Trade:
    """Represents a single trade"""
    date: str  # Format: YYYY-MM-DD
    ticker: str  # e.g., NQ, MES, AAPL, BTCUSD
    side: str  # 'long' or 'short'
    entry_price: float
    exit_price: float
    contracts: int
    commission: float = 0.0
    notes: str = ""
    
    @property
    def pnl(self) -> float:
        """Calculate profit/loss"""
        if self.side == 'long':
            gross = (self.exit_price - self.entry_price) * self.contracts
        else:  # short
            gross = (self.entry_price - self.exit_price) * self.contracts
        return gross - self.commission
    
    @property
    def points(self) -> float:
        """Return price movement in points"""
        return abs(self.exit_price - self.entry_price)


class TradingJournal:
    """Main trading journal class"""
    
    def __init__(self, data_file: Optional[str] = None):
        """Initialize the journal
        
        Args:
            data_file: Path to JSON data file. Defaults to trading_data.json
        """
        if data_file is None:
            data_file = "trading_data.json"
        
        self.data_file = Path(data_file)
        self.trades: List[Trade] = []
        self.closed_days: List[str] = []
        
        self.load()
    
    def load(self):
        """Load trades from JSON file"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.trades = [Trade(**t) for t in data.get('trades', [])]
                    self.closed_days = data.get('closed_days', [])
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not load data file: {e}")
                self.trades = []
                self.closed_days = []
    
    def save(self):
        """Save trades to JSON file"""
        data = {
            'trades': [asdict(t) for t in self.trades],
            'closed_days': self.closed_days
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_trade(self, trade: Trade):
        """Add a new trade"""
        self.trades.append(trade)
        
        # Check if day is already closed for trades
        if trade.date not in self.closed_days:
            self.closed_days.append(trade.date)
        
        self.save()
    
    def get_stats(self) -> dict:
        """Calculate trading statistics"""
        if not self.trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'total_pnl': 0,
                'win_rate': 0,
                'avg_pnl': 0,
                'best_trade': None,
                'worst_trade': None,
                'avg_wins': 0,
                'avg_losses': 0
            }
        
        winning_trades = [t for t in self.trades if t.pnl > 0]
        losing_trades = [t for t in self.trades if t.pnl < 0]
        
        best_trade = max(self.trades, key=lambda t: t.pnl)
        worst_trade = min(self.trades, key=lambda t: t.pnl)
        
        # Convert to dict manually to include properties
        def trade_to_dict(t):
            d = asdict(t)
            d['pnl'] = t.pnl
            d['points'] = t.points
            return d
        
        return {
            'total_trades': len(self.trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'total_pnl': sum(t.pnl for t in self.trades),
            'win_rate': (len(winning_trades) / len(self.trades) * 100) if self.trades else 0,
            'avg_pnl': sum(t.pnl for t in self.trades) / len(self.trades),
            'best_trade': trade_to_dict(best_trade) if best_trade else None,
            'worst_trade': trade_to_dict(worst_trade) if worst_trade else None,
            'avg_wins': sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0,
            'avg_losses': sum(t.pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0
        }
    
    def get_by_ticker(self, ticker: str) -> List[Trade]:
        """Get all trades for a specific ticker"""
        return [t for t in self.trades if t.ticker.upper() == ticker.upper()]
    
    def get_by_date(self, date: str) -> List[Trade]:
        """Get all trades for a specific date"""
        return [t for t in self.trades if t.date == date]
    
    def export_report(self) -> str:
        """Generate a text report of all trades"""
        stats = self.get_stats()
        
        report = f"""
=== TRADING JOURNAL REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

--- STATISTICS ---
Total Trades: {stats['total_trades']}
Win Rate: {stats['win_rate']:.1f}%
Total P&L: ${stats['total_pnl']:,.2f}
Average P&L: ${stats['avg_pnl']:,.2f}

Best Trade: ${stats['best_trade']['pnl']:,.2f} ({stats['best_trade']['ticker']} - {stats['best_trade']['side']})
Worst Trade: ${stats['worst_trade']['pnl']:,.2f} ({stats['worst_trade']['ticker']} - {stats['worst_trade']['side']})

--- ALL TRADES ---
"""
        for trade in self.trades:
            report += f"""
{trade.date} | {trade.ticker} | {trade.side.upper():5} | 
  Entry: ${trade.entry_price:,.2f} → Exit: ${trade.exit_price:,.2f} | 
  Contracts: {trade.contracts} | P&L: ${trade.pnl:,.2f}
  Points: {trade.points:.1f} | Notes: {trade.notes or '-'}
"""
        return report


def main():
    """CLI interface for Trading Journal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Trading Journal - Track and analyze your trades')
    parser.add_argument('--add', action='store_true', help='Add a new trade')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--report', action='store_true', help='Generate full report')
    parser.add_argument('--ticker', help='Filter by ticker')
    parser.add_argument('--date', help='Filter by date (YYYY-MM-DD)')
    parser.add_argument('--data', default='trading_data.json', help='Path to data file')
    
    # Add trade arguments
    add_parser = parser.add_argument_group('Add trade options')
    add_parser.add_argument('--trade-ticker', dest='ticker', help='Ticker symbol')
    add_parser.add_argument('--side', choices=['long', 'short'], help='Long or short')
    add_parser.add_argument('--entry', type=float, help='Entry price')
    add_parser.add_argument('--exit', type=float, help='Exit price')
    add_parser.add_argument('--contracts', type=int, help='Number of contracts')
    add_parser.add_argument('--pnl', type=float, help='P&L amount')
    add_parser.add_argument('--notes', help='Trade notes')
    
    args = parser.parse_args()
    journal = TradingJournal(args.data if hasattr(args, 'data') else 'trading_data.json')
    
    if args.add:
        trade = Trade(
            date=args.date or datetime.now().strftime('%Y-%m-%d'),
            ticker=args.ticker,
            side=args.side,
            entry_price=args.entry,
            exit_price=args.exit,
            contracts=args.contracts,
            notes=args.notes if hasattr(args, 'notes') else ''
        )
        journal.add_trade(trade)
        print(f"✓ Trade added: {trade.ticker} {trade.side} @ ${trade.entry_price} → ${trade.exit_price}")
        print(f"  P&L: ${trade.pnl:,.2f}")
    
    elif args.stats:
        if not journal.trades:
            print("No trades recorded yet. Add some with --add")
        else:
            stats = journal.get_stats()
            print(f"""
--- STATISTICS ---
Total Trades: {stats['total_trades']}
Win Rate: {stats['win_rate']:.1f}%
Total P&L: ${stats['total_pnl']:,.2f}
Average P&L: ${stats['avg_pnl']:,.2f}

Winning: {stats['winning_trades']} | Losing: {stats['losing_trades']}
Avg Win: ${stats['avg_wins']:,.2f} | Avg Loss: ${stats['avg_losses']:,.2f}

Best Trade: ${stats['best_trade']['pnl']:,.2f} ({stats['best_trade']['ticker']})
Worst Trade: ${stats['worst_trade']['pnl']:,.2f} ({stats['worst_trade']['ticker']})
""")
    
    elif args.report:
        print(journal.export_report())
    
    elif args.ticker:
        trades = journal.get_by_ticker(args.ticker)
        print(f"Trades for {args.ticker.upper()}: {len(trades)}")
        for t in trades:
            print(f"  {t.date} | {t.side} | ${t.entry_price}→${t.exit_price} | P&L: ${t.pnl:,.2f}")
    
    elif args.date:
        trades = journal.get_by_date(args.date)
        print(f"Trades on {args.date}: {len(trades)}")
        for t in trades:
            print(f"  {t.ticker} | {t.side} | ${t.entry_price}→${t.exit_price} | P&L: ${t.pnl:,.2f}")
    
    else:
        # Default: show summary
        print(f"Trading Journal - {journal.data_file}")
        print(f"Loaded {len(journal.trades)} trades")
        if journal.trades:
            stats = journal.get_stats()
            print(f"Total P&L: ${stats['total_pnl']:,.2f} | Win Rate: {stats['win_rate']:.1f}%")
            print("\nUse --help for more options")


if __name__ == '__main__':
    main()
