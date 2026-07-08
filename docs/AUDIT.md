# forge — Security, Compliance & Quality Audit

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
| LLM hallucinates compliance rule | Fabricated "Rule 506(x)" requirements | `ComplianceValidator` hardcodes known rules; LLM output cross-checked |
| Prompt injection in asset description | User-supplied NL → LLM | Output is advisory JSON; no execution; user reviews before scaffold |
| Generated contract has exploitable bug | Unaudited scaffolded Solidity | README + AUDIT demand independent audit; v0.1 scaffold uses battle-tested T-REX base |
| Private key leakage | `.env.example` committed | `.env` in `.gitignore` of generated project; README warns |
| Jurisdiction block list incomplete | OFAC/UN list changes | Documented freshness date; operator must verify current sanctions |
| Reentrancy on dividend distribution | Generated dividend contract | Checks-effects-interactions pattern; `ReentrancyGuard` import |
| Oracle manipulation | NAV/price oracle compromise | Chainlink recommended; mention flash-crash TWAP guards |
| Upgrade key compromise | Owner of Compliance contract | Scaffold uses multisig placeholder; README instructs Gnosis Safe |

## ERC-3643 compliance matrix

| Requirement | How forge handles |
|-------------|-------------------|
| ONCHAINID identity verification | Scaffolds IdentityRegistry stub; v0.2 full integration |
| Transfer pre-check | Compliance.sol called on every `transfer()` |
| KYC flag | `kyc_required=true` → IdentityRegistry gate |
| Lock period | Enforced via Compliance.sol holding timestamp |
| Max holders | Checked in canTransfer() |
| Jurisdiction block | Country code in identity claim → blocklist match |

## Regulatory mapping (v0.1)

| Jurisdiction | Rule | forge default |
|--------------|------|---------------|
| US | SEC Reg D 506(c) | accredited-only=true, KYC=true |
| US | SEC Reg D 506(b) | accredited=true up to 35 non-accredited, KYC=true |
| EU | MiCA CASP | KYC=true, EU passport check |
| SG | MAS digital assets | KYC=true, accredited for private |
| Global | OFAC/UN sanctions | KP, IR, SY, CU blocked by default |

## Quality gates

- [ ] `pytest` all green across Py 3.10/3.11/3.12
- [ ] `ruff check .` clean
- [ ] `npx hardhat compile` success on scaffold output
- [ ] `slither` static analysis on generated contracts (manual in v0.1, CI in v0.2)
- [ ] `twine check dist/*`
- [ ] README compliance matrix matches validator ruleset

## Known limitations (v0.1.0)

1. Stub ONCHAINID — production needs full Tokeny integration.
2. No testnet deployment validation — scaffolds compile, deploy flow is manual.
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
