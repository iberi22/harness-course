# 🧠 Project Memory

> Contexto persistente para agentes que trabajan en este proyecto.

## Arquitectura
- **Sitio web:** HTML estático en raíz + `pages/`. CSS en `css/style.css`. JS en `js/shared.js`
- **Evaluador:** `scripts/harness_evaluator.py` — CLI puro, sin servidor
- **Templates fix:** `scripts/harness-fix/templates/` — 6 templates POML

## Decisiones clave
1. **Zero-deps** — stdlib python, HTML/CSS/JS vanilla. Sin frameworks
2. **CLI > MCP** — el evaluador es CLI, no servidor. Los agentes lo llaman con `python3 script.py`
3. **JSON compacto** — `--json` produce ~16KB vs ~400K tokens de análisis verbose
4. **POML native** — validación de recetas `.poml` como formato canónico de skills

## URLs importantes
- **Site:** https://iberi22.github.io/harness-course/
- **Repo:** https://github.com/iberi22/harness-course
- **Evaluador docs:** `docs/harness-evaluator-cli.md`

## Proyectos relacionados
- `~/projects/agents-flows-recipes/` — POML-first, case study (score 64.6% post-fix)
- `~/projects/swal-skills/` — skills catalog (score 58.3% post-fix)
- `~/projects/synapse-trading/` — Rust bot, necesita harness (37%)
