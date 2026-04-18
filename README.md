# Trading Journal

A cross-platform Python trading journal for tracking trades, P&L, and performance across markets (Stocks, Futures, Crypto).

## Features

- Track trades with entry/exit prices, contracts, and notes
- Automatic P&L calculation for long and short positions  
- Win rate statistics and performance metrics
- Export trading reports
- JSON data storage for easy portability
- Command-line interface for quick data entry
- Cross-platform: Works on Mac, Windows, and Linux

## Installation

### Prerequisites

- Python 3.8 or higher

### Setup

```bash
# Clone the repository
git clone https://github.com/adam-bot-dk/trading-journal.git
cd trading-journal

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## Usage

### View Summary
```bash
python trading_journal.py
```

### Add a Trade
```bash
python trading_journal.py --add \
  --date 2026-04-18 \
  --ticker NQ \
  --side long \
  --entry 18500 \
  --exit 18520 \
  --contracts 10 \
  --notes "Breakout setup"
```

### View Statistics
```bash
python trading_journal.py --stats
```

### View All Trades for a Ticker
```bash
python trading_journal.py --ticker NQ
```

### View Trades for a Specific Date
```bash
python trading_journal.py --date 2026-04-18
```

### Generate Full Report
```bash
python trading_journal.py --report
```

## Data Storage

Trades are stored in `trading_data.json`:

```json
{
  "trades": [
    {
      "date": "2026-04-18",
      "ticker": "NQ",
      "side": "long",
      "entry_price": 18500,
      "exit_price": 18520,
      "contracts": 10,
      "commission": 0,
      "notes": "Breakout setup"
    }
  ],
  "closed_days": ["2026-04-18"]
}
```

## Output Examples

### Statistics Output
```
--- STATISTICS ---
Total Trades: 50
Win Rate: 62.0%
Total P&L: $12,450.00
Average P&L: $249.00

Winning: 31 | Losing: 19
Avg Win: $450.00 | Avg Loss: $280.00

Best Trade: $1,200.00 (NQ)
Worst Trade: -$560.00 (MES)
```

### Trade Entry
```
✓ Trade added: NQ long @ $18500 → $18520
  P&L: $200.00
```

## Custom Data File

Use a different data file:
```bash
python trading_journal.py --data my_journal.json --stats
```

## License

MIT License - Feel free to use, modify, and distribute.

## Contributing

Contributions welcome! Please feel free to submit pull requests.

## Author

Jonah Tillman (adam-bot-dk)

## Similar Tools

This was inspired by TradingJournal.exe (a Windows-only application). This Python version provides the same functionality with cross-platform support and open-source flexibility.
