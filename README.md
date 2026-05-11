# Harness Engineering — Curso + Evaluador CLI

[![Tests](https://github.com/iberi22/harness-course/actions/workflows/test.yml/badge.svg)](https://github.com/iberi22/harness-course/actions/workflows/test.yml)
[![Harness CI](https://github.com/iberi22/harness-course/actions/workflows/harness-ci.yml/badge.svg)](https://github.com/iberi22/harness-course/actions/workflows/harness-ci.yml)

Curso de **Harness Engineering** para agentes de IA, con un **evaluador CLI** que escanea cualquier proyecto contra 48 checks en 6 subsistemas.

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

# CI mode (exit 1 si score < 50%)
harness scan . --ci --threshold 50
```

## 📦 Instalación

### Via pip (recomendado)

```bash
pip install git+https://github.com/iberi22/harness-course.git

# O desde el repo clonado:
git clone https://github.com/iberi22/harness-course.git
cd harness-course
pip install -e .
```

### Via curl | bash (pip-less)

```bash
curl -fsSL https://raw.githubusercontent.com/iberi22/harness-course/main/install.sh | bash
```

### Via symlink (legacy, sin pip)

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
| **harness-course** | 44.9% 🟡 | En mejora |

## 🏗️ Arquitectura

- **Sitio:** HTML/CSS/JS vanilla, diseño Linear Dark, GitHub Pages
- **Evaluador:** Python 3 puro (stdlib), 0 dependencias externas
- **Templates fix:** 6 templates POML para auto-generación de harness
- **Skills index:** Catálogo unificado de 44 skills locales + 8 starred repos

## 📚 Contenido

- **Fundamentals** — 12 lecciones sobre por qué los agentes fallan
- **Design Patterns** — 6 patrones de harness engineering
- **Full Course** — 6 módulos: Instructions, State, Verification, Scope, Lifecycle, Skills
- **Resources** — Recursos curados
- **Templates** — Plantillas AGENTS.md, init.sh, etc.

## 🛠️ Harness Evaluator

48 checks en 6 subsistemas:

| Subsistema | Checks | Propósito |
|---|---|---|
| 📋 Instructions | 8 | Briefings, reglas, roadmap |
| 💾 State | 7 | Task tracking, memoria, persistencia |
| ✅ Verification | 6 | Tests, CI/CD, linters |
| 🎯 Scope | 7 | DoD, milestones, CONTRIBUTING |
| 🔄 Lifecycle | 8 | Init, Docker, dependencias |
| 🧠 Skills & POML | 12 | Skills, recetas POML, registry |

## 📋 Licencia

MIT — © 2026 Brahyan Belalcazar (ElBeRi)
