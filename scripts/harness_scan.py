#!/usr/bin/env python3
"""
Harness Assessment Scanner — v1.0
==================================
Analiza un proyecto y evalúa la madurez de su "harness" para agentes de IA
según los 5 subsistemas del Harness Engineering (walkinglabs).

Uso:
    python3 harness_scan.py /ruta/al/proyecto [--json] [--ci] [--threshold 70]

Inspirado en: walkinglabs/learn-harness-engineering
              walkinglabs/awesome-harness-engineering
              iberi22/agent-recipes-repo

Autor: Hermes Agent — Harness Course
"""

import os
import sys
import json
import re
import fnmatch
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional


# ──────────────────────────────────────────────────────────
# DEFINICIONES — Los checks se basan en los 5 subsistemas
# ──────────────────────────────────────────────────────────

@dataclass
class HarnessCheck:
    """Un check individual dentro de un subsistema."""
    id: str
    name: str
    description: str
    weight: float = 1.0  # peso relativo dentro del subsistema
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


# ──────────────────────────────────────────────────────────
# SCANNER ENGINE
# ──────────────────────────────────────────────────────────

class HarnessScanner:
    def __init__(self, root: str):
        self.root = Path(root).resolve()
        if not self.root.is_dir():
            raise NotADirectoryError(f"No existe el directorio: {root}")
        self.subsystems: list[Subsystem] = []

    def scan(self) -> list[Subsystem]:
        """Ejecuta todos los checks y devuelve los subsistemas evaluados."""
        self.subsystems = []

        self._scan_instructions()
        self._scan_state()
        self._scan_verification()
        self._scan_scope()
        self._scan_lifecycle()

        return self.subsystems

    # ── File helpers ──────────────────────────────────────

    def _find(self, glob_pattern: str, max_depth: int = 5) -> list[Path]:
        """Busca archivos por glob, relativo a root."""
        matches = []
        for depth in range(1, max_depth + 1):
            # Build pattern for specific depth
            parts = ["*"] * depth
            pattern = os.path.join(self.root, *parts)
            matches.extend(Path(self.root).glob(glob_pattern))
            # Also check direct children
            if depth == 1:
                matches.extend(self.root.glob(glob_pattern))
        # Deduplicate
        seen = set()
        unique = []
        for m in matches:
            if m not in seen:
                seen.add(m)
                unique.append(m)
        return sorted(unique)

    def _find_files(self, patterns: list[str]) -> list[Path]:
        """Busca archivos por lista de patrones."""
        found = []
        for pat in patterns:
            # Search recursively
            for path in self.root.rglob(pat):
                found.append(path)
        return sorted(found)

    def _file_exists(self, *paths: str) -> Optional[Path]:
        """Retorna el path si existe, None si no."""
        for p in paths:
            candidate = self.root / p
            if candidate.exists():
                return candidate
        return None

    def _check_file(self, check: HarnessCheck, *paths: str) -> None:
        """Verifica si al menos uno de los paths existe."""
        found = self._file_exists(*paths)
        check.passed = found is not None
        if found:
            check.detail = f"Encontrado: {found.relative_to(self.root)}"
            check.files_found = [str(found.relative_to(self.root))]
        else:
            check.detail = f"No encontrado: {', '.join(paths)}"

    def _check_content(self, check: HarnessCheck, pattern: str, *paths: str) -> None:
        """Verifica si un archivo existe Y contiene cierto patrón."""
        found = self._file_exists(*paths)
        if not found:
            check.passed = False
            check.detail = f"No encontrado: {', '.join(paths)}"
            return
        content = found.read_text(encoding="utf-8", errors="replace")
        if re.search(pattern, content, re.IGNORECASE):
            check.passed = True
            check.detail = f"{found.relative_to(self.root)} contiene '{pattern}'"
            check.files_found = [str(found.relative_to(self.root))]
        else:
            check.passed = False
            check.detail = f"{found.relative_to(self.root)} no contiene '{pattern}'"

    def _count_check(self, check: HarnessCheck, patterns: list[str], min_count: int = 1) -> None:
        """Cuenta archivos que coinciden con patrones, pasa si >= min_count."""
        files = self._find_files(patterns)
        check.files_found = [str(f.relative_to(self.root)) for f in files]
        check.passed = len(files) >= min_count
        if check.passed:
            check.detail = f"{len(files)} archivo(s) encontrado(s)"
        else:
            check.detail = f"Solo {len(files)} archivo(s), mínimo requerido: {min_count}"

    # ── Subsystem 1: Instructions ─────────────────────────

    def _scan_instructions(self) -> None:
        sub = Subsystem(
            id="instructions",
            name="📋 Instructions",
            description="El agente necesita instrucciones claras sobre qué hacer y en qué orden.",
        )
        checks = []

        # 1.1 AGENTS.md or CLAUDE.md (main briefing file)
        c = HarnessCheck("1.1", "Briefing principal", "AGENTS.md o CLAUDE.md como punto de entrada", weight=3.0)
        self._check_file(c, "AGENTS.md", "CLAUDE.md", "AGENT.md")
        checks.append(c)

        # 1.2 Progressive disclosure: docs/ directory
        c = HarnessCheck("1.2", "Progressive disclosure", "Directorio docs/ con documentación", weight=1.5)
        doc_path = self.root / "docs"
        c.passed = doc_path.is_dir()
        if c.passed:
            md_files = list(doc_path.glob("*.md"))
            c.detail = f"docs/ con {len(md_files)} archivos markdown"
            c.files_found = [str(p.relative_to(self.root)) for p in md_files[:5]]
        else:
            c.detail = "No existe directorio docs/"
        checks.append(c)

        # 1.3 PLANNING.md (roadmap/architecture)
        c = HarnessCheck("1.3", "PLANNING.md", "Roadmap y arquitectura del proyecto", weight=1.5)
        self._check_file(c, "PLANNING.md", "docs/PLANNING.md", "ROADMAP.md")
        checks.append(c)

        # 1.4 RULES.md (code conventions)
        c = HarnessCheck("1.4", "Rules de codificación", "RULES.md con estándares de código", weight=1.0)
        self._check_file(c, "RULES.md", "CONVENTIONS.md", ".cursorrules")
        checks.append(c)

        # 1.5 README.md con instrucciones de setup
        c = HarnessCheck("1.5", "README.md", "README con instrucciones de setup/build/test", weight=1.0)
        self._check_content(c, r"(docker|install|setup|build|test|run|start)", "README.md")
        checks.append(c)

        # 1.6 Task-specific instructions (CONTEXT.md, BRIEF.md)
        c = HarnessCheck("1.6", "Briefings específicos", "Archivos de instrucción por tarea en docs/", weight=0.5)
        tasks = list(self.root.rglob("BRIEF.md")) + list(self.root.rglob("CONTEXT.md"))
        c.passed = len(tasks) > 0
        c.files_found = [str(p.relative_to(self.root)) for p in tasks[:5]]
        c.detail = f"{len(tasks)} archivo(s) de instrucción encontrados"
        checks.append(c)

        sub.checks = checks
        self.subsystems.append(sub)

    # ── Subsystem 2: State ────────────────────────────────

    def _scan_state(self) -> None:
        sub = Subsystem(
            id="state",
            name="💾 State",
            description="El agente necesita persistencia: saber qué está hecho y qué sigue.",
        )
        checks = []

        # 2.1 TASK.md (live task board)
        c = HarnessCheck("2.1", "Task tracking", "TASK.md con backlog activo", weight=3.0)
        self._check_content(c, r"(\[ \]|\[x\]|progreso|hito|task|tarea|backlog)", "TASK.md", "docs/TASK.md", "TODO.md")
        checks.append(c)

        # 2.2 PROJECT_STATUS.md (functional status)
        c = HarnessCheck("2.2", "Estado funcional", "PROJECT_STATUS.md o STATUS.md", weight=1.5)
        self._check_file(c, "PROJECT_STATUS.md", "STATUS.md", "docs/STATUS.md")
        checks.append(c)

        # 2.3 feature_list.json (features tracking)
        c = HarnessCheck("2.3", "Feature tracking", "feature_list.json con features planificadas", weight=1.0)
        self._check_file(c, "feature_list.json", "features.json", "docs/features.json")
        checks.append(c)

        # 2.4 progress.md (session progress)
        c = HarnessCheck("2.4", "Progreso de sesión", "Archivo de progreso persistente entre sesiones", weight=1.0)
        self._check_file(c, "progress.md", "claude-progress.md", "session.md", "docs/progress.md")
        checks.append(c)

        # 2.5 Git history (recent commits)
        c = HarnessCheck("2.5", "Historial git", "Repositorio git con historial reciente", weight=1.0)
        git_dir = self.root / ".git"
        if git_dir.is_dir():
            c.passed = True
            c.detail = "Repositorio git inicializado"
        else:
            c.passed = False
            c.detail = "No hay repositorio .git"
        checks.append(c)

        # 2.6 Database or persistent storage (optional bonus)
        c = HarnessCheck("2.6", "Persistencia externa", "Base de datos o almacenamiento externo (opt.)", weight=0.5)
        patterns = ["*.db", "*.sqlite", "*.jsonl", "docker-compose.yml", "docker-compose.yaml"]
        storage_files = self._find_files(patterns)
        c.passed = len(storage_files) > 0
        c.files_found = [str(f.relative_to(self.root)) for f in storage_files[:3]]
        c.detail = f"{len(storage_files)} archivo(s) de persistencia"
        checks.append(c)

        sub.checks = checks
        self.subsystems.append(sub)

    # ── Subsystem 3: Verification ─────────────────────────

    def _scan_verification(self) -> None:
        sub = Subsystem(
            id="verification",
            name="✅ Verification",
            description="El agente debe poder verificar su trabajo automáticamente.",
        )
        checks = []

        # 3.1 Test directory
        c = HarnessCheck("3.1", "Directorio de tests", "tests/ o test/ con pruebas", weight=3.0)
        for test_dir in ["tests", "test", "spec", "__tests__"]:
            td = self.root / test_dir
            if td.is_dir():
                py_files = list(td.rglob("*.py"))
                js_files = list(td.rglob("*.ts")) + list(td.rglob("*.js"))
                rs_files = list(td.rglob("*.rs"))
                c.passed = True
                c.detail = f"tests/ ({len(py_files)+len(js_files)+len(rs_files)} archivos)"
                c.files_found = [str(td.relative_to(self.root))]
                break
        if not c.passed:
            c.detail = "No se encontró directorio de tests"
        checks.append(c)

        # 3.2 Test config file
        c = HarnessCheck("3.2", "Configuración de tests", "pytest.ini, vitest.config, jest.config, etc.", weight=1.5)
        self._check_file(c, "pytest.ini", "pyproject.toml", "vitest.config.ts", "vitest.config.js",
                          "jest.config.ts", "jest.config.js", "Cargo.toml")
        checks.append(c)

        # 3.3 Test files exist
        c = HarnessCheck("3.3", "Tests implementados", "Archivos de test con casos reales", weight=2.0)
        test_files = (self._find_files(["*test*.py", "*test*.ts", "*test*.js", "*spec*.py", "*spec*.ts",
                                         "*_test.rs", "*test*.rs", "test_*.py", "test_*.ts"]))
        # Also check inside test directories
        for td_name in ["tests", "test", "spec", "__tests__"]:
            td = self.root / td_name
            if td.is_dir():
                test_files.extend(list(td.rglob("*test*")) + list(td.rglob("*spec*")))
        test_files = list(set(test_files))
        c.files_found = [str(f.relative_to(self.root)) for f in test_files[:5]]
        c.passed = len(test_files) >= 2  # al menos 2 archivos de test
        if c.passed:
            c.detail = f"{len(test_files)} archivo(s) de test"
        else:
            c.detail = f"Solo {len(test_files)} archivo(s) de test (mín: 2)"
        checks.append(c)

        # 3.4 CI/CD config
        c = HarnessCheck("3.4", "CI/CD pipeline", "GitHub Actions, .gitlab-ci.yml, etc.", weight=1.0)
        ci_paths = [".github/workflows", ".gitlab-ci.yml", ".circleci", "Jenkinsfile", ".drone.yml"]
        found_ci = None
        for cp in ci_paths:
            fp = self.root / cp
            if fp.exists():
                found_ci = cp
                break
        c.passed = found_ci is not None
        c.detail = f"Encontrado: {found_ci}" if found_ci else "No se encontró configuración CI/CD"
        if found_ci:
            c.files_found = [found_ci]
        checks.append(c)

        # 3.5 Linter config
        c = HarnessCheck("3.5", "Linter configurado", ".eslintrc, .ruff.toml, clippy.toml, etc.", weight=1.0)
        self._check_file(c, ".eslintrc*", ".prettierrc*", ".ruff.toml", "pyproject.toml",
                          "clippy.toml", ".golangci.yml", ".flake8")
        checks.append(c)

        # 3.6 Type checking (for typed languages)
        c = HarnessCheck("3.6", "Type checking", "TypeScript, mypy, pyright, etc.", weight=0.5)
        type_configs = ["tsconfig.json", "mypy.ini", "pyrightconfig.json", "Cargo.toml"]
        for tc in type_configs:
            if (self.root / tc).exists():
                c.passed = True
                c.detail = f"Encontrado: {tc}"
                c.files_found = [tc]
                break
        if not c.passed:
            c.detail = "No se encontró configuración de type checking"
        checks.append(c)

        sub.checks = checks
        self.subsystems.append(sub)

    # ── Subsystem 4: Scope ────────────────────────────────

    def _scan_scope(self) -> None:
        sub = Subsystem(
            id="scope",
            name="🎯 Scope",
            description="El agente debe trabajar una cosa a la vez, sin overreach.",
        )
        checks = []

        # 4.1 Definition of Done document
        c = HarnessCheck("4.1", "Definition of Done", "DoD explícito: checklist de finalización", weight=2.0)
        self._check_content(c, r"(definition.of.done|dod|done.when|criterios.de.aceptación|criterios.de.aceptacion)",
                            "RULES.md", "CONTRIBUTING.md", "docs/PLANNING.md", "AGENTS.md", "CLAUDE.md")
        checks.append(c)

        # 4.2 One-feature-at-a-time structure (TASK.md with milestones)
        c = HarnessCheck("4.2", "Milestones en TASK.md", "Hitos con progreso, una feature a la vez", weight=2.0)
        task_file = self._file_exists("TASK.md", "docs/TASK.md", "TODO.md")
        if task_file:
            content = task_file.read_text(encoding="utf-8", errors="replace")
            has_milestones = bool(re.search(r"(hito|milestone|module|fase|phase|sprint)", content, re.IGNORECASE))
            has_progress = bool(re.search(r"(\d+%|progreso|progress|status|completado)", content, re.IGNORECASE))
            c.passed = has_milestones or has_progress
            if c.passed:
                c.detail = f"TASK.md con {'hitos y ' if has_milestones else ''}progreso"
                c.files_found = [str(task_file.relative_to(self.root))]
            else:
                c.detail = "TASK.md existe pero sin hitos ni progreso"
        else:
            c.passed = False
            c.detail = "No hay TASK.md"
        checks.append(c)

        # 4.3 Issue/PR templates (GitHub conventions)
        c = HarnessCheck("4.3", "Issue/PR templates", "Plantillas para issues y pull requests", weight=1.0)
        templates = list(self.root.rglob(".github/ISSUE_TEMPLATE/*")) + list(self.root.rglob(".github/PULL_REQUEST_TEMPLATE/*"))
        c.passed = len(templates) > 0
        c.files_found = [str(t.relative_to(self.root)) for t in templates[:4]]
        c.detail = f"{len(templates)} plantilla(s) encontrada(s)" if templates else "No hay plantillas .github/"
        checks.append(c)

        # 4.4 "Discovered During Work" section (backlog)
        c = HarnessCheck("4.4", "Backlog de descubrimientos", "Sección para issues descubiertos durante trabajo", weight=0.5)
        docs_md = list(self.root.rglob("*.md"))
        found_backlog = False
        for f in docs_md:
            content = f.read_text(encoding="utf-8", errors="replace")
            if re.search(r"(discovered.during.work|backlog|por.hacer|icebox)", content, re.IGNORECASE):
                found_backlog = True
                c.files_found = [str(f.relative_to(self.root))]
                break
        c.passed = found_backlog
        c.detail = "Sección de backlog encontrada" if found_backlog else "No se encontró sección de backlog"
        checks.append(c)

        # 4.5 CONTRIBUTING.md (scope rules for contributors)
        c = HarnessCheck("4.5", "CONTRIBUTING.md", "Guía de contribución con límites de alcance", weight=1.0)
        self._check_file(c, "CONTRIBUTING.md", "CONTRIBUTING.adoc")
        checks.append(c)

        sub.checks = checks
        self.subsystems.append(sub)

    # ── Subsystem 5: Lifecycle ────────────────────────────

    def _scan_lifecycle(self) -> None:
        sub = Subsystem(
            id="lifecycle",
            name="🔄 Lifecycle",
            description="El agente debe tener un ciclo de vida: init, trabajo, cleanup.",
        )
        checks = []

        # 5.1 init.sh or init script
        c = HarnessCheck("5.1", "Script de init", "init.sh, setup.sh, bootstrap del proyecto", weight=3.0)
        self._check_file(c, "init.sh", "setup.sh", "bootstrap.sh", "init.ps1", "Makefile")
        checks.append(c)

        # 5.2 Docker support
        c = HarnessCheck("5.2", "Docker/Contenedor", "Dockerfile y/o docker-compose.yml", weight=2.0)
        self._check_file(c, "Dockerfile", "docker-compose.yml", "docker-compose.yaml", "Containerfile")
        checks.append(c)

        # 5.3 Session handoff procedure
        c = HarnessCheck("5.3", "Session handoff", "Procedimiento para retomar trabajo entre sesiones", weight=1.5)
        doc_files = list(self.root.rglob("*.md"))
        found_handoff = False
        for f in doc_files:
            content = f.read_text(encoding="utf-8", errors="replace")
            if re.search(r"(handoff|clean.state|clean.restart|retomar|próxima.sesión|proxima.sesion)", content, re.IGNORECASE):
                found_handoff = True
                c.files_found = [str(f.relative_to(self.root))]
                break
        c.passed = found_handoff
        c.detail = "Procedimiento de handoff encontrado" if found_handoff else "No se encontró procedimiento de handoff"
        checks.append(c)

        # 5.4 Requirements / dependencies file
        c = HarnessCheck("5.4", "Dependencias", "requirements.txt, package.json, Cargo.toml, etc.", weight=1.0)
        self._check_file(c, "requirements.txt", "package.json", "Cargo.toml", "go.mod",
                          "Gemfile", "pyproject.toml", "Pipfile")
        checks.append(c)

        # 5.5 Environment template
        c = HarnessCheck("5.5", "Configuración de entorno", ".env.example para variables requeridas", weight=1.0)
        self._check_file(c, ".env.example", ".env.template", ".env.sample")
        checks.append(c)

        # 5.6 .gitignore
        c = HarnessCheck("5.6", ".gitignore", "Archivo de exclusión git", weight=0.5)
        self._check_file(c, ".gitignore")
        checks.append(c)

        # 5.7 LICENSE
        c = HarnessCheck("5.7", "Licencia", "LICENSE o LICENSE.txt", weight=0.5)
        self._check_file(c, "LICENSE", "LICENSE.md", "LICENSE.txt")
        checks.append(c)

        sub.checks = checks
        self.subsystems.append(sub)

    # ── Scoreboard ───────────────────────────────────────

    def scoreboard(self) -> dict:
        """Calcula puntuación general."""
        total_weight = sum(s.total_weight for s in self.subsystems)
        earned_weight = sum(s.earned_weight for s in self.subsystems)
        overall = round((earned_weight / total_weight * 100), 1) if total_weight > 0 else 0.0

        return {
            "overall": overall,
            "subsystems": {
                s.id: {
                    "name": s.name,
                    "percentage": s.percentage,
                    "summary": s.summary(),
                    "passed": s.passed,
                }
                for s in self.subsystems
            }
        }


