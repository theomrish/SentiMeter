# SentiMeter

A live risk-on / risk-off meter for market days.
Reads the market's mood from data and news.

## What it does

SentiMeter reads scheduled economic releases and market news, and scores whether the day leans risk-on or risk-off.

## Setup

**Prerequisites:** Python 3.11 or later, and Git.

```bash
git clone https://github.com/theomrish/SentiMeter.git
cd SentiMeter
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
py report.py
```

On macOS or Linux, two of those lines differ:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### What you should see

```
Release                  Level      Move  Surprise
CPI YoY                   3.00     -0.20     +0.10
Core CPI YoY              3.70     -0.30     -0.10
Nonfarm Payrolls        254.00    +38.00    +74.00
Unemployment Rate         4.10     -0.10     -0.10
ISM Manufacturing PMI     49.10     +0.60     +1.50
```

Five scheduled economic releases, each reduced to three facts:
**level** (where the series is), **move** (`actual - prior`) and
**surprise** (`actual - consensus`).

### If it doesn't work

- **No `(.venv)` in your prompt after the activate step.** Everything after it
  installs into the wrong Python. Activate first, then install.
- **`pip install` says "already satisfied" for everything.** You are almost
  certainly not in the virtual environment. Check with `Get-Command python` —
  the path should be inside this project folder.
