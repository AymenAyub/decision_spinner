# 🎡 Decision Spinner

A fun little desktop app that spins a colorful wheel and randomly picks a decision for you. Built with **Python + Tkinter** — no external dependencies.

## Features

- 🎨 Clean, modern dark UI with a colorful spinning wheel
- 🍕 Preset categories: Food, Movies, Study, Weekend, Custom
- ➕ Add / ➖ Remove your own options (duplicates & blanks are ignored)
- 🌀 Smooth `after()`-based wheel animation with ease-out deceleration
- 🎯 The result always matches the slice under the fixed pointer
- 📜 Recent results history (last 5) with a Clear button
- 🔁 Reset options back to the category defaults
- ⚠️ Friendly prompt when there are fewer than 2 options

## Setup

```bash
# 1. Create a virtual environment
python -m venv venv

# 2. Activate it
#    Windows (PowerShell):
venv\Scripts\Activate.ps1
#    Windows (cmd):
venv\Scripts\activate.bat
#    macOS / Linux:
source venv/bin/activate

# 3. Run the app
python main.py
```

> No `pip install` needed — only the Python standard library is used.

## How it works

The wheel is drawn on a `tkinter.Canvas` as pie slices. When you press **SPIN**:

1. A winning option is chosen with `random.randint`.
2. The final rotation is computed so that option's slice lands exactly under the top pointer.
3. The wheel animates from its current rotation to the target using an ease-out curve, redrawn ~60 times per second via `root.after()` so the GUI never freezes.

## Project structure

```text
P3_decision_spinner/
├── venv/
├── main.py
└── README.md
```

Have fun letting the wheel decide! 🎉