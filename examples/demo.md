# forge — Walkthrough

Three commands. English → deployment-ready ERC-3643 project.

## Prerequisites

```bash
pip install forge-rwa[anthropic]
export ANTHROPIC_API_KEY=sk-ant-...
node --version   # v18+ for Hardhat
```

No API key? Use demo:

```bash
forge demo --output demo.json
```

---

## 1. Analyze

```bash
forge analyze "Grade A office building in Singapore CBD, \
               fractional ownership, accredited investors only, \
               quarterly rental yield distribution" \
  --output singapore-office.json
```

Result: `singapore-office.json` (see `examples/singapore-office.json` for reference).

Key fields to review:

- `compliance.kyc_required` — always true for regulated assets
- `compliance.accredited_investor_only` — verify matches your legal posture
- `compliance.lock_period_days` — confirm with counsel
- `compliance.jurisdictions_blocked` — update with latest sanctions list
- `oracle.update_frequency_hours` — match yield cadence

---

## 2. Check

```bash
forge check singapore-office.json
```

Expected output:

```
Validation Result: VALID
Compliance Score: 94/100

Warnings:
  - High-risk jurisdiction 'KP' already blocked. Good.
  - Oracle update 24h may lag quarterly NAV — consider 6h during distribution window.
```

Fix warnings before proceeding.

---

## 3. Scaffold

```bash
forge scaffold singapore-office.json --output-dir ./scot-token
```

Creates:

```
scot-token/
  contracts/
    Token.sol
    Compliance.sol
    IdentityRegistry.sol
  scripts/deploy.js
  hardhat.config.js
  package.json
  .env.example
```

---

## 4. Compile + deploy (testnet only)

```bash
cd scot-token
npm install
cp .env.example .env
# edit .env with PRIVATE_KEY + RPC_URL + ETHERSCAN_API_KEY
npx hardhat compile
npx hardhat run scripts/deploy.js --network sepolia
```

---

## 5. MANDATORY before mainnet

1. Securities-law opinion letter (per jurisdiction)
2. Smart-contract audit — Trail of Bits, OpenZeppelin, ConsenSys Diligence
3. Multisig ownership — Gnosis Safe
4. KYC vendor integration — Sumsub, Jumio, Onfido
5. Testnet soak + penetration test
6. Incident-response runbook + pause mechanism verified
