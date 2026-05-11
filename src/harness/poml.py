"""POML Validator — validates and analyzes POML recipes."""
import json
import re
from pathlib import Path
from typing import Optional

from harness.models import (
    POMLIssue,
    POML_LET_RE,
    POML_TOPOLOGY_RE,
    POML_HAS_ROLE,
    POML_HAS_TASK,
    POML_HAS_OUTPUT,
    VALID_TOPOLOGIES,
    VALID_TOOL_MODES,
    VALID_PROVIDERS,
    REQUIRED_LET_NAMES,
)


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

    # ── Validate ──────────────────────────────────────────

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

    # ── Lint ──────────────────────────────────────────────────

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

    # ── Coverage ──────────────────────────────────────────────────

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
