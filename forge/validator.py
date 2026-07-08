"""
ComplianceValidator: Validates an AssetConfig against ERC-3643 requirements
and common compliance rules.

Why validation matters:
The biggest mistakes teams make when deploying RWA tokens:
1. No KYC for US investors → SEC Reg D violation → protocol shutdown
2. Missing lock period for private securities → immediate secondary market = securities violation  
3. Oracle staleness threshold too high → stale NAV = investor losses with no recourse
4. max_supply not set for fixed-supply assets → unexpected inflation
5. No transfer approval for non-fungible assets → compliance breach

The validator catches these BEFORE deployment.
"""

from typing import List
from .models import AssetConfig, ValidationResult

# Asset types that are almost always accredited-investor only in the US
TYPICALLY_ACCREDITED_ONLY = {
    "private_equity",
    "hedge_fund",
    "real_estate",  # commercial; residential can be retail
    "invoice",      # typically institutional
}

# Asset types where oracle is strongly recommended
ORACLE_RECOMMENDED = {
    "real_estate",
    "private_equity",
    "treasury_bond",
    "corporate_bond",
    "invoice",
}

# Jurisdictions that block US persons from certain securities
# (simplified — real implementation uses OFAC lists)
HIGH_RISK_JURISDICTIONS = ["KP", "IR", "CU", "SY"]


class ComplianceValidator:
    """
    Validates AssetConfig for ERC-3643 correctness and common compliance issues.
    
    Usage:
        validator = ComplianceValidator()
        result = validator.validate(config)
        print(result)
    """
    
    def validate(self, config: AssetConfig) -> ValidationResult:
        """
        Run all validation checks on an AssetConfig.
        
        Returns a ValidationResult with:
        - is_valid: True if no blocking errors
        - errors: List of must-fix issues
        - warnings: List of should-fix issues
        - compliance_score: 0-100 quality score
        """
        errors: List[str] = []
        warnings: List[str] = []
        score = 100
        
        # ── ERC-3643 HARD REQUIREMENTS ──
        
        if not config.compliance.kyc_required and config.asset_type in TYPICALLY_ACCREDITED_ONLY:
            errors.append(
                f"KYC must be enabled for {config.asset_type} assets. "
                "ERC-3643 identity registry requires it for regulated securities."
            )
            score -= 20
        
        if not config.token.name or len(config.token.name) < 3:
            errors.append("Token name must be at least 3 characters.")
            score -= 5
        
        if not config.token.symbol or len(config.token.symbol) < 2:
            errors.append("Token symbol must be at least 2 characters.")
            score -= 5
        
        if config.token.symbol and not config.token.symbol.isupper():
            warnings.append(
                f"Token symbol '{config.token.symbol}' should be uppercase "
                "by convention (e.g. 'DOTT' not 'dott')."
            )
            score -= 2
        
        # ── LOCK PERIOD ──
        
        if config.asset_type == "private_equity" and config.compliance.lock_period_days < 365:
            warnings.append(
                "Private equity tokens typically require a 1-year (365-day) lock period "
                f"under Reg D. Current: {config.compliance.lock_period_days} days."
            )
            score -= 10
        
        if config.asset_type == "real_estate" and config.compliance.min_holding_period_days < 90:
            warnings.append(
                "Real estate tokens typically recommend a 90-day minimum holding period "
                "to prevent immediate flipping and maintain regulatory compliance."
            )
            score -= 5
        
        # ── ORACLE ──
        
        if config.asset_type in ORACLE_RECOMMENDED and not config.oracle.enabled:
            warnings.append(
                f"Oracle is not enabled for {config.asset_type}. "
                "Without a price/NAV oracle, token holders have no way to verify "
                "asset valuation on-chain. Strongly recommended."
            )
            score -= 10
        
        if config.oracle.enabled and config.oracle.staleness_threshold_hours > 72:
            warnings.append(
                f"Oracle staleness threshold ({config.oracle.staleness_threshold_hours}h) "
                "is very high. If the oracle stops updating, stale NAV could mislead investors "
                "for days. Recommend ≤48h."
            )
            score -= 5
        
        # ── JURISDICTIONS ──
        
        blocked = set(config.compliance.jurisdictions_blocked)
        for jurisdiction in HIGH_RISK_JURISDICTIONS:
            if jurisdiction not in blocked:
                warnings.append(
                    f"High-risk jurisdiction '{jurisdiction}' is not in the blocked list. "
                    "Consider adding OFAC-sanctioned countries to avoid compliance violations."
                )
                score -= 3
        
        if config.jurisdiction == "US" and not config.compliance.accredited_investor_only:
            if config.asset_type in TYPICALLY_ACCREDITED_ONLY:
                errors.append(
                    f"US-jurisdiction {config.asset_type} tokens require accredited investor "
                    "verification under SEC Regulation D. Set accredited_investor_only=true."
                )
                score -= 20
        
        # ── SUPPLY ──
        
        if config.asset_type == "treasury_bond" and config.token.max_supply is None:
            warnings.append(
                "Treasury bond tokens should have a fixed max_supply matching the bond issuance. "
                "Unlimited supply for a bond token could allow unexpected dilution."
            )
            score -= 8
        
        # ── DIVIDENDS ──
        
        if config.asset_type in ("real_estate", "treasury_bond") and not config.dividend.enabled:
            warnings.append(
                f"{config.asset_type} tokens typically pay yield/dividends. "
                "Consider enabling dividend distribution for investor appeal."
            )
            score -= 3
        
        # ── TRANSFER RESTRICTIONS ──
        
        if (
            config.asset_type == "private_equity"
            and not config.compliance.transfer_approval_required
        ):
            warnings.append(
                "Private equity tokens typically require transfer approval "
                "(the issuer must approve each transfer). Without this, cap table management "
                "becomes difficult and Reg D compliance may be breached."
            )
            score -= 8
        
        # Clamp score
        score = max(0, min(100, score))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            compliance_score=score,
        )
