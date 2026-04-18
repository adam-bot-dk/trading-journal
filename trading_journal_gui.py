#!/usr/bin/env python3
"""
Trading Journal - GUI Version
A simple Tkinter-based interface for tracking trades.

Author: Jonah Tillman (adam-bot-dk)
License: MIT
"""

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from dataclasses import dataclass, asdict
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


class TradingJournalApp:
    """Main GUI application"""
    
    def __init__(self, root, data_file: str = "trading_data.json"):
        self.root = root
        self.data_file = Path(data_file)
        self.trades: List[Trade] = []
        self.closed_days: List[str] = []
        
        self.root.title("Trading Journal")
        self.root.geometry("900x600")
        self.root.minsize(700, 500)
        
        # Load existing trades
        self.load()
        
        self.setup_ui()
        
        # Update stats on load
        self.update_stats()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Trading Journal", font=("Helvetica", 18, "bold"))
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Split into two panes: forms and trades
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.grid(row=1, column=0, sticky="nsew")
        
        # LEFT PANEL - Add Trade Form
        left_frame = ttk.LabelFrame(paned, text="Add New Trade", padding="10")
        paned.add(left_frame, weight=0)
        
        # Date
        ttk.Label(left_frame, text="Date:").grid(row=0, column=0, sticky="w", pady=5)
        self.date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        date_entry = ttk.Entry(left_frame, textvariable=self.date_var, width=15)
        date_entry.grid(row=0, column=1, sticky="w", padx=(5, 10), pady=5)
        ttk.Label(left_frame, text="(YYYY-MM-DD)").grid(row=0, column=2, sticky="w")
        
        # Ticker
        ttk.Label(left_frame, text="Ticker:").grid(row=1, column=0, sticky="w", pady=5)
        ticker_entry = ttk.Entry(left_frame, textvariable=tk.StringVar(), width=20)
        ticker_entry.grid(row=1, column=1, sticky="w", padx=(5, 10), pady=5)
        self.current_ticker = ticker_entry
        
        # Side
        ttk.Label(left_frame, text="Side:").grid(row=2, column=0, sticky="w", pady=5)
        self.side_var = tk.StringVar(value="long")
        side_combo = ttk.Combobox(left_frame, textvariable=self.side_var, values=['long', 'short'], width=17)
        side_combo.grid(row=2, column=1, sticky="w", padx=(5, 10), pady=5)
        
        # Entry Price
        ttk.Label(left_frame, text="Entry Price:").grid(row=3, column=0, sticky="w", pady=5)
        self.entry_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.entry_var, width=20).grid(row=3, column=1, sticky="w", padx=(5, 10), pady=5)
        
        # Exit Price
        ttk.Label(left_frame, text="Exit Price:").grid(row=4, column=0, sticky="w", pady=5)
        self.exit_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.exit_var, width=20).grid(row=4, column=1, sticky="w", padx=(5, 10), pady=5)
        
        # Contracts
        ttk.Label(left_frame, text="Contracts:").grid(row=5, column=0, sticky="w", pady=5)
        self.contracts_var = tk.StringVar(value="1")
        ttk.Spinbox(left_frame, from_=1, to=999, textvariable=self.contracts_var, width=20).grid(row=5, column=1, sticky="w", padx=(5, 10), pady=5)
        
        # Commission
        ttk.Label(left_frame, text="Commission:").grid(row=6, column=0, sticky="w", pady=5)
        self.commission_var = tk.StringVar(value="0")
        ttk.Entry(left_frame, textvariable=self.commission_var, width=20).grid(row=6, column=1, sticky="w", padx=(5, 10), pady=5)
        
        # Notes
        ttk.Label(left_frame, text="Notes:").grid(row=7, column=0, sticky="w", pady=5)
        self.notes_var = tk.StringVar()
        self.notes_entry = ttk.Entry(left_frame, textvariable=self.notes_var, width=35)
        self.notes_entry.grid(row=7, column=1, sticky="w", padx=(5, 10), pady=5)
        
        # Add button
        add_btn = ttk.Button(left_frame, text="Add Trade", command=self.add_trade)
        add_btn.grid(row=8, column=0, columnspan=3, pady=15)
        
        # RIGHT PANEL - Trades List
        right_frame = ttk.LabelFrame(paned, text="Trade History", padding="10")
        paned.add(right_frame, weight=1)
        
        # Treeview for trades
        columns = ('Date', 'Ticker', 'Side', 'Entry', 'Exit', 'Contracts', 'PnL')
        self.trades_tree = ttk.Treeview(right_frame, columns=columns, show='headings', height=15)
        
        self.trades_tree.heading('Date', text='Date')
        self.trades_tree.heading('Ticker', text='Ticker')
        self.trades_tree.heading('Side', text='Side')
        self.trades_tree.heading('Entry', text='Entry')
        self.trades_tree.heading('Exit', text='Exit')
        self.trades_tree.heading('Contracts', text='Contracts')
        self.trades_tree.heading('PnL', text='P&L')
        
        self.trades_tree.column('Date', width=90)
        self.trades_tree.column('Ticker', width=80)
        self.trades_tree.column('Side', width=60)
        self.trades_tree.column('Entry', width=90)
        self.trades_tree.column('Exit', width=90)
        self.trades_tree.column('Contracts', width=70)
        self.trades_tree.column('PnL', width=80)
        
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.trades_tree.yview)
        self.trades_tree.configure(yscrollcommand=scrollbar.set)
        
        self.trades_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        right_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)
        
        # Delete button
        delete_btn = ttk.Button(right_frame, text="Delete Selected", command=self.delete_trade)
        delete_btn.grid(row=1, column=0, columnspan=2, pady=5)
        
        # BOTTOM PANEL - Statistics
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="10")
        stats_frame.grid(row=2, column=0, sticky="ew", pady=10)
        main_frame.columnconfigure(0, weight=1)
        
        self.stats_text = tk.Text(stats_frame, height=4, wrap=tk.WORD, width=80)
        self.stats_text.grid(row=0, column=0, sticky="ew")
        self.stats_text.configure(state='disabled')
        
        # Buttons for actions
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, sticky="e", pady=(0, 0))
        
        ttk.Button(btn_frame, text="Refresh Stats", command=self.update_stats).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Export Report", command=self.export_report).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Clear All", command=self.clear_all).pack(side=tk.RIGHT, padx=5)
    
    def add_trade(self):
        """Add a new trade from form"""
        try:
            ticker = self.current_ticker.get().strip().upper()
            if not ticker:
                messagebox.showerror("Error", "Please enter a ticker symbol")
                return
            
            date = self.date_var.get().strip()
            if not self.validate_date(date):
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                return
            
            side = self.side_var.get()
            entry = float(self.entry_var.get() or 0)
            exit = float(self.exit_var.get() or 0)
            contracts = int(self.contracts_var.get() or 1)
            commission = float(self.commission_var.get() or 0)
            notes = self.notes_var.get().strip()
            
            if entry == 0 or exit == 0:
                messagebox.showerror("Error", "Please enter both entry and exit prices")
                return
            
            # Create and save trade
            trade = Trade(
                date=date,
                ticker=ticker,
                side=side,
                entry_price=entry,
                exit_price=exit,
                contracts=contracts,
                commission=commission,
                notes=notes
            )
            
            self.trades.append(trade)
            if trade.date not in self.closed_days:
                self.closed_days.append(trade.date)
            
            self.save()
            self.refresh_trades()
            self.update_stats()
            
            # Clear form
            self.entry_var.set('')
            self.exit_var.set('')
            self.notes_var.set('')
            
            messagebox.showinfo("Success", f"Trade added:\n{ticker} {side} @ ${entry} → ${exit}\nP&L: ${trade.pnl:,.2f}")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error adding trade: {e}")
    
    def validate_date(self, date_str: str) -> bool:
        """Validate date format"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def delete_trade(self):
        """Delete selected trade"""
        selected = self.trades_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a trade to delete")
            return
        
        if messagebox.askyesno("Confirm", "Delete this trade?"):
            item = self.trades_tree.item(selected[0])
            idx = item['values'][0]
            self.trades.pop(int(idx))
            self.save()
            self.refresh_trades()
            self.update_stats()
    
    def refresh_trades(self):
        """Refresh the trades list"""
        # Clear existing
        for item in self.trades_tree.get_children():
            self.trades_tree.delete(item)
        
        # Add trades
        for i, trade in enumerate(self.trades):
            pnl_color = 'green' if trade.pnl > 0 else 'red' if trade.pnl < 0 else 'black'
            pnl_text = f"${trade.pnl:+,.2f}"
            
            self.trades_tree.insert('', tk.END, text=str(i), 
                                  values=(trade.date, trade.ticker, trade.side, 
                                         f"${trade.entry_price:,.2f}", f"${trade.exit_price:,.2f}",
                                         trade.contracts, pnl_text),
                                  tags=(pnl_color,))
        
        self.trades_tree.tag_configure('green', foreground='green')
        self.trades_tree.tag_configure('red', foreground='red')
        self.trades_tree.tag_configure('black', foreground='black')
    
    def update_stats(self):
        """Update statistics display"""
        if not self.trades:
            stats = "No trades recorded yet. Add your first trade above!"
        else:
            stats = self.get_stats_summary()
        
        self.stats_text.configure(state='normal')
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats)
        self.stats_text.configure(state='disabled')
    
    def get_stats_summary(self) -> str:
        """Get summary statistics"""
        winning = [t for t in self.trades if t.pnl > 0]
        losing = [t for t in self.trades if t.pnl < 0]
        
        return f"""
