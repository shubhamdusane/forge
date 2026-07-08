"""
forge CLI — command line interface.

Commands:
    forge analyze "description"  → analyze asset and print config
    forge check config.json      → validate a saved config
    forge scaffold config.json   → generate contracts from config
    forge demo                   → run with a built-in example (no API key needed)
"""

import argparse
import json
import sys
import os


def cmd_analyze(args):
    from .analyzer import AssetAnalyzer
    
    description = " ".join(args.description)
    
    analyzer = AssetAnalyzer(
        provider=args.provider,
    )
    
    print(f"🔬 Analyzing asset: {description[:80]}...")
    config = analyzer.analyze(description, verbose=args.verbose)
    
    output = config.to_json()
    
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"✅ Config saved to {args.output}")
    else:
        print("\n" + output)
    
    # Always print warnings
    if config.warnings:
        print("\n⚠ Warnings:")
        for w in config.warnings:
            print(f"  • {w}")
    
    if config.recommendations:
        print("\n💡 Recommendations:")
        for r in config.recommendations:
            print(f"  • {r}")


def cmd_check(args):
    from .validator import ComplianceValidator
    from .models import AssetConfig
    
    try:
        with open(args.config_file, "r") as f:
            config = AssetConfig.from_json(f.read())
    except FileNotFoundError:
        print(f"Error: File not found: {args.config_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.config_file}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to load config: {e}", file=sys.stderr)
        sys.exit(1)
    
    validator = ComplianceValidator()
    result = validator.validate(config)
    
    print(result)
    
    # Exit with non-zero if invalid
    if not result.is_valid:
        sys.exit(1)


def cmd_scaffold(args):
    from .scaffolder import Scaffolder
    from .models import AssetConfig
    
    try:
        with open(args.config_file, "r") as f:
            config = AssetConfig.from_json(f.read())
    except FileNotFoundError:
        print(f"Error: File not found: {args.config_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.config_file}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to load config: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Run validation first
    from .validator import ComplianceValidator
    validator = ComplianceValidator()
    result = validator.validate(config)
    
    if not result.is_valid:
        print("❌ Config has errors. Fix them before scaffolding:")
        for e in result.errors:
            print(f"  ✗ {e}")
        sys.exit(1)
    
    scaffolder = Scaffolder()
    scaffolder.generate(config, output_dir=args.output_dir)


def cmd_demo(args):
    """Run a demo without requiring an API key."""
    from .models import (
        AssetConfig, TokenConfig, ComplianceRules, OracleConfig, DividendConfig
    )
    from .validator import ComplianceValidator
    from .scaffolder import Scaffolder
    
    print("🎬 Running forge demo (no API key required)\n")
    
    # Manually construct a sample config (mimics what LLM would produce)
    config = AssetConfig(
        asset_type="real_estate",
        asset_name="Marina Bay Office Tower",
        asset_description="Grade A commercial office tower in Singapore CBD, fractional ownership via ERC-3643",
        jurisdiction="SG",
        token=TokenConfig(
            name="Marina Bay Office Tower Token",
            symbol="MBOT",
            decimals=18,
            max_supply=1_000_000,
            transferable=True,
            pausable=True,
        ),
        compliance=ComplianceRules(
            kyc_required=True,
            accredited_investor_only=True,
            max_investors=500,
            min_holding_period_days=90,
            max_holding_percentage=20.0,
            jurisdictions_blocked=["KP", "IR", "CU"],
            lock_period_days=180,
        ),
        oracle=OracleConfig(
            enabled=True,
            provider="chainlink",
            update_frequency_hours=24,
            staleness_threshold_hours=48,
        ),
        dividend=DividendConfig(
            enabled=True,
            payment_token="USDC",
            distribution_frequency="quarterly",
            auto_distribute=False,
        ),
        risk_level="medium",
        liquidity_profile="semi-liquid",
        analysis_summary=(
            "Singapore commercial real estate tokenized via ERC-3643. "
            "KYC required, accredited investors only, 180-day lock period. "
            "Quarterly USDC dividends from rental yield."
        ),
    )
    
    print("📋 Sample AssetConfig:")
    print(config.to_json())
    
    # Validate
    print("\n🔍 Running compliance validation...")
    validator = ComplianceValidator()
    result = validator.validate(config)
    print(result)
    
    # Scaffold
    output_dir = args.output_dir or "./forge-demo-contracts"
    print(f"\n🏗 Generating contracts in {output_dir}/...")
    scaffolder = Scaffolder()
    scaffolder.generate(config, output_dir=output_dir)
    
    print("\n✅ Demo complete!")


def main():
    parser = argparse.ArgumentParser(
        prog="forge",
        description="AI-assisted ERC-3643 Real World Asset tokenization scaffolder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  forge analyze "commercial real estate in Dubai, accredited investors only"
  forge analyze "US Treasury 10-year bond, retail investors" --output config.json
  forge check config.json
  forge scaffold config.json --output-dir ./my-token
  forge demo
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # analyze
    p_analyze = subparsers.add_parser("analyze", help="Analyze an asset description")
    p_analyze.add_argument("description", nargs="+", help="Natural language asset description")
    p_analyze.add_argument("--output", "-o", help="Save config to this JSON file")
    p_analyze.add_argument("--provider", default="anthropic", choices=["anthropic", "openai"])
    p_analyze.add_argument("--verbose", "-v", action="store_true")
    
    # check
    p_check = subparsers.add_parser("check", help="Validate a config JSON file")
    p_check.add_argument("config_file", help="Path to config.json")
    
    # scaffold
    p_scaffold = subparsers.add_parser("scaffold", help="Generate contracts from config")
    p_scaffold.add_argument("config_file", help="Path to config.json")
    p_scaffold.add_argument("--output-dir", "-o", default="./contracts", help="Output directory")
    
    # demo
    p_demo = subparsers.add_parser("demo", help="Run demo without API key")
    p_demo.add_argument("--output-dir", "-o", default=None)
    
    args = parser.parse_args()
    
    dispatch = {
        "analyze": cmd_analyze,
        "check": cmd_check,
        "scaffold": cmd_scaffold,
        "demo": cmd_demo,
    }
    
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
