"""Tests for forge core modules — models, validator, and scaffolder."""

import json
import os
import tempfile

from forge.models import (
    AssetConfig,
    ComplianceRules,
    TokenConfig,
    ValidationResult,
)
from forge.scaffolder import Scaffolder
from forge.validator import ComplianceValidator

# ── MODEL TESTS ───────────────────────────────────────────────────────────────


class TestTokenConfig:
    def test_defaults(self):
        tc = TokenConfig(name="Test Token", symbol="TST")
        assert tc.decimals == 18
        assert tc.transferable is True
        assert tc.pausable is True
        assert tc.max_supply is None

    def test_custom_values(self):
        tc = TokenConfig(name="Test Token", symbol="TKN", decimals=8, max_supply=1000)
        assert tc.decimals == 8
        assert tc.max_supply == 1000


class TestComplianceRules:
    def test_defaults(self):
        cr = ComplianceRules()
        assert cr.kyc_required is True
        assert cr.accredited_investor_only is False
        assert cr.lock_period_days == 0

    def test_with_values(self):
        cr = ComplianceRules(
            kyc_required=True,
            accredited_investor_only=True,
            max_investors=200,
            lock_period_days=180,
        )
        assert cr.max_investors == 200
        assert cr.lock_period_days == 180


class TestAssetConfig:
    def _make_config(self, **overrides):
        defaults = dict(
            asset_type="treasury_bond",
            asset_name="US Treasury Bond",
            jurisdiction="US",
            token=TokenConfig(name="US Treasury Bond Token", symbol="USTB"),
            compliance=ComplianceRules(kyc_required=False),
        )
        defaults.update(overrides)
        return AssetConfig(**defaults)

    def test_roundtrip(self):
        config = self._make_config(
            asset_type="treasury_bond",
            token=TokenConfig(name="USTB Token", symbol="USTB"),
            compliance=ComplianceRules(kyc_required=False),
        )
        data = config.to_dict()
        restored = AssetConfig.from_dict(data)
        assert restored.asset_type == "treasury_bond"
        assert restored.token.symbol == "USTB"
        assert restored.compliance.kyc_required is False

    def test_to_json(self):
        config = self._make_config()
        j = config.to_json()
        data = json.loads(j)
        assert data["asset_name"] == "US Treasury Bond"

    def test_from_json(self):
        j = json.dumps(
            {
                "asset_type": "art",
                "asset_name": "Mona Lisa",
                "token": {"name": "Mona Lisa Token", "symbol": "MLT"},
            }
        )
        config = AssetConfig.from_json(j)
        assert config.asset_type == "art"
        assert config.asset_name == "Mona Lisa"

    def test_from_dict_unknown_keys(self):
        """from_dict should ignore unknown keys gracefully."""
        data = {
            "asset_type": "invoice",
            "unknown_field": "value",
            "token": {"name": "Invoice Token", "symbol": "INV"},
        }
        config = AssetConfig.from_dict(data)
        assert config.asset_type == "invoice"


# ── VALIDATOR TESTS ───────────────────────────────────────────────────────────


class TestComplianceValidator:
    def setup_method(self):
        self.validator = ComplianceValidator()

    def _make_config(self, **overrides):
        defaults = dict(
            asset_type="treasury_bond",
            asset_name="Test Bond",
            jurisdiction="US",
            token=TokenConfig(name="Test Bond Token", symbol="TBT"),
            compliance=ComplianceRules(kyc_required=True),
        )
        defaults.update(overrides)
        return AssetConfig(**defaults)

    def test_valid_config(self):
        config = self._make_config(
            compliance=ComplianceRules(kyc_required=True),
        )
        result = self.validator.validate(config)
        assert result.is_valid is True
        assert result.compliance_score > 0

    def test_missing_kyc(self):
        config = self._make_config(
            asset_type="private_equity",
            compliance=ComplianceRules(kyc_required=False),
        )
        result = self.validator.validate(config)
        # Should have warnings about missing KYC for private equity
        assert len(result.warnings) > 0 or result.compliance_score < 100

    def test_score_range(self):
        config = self._make_config(
            asset_type="real_estate",
            compliance=ComplianceRules(kyc_required=True, lock_period_days=180),
        )
        result = self.validator.validate(config)
        assert 0 <= result.compliance_score <= 100

    def test_validation_result_str(self):
        result = ValidationResult(is_valid=True, compliance_score=95)
        s = str(result)
        assert "VALID" in s
        assert "95" in s


# ── SCAFFOLDER TESTS ──────────────────────────────────────────────────────────


class TestScaffolder:
    def test_generate_creates_files(self):
        config = AssetConfig(
            asset_type="treasury_bond",
            asset_name="Test Bond",
            token=TokenConfig(name="Test Bond Token", symbol="TBT"),
            compliance=ComplianceRules(kyc_required=True, lock_period_days=30),
        )
        scaffolder = Scaffolder()
        with tempfile.TemporaryDirectory() as tmpdir:
            scaffolder.generate(config, output_dir=tmpdir)
            # Files are in subdirectories
            contracts_dir = os.path.join(tmpdir, "contracts")
            scripts_dir = os.path.join(tmpdir, "scripts")
            assert os.path.isdir(contracts_dir)
            assert os.path.isdir(scripts_dir)
            assert "Token.sol" in os.listdir(contracts_dir)
            assert "Compliance.sol" in os.listdir(contracts_dir)
            assert "deploy.js" in os.listdir(scripts_dir)

    def test_generate_sol_not_empty(self):
        config = AssetConfig(
            asset_type="real_estate",
            asset_name="Test RE",
            token=TokenConfig(name="Test RE Token", symbol="RE"),
            compliance=ComplianceRules(kyc_required=True),
        )
        scaffolder = Scaffolder()
        with tempfile.TemporaryDirectory() as tmpdir:
            scaffolder.generate(config, output_dir=tmpdir)
            token_sol = os.path.join(tmpdir, "contracts", "Token.sol")
            with open(token_sol, encoding="utf-8") as f:
                content = f.read()
            assert len(content) > 100
            assert "ERC3643" in content or "T-REX" in content or "erc3643" in content.lower()
