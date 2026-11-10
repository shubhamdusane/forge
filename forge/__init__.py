"""
forge — AI-assisted ERC-3643 Real World Asset tokenization scaffolder.
Built by Shubham Dusane | github.com/shubhamdusane/forge
"""

__version__ = "0.1.0"
__author__ = "Shubham Dusane"

from .analyzer import AssetAnalyzer
from .models import AssetConfig, ComplianceRules, TokenConfig
from .scaffolder import Scaffolder
from .validator import ComplianceValidator

__all__ = [
    "AssetAnalyzer",
    "AssetConfig",
    "ComplianceRules",
    "ComplianceValidator",
    "Scaffolder",
    "TokenConfig",
]
