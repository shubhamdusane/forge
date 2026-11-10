"""
Data models for forge.
All configuration objects use Python dataclasses for serialization.
"""

import json
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class TokenConfig:
    """ERC-20 token parameters for the wrapped RWA token."""

    name: str
    symbol: str
    decimals: int = 18
    max_supply: int | None = None  # None = unlimited
    transferable: bool = True
    pausable: bool = True


@dataclass
class ComplianceRules:
    """
    ERC-3643 compliance rule configuration.

    ERC-3643 (T-REX protocol) requires:
    - An identity registry (who is allowed to hold tokens)
    - Compliance rules (what conditions must be met)
    - Transfer restrictions (can holders transfer freely?)
    """

    kyc_required: bool = True
    accredited_investor_only: bool = False
    max_investors: int | None = None
    min_holding_period_days: int = 0
    max_holding_percentage: float | None = None  # e.g. 10.0 = max 10% per holder
    jurisdictions_blocked: list[str] = field(default_factory=list)
    jurisdictions_allowed: list[str] = field(default_factory=list)  # empty = all allowed
    transfer_approval_required: bool = False
    lock_period_days: int = 0  # tokens locked after purchase


@dataclass
class OracleConfig:
    """Chainlink oracle configuration for NAV/price feeds."""

    enabled: bool = True
    provider: str = "chainlink"
    feed_address: str = ""  # Populated by scaffolder for known assets
    update_frequency_hours: int = 24
    staleness_threshold_hours: int = 48


@dataclass
class DividendConfig:
    """Yield/dividend distribution configuration."""

    enabled: bool = False
    payment_token: str = "USDC"  # Token used for payouts
    distribution_frequency: str = "monthly"  # daily, weekly, monthly, quarterly, annual
    auto_distribute: bool = False  # Requires human trigger if False


@dataclass
class AssetConfig:
    """
    Complete configuration for a Real World Asset tokenization.

    This is the primary output of `forge analyze`.
    It contains everything needed to deploy an ERC-3643 compliant token.
    """

    # Basic asset info
    asset_type: str = ""  # e.g. "real_estate", "treasury_bond", "private_equity"
    asset_name: str = ""
    asset_description: str = ""
    jurisdiction: str = ""  # Primary legal jurisdiction

    # Token configuration
    token: TokenConfig = field(default_factory=TokenConfig)

    # Compliance rules
    compliance: ComplianceRules = field(default_factory=ComplianceRules)

    # Oracle for price/NAV
    oracle: OracleConfig = field(default_factory=OracleConfig)

    # Dividend/yield
    dividend: DividendConfig = field(default_factory=DividendConfig)

    # Risk metadata
    risk_level: str = "medium"  # low, medium, high
    liquidity_profile: str = "illiquid"  # liquid, semi-liquid, illiquid

    # Warnings from analysis
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    # Raw LLM analysis
    analysis_summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AssetConfig":
        token = TokenConfig(**data.get("token", {}))
        compliance = ComplianceRules(**data.get("compliance", {}))
        oracle = OracleConfig(**data.get("oracle", {}))
        dividend = DividendConfig(**data.get("dividend", {}))

        return cls(
            asset_type=data.get("asset_type", ""),
            asset_name=data.get("asset_name", ""),
            asset_description=data.get("asset_description", ""),
            jurisdiction=data.get("jurisdiction", ""),
            token=token,
            compliance=compliance,
            oracle=oracle,
            dividend=dividend,
            risk_level=data.get("risk_level", "medium"),
            liquidity_profile=data.get("liquidity_profile", "illiquid"),
            warnings=data.get("warnings", []),
            recommendations=data.get("recommendations", []),
            analysis_summary=data.get("analysis_summary", ""),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "AssetConfig":
        return cls.from_dict(json.loads(json_str))


@dataclass
class ValidationResult:
    """Result of compliance validation."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    compliance_score: int = 0  # 0-100

    def __str__(self) -> str:
        status = "✅ VALID" if self.is_valid else "❌ INVALID"
        lines = [
            f"Validation Result: {status}",
            f"Compliance Score: {self.compliance_score}/100",
        ]
        if self.errors:
            lines.append("\nErrors:")
            for e in self.errors:
                lines.append(f"  ✗ {e}")
        if self.warnings:
            lines.append("\nWarnings:")
            for w in self.warnings:
                lines.append(f"  ⚠ {w}")
        return "\n".join(lines)
