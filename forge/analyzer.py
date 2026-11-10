"""
AssetAnalyzer: Uses an LLM to analyze a natural language asset description
and extract a structured AssetConfig.

This is forge's core intelligence layer.

How it works:
1. Takes a natural language description: "tokenize a commercial real estate
   property in Dubai, fractional ownership for accredited investors only"
2. Constructs a structured prompt with ERC-3643 domain knowledge baked in
3. Calls the LLM (Claude or OpenAI)
4. Parses the JSON response into an AssetConfig
5. Adds recommendations based on asset type patterns

Why LLM vs. rules engine:
- RWA descriptions are highly varied (real estate, bonds, invoices, art, carbon credits)
- Compliance requirements differ by asset class and jurisdiction
- An LLM trained on securities law can infer requirements a rules engine would miss
  e.g. "commercial real estate in Dubai" → LLM knows UAE allows foreign ownership
  but has specific RERA (Real Estate Regulatory Authority) requirements
"""

import json
import os

from .models import (
    AssetConfig,
)

ANALYSIS_SYSTEM_PROMPT = """You are an expert in Real World Asset (RWA) tokenization, 
ERC-3643 (T-REX protocol), securities law, and DeFi compliance.

Your task: analyze an asset description and output a complete JSON configuration for 
tokenizing that asset as a draft configuration for human legal and security review.

You understand:
- ERC-3643 requires: identity registry (KYC), compliance rules, transfer restrictions
- Different asset classes have different regulatory requirements:
  * Real estate: often requires accredited investor status, long lock periods
  * Treasury bonds/government securities: lower restrictions, often retail-eligible
  * Private equity: typically requires accredited investors, long lock periods, transfer restrictions
  * Invoice financing: short duration, often institutional only
  * Carbon credits: few restrictions, but jurisdiction-specific
  * Art/collectibles: high illiquidity, often no dividends
- Jurisdictions matter: US (SEC), EU (MiCA), UAE (RERA/ADGM), Singapore (MAS), etc.
- Oracle requirements: real estate needs NAV oracles, bonds need yield/price feeds
- Dividend configs: bonds pay coupons, real estate pays rental yield, equity pays dividends

ALWAYS output valid JSON matching this exact schema. No explanations, no markdown, just JSON:
{
  "asset_type": "string (real_estate|treasury_bond|private_equity|invoice|carbon_credit|art|other)",
  "asset_name": "string (short memorable name for the token)",
  "asset_description": "string (1-2 sentence description)",
  "jurisdiction": "string (primary legal jurisdiction, e.g. US, UAE, EU, SG)",
  "token": {
    "name": "string (full token name, e.g. 'Dubai Office Tower Token')",
    "symbol": "string (3-5 char ticker, e.g. 'DOTT')",
    "decimals": 18,
    "max_supply": null or integer (null = unlimited, set for fixed-supply assets),
    "transferable": boolean,
    "pausable": true
  },
  "compliance": {
    "kyc_required": boolean,
    "accredited_investor_only": boolean,
    "max_investors": null or integer,
    "min_holding_period_days": integer,
    "max_holding_percentage": null or float,
    "jurisdictions_blocked": ["list of ISO country codes"],
    "jurisdictions_allowed": [],
    "transfer_approval_required": boolean,
    "lock_period_days": integer
  },
  "oracle": {
    "enabled": boolean,
    "provider": "chainlink",
    "feed_address": "",
    "update_frequency_hours": integer,
    "staleness_threshold_hours": integer
  },
  "dividend": {
    "enabled": boolean,
    "payment_token": "USDC",
    "distribution_frequency": "string (daily|weekly|monthly|quarterly|annual)",
    "auto_distribute": boolean
  },
  "risk_level": "string (low|medium|high)",
  "liquidity_profile": "string (liquid|semi-liquid|illiquid)",
  "warnings": ["list of compliance warnings the deployer must be aware of"],
  "recommendations": ["list of specific actions recommended before deployment"],
  "analysis_summary": "string (2-3 sentences summarizing the tokenization approach)"
}"""


class AssetAnalyzer:
    """
    Analyzes natural language asset descriptions to produce ERC-3643 configs.

    Usage:
        analyzer = AssetAnalyzer()  # uses ANTHROPIC_API_KEY env var
        config = analyzer.analyze("Commercial real estate in Dubai,
                                   fractional ownership for accredited investors")
        print(config.to_json())

    Supports:
        - Anthropic Claude (default, recommended)
        - OpenAI GPT-4 (set provider="openai")
        - Any OpenAI-compatible API
    """

    def __init__(
        self,
        provider: str = "anthropic",
        api_key: str | None = None,
        model: str | None = None,
    ):
        self.provider = provider

        if provider == "anthropic":
            self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError(
                    "Anthropic API key required. Set ANTHROPIC_API_KEY env var "
                    "or pass api_key parameter."
                )
            self.model = model or "claude-sonnet-4-20250514"

        elif provider == "openai":
            self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError(
                    "OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key parameter."
                )
            self.model = model or "gpt-4o"
        else:
            raise ValueError(f"Unknown provider: {provider}. Use 'anthropic' or 'openai'.")

    def analyze(self, description: str, verbose: bool = False) -> AssetConfig:
        """
        Analyze a natural language asset description.

        Args:
            description: Natural language description of the asset to tokenize.
                        e.g. "Grade A office building in Singapore CBD,
                               fractional ownership, targeting retail investors"
            verbose: If True, print raw LLM response for debugging.

        Returns:
            AssetConfig with all tokenization parameters populated.

        Raises:
            ValueError: If the LLM returns invalid JSON.
            RuntimeError: If the API call fails.
        """
        if verbose:
            print(f"[forge] Analyzing: {description[:80]}...")

        if self.provider == "anthropic":
            raw = self._call_anthropic(description)
        else:
            raw = self._call_openai(description)

        if verbose:
            print(f"[forge] Raw response:\n{raw}")

        return self._parse_response(raw)

    def _call_anthropic(self, description: str) -> str:
        """Call Anthropic Claude API."""
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic package required. Install with: pip install anthropic")

        client = anthropic.Anthropic(api_key=self.api_key)

        message = client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=ANALYSIS_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Analyze this asset and produce the tokenization config:\n\n{description}",
                }
            ],
        )

        return message.content[0].text

    def _call_openai(self, description: str) -> str:
        """Call OpenAI GPT API."""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package required. Install with: pip install openai")

        client = OpenAI(api_key=self.api_key)

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Analyze this asset and produce the tokenization config:\n\n{description}",
                },
            ],
            response_format={"type": "json_object"},
            max_tokens=2048,
        )

        return response.choices[0].message.content

    def _parse_response(self, raw: str) -> AssetConfig:
        """Parse raw JSON response into AssetConfig."""
        # Strip markdown code blocks if present
        clean = raw.strip()
        if clean.startswith("```"):
            lines = clean.split("\n")
            clean = "\n".join(lines[1:-1])

        try:
            data = json.loads(clean)
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM returned invalid JSON: {e}\n\nRaw response:\n{raw}")

        return AssetConfig.from_dict(data)
