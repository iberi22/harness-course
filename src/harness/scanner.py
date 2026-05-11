"""Harness Scanner — scans a project and evaluates the 6 harness subsystems."""
import json
import re
import fnmatch
from pathlib import Path
from typing import Optional

from harness.models import (
    HarnessCheck,
    Subsystem,
    SKILL_FRONTMATTER_RE,
    POML_TOPOLOGY_RE,
    POML_HAS_ROLE,
    POML_HAS_TASK,
    POML_LET_RE,
    VALID_PROVIDERS,
)


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
        except ImportError:
            return bool(re.search(r"^name:\s*\S+", m.group(1), re.MULTILINE))
        except Exception:
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
