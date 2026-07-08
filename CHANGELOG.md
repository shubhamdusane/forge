# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-08

### Added
- Initial release of forge-rwa
- `forge analyze` CLI command — LLM-powered asset description to AssetConfig JSON
- `forge check` CLI command — compliance validation against ERC-3643 rules
- `forge scaffold` CLI command — generates Solidity contracts and Hardhat deploy scripts
- Python API: `AssetAnalyzer`, `ComplianceValidator`, `Scaffolder`
- Support for asset types: real_estate, treasury_bond, private_equity, invoice, carbon_credit, art
- Jurisdiction-aware compliance rules (US, EU, SG, AE)
- Chainlink oracle integration for NAV/price feeds
- Dividend distribution configuration
- Comprehensive test suite
- `py.typed` marker for PEP 561
