# forge — Self-assessment: threats, limitations and quality gates

> This is the author's own self-assessment. **No external audit of forge or of its generated contracts has been performed.**

## ⚠ Legal disclaimer

**forge generates code and configuration. It does NOT provide legal advice.**

Token offerings may constitute regulated securities in your jurisdiction. You are responsible for:

- Consulting a qualified securities lawyer before any token issuance
- Independent legal review of every generated config
- Independent smart-contract security audit before mainnet deployment
- Compliance with local KYC/AML, tax, data-protection law

forge's LLM analysis is a **starting point**, not a final answer.

---

## Threat model

| Threat | Vector | Mitigation |
|--------|--------|------------|
| LLM hallucinates compliance rule | Fabricated "Rule 506(x)" requirements | `ComplianceValidator` applies a small set of hardcoded heuristics to the parsed config (it does not verify the LLM's legal claims); human review required |
| Prompt injection in asset description | User-supplied NL → LLM | Output is advisory JSON; no execution; user reviews before scaffold |
| Generated contract has exploitable bug | Unaudited scaffolded Solidity | Not mitigated. Output is unaudited and uncompiled in CI; the token extends the T-REX base, the compliance contract is forge's own template code. Independent audit required before any real use |
| Private key leakage | `.env.example` committed | Generated project ships `.env.example` only; the scaffold does not currently write a `.gitignore`, so add one before committing |
| Jurisdiction block list incomplete | OFAC/UN list changes | Static four-country list (KP, IR, CU, SY) in validator; no freshness guarantee and not enforced on-chain. Operator must verify current sanctions |
| Reentrancy on dividend distribution | Generated dividend contract | Not applicable in v0.1: no dividend contract is generated (planned v0.3) |
| Oracle manipulation | NAV/price oracle compromise | Config-only: oracle settings are not wired into generated contracts in v0.1 |
| Upgrade key compromise | Owner of Compliance contract | Not implemented in the scaffold. Operator must put admin keys behind a multisig themselves |

## ERC-3643 compliance matrix

| Requirement | How forge handles |
|-------------|-------------------|
| ONCHAINID identity verification | Deploy script uses stock T-REX IdentityRegistry; no ONCHAINID handling (planned v0.2) |
| Transfer pre-check | Compliance.sol called on every `transfer()` |
| KYC flag | `kyc_required=true` → IdentityRegistry gate |
| Lock period | Generated Compliance.sol tracks first-receipt timestamp (untested) |
| Max holders | Generated Compliance.sol checks a holder counter in canTransfer() (untested) |
| Jurisdiction block | Not enforced by generated contracts in v0.1 (config/comment only) |

## Regulatory mapping (v0.1)

| Jurisdiction | Rule | forge default |
|--------------|------|---------------|
| US | SEC Reg D 506(c) | accredited-only=true, KYC=true |
| US | SEC Reg D 506(b) | accredited=true up to 35 non-accredited, KYC=true |
| EU | MiCA CASP | KYC=true, EU passport check |
| SG | MAS digital assets | KYC=true, accredited for private |
| Global | OFAC/UN sanctions | KP, IR, SY, CU flagged by the validator if missing (not a sanctions screen) |

## Quality gates

- [ ] `pytest` all green across Py 3.10/3.11/3.12
- [ ] `ruff check .` clean
- [ ] `npx hardhat compile` success on scaffold output
- [ ] `slither` static analysis on generated contracts (manual in v0.1, CI in v0.2)
- [ ] `twine check dist/*`
- [ ] README compliance matrix matches validator ruleset

## Known limitations (v0.1.0)

1. No ONCHAINID integration — production needs full Tokeny integration.
2. Generated contracts are not compiled or tested in CI and no testnet deployment has been validated; deploy flow is manual.
3. Dividend contract generation deferred to v0.3.
4. Jurisdiction list static — no live sanctions feed.
5. Only English asset descriptions reliably parsed.

## Recommended pre-mainnet checklist

1. Independent securities-law opinion letter per jurisdiction
2. Smart-contract audit by reputable firm (Trail of Bits, OpenZeppelin, ConsenSys Diligence)
3. Testnet deployment + penetration test
4. KYC vendor integration (Sumsub, Jumio, Onfido)
5. Multisig ownership (Gnosis Safe) for all admin keys
6. Incident response playbook + pause mechanism tested
