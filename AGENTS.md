# 🤖 Harness Course — Agent Briefing

## Identity
You are an agent working on **Harness Course**, a static GitHub Pages site (HTML/CSS/JS) that teaches Harness Engineering to AI agents.

## Stack
- **Frontend:** HTML5, vanilla CSS3, vanilla JavaScript
- **Design:** Linear Dark (inspired by `popular-web-designs`)
- **Hosting:** GitHub Pages (`iberi22.github.io/harness-course/`)
- **Key tool:** `scripts/harness_evaluator.py` — harness scanner

## Conventions
- **CSS:** Utility-first classes + components in `css/style.css`
- **JS:** Modules in `js/shared.js` (no framework)
- **Pages:** In `pages/`; keep sidebar, search, and footer in sync across all pages
- **Do not** use npm, webpack, React, or Tailwind — zero dependencies
- **Commits:** conventional style — `feat:`, `fix:`, `docs:`, `chore:`

## How Agents Should Use This Repo
1. `pip install -e .` (or `harness -h` if already installed)
2. `harness scan . --json` → diagnosis
3. `harness fix .` → generate missing files
4. Re-scan until score ≥ 80%

## Definition of Done
- Code written to spec
- No visual regressions
- Documented in AGENTS.md if applicable
- Committed with a descriptive message
- No hardcoded secrets

---

# 🤖 Harness Course — Briefing para Agentes

## Identidad
Eres un agente trabajando en **Harness Course**, un sitio estático en GitHub Pages (HTML/CSS/JS) que enseña Harness Engineering a agentes de IA.

## Stack
- **Frontend:** HTML5, CSS3 vanilla, JavaScript vanilla
- **Design:** Linear Dark (inspirado en `popular-web-designs`)
- **Hosting:** GitHub Pages (`iberi22.github.io/harness-course/`)
- **Herramienta clave:** `scripts/harness_evaluator.py` — scanner de harness

## Convenciones
- **CSS:** clases Utility-first + componentes en `css/style.css`
- **JS:** módulos en `js/shared.js` (sin framework)
- **Páginas:** en `pages/`, sincronizar sidebar, búsqueda y footer en todas
- **No** usar npm, webpack, React ni Tailwind — cero dependencias
- **Commits:** estilo convencional — `feat:`, `fix:`, `docs:`, `chore:`

## Cómo los Agentes Deben Usar Este Repo
1. `pip install -e .` (o `harness -h` si ya está instalado)
2. `harness scan . --json` → diagnóstico
3. `harness fix .` → generar archivos faltantes
4. Re-escanear hasta score ≥ 80%

## Definition of Done
- Código escrito según especificación
- Sin regresiones visuales
- Documentado en AGENTS.md si aplica
- Comiteado con mensaje descriptivo
- Sin secrets hardcodeados
