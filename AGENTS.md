# 🤖 Harness Course — Agent Briefing

## Identidad
Eres un agente trabajando en **Harness Course**, un sitio estático GitHub Pages (HTML/CSS/JS) que enseña Harness Engineering a agentes de IA.

## Stack
- **Frontend:** HTML5, CSS3 vanilla, JavaScript vanilla
- **Design:** Linear Dark (inspirado en `popular-web-designs`)
- **Hosting:** GitHub Pages (`iberi22.github.io/harness-course/`)
- **Herramienta clave:** `scripts/harness_evaluator.py` — scanner de harness

## Convenciones
- **CSS:** clases Utility-first + componentes en `css/style.css`
- **JS:** módulos en `js/shared.js` (no framework)
- **Páginas:** en `pages/`, sincronizar sidebar/search/footer en todas
- **No** usar npm, webpack, React, Tailwind — cero dependencias
- **Commits:** `feat:`, `fix:`, `docs:`, `chore:` convencional

## How Agents Should Use This Repo
1. `python3 scripts/harness_evaluator.py scan . --json` → diagnóstico
2. `python3 scripts/harness_evaluator.py fix .` → generar archivos faltantes
3. Re-escanear hasta score ≥ 80%

## Definition of Done
- Código escrito según spec
- Sin regresiones visuales
- Documentado en AGENTS.md si aplica
- Comiteado con mensaje descriptivo
- Sin secrets hardcodeados
