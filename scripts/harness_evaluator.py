#!/usr/bin/env python3
"""
Harness Evaluator v2 — 🔧 Agent Workspace Maturity Scanner
==============================================================
Evalúa la madurez del "harness" de cualquier proyecto para agentes de IA.
Combina código determinista (file scanning, 48 checks) con un pipeline LLM
para generar recomendaciones contextuales.

CLI puro. Sin dependencias externas. Sin servidores.

Subcomandos:
  scan <path>       Escanea un proyecto (comportamiento por defecto)
  poml validate     Valida recetas POML contra el schema
  poml lint         Analiza calidad de recetas POML
  poml coverage     Estadísticas de cobertura POML

Uso:
    harness scan /ruta/al/proyecto
    harness scan . --json
    harness scan . --llm
    harness poml validate /ruta --schema path/to/schema.yaml
    harness poml lint /ruta
    harness poml coverage /ruta
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

# ── Constants ──────────────────────────────────────────────────────────
VERSION = "2.1.0"

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


# ═══════════════════════════════════════════════════════════════════════
# POML VALIDATOR
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class POMLIssue:
    file: str
    line: int
    severity: str  # error, warning, info
    message: str
    code: str


class POMLValidator:
    """Valida y analiza recetas POML."""

    def __init__(self, root: str, schema_path: Optional[str] = None):
        self.root = Path(root).resolve()
        self.schema_path = Path(schema_path) if schema_path else None
        self.poml_files: list[Path] = []
        self._discover()

    def _discover(self) -> None:
        for f in self.root.rglob("*.poml"):
            rel = f.relative_to(self.root)
            # Skip hidden dirs
            if any(p.startswith(".") for p in rel.parts[:-1]):
                continue
            self.poml_files.append(f)
        self.poml_files.sort()

    # ── Validate ────────────────────────────────────────────────

    def validate(self) -> list[POMLIssue]:
        """Valida todos los .poml contra reglas estructurales y schema."""
        issues = []
        for f in self.poml_files:
            issues.extend(self._validate_file(f))
        return issues

    def _validate_file(self, path: Path) -> list[POMLIssue]:
        issues = []
        content = path.read_text(encoding="utf-8", errors="replace")
        lines = content.split("\n")
        rel = str(path.relative_to(self.root))

        # 1. Must start with <poml>
        stripped = content.strip()
        if not stripped.startswith("<poml>"):
            issues.append(POMLIssue(rel, 1, "error", "No comienza con <poml>", "P001"))

        # 2. Must close with </poml>
        if not stripped.endswith("</poml>"):
            last = len(lines)
            issues.append(POMLIssue(rel, last, "error", "No termina con </poml>", "P002"))

        # 3. Well-formed tags
        self._check_tag_balance(rel, content, issues)

        # 4. Required <let> names
        found_lets = set()
        for m in POML_LET_RE.finditer(content):
            name = m.group(1)
            found_lets.add(name)
            # Validate topology value
            if name == "topology":
                val = m.group(2).strip()
                if val not in VALID_TOPOLOGIES:
                    line = self._find_line(lines, m.start())
                    issues.append(POMLIssue(rel, line, "error",
                        f"Topology inválida: '{val}'. Válidas: {', '.join(sorted(VALID_TOPOLOGIES))}", "P010"))
            # Validate tool_mode
            if name == "tool_mode":
                val = m.group(2).strip()
                if val not in VALID_TOOL_MODES:
                    line = self._find_line(lines, m.start())
                    issues.append(POMLIssue(rel, line, "warning",
                        f"tool_mode inválido: '{val}'. Válidos: {', '.join(VALID_TOOL_MODES)}", "P011"))
            # Validate providers JSON
            if name == "providers":
                val = m.group(2).strip()
                try:
                    providers_dict = json.loads(val)
                    for prov in providers_dict:
                        if prov not in VALID_PROVIDERS:
                            line = self._find_line(lines, m.start())
                            issues.append(POMLIssue(rel, line, "warning",
                                f"Provider no estándar: '{prov}'. Estándar: {', '.join(sorted(VALID_PROVIDERS))}", "P012"))
                except json.JSONDecodeError:
                    line = self._find_line(lines, m.start())
                    issues.append(POMLIssue(rel, line, "error", "providers no es JSON válido", "P013"))

        for required in REQUIRED_LET_NAMES:
            if required not in found_lets:
                issues.append(POMLIssue(rel, 1, "error",
                    f"Falta <let name=\"{required}\"> requerido", "P020"))

        # 5. Must have <role> section
        if not POML_HAS_ROLE.search(content):
            issues.append(POMLIssue(rel, 1, "warning", "No tiene sección <role>", "P030"))

        # 6. Must have <task> section
        if not POML_HAS_TASK.search(content):
            issues.append(POMLIssue(rel, 1, "warning", "No tiene sección <task>", "P031"))

        return issues

    def _check_tag_balance(self, rel: str, content: str, issues: list[POMLIssue]) -> None:
        """Verifica que los tags XML estén balanceados."""
        # Simple stack-based check for poml, role, task, let, etc.
        # Skip <let> since it's self-closing in POML convention
        tag_pattern = re.compile(r"</?(\w+)[^>]*>")
        stack = []
        for m in tag_pattern.finditer(content):
            tag = m.group(1)
            if tag in ("let", "stylesheet", "commentary"):
                continue  # POML lets are self-closing
            if m.group().startswith("</"):
                if stack and stack[-1] == tag:
                    stack.pop()
                else:
                    issues.append(POMLIssue(rel, 1, "warning",
                        f"Tag de cierre </{tag}> sin apertura correspondiente", "P040"))
            elif not m.group().endswith("/>"):
                stack.append(tag)

    def _find_line(self, lines: list[str], pos: int) -> int:
        """Encuentra el número de línea para una posición."""
        total = 0
        for i, line in enumerate(lines):
            total += len(line) + 1  # +1 for newline
            if total > pos:
                return i + 1
        return len(lines)

    # ── Lint ───────────────────────────────────────────────────

    def lint(self) -> list[POMLIssue]:
        """Análisis más profundo de calidad de recetas POML."""
        issues = []
        for f in self.poml_files:
            issues.extend(self._lint_file(f))
        return issues

    def _lint_file(self, path: Path) -> list[POMLIssue]:
        issues = []
        content = path.read_text(encoding="utf-8", errors="replace")
        lines = content.split("\n")
        rel = str(path.relative_to(self.root))

        # L1: tool_aliases vs tools consistency
        lets = {m.group(1): m.group(2).strip() for m in POML_LET_RE.finditer(content)}

        tools_raw = lets.get("tools", "[]")
        aliases_raw = lets.get("tool_aliases", "{}")
        try:
            tools = json.loads(tools_raw) if isinstance(tools_raw, str) else tools_raw
            aliases = json.loads(aliases_raw) if isinstance(aliases_raw, str) else aliases_raw
        except json.JSONDecodeError:
            tools, aliases = [], {}

        # Check each tool has an alias or is standard
        standard_tools = {"fs.read", "fs.write", "fs.replace", "shell.run", "fs.search", "web.fetch"}
        if isinstance(tools, list):
            for tool in tools:
                if tool not in standard_tools and tool not in aliases:
                    # Check if it has a @provider suffix that's aliased
                    base = tool.split("@")[0] if "@" in tool else tool
                    if base not in aliases and base not in standard_tools:
                        issues.append(POMLIssue(rel, 1, "info",
                            f"Tool '{tool}' no tiene alias en tool_aliases", "L010"))

        # L2: topology appropriateness
        topo = lets.get("topology", "").strip()
        if topo == "solo" and len(self.poml_files) > 20:
            issues.append(POMLIssue(rel, 1, "info",
                "Topology 'solo' en proyecto grande (>20 recetas). ¿Considerar 'multi'?", "L020"))

        # L3: check for empty sections
        if POML_HAS_ROLE.search(content):
            role_match = re.search(r"<role>\s*</role>", content, re.DOTALL)
            if role_match:
                issues.append(POMLIssue(rel, 1, "warning", "Sección <role> vacía", "L030"))

        if POML_HAS_TASK.search(content):
            task_match = re.search(r"<task>\s*</task>", content, re.DOTALL)
            if task_match:
                issues.append(POMLIssue(rel, 1, "warning", "Sección <task> vacía", "L031"))

        # L4: output-format presence
        if not POML_HAS_OUTPUT.search(content):
            issues.append(POMLIssue(rel, 1, "info", "No tiene <output-format> definido", "L040"))

        # L5: temperature check (avoid 0.0 which disables creativity entirely)
        prov_raw = lets.get("providers", "{}")
        try:
            prov = json.loads(prov_raw) if isinstance(prov_raw, str) else prov_raw
            for pname, pconf in prov.items() if isinstance(prov, dict) else []:
                temp = pconf.get("temperature", 1.0) if isinstance(pconf, dict) else 1.0
                if temp == 0.0:
                    issues.append(POMLIssue(rel, 1, "info",
                        f"Provider '{pname}' temperature=0.0 (sin creatividad)", "L050"))
                elif temp > 1.0:
                    issues.append(POMLIssue(rel, 1, "info",
                        f"Provider '{pname}' temperature={temp} (muy alta para codegen)", "L051"))
        except json.JSONDecodeError:
            pass

        return issues

    # ── Coverage ───────────────────────────────────────────────

    def coverage(self) -> dict:
        """Estadísticas de cobertura y calidad POML."""
        total = len(self.poml_files)
        if total == 0:
            return {"total": 0, "message": "No se encontraron archivos .poml"}

        with_role = 0
        with_task = 0
        with_output = 0
        with_all_sections = 0
        with_topology = 0
        multi_provider = 0
        by_category: dict[str, int] = {}

        for f in self.poml_files:
            content = f.read_text(encoding="utf-8", errors="replace")
            rel = f.relative_to(self.root)
            category = rel.parts[0] if len(rel.parts) > 1 else "root"

            # Category count
            by_category[category] = by_category.get(category, 0) + 1

            # Sections
            has_role = bool(POML_HAS_ROLE.search(content))
            has_task = bool(POML_HAS_TASK.search(content))
            has_output = bool(POML_HAS_OUTPUT.search(content))
            has_topo = bool(POML_TOPOLOGY_RE.search(content))

            if has_role:
                with_role += 1
            if has_task:
                with_task += 1
            if has_output:
                with_output += 1
            if has_role and has_task and has_output:
                with_all_sections += 1
            if has_topo:
                with_topology += 1

            # Multi-provider
            providers_match = POML_LET_RE.findall(content)
            for name, val in providers_match:
                if name == "providers":
                    try:
                        prov = json.loads(val.strip())
                        if isinstance(prov, dict) and len(prov) >= 2:
                            multi_provider += 1
                    except json.JSONDecodeError:
                        pass
                    break

        return {
            "total": total,
            "by_category": dict(sorted(by_category.items())),
            "sections": {
                "with_role": with_role,
                "with_task": with_task,
                "with_output": with_output,
                "with_all_sections": with_all_sections,
            },
            "pct_with_role": round(with_role / total * 100, 1),
            "pct_with_task": round(with_task / total * 100, 1),
            "pct_with_output": round(with_output / total * 100, 1),
            "pct_complete": round(with_all_sections / total * 100, 1),
            "pct_with_topology": round(with_topology / total * 100, 1),
            "multi_provider_recipes": multi_provider,
        }


# ═══════════════════════════════════════════════════════════════════════
# SCANNER ENGINE (original)
# ═══════════════════════════════════════════════════════════════════════

class HarnessScanner:
    """Escanea un proyecto y evalúa los 6 subsistemas del harness."""

    def __init__(self, root: str):
        self.root = Path(root).resolve()
        if not self.root.is_dir():
            raise NotADirectoryError(f"El directorio no existe: {root}")
        self.subsystems: list[Subsystem] = []
        self._file_cache: dict[str, str] = {}

    def scan(self) -> list[Subsystem]:
        self.subsystems = []
        self._scan_instructions()
        self._scan_state()
        self._scan_verification()
        self._scan_scope()
        self._scan_lifecycle()
        self._scan_skills()
        return self.subsystems

    # ── File helpers ───────────────────────────────────────────────

    def _cache_read(self, path: Path) -> str:
        key = str(path)
        if key not in self._file_cache:
            try:
                self._file_cache[key] = path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                self._file_cache[key] = ""
        return self._file_cache[key]

    def _exists(self, *paths: str) -> Optional[Path]:
        for p in paths:
            candidate = self.root / p
            if candidate.exists():
                return candidate
        return None

    def _check_file(self, check: HarnessCheck, *paths: str) -> None:
        found = self._exists(*paths)
        check.passed = found is not None
        if found:
            check.detail = f"Encontrado: {found.relative_to(self.root)}"
            check.files_found = [str(found.relative_to(self.root))]
        else:
            check.detail = f"No encontrado: {', '.join(paths)}"

    def _check_content(self, check: HarnessCheck, pattern: str, *paths: str) -> None:
        found = self._exists(*paths)
        if not found:
            check.passed = False
            check.detail = f"No encontrado: {', '.join(paths)}"
            return
        content = self._cache_read(found)
        if re.search(pattern, content, re.IGNORECASE):
            check.passed = True
            check.detail = f"{found.relative_to(self.root)} contiene patrón"
            check.files_found = [str(found.relative_to(self.root))]
        else:
            check.passed = False
            check.detail = f"{found.relative_to(self.root)} no contiene patrón"

    def _find_files(self, patterns: list[str]) -> list[Path]:
        found = []
        for pat in patterns:
            for path in self.root.rglob(pat):
                rel = path.relative_to(self.root)
                parts = rel.parts[:-1] if rel.parts else []
                skip = False
                for p in parts:
                    if p.startswith(".") and p not in (".git", ".github"):
                        skip = True
                        break
                if skip:
                    continue
                found.append(path)
        return sorted(set(found))

    def _count_check(self, check: HarnessCheck, patterns: list[str], min_count: int = 1) -> None:
        files = self._find_files(patterns)
        check.files_found = [str(f.relative_to(self.root)) for f in files[:10]]
        check.passed = len(files) >= min_count
        if check.passed:
            check.detail = f"{len(files)} archivo(s) encontrado(s)"
        else:
            check.detail = f"Solo {len(files)} archivo(s), mínimo: {min_count}"

    def _count_dir(self, check: HarnessCheck, dirname: str, glob_pat: str = "*") -> None:
        d = self.root / dirname
        if not d.is_dir():
            check.passed = False
            check.detail = f"No existe directorio {dirname}/"
            return
        files = list(d.rglob(glob_pat))
        check.files_found = [str(f.relative_to(self.root)) for f in files[:5]]
        check.passed = len(files) > 0
        check.detail = f"{len(files)} archivo(s) en {dirname}/"

    # ═══════════════════════════════════════════════════════════════════
    # S1: Instructions
    # ═══════════════════════════════════════════════════════════════════

    def _scan_instructions(self) -> None:
        sub = Subsystem("instructions", "📋 Instructions",
                        "El agente necesita instrucciones claras sobre qué hacer y en qué orden.")
        checks = []

        c = HarnessCheck("1.1", "Briefing principal", "AGENTS.md o CLAUDE.md como punto de entrada", 3.0)
        self._check_file(c, "AGENTS.md", "CLAUDE.md", "AGENT.md")
        checks.append(c)

        c = HarnessCheck("1.2", "Progressive disclosure", "Directorio docs/ con documentación", 1.5)
        self._count_dir(c, "docs", "*.md")
        checks.append(c)

        c = HarnessCheck("1.3", "Plan/roadmap", "PLANNING.md, ROADMAP.md o docs/PLANNING.md", 1.5)
        self._check_file(c, "PLANNING.md", "ROADMAP.md", "docs/PLANNING.md")
        checks.append(c)

        c = HarnessCheck("1.4", "Rules de codificación", "RULES.md, CONVENTIONS.md o .cursorrules", 1.0)
        self._check_file(c, "RULES.md", "CONVENTIONS.md", ".cursorrules")
        checks.append(c)

        c = HarnessCheck("1.5", "README.md", "README con instrucciones setup/build/test", 1.0)
        self._check_content(c, r"(docker|install|setup|build|test|run|start)", "README.md")
        checks.append(c)

        c = HarnessCheck("1.6", "Briefings específicos", "Archivos BRIEF.md, CONTEXT.md o PRD en docs/", 0.5)
        briefs = list(self.root.rglob("BRIEF.md")) + list(self.root.rglob("CONTEXT.md")) + list(self.root.rglob("docs/**/PRD*.md"))
        c.passed = len(briefs) > 0
        c.files_found = [str(p.relative_to(self.root)) for p in briefs[:5]]
        c.detail = f"{len(briefs)} archivo(s) de briefing"
        checks.append(c)

        c = HarnessCheck("1.7", "SOUL.md (identidad)", "Define personalidad y propósito del agente", 1.0)
        self._check_file(c, "SOUL.md", "IDENTITY.md")
        checks.append(c)

        c = HarnessCheck("1.8", "TOOLS.md", "Documentación de herramientas locales del agente", 0.5)
        self._check_file(c, "TOOLS.md")
        checks.append(c)

        sub.checks = checks
        self.subsystems.append(sub)

    # ═══════════════════════════════════════════════════════════════════
    # S2: State
    # ═══════════════════════════════════════════════════════════════════

    def _scan_state(self) -> None:
        sub = Subsystem("state", "💾 State",
                        "El agente necesita persistencia: saber qué está hecho y qué sigue.")
        checks = []

        c = HarnessCheck("2.1", "Task tracking", "TASK.md con backlog activo y progreso", 3.0)
        self._check_content(c, r"(\[ \]|\[x\]|progreso|hito|task|backlog|TODO)", "TASK.md", "docs/TASK.md", "TODO.md")
        checks.append(c)

        c = HarnessCheck("2.2", "Estado funcional", "PROJECT_STATUS.md o STATUS.md", 1.5)
        self._check_file(c, "PROJECT_STATUS.md", "STATUS.md", "docs/STATUS.md")
        checks.append(c)

        c = HarnessCheck("2.3", "Memoria a largo plazo", "MEMORY.md con conocimiento curado", 2.0)
        self._check_file(c, "MEMORY.md")
        checks.append(c)

        c = HarnessCheck("2.4", "Diario de sesiones", "Directorio memory/ con notas diarias", 1.5)
        self._count_dir(c, "memory", "*.md")
        checks.append(c)

        c = HarnessCheck("2.5", "Historial git", "Repositorio git con historial reciente", 1.0)
        if (self.root / ".git").is_dir():
            c.passed = True
            c.detail = "Repositorio git inicializado"
        else:
            c.passed = False
            c.detail = "No hay repositorio .git"
        checks.append(c)

        c = HarnessCheck("2.6", "Persistencia externa", "Base de datos o almacenamiento externo", 0.5)
        storage = self._find_files(["*.db", "*.sqlite", "*.jsonl", "docker-compose.yml", "docker-compose.yaml"])
        c.passed = len(storage) > 0
        c.files_found = [str(f.relative_to(self.root)) for f in storage[:3]]
        c.detail = f"{len(storage)} archivo(s) de persistencia"
        checks.append(c)

        c = HarnessCheck("2.7", "Heartbeat system", "HEARTBEAT.md con checklist periódico", 0.5)
        self._check_file(c, "HEARTBEAT.md")
        checks.append(c)

        sub.checks = checks
        self.subsystems.append(sub)

    # ═══════════════════════════════════════════════════════════════════
    # S3: Verification
    # ═══════════════════════════════════════════════════════════════════

    def _scan_verification(self) -> None:
        sub = Subsystem("verification", "✅ Verification",
                        "El agente debe poder verificar su trabajo automáticamente.")
        checks = []

        c = HarnessCheck("3.1", "Directorio de tests", "tests/, test/, spec/ o __tests__/", 3.0)
        for td_name in ["tests", "test", "spec", "__tests__"]:
            td = self.root / td_name
            if td.is_dir() and list(td.iterdir()):
                test_count = sum(1 for _ in td.rglob("*"))
                c.passed = True
                c.detail = f"{td_name}/ ({test_count} archivos)"
                c.files_found = [str(td.relative_to(self.root))]
                break
        if not c.passed:
            c.detail = "No se encontró directorio de tests"
        checks.append(c)

        c = HarnessCheck("3.2", "Configuración de tests", "pytest.ini, vitest.config, Cargo.toml, etc.", 1.5)
        self._check_file(c, "pytest.ini", "pyproject.toml", "vitest.config.ts", "vitest.config.js",
                          "jest.config.ts", "jest.config.js", "Cargo.toml", "go.mod")
        checks.append(c)

        c = HarnessCheck("3.3", "Tests implementados", "Archivos de test con casos reales", 2.0)
        test_files = self._find_files(
            ["*test*.py", "*test*.ts", "*test*.js", "*spec*.py", "*spec*.ts", "*_test.rs",
             "test_*.py", "test_*.ts", "*test*.rs", "*.test.js", "*.test.ts", "*.spec.js", "*.spec.ts"]
        )
        c.files_found = [str(f.relative_to(self.root)) for f in test_files[:5]]
        c.passed = len(test_files) >= 2
        c.detail = f"{len(test_files)} archivo(s) de test" if c.passed else f"Solo {len(test_files)} test(s), mínimo: 2"
        checks.append(c)

        c = HarnessCheck("3.4", "CI/CD pipeline", "GitHub Actions, GitLab CI, CircleCI, etc.", 1.0)
        for cp in [".github/workflows", ".gitlab-ci.yml", ".circleci", "Jenkinsfile", ".drone.yml"]:
            if (self.root / cp).exists():
                c.passed = True
                c.detail = f"Encontrado: {cp}"
                c.files_found = [cp]
                break
        if not c.passed:
            c.detail = "No hay configuración CI/CD"
        checks.append(c)

        c = HarnessCheck("3.5", "Linter configurado", ".eslintrc, .ruff.toml, clippy.toml, etc.", 1.0)
        self._check_file(c, ".eslintrc*", ".prettierrc*", ".ruff.toml", "clippy.toml",
                          ".golangci.yml", ".flake8")
        checks.append(c)

        c = HarnessCheck("3.6", "Type checking", "tsconfig.json, mypy.ini, pyrightconfig.json", 0.5)
        for tc in ["tsconfig.json", "mypy.ini", "pyrightconfig.json", "Cargo.toml"]:
            if (self.root / tc).exists():
                c.passed = True
                c.detail = f"Encontrado: {tc}"
                c.files_found = [tc]
                break
        if not c.passed:
            c.detail = "No hay type checking configurado"
        checks.append(c)

        sub.checks = checks
        self.subsystems.append(sub)

    # ═══════════════════════════════════════════════════════════════════
    # S4: Scope
    # ═══════════════════════════════════════════════════════════════════

    def _scan_scope(self) -> None:
        sub = Subsystem("scope", "🎯 Scope",
                        "El agente debe trabajar una cosa a la vez, sin overreach.")
        checks = []

        c = HarnessCheck("4.1", "Definition of Done", "DoD explícito: criterios de finalización", 2.0)
        self._check_content(c,
            r"(definition.of.done|dod|done.when|criterios.de.aceptación|criterios.de.aceptacion)",
            "RULES.md", "CONTRIBUTING.md", "docs/PLANNING.md", "AGENTS.md", "CLAUDE.md")
        checks.append(c)

        c = HarnessCheck("4.2", "Milestones", "TASK.md con hitos y progreso", 2.0)
        task_file = self._exists("TASK.md", "docs/TASK.md", "TODO.md")
        if task_file:
            content = self._cache_read(task_file)
            has_milestones = bool(re.search(r"(hito|milestone|module|fase|phase|sprint)", content, re.IGNORECASE))
            has_progress = bool(re.search(r"(\d+%|progreso|progress|status|completado|hecho)", content, re.IGNORECASE))
            c.passed = has_milestones or has_progress
            c.detail = f"TASK.md con {'hitos y ' if has_milestones else ''}progreso" if c.passed else "TASK.md existe pero sin hitos ni progreso"
            c.files_found = [str(task_file.relative_to(self.root))]
        else:
            c.passed = False
            c.detail = "No hay TASK.md"
        checks.append(c)

        c = HarnessCheck("4.3", "Issue/PR templates", "Plantillas .github para issues y PRs", 1.0)
        templates = list(self.root.rglob(".github/ISSUE_TEMPLATE/*")) + list(self.root.rglob(".github/PULL_REQUEST_TEMPLATE/*"))
        c.passed = len(templates) > 0
        c.files_found = [str(t.relative_to(self.root)) for t in templates[:4]]
        c.detail = f"{len(templates)} plantilla(s)" if templates else "No hay plantillas .github/"
        checks.append(c)

        c = HarnessCheck("4.4", "Backlog", "Sección para issues descubiertos durante trabajo", 0.5)
        found_backlog = False
        for f in self.root.rglob("*.md"):
            if any(part.startswith(".") for part in f.relative_to(self.root).parts[:-1]):
                continue
            content = self._cache_read(f)
            if re.search(r"(discovered.during.work|backlog|por.hacer|icebox|pendiente)", content, re.IGNORECASE):
                found_backlog = True
                c.files_found = [str(f.relative_to(self.root))]
                break
        c.passed = found_backlog
        c.detail = "Backlog encontrado" if found_backlog else "No se encontró backlog"
        checks.append(c)

        c = HarnessCheck("4.5", "CONTRIBUTING.md", "Guía de contribución con límites de alcance", 1.0)
        self._check_file(c, "CONTRIBUTING.md", "CONTRIBUTING.adoc")
        checks.append(c)

        c = HarnessCheck("4.6", "USER.md", "Perfil del usuario: preferencias, estilo, contexto", 1.0)
        self._check_file(c, "USER.md")
        checks.append(c)

        c = HarnessCheck("4.7", "BOOTSTRAP.md", "Instrucciones de primer arranque para el agente", 0.5)
        self._check_file(c, "BOOTSTRAP.md")
        checks.append(c)

        sub.checks = checks
        self.subsystems.append(sub)

    # ═══════════════════════════════════════════════════════════════════
    # S5: Lifecycle
    # ═══════════════════════════════════════════════════════════════════

    def _scan_lifecycle(self) -> None:
        sub = Subsystem("lifecycle", "🔄 Lifecycle",
                        "El agente debe tener un ciclo de vida: init, trabajo, cleanup.")
        checks = []

        c = HarnessCheck("5.1", "Script de init", "init.sh, setup.sh, bootstrap, Makefile", 3.0)
        self._check_file(c, "init.sh", "setup.sh", "bootstrap.sh", "init.ps1", "Makefile", "bootstrap")
        checks.append(c)

        c = HarnessCheck("5.2", "Docker/Contenedor", "Dockerfile, docker-compose.yml o Containerfile", 2.0)
        self._check_file(c, "Dockerfile", "docker-compose.yml", "docker-compose.yaml", "Containerfile")
        checks.append(c)

        c = HarnessCheck("5.3", "Session handoff", "Procedimiento para retomar trabajo entre sesiones", 1.5)
        found_handoff = False
        for f in self.root.rglob("*.md"):
            if any(part.startswith(".") for part in f.relative_to(self.root).parts[:-1]):
                continue
            content = self._cache_read(f)
            if re.search(r"(handoff|clean.state|clean.restart|retomar|próxima.sesión)", content, re.IGNORECASE):
                found_handoff = True
                c.files_found = [str(f.relative_to(self.root))]
                break
        c.passed = found_handoff
        c.detail = "Handoff documentado" if found_handoff else "No hay procedimiento de handoff"
        checks.append(c)

        c = HarnessCheck("5.4", "Dependencias", "requirements.txt, package.json, Cargo.toml, etc.", 1.0)
        self._check_file(c, "requirements.txt", "package.json", "Cargo.toml", "go.mod",
                          "Gemfile", "pyproject.toml", "Pipfile")
        checks.append(c)

        c = HarnessCheck("5.5", "Config de entorno", ".env.example o .env.template", 1.0)
        self._check_file(c, ".env.example", ".env.template", ".env.sample")
        checks.append(c)

        c = HarnessCheck("5.6", ".gitignore", "Archivo de exclusión git", 0.5)
        self._check_file(c, ".gitignore")
        checks.append(c)

        c = HarnessCheck("5.7", "Licencia", "LICENSE, LICENSE.md o LICENSE.txt", 0.5)
        self._check_file(c, "LICENSE", "LICENSE.md", "LICENSE.txt")
        checks.append(c)

        c = HarnessCheck("5.8", ".env actual", "Archivo .env con configuración real", 0.5)
        self._check_file(c, ".env")
        checks.append(c)

        sub.checks = checks
        self.subsystems.append(sub)

    # ═══════════════════════════════════════════════════════════════════
    # S6: Skills & POML
    # ═══════════════════════════════════════════════════════════════════

    def _scan_skills(self) -> None:
        sub = Subsystem("skills", "🧠 Skills & POML",
                        "El proyecto debe tener un catálogo de skills bien estructurado.")
        checks = []

        c = HarnessCheck("6.1", "Directorio skills/", "skills/ con subdirectorios y SKILL.md", 3.0)
        skills_dir = self.root / "skills"
        if skills_dir.is_dir():
            skill_items = [d for d in skills_dir.iterdir() if d.is_dir()]
            skill_files = list(skills_dir.rglob("SKILL.md"))
            c.passed = len(skill_files) > 0
            c.files_found = [str(d.relative_to(self.root)) for d in skill_items[:8]]
            c.detail = f"{len(skill_files)} SKILL.md en {len(skill_items)} subdirectorios"
        else:
            c.passed = False
            c.detail = "No existe directorio skills/"
        checks.append(c)

        c = HarnessCheck("6.2", "Recetas POML", "poml/ con archivos .poml de agentes", 2.0)
        poml_dir = self.root / "poml"
        if poml_dir.is_dir():
            poml_files = list(poml_dir.rglob("*.poml"))
            c.passed = len(poml_files) > 0
            c.files_found = [str(f.relative_to(self.root)) for f in poml_files[:5]]
            c.detail = f"{len(poml_files)} archivo(s) .poml"
        else:
            c.passed = False
            c.detail = "No existe directorio poml/"
        checks.append(c)

        c = HarnessCheck("6.3", "Manifest de skills", "_registry/manifest.yaml con catálogo central", 2.0)
        self._check_file(c, "_registry/manifest.yaml", "_registry/manifest.yml")
        checks.append(c)

        c = HarnessCheck("6.4", "Esquema de validación", "schema/recipe.schema.yaml", 1.0)
        self._check_file(c, "schema/recipe.schema.yaml", "schema/recipe.schema.yml")
        checks.append(c)

        c = HarnessCheck("6.5", "SKILL.md frontmatter", "Todos los SKILL.md tienen YAML frontmatter", 2.0)
        skill_mds = list((self.root / "skills").rglob("SKILL.md")) if (self.root / "skills").is_dir() else []
        if skill_mds:
            all_have_fm = all(self._has_valid_frontmatter(f) for f in skill_mds)
            c.passed = all_have_fm
            c.files_found = [str(f.relative_to(self.root)) for f in skill_mds[:5]]
            c.detail = f"Todos los {len(skill_mds)} SKILL.md con frontmatter" if all_have_fm else "Algunos SKILL.md sin frontmatter válido"
        else:
            c.passed = False
            c.detail = "No hay SKILL.md para validar"
        checks.append(c)

        c = HarnessCheck("6.6", "POML topology", "Las recetas POML definen topology", 1.5)
        poml_dir = self.root / "poml"
        poml_files = list(poml_dir.rglob("*.poml")) if poml_dir.is_dir() else []
        if poml_files:
            all_have_topo = all(self._poml_has_topology(f) for f in poml_files)
            c.passed = all_have_topo
            c.files_found = [str(f.relative_to(self.root)) for f in poml_files[:3]]
            c.detail = f"{'Todas' if all_have_topo else 'Algunas'} recetas con <topology>"
        else:
            c.passed = False
            c.detail = "No hay archivos .poml"
        checks.append(c)

        c = HarnessCheck("6.7", "POML role + task", "Las recetas POML tienen <role> y <task>", 1.5)
        if poml_files:
            complete = sum(1 for f in poml_files if self._poml_has_role_task(f))
            c.passed = complete == len(poml_files)
            c.detail = f"{complete}/{len(poml_files)} recetas completas (role + task)"
            c.files_found = [str(f.relative_to(self.root)) for f in poml_files[:3]]
        else:
            c.passed = False
            c.detail = "No hay archivos .poml"
        checks.append(c)

        c = HarnessCheck("6.8", "Skill provider", "Script para cargar skills dinámicamente", 1.0)
        self._check_file(c, "_registry/skill-provider.js", "_registry/skill-provider.py", "_registry/provider")
        checks.append(c)

        c = HarnessCheck("6.9", "Multi-provider", "Recetas POML con múltiples providers (openai/gemini/qwen)", 1.0)
        multi_count = sum(1 for f in poml_files if self._poml_is_multi_provider(f))
        c.passed = multi_count >= 1
        c.detail = f"{multi_count} receta(s) multi-provider" if c.passed else "No hay recetas multi-provider"
        checks.append(c)

        c = HarnessCheck("6.10", "Variedad de skills", "Skills en múltiples categorías", 0.5)
        if skills_dir.is_dir():
            skill_subdirs = [d.name for d in skills_dir.iterdir() if d.is_dir()]
            c.passed = len(skill_subdirs) >= 5
            c.files_found = skill_subdirs[:10]
            c.detail = f"{len(skill_subdirs)} categorías de skills"
        else:
            c.passed = False
            c.detail = "No hay skills/"
        checks.append(c)

        c = HarnessCheck("6.11", "SKILLS_SYSTEM.md", "Documentación del sistema de skills", 0.5)
        self._check_file(c, "SKILLS_SYSTEM.md", "SKILLS.md")
        checks.append(c)

        c = HarnessCheck("6.12", "Skills versionados", "SKILL.md con versión y licencia en metadata", 0.5)
        if skill_mds:
            versioned = sum(1 for f in skill_mds if self._skill_has_version(f))
            c.passed = versioned >= len(skill_mds) * 0.5
            c.detail = f"{versioned}/{len(skill_mds)} skills versionados"
        else:
            c.passed = False
            c.detail = "No hay skills"
        checks.append(c)

        sub.checks = checks
        self.subsystems.append(sub)

    # ── Skill/POML helpers ─────────────────────────────────────────

    def _has_valid_frontmatter(self, path: Path) -> bool:
        content = self._cache_read(path)
        m = SKILL_FRONTMATTER_RE.match(content)
        if not m:
            return False
        try:
            import yaml
            yaml.safe_load(m.group(1))
            return True
        except Exception:
            return bool(re.search(r"^name:\s*\S+", m.group(1), re.MULTILINE))
        except ImportError:
            return bool(re.search(r"^name:\s*\S+", m.group(1), re.MULTILINE))

    def _poml_has_topology(self, path: Path) -> bool:
        return bool(POML_TOPOLOGY_RE.search(self._cache_read(path)))

    def _poml_has_role_task(self, path: Path) -> bool:
        content = self._cache_read(path)
        return bool(POML_HAS_ROLE.search(content)) and bool(POML_HAS_TASK.search(content))

    def _poml_is_multi_provider(self, path: Path) -> bool:
        content = self._cache_read(path)
        for name, val in POML_LET_RE.findall(content):
            if name == "providers":
                try:
                    prov = json.loads(val.strip())
                    return isinstance(prov, dict) and len(prov) >= 2
                except json.JSONDecodeError:
                    return False
        return False

    def _skill_has_version(self, path: Path) -> bool:
        content = self._cache_read(path)
        m = SKILL_FRONTMATTER_RE.match(content)
        if not m:
            return False
        fm = m.group(1)
        return bool(re.search(r"^version:", fm, re.MULTILINE)) or bool(re.search(r"license:", fm, re.MULTILINE))


# ── LLM Recommendations Generator ─────────────────────────────────────

def generate_llm_prompt(subsystems: list[Subsystem]) -> str:
    total_w = sum(s.total_weight for s in subsystems)
    earned_w = sum(s.earned_weight for s in subsystems)
    overall = round((earned_w / total_w * 100), 1) if total_w > 0 else 0.0

    prompt_parts = [
        "# Harness Evaluation Report — LLM Recommendations\n",
        f"Overall Score: {overall}%\n",
        "## Subsystem Scores\n",
    ]
    for s in subsystems:
        prompt_parts.append(f"- {s.name}: {s.percentage}% ({s.summary()})")

    prompt_parts.append("\n## Failed Checks (Needs Attention)\n")
    for s in subsystems:
        failed = [c for c in s.checks if not c.passed]
        if failed:
            prompt_parts.append(f"### {s.name}\n")
            for c in failed:
                prompt_parts.append(f"- [{c.id}] {c.name}: {c.detail}")

    prompt_parts.append("""
