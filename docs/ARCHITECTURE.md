# forge - Architecture

forge is a small Python package (no runtime dependencies; `anthropic` / `openai` are optional extras) with three stages:

```
description (text) --> AssetAnalyzer --> AssetConfig (dataclasses) --> ComplianceValidator --> ValidationResult
                                                 |
                                                 +--> Scaffolder --> contracts/, scripts/, hardhat.config.js, .env.example
```

| Module | Role | Notes |
|--------|------|-------|
| `forge/models.py` | `AssetConfig`, `TokenConfig`, `ComplianceRules`, `OracleConfig`, `DividendConfig`, `ValidationResult` | Plain dataclasses |
| `forge/analyzer.py` | Calls Anthropic or OpenAI with a system prompt and parses the JSON reply into an `AssetConfig` | The only non-deterministic stage; output is advisory |
| `forge/validator.py` | Applies hardcoded Python heuristics to an `AssetConfig` and returns errors, warnings and a 0-100 score | Not derived from statute; not a sanctions screen |
| `forge/scaffolder.py` | Renders string templates into Solidity (`Token.sol`, `Compliance.sol`), a Hardhat deploy script and config | Output is not compiled or tested in CI |
| `forge/cli.py` | `forge analyze | check | scaffold | demo` | `demo` uses a built-in config, no API key |

## What the generated contracts enforce

Only a holder cap, a lock period and a minimum holding period (in `Compliance.sol`). KYC, accredited-investor, blocked-jurisdiction, oracle and dividend settings live in the config and generated comments / `.env.example`; they are not enforced on-chain by forge's templates.

See the README's "Status & limitations" and `docs/AUDIT.md`.
