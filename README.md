
# ⚡ Ultimate Data-Driven Market Intelligence Platform

![Status](https://img.shields.io/badge/Status-Production_Ready-green)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-lightgrey)

A professional-grade financial analysis terminal that attempts to "Solve the Market" using a fusion of **Deep Learning (LSTM/XGBoost)**, **Hyper-Intelligence (Causal Chains)**, and **Multi-Agent Systems**.

---

## 🏗️ System Architecture

This system uses a **Multi-Agent Orchestrator** to fuse signals from 6 distinct intelligence engines.

```mermaid
graph TD
    User([User]) --> CLI{Ultimate CLI}
    CLI --> Orchestrator[Analysis Orchestrator]
    
    subgraph "Data Fusion Layer"
        Orchestrator --> Tech[Technical Engine]
        Orchestrator --> Quant[Quant Engine]
        Orchestrator --> ML[Machine Learning]
        Orchestrator --> Sentinel[Sentiment Aggregator]
    end
    
    subgraph "Hyper-Intelligence Layer"
        Orchestrator --> Macro[🌍 Macro Engine]
        Orchestrator --> Forensics[🔍 Forensic Validator]
        Orchestrator --> Graph[🕸️ Knowledge Graph]
    end
    
    subgraph "Self-Learning Layer"
        RL[Feedback Loop] --> Orchestrator
        ML --> RL
        RL --> Weights[(Policy Weights)]
    end
    
    Quant --> Signal{Decision Engine}
    Tech --> Signal
    ML --> Signal
    Macro --> Signal
    
    Signal --> CLI
```

---

## 🚀 Quick Start

### 🐧 Linux / Mac
One command to install dependencies, start backend services, and launch the CLI:
```bash
./ultimate.sh
```
*Prompts for stock symbol (Default: `RELIANCE.NS`)*

### 🪟 Windows
Double-click `ultimate.bat` or run from CMD:
```cmd
ultimate.bat
```
*Auto-installs Python requirements if missing.*

---

## 🧠 Key Technologies

### 1. 🔮 Crystal Ball (Intraday Forecasting)
Uses high-frequency simulation to project price action **60 minutes** into the future.
- **Model**: Linear Regression on Volatility-Adjusted Returns.
- **Data**: 1-minute interval granularity.

### 2. 🕸️ Causal Intelligence Chain
Doesn't just look at price. Validates the **"Why"**:
- **Macro**: Scans for global risks (War, Sanctions, Weather).
- **Forensics**: Checks for accounting irregularities.
- **Graph**: Traces supply chain dependencies (e.g., Oil Price -> Paint Stocks).

### 3. 🛡️ Quantitative Rigor (CS229)
Models are mathematically verified:
- **LSTM**: Uses **Z-Score Normalization** (`(x-μ)/σ`) and **Huber Loss**.
- **XGBoost**: Uses **Scale_Pos_Weight** to correct for the rarity of profitable trade signals.
- **Regularization**: L1/L2 penalties to prevent overfitting.

---

## 📂 Project Structure

- `ultimate_cli.py`: The interactive terminal UI (Rich).
- `ultimate.sh` / `ultimate.bat`: Cross-platform launchers.
- `worker/src/`:
  - `orchestrator_enhanced.py`: Main logic hub.
  - `ml/`: LSTM and XGBoost models.
  - `engines/`: Decision, Macro, and Technical engines.
  - `knowledge_graph/`: NetworkX dependency graphs.

---

## 🛠️ Advanced Usage

**Direct Launch (Skip Menu):**
```bash
# Linux
./venv/bin/python ultimate_cli.py TATASTEEL.NS

# Windows
venv\Scripts\python ultimate_cli.py TATASTEEL.NS
```

---

**Confidence Score** is a dynamic metric derived from the **Reinforcement Learning (RL)** feedback loop. It adjusts based on 20+ factors including historical accuracy for the specific ticker.
# Market-Analysis