# ──────────────────────────────────────────────────────────
# REPORTING
# ──────────────────────────────────────────────────────────

def print_report(subsystems: list[Subsystem], json_output: bool = False) -> None:
    """Imprime el reporte completo."""
    if json_output:
        data = {
            "scanned_path": str(subsystems[0].checks[0].files_found[0]) if subsystems and subsystems[0].checks and subsystems[0].checks[0].files_found else str(Path.cwd()),
            "subsystems": []
        }
        for sub in subsystems:
            sub_data = {
                "id": sub.id,
                "name": sub.name,
                "description": sub.description,
                "percentage": sub.percentage,
                "passed": sub.passed,
                "checks": []
            }
            for c in sub.checks:
                sub_data["checks"].append({
                    "id": c.id,
                    "name": c.name,
                    "passed": c.passed,
                    "weight": c.weight,
                    "detail": c.detail,
                    "files_found": c.files_found
                })
            data["subsystems"].append(sub_data)

        # Calculate overall
        total_w = sum(s.total_weight for s in subsystems)
        earned_w = sum(s.earned_weight for s in subsystems)
        data["overall_percentage"] = round((earned_w / total_w * 100), 1) if total_w > 0 else 0.0
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    # ── Human-readable output ──────────────────────────
    W = os.get_terminal_size().columns if sys.stdout.isatty() else 80

    print()
    print("=" * W)
    print("  🔧  HARNESS ASSESSMENT SCANNER  🔧".center(W))
    print("=" * W)
    print()
    print(f"  Proyecto escaneado: {subsystems[0].checks[0].files_found if subsystems else ''}")
    print()

    for sub in subsystems:
        # Subsystem header
        status_icon = "✅" if sub.passed else "⚠️"
        bar_len = W - 42
        filled = int(bar_len * sub.percentage / 100)
        bar = "█" * filled + "░" * (bar_len - filled)

        print(f"  {status_icon}  {sub.name}")
        print(f"     {sub.description}")
        print(f"     [{bar}] {sub.percentage:>5.1f}%  —  {sub.summary()}")
        print()

        # Individual checks
        for c in sub.checks:
            ok = "✓" if c.passed else "✗"
            print(f"     {ok}  {c.id} {c.name}")
            print(f"        {c.detail}")
            if c.files_found:
                print(f"        Archivos: {', '.join(c.files_found[:3])}")
                if len(c.files_found) > 3:
                    print(f"           ... y {len(c.files_found) - 3} más")
            print()

    # Overall score
    print("─" * W)
    total_w = sum(s.total_weight for s in subsystems)
    earned_w = sum(s.earned_weight for s in subsystems)
    overall = round((earned_w / total_w * 100), 1) if total_w > 0 else 0.0

    # Grade
    if overall >= 80:
        grade = "🟢 EXCELENTE"
    elif overall >= 60:
        grade = "🔵 BUENO"
    elif overall >= 40:
        grade = "🟡 REGULAR"
    elif overall >= 20:
        grade = "🟠 DÉBIL"
    else:
        grade = "🔴 CRÍTICO"

    print(f"  PUNTUACIÓN GLOBAL: {overall}%  —  {grade}".center(W))
    print()

    if overall < 40:
        print("  🎯 Prioridades sugeridas:")
        for sub in sorted(subsystems, key=lambda s: s.percentage):
            if sub.percentage < 50:
                print(f"     • {sub.name} ({sub.percentage}%) — {sub.description}")
    print()
    print("=" * W)
    print()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Harness Assessment Scanner — Evalúa la madurez del harness para agentes de IA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python3 harness_scan.py /ruta/al/proyecto
  python3 harness_scan.py . --json
  python3 harness_scan.py . --ci --threshold 60
        """
    )
    parser.add_argument("path", help="Ruta al proyecto a escanear")
    parser.add_argument("--json", action="store_true", help="Salida en formato JSON")
    parser.add_argument("--ci", action="store_true", help="Modo CI: exit code 1 si no pasa el threshold")
    parser.add_argument("--threshold", type=int, default=50, help="Threshold mínimo para CI (default: 50)")

    args = parser.parse_args()

    try:
        scanner = HarnessScanner(args.path)
        subsystems = scanner.scan()
    except NotADirectoryError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    # Calculate overall
    total_w = sum(s.total_weight for s in subsystems)
    earned_w = sum(s.earned_weight for s in subsystems)
    overall = round((earned_w / total_w * 100), 1) if total_w > 0 else 0.0

    print_report(subsystems, json_output=args.json)

    if args.ci and overall < args.threshold:
        print(f"[CI FAIL] Overall: {overall}% < threshold: {args.threshold}%", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
