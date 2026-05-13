[![Tests](https://github.com/iberi22/harness-course/actions/workflows/test.yml/badge.svg)](https://github.com/iberi22/harness-course/actions/workflows/test.yml)
[![Harness CI](https://github.com/iberi22/harness-course/actions/workflows/harness-ci.yml/badge.svg)](https://github.com/iberi22/harness-course/actions/workflows/harness-ci.yml)

# Harness Engineering — Course + CLI Evaluator

**Harness Engineering** course for AI agents, with a **CLI evaluator** that scans any project against 42 checks across 6 subsystems.

🌐 **Site:** [iberi22.github.io/harness-course/](https://iberi22.github.io/harness-course/)
🔧 **CLI:** `harness scan . --json` — scan and score your project

## 🚀 Quick Start

```bash
# Evaluate any project
harness scan ~/projects/my-project

# Compact JSON (16KB) for agents
harness scan ~/projects/my-project --json

# Auto-generate missing files
harness fix ~/projects/my-project

# CI mode (exit 1 if score < 50%)
harness scan . --ci --threshold 50
```

## 📦 Installation

### Via pip (recommended)

```bash
pip install git+https://github.com/iberi22/harness-course.git

# Or from a cloned repo:
git clone https://github.com/iberi22/harness-course.git
cd harness-course
pip install -e .
```

### Via curl | bash (pip-less)

```bash
curl -fsSL https://raw.githubusercontent.com/iberi22/harness-course/main/install.sh | bash
```

### Via symlink (legacy, no pip)

```bash
git clone https://github.com/iberi22/harness-course.git ~/projects/harness-course
ln -sf ~/projects/harness-course/scripts/harness_evaluator.py ~/.local/bin/harness
chmod +x ~/.local/bin/harness
```

## 📊 Evaluated Projects

| Project | Score | Status |
|---|---|---|
| **agents-flows-recipes** | 64.6% 🟡 | Post-fix |
| **swal-skills** | 58.3% 🟡 | Post-fix |
| **synapse-trading** | ~50% 🟡 | Post-fix |
| **harness-course** | **100.0%** 🟢 | EXCELLENT |

## 🏗️ Architecture

- **Site:** Vanilla HTML/CSS/JS, Linear Dark design, GitHub Pages
- **Evaluator:** Pure Python 3 (stdlib), 0 external dependencies
- **Fix templates:** 6 POML templates for auto-generating harness files
- **Skills index:** Unified catalog of local skills + starred repos

## 📚 Content

- **Fundamentals** — 12 lessons on why agents fail
- **Design Patterns** — 6 harness engineering patterns
- **Full Course** — 6 modules: Instructions, State, Verification, Scope, Lifecycle, Skills
- **Resources** — Curated resources
- **Templates** — AGENTS.md, init.sh, and other templates

## 🛠️ Harness Evaluator

42 checks across 6 subsystems:

| Subsystem | Checks | Purpose |
|---|---|---|
| 📋 Instructions | 8 | Briefings, rules, roadmap |
| 💾 State | 7 | Task tracking, memory, persistence |
| ✅ Verification | 6 | Tests, CI/CD, linters |
| 🎯 Scope | 7 | DoD, milestones, CONTRIBUTING |
| 🔄 Lifecycle | 8 | Init, Docker, dependencies |
| 🧠 Skills & POML | 6 | Skills, POML recipes, registry |

## 🧪 Tests & CI

- **3 test files:** `test_html_validation.py`, `test_integrity.py`, `test_suite.py`
- **GitHub Actions:** `test.yml` + `harness-ci.yml`

## 📋 License

MIT — © 2026 Brahyan Belalcazar (ElBeRi)

---

# Harness Engineering — Curso + Evaluador CLI

Curso de **Harness Engineering** para agentes de IA, con un **evaluador CLI** que escanea cualquier proyecto contra 42 checks en 6 subsistemas.

🌐 **Sitio:** [iberi22.github.io/harness-course/](https://iberi22.github.io/harness-course/)
🔧 **CLI:** `harness scan . --json` — escanea y puntúa tu proyecto

## 🚀 Quick Start

```bash
# Evaluar cualquier proyecto
harness scan ~/projects/mi-proyecto

# JSON compacto (16KB) para agentes
harness scan ~/projects/mi-proyecto --json

# Generar archivos faltantes automáticamente
harness fix ~/projects/mi-proyecto

# Modo CI (exit 1 si score < 50%)
harness scan . --ci --threshold 50
```

## 📦 Instalación

### Vía pip (recomendado)

```bash
pip install git+https://github.com/iberi22/harness-course.git

# O desde el repo clonado:
git clone https://github.com/iberi22/harness-course.git
cd harness-course
pip install -e .
```

### Vía curl | bash (sin pip)

```bash
curl -fsSL https://raw.githubusercontent.com/iberi22/harness-course/main/install.sh | bash
```

### Vía symlink (legacy, sin pip)

```bash
git clone https://github.com/iberi22/harness-course.git ~/projects/harness-course
ln -sf ~/projects/harness-course/scripts/harness_evaluator.py ~/.local/bin/harness
chmod +x ~/.local/bin/harness
```

## 📊 Proyectos Evaluados

| Proyecto | Score | Estado |
|---|---|---|
| **agents-flows-recipes** | 64.6% 🟡 | Post-fix |
| **swal-skills** | 58.3% 🟡 | Post-fix |
| **synapse-trading** | ~50% 🟡 | Post-fix |
| **harness-course** | **100.0%** 🟢 | EXCELENTE |

## 🏗️ Arquitectura

- **Sitio:** HTML/CSS/JS vanilla, diseño Linear Dark, GitHub Pages
- **Evaluador:** Python 3 puro (stdlib), 0 dependencias externas
- **Templates fix:** 6 templates POML para auto-generación de harness
- **Skills index:** Catálogo unificado de skills locales + repos starred

## 📚 Contenido

- **Fundamentals** — 12 lecciones sobre por qué los agentes fallan
- **Design Patterns** — 6 patrones de harness engineering
- **Full Course** — 6 módulos: Instructions, State, Verification, Scope, Lifecycle, Skills
- **Resources** — Recursos curados
- **Templates** — Plantillas AGENTS.md, init.sh, etc.

## 🛠️ Harness Evaluator

42 checks en 6 subsistemas:

| Subsistema | Checks | Propósito |
|---|---|---|
| 📋 Instructions | 8 | Briefings, reglas, roadmap |
| 💾 State | 7 | Task tracking, memoria, persistencia |
| ✅ Verification | 6 | Tests, CI/CD, linters |
| 🎯 Scope | 7 | DoD, milestones, CONTRIBUTING |
| 🔄 Lifecycle | 8 | Init, Docker, dependencias |
| 🧠 Skills & POML | 6 | Skills, recetas POML, registry |

## 🧪 Tests y CI

- **3 archivos de test:** `test_html_validation.py`, `test_integrity.py`, `test_suite.py`
- **GitHub Actions:** `test.yml` + `harness-ci.yml`

## 📋 Licencia

MIT — © 2026 Brahyan Belalcazar (ElBeRi)