=== TRADING JOURNAL STATS ===
Total Trades: {len(self.trades)} | Win Rate: {len(winning)/len(self.trades)*100:.1f}%
Total P&L: ${sum(t.pnl for t in self.trades):,.2f}

Winning: {len(winning)} | Losing: {len(losing)}
Best Trade: ${max(self.trades, key=lambda t: t.pnl).pnl:,.2f} ({max(self.trades, key=lambda t: t.pnl).ticker})
Worst Trade: ${min(self.trades, key=lambda t: t.pnl).pnl:,.2f} ({min(self.trades, key=lambda t: t.pnl).ticker})
"""
    
    def export_report(self):
        """Export full report to file"""
        filename = simpledialog.askstring("Export Report", "Enter filename (without extension):", initialvalue=datetime.now().strftime('%Y-%m-%d_report'))
        if filename:
            filepath = Path(f"{filename}.txt")
            report = f"""=== TRADING JOURNAL REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{self.get_stats_summary()}

=== ALL TRADES ===
"""
            for i, trade in enumerate(self.trades, 1):
                report += f"""
{i}. {trade.date} | {trade.ticker} | {trade.side.upper():5} | 
   Entry: ${trade.entry_price:,.2f} → Exit: ${trade.exit_price:,.2f} | 
   Contracts: {trade.contracts} | P&L: ${trade.pnl:,.2f}
   Points: {trade.points:.1f} | Notes: {trade.notes or '-'}
"""
            
            with open(filepath, 'w') as f:
                f.write(report)
            
            messagebox.showinfo("Exported", f"Report saved to:\n{filepath}")
    
    def clear_all(self):
        """Clear all trades"""
        if messagebox.askyesno("Confirm", "Delete ALL trades? This cannot be undone."):
            self.trades = []
            self.closed_days = []
            self.save()
            self.refresh_trades()
            self.update_stats()
    
    def load(self):
        """Load trades from JSON file"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    for t_data in data.get('trades', []):
                        self.trades.append(Trade(**t_data))
                    self.closed_days = data.get('closed_days', [])
            except Exception as e:
                messagebox.showwarning("Warning", f"Could not load data: {e}")
    
    def save(self):
        """Save trades to JSON file"""
        data = {
            'trades': [asdict(t) for t in self.trades],
            'closed_days': self.closed_days
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Trading Journal - GUI')
    parser.add_argument('--data', default='trading_data.json', help='Path to data file')
    args = parser.parse_args()
    
    root = tk.Tk()
    app = TradingJournalApp(root, args.data)
    root.mainloop()


if __name__ == '__main__':
    main()
