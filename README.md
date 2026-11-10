# forge

**AI-assisted ERC-3643 Real World Asset tokenization scaffolder.**

> Turn a plain-English asset description into a **draft** ERC-3643 (T-REX) config and Solidity/Hardhat scaffold for legal and security review.

> **Not audited. Not for mainnet value.** The generated contracts have never been compiled in CI, tested on-chain, or reviewed by a smart-contract auditor or securities lawyer. See [Status & limitations](#status--limitations).

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
- [Status & limitations](#status--limitations)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [License](#license)

---

## What is forge?

forge is a CLI tool and Python library that uses an LLM (Anthropic or OpenAI) to turn a natural-language description of a real-world asset into a structured JSON config, runs that config through a small rule-based sanity checker, and then renders Solidity contract templates and a Hardhat deploy script from it. The output is a starting point for review, not a finished or compliant deployment.

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
│              LLM ANALYSIS (Claude / OpenAI)                │
│                                                             │
│  • Detects asset type: real_estate                          │
│  • Detects jurisdiction: SG (Singapore)                     │
│  • Proposes compliance fields: KYC, accredited, lock period │
│  • Proposes an oracle setting (config only)                 │
│  • Proposes a dividend setting (config only)                │
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
│  • hardcoded          │  │  • contracts/Token.sol            │
│    Python heuristics │  │  • contracts/Compliance.sol       │
│  • Score 0-100       │  │  • scripts/deploy.js (Hardhat)    │
│                      │  │  • hardhat.config.js, .env.example│
└──────────────────────┘  └──────────────────────────────────┘
```

---

## Installation

```bash
# With Anthropic Claude (recommended)
pip install forge-rwa[anthropic]
export ANTHROPIC_API_KEY=sk-ant-...

# With OpenAI
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
# Review the generated files first. They have NOT been compiled or tested by this project.
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
│   ├── validator.py         # Rule-based config sanity checks (hardcoded heuristics)
│   ├── scaffolder.py        # Solidity/Hardhat template renderer
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

## Status & limitations

**Alpha (v0.1.0). Not audited. Not for mainnet value. Not legal advice.**

What it actually does:

- `forge analyze` sends your description to an LLM (Anthropic or OpenAI, your API key) and parses the reply into a JSON config. The LLM output is advisory and can be wrong.
- `forge check` runs `forge/validator.py`: a short list of **hardcoded Python heuristics** (for example: KYC on for private equity / real estate / invoice, US accredited-investor flag, 365-day lock for private equity, oracle recommended, a four-country blocklist of KP, IR, CU, SY). They are simplified rules of thumb written by the author. They are **not** derived from any statute, **not** a sanctions screen, **not** jurisdiction-aware beyond the few `if` statements in that file, and not checked by a lawyer. A high score does not mean a configuration is compliant.
- `forge scaffold` renders string templates into `contracts/Token.sol`, `contracts/Compliance.sol`, `scripts/deploy.js`, `hardhat.config.js`, `.env.example` and a package.json. The token extends the Tokeny T-REX `Token`; the compliance contract implements a holder cap, a lock period and a minimum holding period.

What it does NOT do (v0.1):

- The generated Solidity is **not compiled or tested in this repo's CI** and has never been deployed by this project. It may not compile against the T-REX version your `npm install` resolves.
- `jurisdictions_blocked`, `accredited_investor_only`, oracle and dividend settings are written into config, comments and `.env.example`, but are **not enforced by the generated contracts**. Only holder cap, lock period and minimum holding period are.
- ONCHAINID / identity-claim handling is not implemented; deployment relies on the stock T-REX identity registry that you must populate yourself.
- No dividend-distribution contract is generated (roadmap v0.3).
- No security audit, no formal verification, no legal opinion. Do not put real value or real investors on generated contracts.

Before anyone issues a real token you need, at minimum: a securities-law opinion per jurisdiction, an independent smart-contract audit, and a testnet deployment. See [docs/AUDIT.md](docs/AUDIT.md).

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
