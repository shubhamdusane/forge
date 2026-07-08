# forge

**AI-assisted ERC-3643 Real World Asset tokenization scaffolder.**

> Turn a natural language asset description into a deployment-ready ERC-3643 token in minutes, not weeks.

[![PyPI](https://img.shields.io/pypi/v/forge-rwa)](https://pypi.org/project/forge-rwa/)
[![Python](https://img.shields.io/pypi/pyversions/forge-rwa)](https://pypi.org/project/forge-rwa/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-14%20passing-brightgreen.svg)](tests/)

---

## Table of Contents

- [What is forge?](#what-is-forge)
- [The Problem](#the-problem)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [CLI Reference](#cli-reference)
- [Python API](#python-api)
- [Asset Types](#asset-types)
- [Architecture](#architecture)
- [ERC-3643 Explained](#erc-3643-explained)
- [Configuration Reference](#configuration-reference)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [License](#license)

---

## What is forge?

forge is a CLI tool and Python library that uses AI (Claude/GPT-4) to analyze natural language descriptions of real-world assets and generate deployment-ready ERC-3643 (T-REX) compliant token contracts.

**For beginners:** ERC-3643 is the Ethereum standard for tokenizing real-world assets like real estate, bonds, or art. Unlike regular ERC-20 tokens (which anyone can send to anyone), ERC-3643 tokens enforce compliance rules — you must be KYC-verified, an accredited investor, or meet other legal requirements before you can hold or transfer them.

---

## The Problem

Setting up a compliant RWA token from scratch takes **weeks**:

```
Week 1: Research which ERC standard to use
Week 2: Figure out compliance rules for your jurisdiction
Week 3: Write smart contracts from scratch
Week 4: Deploy to testnet and fix bugs
Week 5: Legal review of compliance configuration
Week 6: Mainnet deployment
```

**Getting these wrong isn't a UX problem — it's a legal problem.** An incorrect compliance configuration can mean your protocol violates securities law.

---

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR INPUT (Natural Language)            │
│                                                             │
│  "Grade A office building in Singapore CBD,                │
│   fractional ownership, accredited investors only,          │
│   quarterly rental yield distribution"                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              LLM ANALYSIS (Claude / GPT-4)                 │
│                                                             │
│  • Detects asset type: real_estate                          │
│  • Detects jurisdiction: SG (Singapore)                     │
│  • Maps compliance rules: KYC + accredited + lock period    │
│  • Recommends oracle: Chainlink NAV feed                   │
│  • Configures dividends: quarterly USDC distribution        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  ASSET CONFIG (JSON)                        │
│                                                             │
│  {                                                         │
│    "asset_type": "real_estate",                            │
│    "token": { "name": "SCOT", "symbol": "SCOT" },         │
│    "compliance": { "kyc_required": true, ... },            │
│    "oracle": { "provider": "chainlink", ... },             │
│    "dividend": { "frequency": "quarterly", ... }           │
│  }                                                         │
└──────────────┬──────────────────────┬───────────────────────┘
               │                      │
               ▼                      ▼
┌──────────────────────┐  ┌──────────────────────────────────┐
│    VALIDATOR         │  │    SCAFFOLDER                     │
│                      │  │                                   │
│  • ERC-3643 rules    │  │  • Token.sol (ERC-3643)          │
│  • Jurisdiction      │  │  • Compliance.sol                 │
│  • Lock periods      │  │  • IdentityRegistry.sol           │
│  • Score 0-100       │  │  • deploy.js (Hardhat)           │
│                      │  │  • hardhat.config.js             │
└──────────────────────┘  └──────────────────────────────────┘
```

---

## Installation

```bash
# With Anthropic Claude (recommended)
pip install forge-rwa[anthropic]
export ANTHROPIC_API_KEY=sk-ant-...

# With OpenAI GPT-4
pip install forge-rwa[openai]
export OPENAI_API_KEY=sk-...

# Both providers
pip install forge-rwa[all]

# Development tools
pip install forge-rwa[dev]
```

---

## Quick Start

### 1. Analyze an asset

```bash
forge analyze "US Treasury 10-year bond, retail investors eligible, semi-annual coupon" --output bond.json
```

### 2. Validate the config

```bash
forge check bond.json
```

### 3. Generate contracts

```bash
forge scaffold bond.json --output-dir ./my-token
cd my-token && npm install && npx hardhat compile
```

---

## CLI Reference

| Command | Description | Example |
|---------|-------------|---------|
| `forge analyze` | LLM-powered asset analysis | `forge analyze "real estate in Dubai"` |
| `forge check` | Validate compliance config | `forge check config.json` |
| `forge scaffold` | Generate Solidity contracts | `forge scaffold config.json -o ./token` |
| `forge demo` | Run without API key | `forge demo` |

---

## Python API

```python
from forge import AssetAnalyzer, ComplianceValidator, Scaffolder

# Analyze
analyzer = AssetAnalyzer()
config = analyzer.analyze("US Treasury bond, retail eligible, quarterly coupon")

# Validate
validator = ComplianceValidator()
result = validator.validate(config)
print(f"Score: {result.compliance_score}/100")

# Scaffold
if result.is_valid:
    scaffolder = Scaffolder()
    scaffolder.generate(config, output_dir="./my-token")
```

---

## Asset Types

| Type | KYC | Accredited Only | Lock Period | Oracle | Dividends |
|------|-----|-----------------|-------------|--------|-----------|
| `real_estate` | ✅ | Often | 90-180 days | NAV | Rental yield |
| `treasury_bond` | ✅ | No | Short | Price | Coupon |
| `private_equity` | ✅ | Yes | 1+ year | NAV | Dividends |
| `invoice` | ✅ | Institutional | Until maturity | Price | Interest |
| `carbon_credit` | Optional | No | None | Price | None |
| `art` | Optional | No | None | NAV | None |

---

## Architecture

```
forge/
├── forge/
│   ├── __init__.py          # Package exports
│   ├── cli.py               # CLI entry point
│   ├── models.py            # AssetConfig, TokenConfig, ComplianceRules
│   ├── analyzer.py          # LLM-powered asset analysis
│   ├── validator.py         # Compliance validation engine
│   ├── scaffolder.py        # Solidity contract generator
│   └── py.typed             # PEP 561 marker
├── tests/
│   └── test_forge.py        # 14 tests
├── pyproject.toml
├── LICENSE
└── CHANGELOG.md
```

---

## ERC-3643 Explained

**ERC-3643** (also called T-REX — Token for Regulated EXchanges) is the standard for compliant security tokens on EVM chains.

### The 4 Core Components

1. **ONCHAINID (Identity)** — Every token holder needs an on-chain identity linked to their KYC
2. **Identity Registry** — Maps wallet addresses → verified identities
3. **Compliance Module** — Enforces rules (max holders, lock periods, jurisdictions) on every transfer
4. **Token Contract** — ERC-3643 token that checks compliance before every transfer

### Why Not ERC-20?

ERC-20 has no compliance hooks — anyone can transfer to anyone. RWA tokens represent regulated securities requiring:
- KYC before receiving tokens
- Accredited investor verification
- Lock periods enforced on-chain
- Max holder counts (Reg D limits)
- Transfer restrictions (sanctioned countries blocked)

---

## Configuration Reference

```json
{
  "asset_type": "real_estate",
  "asset_name": "Singapore CBD Office Tower",
  "jurisdiction": "SG",
  "token": {
    "name": "Singapore CBD Office Tower Token",
    "symbol": "SCOT",
    "decimals": 18,
    "max_supply": 1000000,
    "transferable": true,
    "pausable": true
  },
  "compliance": {
    "kyc_required": true,
    "accredited_investor_only": true,
    "max_investors": 500,
    "lock_period_days": 180,
    "jurisdictions_blocked": ["KP", "IR", "CU", "SY"]
  },
  "oracle": {
    "enabled": true,
    "provider": "chainlink",
    "update_frequency_hours": 24
  },
  "dividend": {
    "enabled": true,
    "payment_token": "USDC",
    "distribution_frequency": "quarterly"
  }
}
```

---

## Contributing

```bash
git clone https://github.com/shubhamdusane/forge
cd forge
pip install -e ".[dev]"
pytest tests/
```

---

## Roadmap

- [x] v0.1 — analyze / check / scaffold (CLI + Python API)
- [ ] v0.2 — ONCHAINID integration
- [ ] v0.3 — Dividend distribution contracts
- [ ] v0.4 — Multi-jurisdiction templates (US/EU/UAE/SG)
- [ ] v0.5 — Testnet deployment wizard
- [ ] v1.0 — Full production suite

---

## License

MIT © 2026 Shubham Dusane
