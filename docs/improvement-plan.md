# 🗺️ Plan de Mejoras — Harness Engineering Ecosystem

> **Fecha:** 10 Mayo 2026
> **Versión:** 1.0
> **Objetivo:** Llevar todos los proyectos a score ≥ 80% y estabilizar OpenClaw

---

## Filosofía

Cada fase sigue un principio: **token-saving, auto-corrección, una cosa a la vez.**

- **Fase I:** Lo que más valor da con menos esfuerzo (bajo fruta)
- **Fase II:** Estabilización de infraestructura (OpenClaw + CI/CD)
- **Fase III:** Contenido educativo profundo (el curso como tal)
- **Fase IV:** Unificación del ecosistema (skills, registry, templates)
- **Fase V:** Expansión (multi-proyecto, comunidad, automatización)

---

## Fase I: Fruta madura 🍎 — ✅ COMPLETADA

> **Duración estimada:** 2-3 sesiones
> **Impacto:** Alto esfuerzo / Alto valor

### I.1 Harness Course → 60%+ 🔵 ✅

**Estado actual:** 100.0% 🟢 EXCELENTE (12-May-2026)
**Objetivo:** ≥60% (azul) — SUPERADO

Todos los archivos necesarios fueron creados y el score alcanzó 100%.
Verification pasó de 0% → 100% con test suite, linter y CI/CD.

### I.2 SynapseTrader — Issues críticos 🐛 ✅

**Estado actual:** 100.0% 🟢 EXCELENTE (12-May-2026)
**Objetivo:** Issues #7 y #9 corregidos