## Your Task
Eres un experto en Harness Engineering para agentes de IA. Basado en los resultados del scan:

1. **Prioriza** las 3-5 acciones más impactantes
2. **Recomienda** pasos concretos y accionables
3. **Sugiere** qué skills o archivos crear primero
4. **Identifica** riesgos si no se abordan

Responde en español, concreto, sin rodeos.
""")
    return "\n".join(prompt_parts)


# ── Reporting ──────────────────────────────────────────────────────────

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


def build_json_report(subsystems: list[Subsystem]) -> dict:
    total_w = sum(s.total_weight for s in subsystems)
    earned_w = sum(s.earned_weight for s in subsystems)
    overall = round((earned_w / total_w * 100), 1) if total_w > 0 else 0.0
    grade, _ = score_to_grade(overall)

    return {
        "version": VERSION,
        "overall": {"score": overall, "grade": grade},
        "subsystems": [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "percentage": s.percentage,
                "passed": s.passed,
                "summary": s.summary(),
                "checks": [
                    {
                        "id": c.id,
                        "name": c.name,
                        "passed": c.passed,
                        "weight": c.weight,
                        "detail": c.detail,
                        "files_found": c.files_found,
                    }
                    for c in s.checks
                ],
            }
            for s in subsystems
        ],
        "recommendations": {
            "llm_prompt": generate_llm_prompt(subsystems),
        },
    }


def print_report(subsystems: list[Subsystem], json_output: bool = False) -> None:
    report = build_json_report(subsystems)

    if json_output:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    W = os.get_terminal_size().columns if sys.stdout.isatty() else 80
    print()
    print("=" * W)
    print("  🔧  HARNESS EVALUATOR v2  🔧".center(W))
    print("=" * W)
    print()

    overall = report["overall"]
    print(f"  Puntuación Global: {overall['score']}%  —  {overall['grade']}".center(W))
    print()

    for sub in report["subsystems"]:
        status_icon = "✅" if sub["passed"] else "⚠️"
        bar_len = W - 42
        filled = int(bar_len * sub["percentage"] / 100)
        bar = "█" * filled + "░" * (bar_len - filled)

        print(f"  {status_icon}  {sub['name']}")
        print(f"     {sub['description']}")
        print(f"     [{bar}] {sub['percentage']:>5.1f}%  —  {sub['summary']}")
        print()

        for c in sub["checks"]:
            ok = "✓" if c["passed"] else "✗"
            print(f"     {ok}  {c['id']} {c['name']}")
            print(f"        {c['detail']}")
            if c["files_found"]:
                print(f"        📁 {', '.join(c['files_found'][:3])}")
                if len(c["files_found"]) > 3:
                    print(f"           ... y {len(c['files_found']) - 3} más")
            print()

    print("─" * W)
    print(f"  PUNTUACIÓN GLOBAL: {overall['score']}%  —  {overall['grade']}".center(W))

    failed_subs = [s for s in report["subsystems"] if not s["passed"]]
    if failed_subs:
        print()
        print("  🎯 Prioridades sugeridas:")
        for s in sorted(failed_subs, key=lambda x: x["percentage"]):
            print(f"     • {s['name']} ({s['percentage']}%)")
        print()
        print("  💡 Usa --llm para generar recomendaciones IA contextuales")
    print("=" * W)
    print()


# ── CLI: POML subcommand renderers ────────────────────────────────────

def cmd_poml_validate(args: argparse.Namespace) -> None:
    validator = POMLValidator(args.path, schema_path=getattr(args, "schema", None))
    issues = validator.validate()

    if not validator.poml_files:
        print(f"  ⚠️  No se encontraron archivos .poml en {args.path}")
        return

    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    infos = [i for i in issues if i.severity == "info"]

    print()
    print(f"  📋 POML Validate — {len(validator.poml_files)} archivos")
    print(f"     {len(errors)} errores, {len(warnings)} warnings, {len(infos)} informativos")
    print()

    if args.json:
        print(json.dumps({
            "total_files": len(validator.poml_files),
            "errors": [asdict(i) for i in errors],
            "warnings": [asdict(i) for i in warnings],
            "infos": [asdict(i) for i in infos],
        }, indent=2, ensure_ascii=False))
        return

    for issue_list, label in [(errors, "ERROR"), (warnings, "WARN"), (infos, "INFO")]:
        if not issue_list:
            continue
        for i in issue_list:
            print(f"  [{label}] {i.code} — {i.file}:{i.line}")
            print(f"         {i.message}")
        print()


def cmd_poml_lint(args: argparse.Namespace) -> None:
    validator = POMLValidator(args.path)
    issues = validator.lint()

    if not validator.poml_files:
        print(f"  ⚠️  No se encontraron archivos .poml en {args.path}")
        return

    warnings = [i for i in issues if i.severity == "warning"]
    infos = [i for i in issues if i.severity == "info"]

    print()
    print(f"  🔍 POML Lint — {len(validator.poml_files)} archivos")
    print(f"     {len(warnings)} warnings, {len(infos)} sugerencias")
    print()

    if args.json:
        print(json.dumps({
            "total_files": len(validator.poml_files),
            "warnings": [asdict(i) for i in warnings],
            "infos": [asdict(i) for i in infos],
        }, indent=2, ensure_ascii=False))
        return

    for label, issue_list in [("WARN", warnings), ("INFO", infos)]:
        if not issue_list:
            continue
        for i in issue_list:
            print(f"  [{label}] {i.code} — {i.file}:{i.line}")
            print(f"         {i.message}")
        print()

    if not warnings and not infos:
        print("  ✅ Sin issues de lint. Recetas limpias.")
        print()


def cmd_poml_coverage(args: argparse.Namespace) -> None:
    validator = POMLValidator(args.path)
    stats = validator.coverage()

    if stats.get("total", 0) == 0:
        print(f'{{"error":"{stats.get("message","No hay archivos .poml")}"}}' if args.json else f"  ⚠️  {stats.get('message', 'No hay archivos .poml')}")
        return

    if args.json:
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        return

    print()
    print(f"  📊 POML Coverage — {stats['total']} archivos .poml")
    print()

    if args.json:
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        return

    print(f"  Categorías: {len(stats['by_category'])}")
    for cat, count in stats["by_category"].items():
        bar = "█" * count
        print(f"    {cat}: {bar} ({count})")
    print()

    s = stats["sections"]
    print(f"  Secciones:")
    print(f"    <role>         {s['with_role']:>3}/{stats['total']} ({stats['pct_with_role']:>5.1f}%)")
    print(f"    <task>         {s['with_task']:>3}/{stats['total']} ({stats['pct_with_task']:>5.1f}%)")
    print(f"    <output-format> {s['with_output']:>3}/{stats['total']} ({stats['pct_with_output']:>5.1f}%)")
    print(f"    Completas      {s['with_all_sections']:>3}/{stats['total']} ({stats['pct_complete']:>5.1f}%)")
    print(f"    Con topology   {stats['pct_with_topology']}%")
    print(f"    Multi-provider {stats['multi_provider_recipes']} recetas")
    print()


# ── CLI: Fix command ───────────────────────────────────────────────────

def cmd_fix(args: argparse.Namespace) -> None:
    """Genera archivos faltantes del harness desde templates POML."""
    templates_dir = Path(args.templates)

    if not templates_dir.is_dir():
        print(f"[ERROR] Directorio de templates no encontrado: {templates_dir}", file=sys.stderr)
        sys.exit(1)

    # Load templates
    tmpl_files = sorted(templates_dir.glob("*.poml"))
    if not tmpl_files:
        print(f"[ERROR] No hay templates POML en {templates_dir}", file=sys.stderr)
        sys.exit(1)

    # Index templates by output file name and their check associations
    templates = {}
    for tf in tmpl_files:
        content = tf.read_text(encoding="utf-8")
        m = re.search(r'<let\s+name="output">(.*?)</let>', content)
        if m:
            out_file = m.group(1).strip()
            out_m = re.search(r'<output>(.*?)</output>', content, re.DOTALL)
            if out_m:
                # Extract check_ids or use fallback matching
                ids_m = re.search(r'<let\s+name="check_ids">\[(.*?)\]</let>', content)
                check_ids = [x.strip().strip('"') for x in ids_m.group(1).split(",")] if ids_m else []
                # Extract trigger keywords
                trig_m = re.search(r'<let\s+name="triggers">\[(.*?)\]</let>', content)
                triggers = [x.strip().strip('"') for x in trig_m.group(1).split(",")] if trig_m else []
                templates[out_file] = {
                    "content": out_m.group(1).strip(),
                    "check_ids": check_ids,
                    "triggers": triggers,
                }

    # Scan project
    try:
        scanner = HarnessScanner(args.path)
        subsystems = scanner.scan()
    except NotADirectoryError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    # Find failed checks that match templates
    project_root = Path(args.path).resolve()
    generated = 0

    print()
    print(f"  🔧 Harness Fix — {project_root.name}")
    print()

    for s in subsystems:
        for c in s.checks:
            if c.passed:
                continue
            for out_file, tmpl in templates.items():
                content = tmpl["content"]
                check_ids = tmpl["check_ids"]
                triggers = tmpl["triggers"]
                target = project_root / out_file
                if target.exists() and not args.all:
                    continue
                match = c.id in check_ids
                if not match:
                    cname_lower = c.name.lower()
                    for trig in triggers:
                        if trig.lower() in cname_lower:
                            match = True
                            break
                if match:
                    if args.dry_run:
                        print(f"  📄 Generaría: {out_file} (fix: {c.id} {c.name})")
                        generated += 1
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_text(content + "\n")
                        print(f"  ✅ {out_file} — generado ({c.id} {c.name})")
                        generated += 1
                    break

    if generated == 0:
        print("  ✨ No hay archivos que generar. El harness está completo.")
    elif args.dry_run:
        print(f"\n  📋 {generated} archivo(s) listos para generar. Usa --all para escribirlos.")
    else:
        print(f"\n  ✅ {generated} archivo(s) generados. Vuelve a escanear para ver el nuevo score.")
    print()


# ── CLI Entry Point ───────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Harness Evaluator v2 — Evalúa la madurez del harness para agentes de IA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--json", action="store_true", help="Salida en formato JSON")
    parser.add_argument("--version", action="version", version=f"Harness Evaluator v{VERSION}")

    subparsers = parser.add_subparsers(dest="command", help="Subcomandos")

    # ── scan (default) ─────────────────────────────────────────────
    scan_p = subparsers.add_parser("scan", help="Escanea un proyecto (por defecto)")
    scan_p.add_argument("path", help="Ruta al proyecto a escanear")
    scan_p.add_argument("--json", action="store_true", help="Salida en formato JSON")
    scan_p.add_argument("--llm", action="store_true", help="Generar prompt LLM para recomendaciones")
    scan_p.add_argument("--ci", action="store_true", help="Modo CI: exit 1 si no pasa threshold")
    scan_p.add_argument("--threshold", type=int, default=50, help="Threshold mínimo para CI")
    scan_p.set_defaults(func=cmd_scan)

    # ── poml validate ──────────────────────────────────────────────
    pv = subparsers.add_parser("poml", help="Comandos para recetas POML")
    pv_sub = pv.add_subparsers(dest="poml_command", help="Subcomando POML")

    pv_validate = pv_sub.add_parser("validate", help="Valida recetas POML contra schema")
    pv_validate.add_argument("path", help="Ruta al proyecto con archivos .poml")
    pv_validate.add_argument("--schema", help="Ruta al recipe.schema.yaml")
    pv_validate.add_argument("--json", action="store_true", help="Salida JSON")
    pv_validate.set_defaults(func=cmd_poml_validate)

    pv_lint = pv_sub.add_parser("lint", help="Analiza calidad de recetas POML")
    pv_lint.add_argument("path", help="Ruta al proyecto con archivos .poml")
    pv_lint.add_argument("--json", action="store_true", help="Salida JSON")
    pv_lint.set_defaults(func=cmd_poml_lint)

    pv_coverage = pv_sub.add_parser("coverage", help="Estadísticas de cobertura POML")
    pv_coverage.add_argument("path", help="Ruta al proyecto con archivos .poml")
    pv_coverage.add_argument("--json", action="store_true", help="Salida JSON")
    pv_coverage.set_defaults(func=cmd_poml_coverage)

    # ── fix ─────────────────────────────────────────────────────────
    fix_p = subparsers.add_parser("fix", help="Genera archivos faltantes del harness desde templates POML")
    fix_p.add_argument("path", help="Ruta al proyecto a reparar")
    fix_p.add_argument("--templates", default=os.path.join(os.path.dirname(__file__), "harness-fix", "templates"),
                       help="Directorio con templates POML (default: junto al script)")
    fix_p.add_argument("--dry-run", action="store_true", help="Mostrar qué generaría sin escribir")
    fix_p.add_argument("--all", action="store_true", help="Generar todos los archivos faltantes")
    fix_p.set_defaults(func=cmd_fix)

    # ── Backwards compat: if no subcommand, treat first arg as path ─
    args = parser.parse_args()

    if args.command is None:
        # Legacy mode: python3 script.py path [--json --llm --ci]
        argv = sys.argv[1:]
        if not argv or argv[0].startswith("-"):
            parser.print_help()
            sys.exit(0)
        # Re-parse as scan
        scan_args = scan_p.parse_args(argv)
        cmd_scan(scan_args)
        return

    if hasattr(args, "func"):
        args.func(args)


def cmd_scan(args: argparse.Namespace) -> None:
    try:
        scanner = HarnessScanner(args.path)
        subsystems = scanner.scan()
    except NotADirectoryError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    report = build_json_report(subsystems)
    overall = report["overall"]["score"]

    if getattr(args, "llm", False):
        print(generate_llm_prompt(subsystems))
        return

    print_report(subsystems, json_output=args.json)

    if getattr(args, "ci", False) and overall < args.threshold:
        print(f"[CI FAIL] Overall: {overall}% < threshold: {args.threshold}%", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
