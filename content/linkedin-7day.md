# forge — 7-Day LinkedIn Launch Cycle

## Day 1 — Problem

Setting up a compliant Real World Asset token takes weeks. Getting it wrong is a legal problem, not a UX problem.

Every RWA team I've worked with asks the same questions in week one:

- Which ERC standard — ERC-20, ERC-1400, ERC-3643?
- Do we need KYC? Accredited-investor verification?
- What lock period is legal for private equity vs. treasury vs. real estate?
- How do we block sanctioned jurisdictions on-chain?
- How do we configure Chainlink oracles for NAV?

Getting these wrong doesn't mean a broken demo. It means the token itself may violate securities law the moment someone buys it.

The $10B+ RWA ecosystem is growing 40% year-over-year. Most teams are still figuring this out with Google searches, $500/hr legal calls, and trial and error.

I led an RWA protocol from architecture to mainnet. Built something to compress that knowledge into a CLI. More soon.

---

## Day 2 — Insight / Why ERC-3643 matters

ERC-20 was designed for crypto. RWA tokens are regulated securities. These are not the same problem.

ERC-20 has no compliance hooks. Anyone can transfer to anyone. That's fine for ETH. It's not fine for tokenized Singapore real estate with a 500-holder cap and accredited-investor requirement.

ERC-3643 (T-REX) encodes compliance in the protocol layer:

- KYC required before receiving tokens
- Accredited-investor verification for US securities
- Lock periods enforced on-chain
- Holder-count caps (Reg D limits)
- Transfer blocks to sanctioned jurisdictions

The difference: terms-of-service can be ignored. Protocol rules cannot.

If your RWA product is "ERC-20 + KYC on the frontend," auditors can still sue you. The checks have to be on-chain.

---

## Day 3 — Build in public

Building forge: natural-language asset description → production-ready ERC-3643 scaffold.

```
forge analyze "Grade A office building in Singapore CBD,
               fractional ownership, accredited only,
               quarterly rental yield"
```

→ AssetConfig JSON with KYC flags, lock periods, jurisdiction blocks, oracle config.

```
forge check singapore-office.json
```

→ compliance score 94/100 + warnings.

```
forge scaffold singapore-office.json --output-dir ./scot-token
```

→ Token.sol + Compliance.sol + Hardhat deploy scripts.

Today's milestone: validator now catches 12 common misconfigs — missing holder caps, inconsistent lock periods, oracle frequencies misaligned with yield cadence.

---

## Day 4 — Behind the scenes

The LLM in forge is NOT generic code generation. It's a 600-token system prompt packed with compressed domain knowledge:

- ERC-3643 spec (T-REX, Tokeny Solutions)
- SEC Reg D 506(b) vs 506(c) decision tree
- MiCA CASP requirements
- MAS Singapore digital asset rules
- Asset class → compliance template mapping

Every asset class has a different default:

- Private equity (US) → accredited only + 1yr lock
- Treasury bond → retail-eligible, short lock
- Real estate → KYC + 90–180d lock + holder cap
- Carbon credit → KYC optional, no lock
- Invoice → institutional only

The validator cross-checks the LLM output against hardcoded rules. LLM says "accredited=false for US 506(c)"? Validator catches it. Defense in depth.

---

## Day 5 — Tease launch

Shipping forge in 24h.

`pip install forge-rwa[anthropic]`
`forge analyze "your asset" --output config.json`

Goes from English to deployment-ready ERC-3643 project in 3 commands.

MIT license. Python-only interface, Solidity output.

**Not legal advice.** Still need a securities lawyer. Still need an independent contract audit. forge compresses the common cases; your counsel confirms them.

Anyone shipping RWA in the next 6 months — drop a comment, I'll run your asset through it pre-launch.

---

## Day 6 — 🚀 LAUNCH

forge is live.

```bash
pip install forge-rwa[anthropic]
export ANTHROPIC_API_KEY=sk-ant-...

forge analyze "commercial real estate in Dubai, accredited only" \
  --output dubai.json
forge check dubai.json
forge scaffold dubai.json --output-dir ./dubai-token
```

You get:

- AssetConfig JSON (compliance + oracle + dividend)
- Validator report with 0–100 compliance score
- Hardhat project with Token.sol, Compliance.sol, deploy scripts, .env.example

Works for real_estate, treasury_bond, private_equity, invoice, carbon_credit, art.

**Required after scaffold:** independent legal opinion + independent smart-contract audit before mainnet. forge gets you from zero to reviewable draft in 10 minutes, not 10 weeks.

MIT license. Repo + PyPI in comments.

---

## Day 7 — Learnings + CTA

A week of forge. What I learned:

1. **Compliance defaults beat compliance rules.** People don't read rules — they accept defaults. Better defaults = safer tokens.

2. **Validator > Analyzer.** LLMs hallucinate regs. Hardcoded validator catches the hallucinations. Two-layer architecture is non-optional for safety-critical LLM apps.

3. **Jurisdiction specificity is the moat.** "Compliant token" is fluff. "Compliant Reg D 506(c) token with Singapore MAS retail-eligible secondary" is a product.

4. **Solidity + CLI + LLM is underexplored.** Most AI tooling stops at off-chain. Generating on-chain rule enforcement from NL is a new surface.

5. **Legal disclaimers are a feature.** Every output reminds users: this is a draft, get a lawyer. Users respect this more than they tolerate it.

Next: ONCHAINID full integration, dividend contracts, multi-jurisdiction templates, testnet deployment wizard.

If you build RWA, try it. If you break it, open an issue. That's the v0.2 path.

Repo + PyPI below.