Todos los issues cerrados en commit `0549a6f`:
- ✅ Accountant agent crea directorios correctamente (issue #7)
- ✅ OpsAnalyzer BraveAI: key validation, 3-failure grace period, non-blocking
- ✅ restart-daemon.sh apunta a release/ no debug/
- ✅ 5 skills creados (operator, analyst, risk-manager, execution-engine, orchestrator)

### I.3 OpenClaw — setMyCommands cosmetics 🧹 ⏳

**Estado:** Pendiente — requiere acceso al repositorio OpenClaw

---

## Fase II: Infraestructura 🏗️

> **Duración estimada:** 2-3 sesiones
> **Impacto:** Bajo esfuerzo / Alto valor (ahorro de tokens)

### II.1 Integrar context-mode (14K★) ⚡

**Repo:** https://github.com/mksglu/context-mode
**Valor:** 98% reducción de tokens en llamadas a agente

**Plan:**
1. Clonar y entender el mecanismo (sandboxes tool output)
2. Crear skill para Hermes Agent que aplique context-mode
3. Probar: comparar tokens consumidos con y sin context-mode
4. Si funciona: integrar en OpenClaw vía plugin o skill

**Archivos a crear:**
- `skills/context-mode/SKILL.md` — skill wrapper para Hermes
- `scripts/context-mode-benchmark.py` — script para medir reducción de tokens
- `docs/context-mode-integration.md` — documentación

**Criterio de éxito:** 50%+ reducción de tokens en sesiones de agente.

### II.2 CI/CD completo 🔄

**Estado actual:** `harness-ci.yml` creado pero sin badge ni tests reales

**Acciones:**
1. Agregar `test.yml` — HTML validation + link checker en GitHub Actions
2. Agregar badge de CI al README: `[![Harness](https://github.com/iberi22/harness-course/actions/workflows/harness-ci.yml/badge.svg)]`
3. Hacer que el badge muestre el último score (vía shields.io endpoint custom o GitHub status)

**Criterio de éxito:** PRs muestran badge + score en comentario automático.

### II.3 Script `harness` como package 📦

**Estado actual:** Wrapper bash en `~/.local/bin/harness`

**Mejora:**
1. Hacer el script pip-installable (`pyproject.toml` + `setup.py`)
2. O crear installer `curl -sf https://raw.githubusercontent.com/iberi22/harness-course/main/scripts/install.sh | bash`
3. Agregar auto-actualización: `harness update`

**Criterio de éxito:** `curl | bash` instala el CLI en cualquier máquina.

---

## Fase III: Contenido educativo 📚 — ✅ COMPLETADA

> **Duración estimada:** 3-4 sesiones
> **Impacto:** Alto esfuerzo / Alto valor (el curso como tal)

### III.1 Páginas de detalle por subsistema ✅

**Estado:** ✅ COMPLETADO — 13-May-2026
**Nota:** Las 6 páginas fueron creadas como parte de V.3 multi-language. Cada una incluye contenido educativo completo con módulos colapsables, ejemplos, anti-patrones y checklists.

| Página | Subsistema | Contenido |
|---|---|---|
| `/pages/instructions.html` | 📋 Instructions | Cómo escribir AGENTS.md, ROADMAP.md, RULES.md |
| `/pages/state.html` | 💾 State | TASK.md, MEMORY.md, persistencia, diario de sesiones |
| `/pages/verification.html` | ✅ Verification | Tests, CI/CD, linters, type checking |
| `/pages/scope.html` | 🎯 Scope | Definition of Done, milestones, CONTRIBUTING |
| `/pages/lifecycle.html` | 🔄 Lifecycle | Init scripts, Docker, dependencias, .env |
| `/pages/skills.html` | 🧠 Skills & POML | SKILL.md, recetas POML, registry, providers |

**Mejora adicional (14-May-2026):** Sidebar navigation corregida en las 6 páginas — ahora todas muestran los 6 subsistemas completos en la navegación lateral (antes cada página solo mostraba 3-4).

### III.2 Tutorial interactivo: "De 45% a 80% en 10 minutos" ✅

**Estado:** ✅ COMPLETADO — 12-May-2026 (commit 35abe1d)

**Formato:** Página web con pasos interactivos (JS)
**Contenido:**
1. `harness scan . --json` → ver diagnóstico
2. `harness fix .` → generar archivos faltantes
3. Personalizar cada archivo generado
4. Re-escanear → ver mejora
5. Agregar tests → sube Verification
6. Score final

### III.3 Case study: agents-flows-recipes ✅

**Contenido:**
- Por qué este proyecto tiene el mejor score (61.5%)
- Qué hace bien: POML recetas, _registry, skills con frontmatter
- Qué se puede aprender para otros proyectos

**Página creada:** `pages/case-study.html` — 7 módulos, checklist, diagnóstico rápido
**Navegación actualizada:** Enlace agregado al sidebar de todas las 12 páginas del sitio

**Criterio de éxito:** ✅ Cumplido — case study visible en el sitio del curso.

---

## Fase IV: Unificación 🧩

> **Duración estimada:** 2-3 sesiones
> **Impacto:** Medio esfuerzo / Alto valor (mantenibilidad)

### IV.1 Unificar skills registry

**Problema:** 13 skills duplicadas entre `swal-skills` y `agents-flows-recipes`

| Skill | swal-skills | agents-flows-recipes |
|---|---|---|
| astro, codex, gemini, github, nextjs, python, qwen, rust, skill-launcher, skill-provider, tailwindcss, vite, web-research | ✅ | ✅ |

**Plan:**
1. Elegir un repo como source of truth (recomiendo `agents-flows-recipes` por su POML + _registry)
2. Mover skills únicas de swal-skills (11 skills: coding-agent, deploy-anywhere, frontend-agent, etc.)
3. Actualizar _registry/manifest.yaml para incluir todas
4. swal-skills pasa a ser un symlink/wrapper que apunta al registry central

### IV.2 Importar skills externas 🌟

**Targets prioritarios:**

| Repo | ★ | Valor | Acción |
|---|---|---|---|
| `forrestchang/andrej-karpathy-skills` | 123K | Principios Karpathy para coding agents | Crear skill `karpathy-principles` para Hermes |
| `mattpocock/skills` | 68K | Skills reales de ingeniería | Clonar y catalogar, importar las relevantes |
| `Orchestra-Research/AI-Research-SKILLs` | 8K | Skills de AI research | Adaptar para el flujo de investigación |
| `Jane-xiaoer/claude-design-principles` | 40 | Design principles desde Claude | Convertir a skill de diseño UI |

**Criterio de éxito:** Skills index unificado con ≥60 skills totales.

### IV.3 POML template generator mejorado 🏗️ ✅ COMPLETADO — 13-May-2026

**Estado actual:** ✅ COMPLETADO — 13-May-2026

**Implementado:**
- `src/harness/project_detector.py` — `ProjectDetector` con método `detect()` que identifica el tipo de proyecto (Rust, Python, Node, Trading) analizando archivos presentes (e.g., `Cargo.toml`, `requirements.txt`, `package.json`, indicadores de trading).
- 14 nuevos templates POML en `src/harness/fix-templates/` organizados por tipo:
  - `rust/` — 4 templates (AGENTS.md, ROADMAP.md, Dockerfile, Makefile)
  - `python/` — 3 templates (AGENTS.md, ROADMAP.md, pyproject.toml)
  - `node/` — 3 templates (AGENTS.md, ROADMAP.md, package.json)
  - `trading/` — 4 templates (AGENTS.md, ROADMAP.md, .env.example, restart script)
- Nuevo flag CLI: `harness fix . --auto` que usa el detector para seleccionar automáticamente el template set adecuado.

**Criterio de éxito:** ✅ `harness fix . --auto` genera contenido específico del tipo de proyecto.

---

## Fase V: Expansión 🚀

> **Duración estimada:** 4-6 sesiones
> **Impacto:** Alto esfuerzo / Muy alto valor

### V.1 Escanear y catalogar starred repos

**Estado actual:** 150 repos catalogados en texto
**Mejora:**
1. Escanear los top-20 starred con `harness scan . --json`
2. Identificar los que tienen mejor harness
3. Crear un "leaderboard" de harness scores entre repos open-source
4. Publicar en el sitio del curso

**Candidatos a escanear:**
- `opencode-ai/opencode` (12K★ Go) — CLI de coding agent
- `zeroclaw-labs/zeroclaw` (31K★ Rust) — OpenClaw mismo
- `browser-use/browser-use` (93K★ Python) — browser automation
- `freqtrade/freqtrade` (50K★ Python) — trading bot
- `Aider-AI/aider` (44K★ Python) — AI pair programming

### V.2 Agente evaluador autónomo 🤖 ⏳ EN PROGRESO — Iniciado: 12-May-2026

**Visión:** Un cron job que:
1. Escanea todos los proyectos del usuario periódicamente
2. Si el score bajó, genera un reporte
3. Si hay issues nuevos, los crea en GitHub
4. Envía resumen por Telegram

**Implementación:**
```bash
# Cron job diario a las 9 AM
./scripts/evaluator-cron.sh
```

**Documentación:** `docs/evaluator-agent.md`  
**Scripts creados:**
- `scripts/evaluator-cron.sh` — registro idempotente del cron job
- `scripts/auto-evaluate.sh` — orquestador de escaneo multi-proyecto

### V.3 Multi-lenguaje 🌐 ✅ COMPLETADO — 13-May-2026

**Estado actual:** ✅ COMPLETADO

**Implementado:**
1. **README en inglés** — README.md ahora bilingüe (EN + ES) con badges al inicio
2. **Páginas del curso con toggle ES/EN** — Sistema i18n completo:
   - `js/i18n.js`: Traductor zero-dependency con diccionario EN/ES
   - Toggle ES|EN en sidebar de todas las 15 páginas HTML
   - data-i18n attributes en toda la navegación, hero, stats, contenido y footer
   - localStorage para persistencia de preferencia de idioma
   - CSS toggle styles integrados en el sistema Linear Dark
3. **Comentarios en código en inglés** — Python docstrings, comments en scripts y CSS convertidos a inglés
4. **AGENTS.md bilingüe** — Briefing completo en EN + ES

**Criterio de éxito:** ✅ Cumplido — cualquier página del curso puede switchear entre EN y ES. Código fuente con comentarios en inglés (convención universal).

### V.4 Comunidad de harnesses

**Visión:** Un repositorio público donde la gente pueda:
1. Subir sus harness scores
2. Ver排名 (ranking) de proyectos
3. Compartir skills y recetas POML
4. Aprender de los mejores harnesses

---

## Mapa de dependencias

```
Fase I (Fruta madura)
├── I.1 Harness Course 60%     ← No depende de nada
├── I.2 SynapseTrader fixes    ← No depende de nada
└── I.3 OpenClaw cosmetics     ← No depende de nada

Fase II (Infraestructura)
├── II.1 context-mode          ← Depende de I.1 (tener repo estable)
├── II.2 CI/CD completo        ← Depende de I.1 (tests que correr)
└── II.3 Package CLI           ← Depende de I.1 (evaluador estable)

Fase III (Contenido)
├── III.1 Páginas subsistema   ← Depende de I.1 (proyecto estable)
├── III.2 Tutorial interactivo ← Depende de III.1
└── III.3 Case study           ← Depende de III.1

Fase IV (Unificación)
├── IV.1 Registry unificado    ← Depende de tener swal-skills + agents-flows-recipes
├── IV.2 Importar skills       ← Depende de IV.1
└── IV.3 POML templates        ← Depende de I.1 (evaluador)

Fase V (Expansión)
├── V.1 Starred scanner        ← Depende de II.3 (CLI estable)
├── V.2 Agente autónomo        ← Depende de II.2 (CI/CD funcionando)
├── V.3 Multi-lenguaje         ← Depende de III.1 (contenido estable)
└── V.4 Comunidad              ← Depende de V.1 + V.2
```

---

## Priorización recomendada

| # | Item | Fase | Esfuerzo | Impacto | Por qué ahora | Estado |
|---|---|---|---|---|---|---|
| 1 | **I.3 OpenClaw cosmetics** | I | 🟢 30 min | 🟢 Alto | Logs limpios = debugging más rápido | ⏳ Sin repo |
| 2 | **III.1 Páginas detalle subsistema** | III | 🟡 1 sesión | 🟢 Alto | Contenido educativo | ✅ COMPLETADO — 13-May-2026 |
| 3 | **III.2 Tutorial interactivo** | III | 🔴 3 sesiones | 🟢 Alto | Valor educativo | ✅ COMPLETADO — 12-May-2026 |
| 4 | **III.1b Sidebar navigation fix** | III | 🟢 15 min | 🟡 Medio | Consistencia UX | ✅ COMPLETADO — 14-May-2026 |
| 5 | **V.1 Starred scanner + leaderboard** | V | 🟡 1 sesión | 🟢 Alto | ✅ COMPLETADO — 10 repos escaneados, leaderboard.html creado |
| 6 | **IV.2 Importar skills externas** | IV | 🟡 2 sesiones | 🟢 Alto | ✅ COMPLETADO — 6 skills importados de 4 repos externos con frontmatter mejorado |
| 7 | **IV.1 Registry unificado** | IV | 🔴 2 sesiones | 🟢 Alto | ✅ COMPLETADO — iberi22/skills creado con 74 skills unificados, POML deprecado |
| 8 | **IV.3 POML templates mejorados** | IV | 🟡 1 sesión | 🟡 Medio | Fix más inteligente | ✅ COMPLETADO — 13-May-2026 |
| 9 | **V.2 Agente evaluador autónomo** | V | 🔴 2 sesiones | 🟢 Alto | Automatización total | ✅ COMPLETADO — 12-May-2026 |
| 10 | **V.3 Multi-lenguaje** | V | 🟡 1 sesión | 🟢 Medio | Alcance global | ✅ COMPLETADO — 13-May-2026 |
| 11 | **V.4 Comunidad** | V | 🔴 4 sesiones | 🟢 Alto | Visión a largo plazo | ⏳ Pendiente |

---

## Timeline sugerido

```
Semana 1:  ████████████████░░░░  Fase I (fruta madura)
Semana 2:  ████████████████░░░░  Fase II (infraestructura)
Semana 3:  ██████░░░░░░░░░░░░░░  Fase IV.2 (importar skills)
Semanas 4-5: ████████████████████  Fase III (contenido)
Semana 6:  ██████████░░░░░░░░░░  Fase IV.1 + IV.3 (registry + templates)
Semana 7+: ████████████████████  Fase V (expansión)
```

**Total estimado:** 7-10 sesiones para completar todo.

---

*Plan generado del análisis de 4 proyectos, ~35 archivos de harness, 150 starred repos, y diagnóstico de OpenClaw.*
