"""Data models and constants for Harness Evaluator."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import re

# ── Constants ──────────────────────────────────────────────────────────
VERSION = "2.2.0"

SKILL_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
POML_TOPOLOGY_RE = re.compile(r'<let\s+name="topology">(.*?)</let>')
POML_HAS_ROLE = re.compile(r"<role>")
POML_HAS_TASK = re.compile(r"<task>")
POML_HAS_OUTPUT = re.compile(r"<output-format>")
POML_TAG_RE = re.compile(r"<(/?)(\w+)>")
POML_LET_RE = re.compile(r'<let\s+name="(\w+)">(.*?)</let>', re.DOTALL)

VALID_TOPOLOGIES = {"solo", "multi", "rag", "tools-first"}
VALID_TOOL_MODES = {"auto", "required", "none"}
VALID_PROVIDERS = {"openai", "gemini", "qwen", "anthropic", "deepseek"}
REQUIRED_LET_NAMES = {"topology", "providers", "tools", "bench_id"}


# ── Data Classes ───────────────────────────────────────────────────────

@dataclass
class HarnessCheck:
    id: str
    name: str
    description: str
    weight: float = 1.0
    passed: bool = False
    detail: str = ""
    files_found: list[str] = field(default_factory=list)

    @property
    def score(self) -> float:
        return self.weight if self.passed else 0.0


@dataclass
class Subsystem:
    id: str
    name: str
    description: str
    checks: list[HarnessCheck] = field(default_factory=list)

    @property
    def total_weight(self) -> float:
        return sum(c.weight for c in self.checks)

    @property
    def earned_weight(self) -> float:
        return sum(c.score for c in self.checks)

    @property
    def percentage(self) -> float:
        if self.total_weight == 0:
            return 0.0
        return round((self.earned_weight / self.total_weight) * 100, 1)

    @property
    def passed(self) -> bool:
        return self.percentage >= 50.0

    def summary(self) -> str:
        ok = sum(1 for c in self.checks if c.passed)
        total = len(self.checks)
        return f"{ok}/{total} checks — {self.percentage}%"


@dataclass
class POMLIssue:
    file: str
    line: int
    severity: str  # error, warning, info
    message: str
    code: str


# ── Grade helper ───────────────────────────────────────────────────────

def score_to_grade(score: float) -> tuple[str, str]:
    if score >= 80:
        return "🟢 EXCELENTE", "green"
    elif score >= 60:
        return "🔵 BUENO", "blue"
    elif score >= 40:
        return "🟡 REGULAR", "yellow"
    elif score >= 20:
        return "🟠 DÉBIL", "orange"
    else:
        return "🔴 CRÍTICO", "red"
