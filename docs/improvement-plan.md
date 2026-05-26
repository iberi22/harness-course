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

### I.3 OpenClaw — setMyCommands cosmetics 🧹 ✅

**Estado:** ✅ COMPLETADO — Fix ya existía en commit `fca9dae1` (25-Abr-2026). La truncación de comandos a 100 ya estaba implementada; el plan lo marcaba pendiente por falta de acceso al repo.

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

**Mejora adicional #1 (14-May-2026):** Sidebar navigation corregida en 7 páginas (instructions, leaderboard, lifecycle, scope, skills, state, verification) — ahora muestran los 6 subsistemas completos.

**Mejora adicional #2 (14-May-2026):** Sidebar navigation completada en las 8 páginas restantes (index, case-study, course, design-patterns, fundamentals, resources, templates, tutorial). Ahora las 15 páginas del sitio tienen navegación lateral completa y consistente con los 14 enlaces.

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
| 1 | **I.3 OpenClaw cosmetics** | I | 🟢 30 min | 🟢 Alto | Logs limpios = debugging más rápido | ✅ COMPLETADO — fix ya existía desde 25-Abr |
| 2 | **III.1 Páginas detalle subsistema** | III | 🟡 1 sesión | 🟢 Alto | Contenido educativo | ✅ COMPLETADO — 13-May-2026 |
| 3 | **III.2 Tutorial interactivo** | III | 🔴 3 sesiones | 🟢 Alto | Valor educativo | ✅ COMPLETADO — 12-May-2026 |
| 4 | **III.1b Sidebar navigation fix** | III | 🟢 15 min | 🟡 Medio | Consistencia UX | ✅ COMPLETADO — 14-May-2026 |
| 5 | **V.1 Starred scanner + leaderboard** | V | 🟡 1 sesión | 🟢 Alto | ✅ COMPLETADO — 13 repos escaneados, leaderboard.html creado y expandido |
| 6 | **IV.2 Importar skills externas** | IV | 🟡 2 sesiones | 🟢 Alto | ✅ COMPLETADO — 6 skills importados de 4 repos externos con frontmatter mejorado |
| 7 | **IV.1 Registry unificado** | IV | 🔴 2 sesiones | 🟢 Alto | ✅ COMPLETADO — iberi22/skills creado con 74 skills unificados, POML deprecado |
| 8 | **IV.3 POML templates mejorados** | IV | 🟡 1 sesión | 🟡 Medio | Fix más inteligente | ✅ COMPLETADO — 13-May-2026 |
| 9 | **V.2 Agente evaluador autónomo** | V | 🔴 2 sesiones | 🟢 Alto | Automatización total | ✅ COMPLETADO — 12-May-2026 |
| 10 | **V.3 Multi-lenguaje** | V | 🟡 1 sesión | 🟢 Medio | Alcance global | ✅ COMPLETADO — 13-May-2026 |
| 11 | **V.4 Comunidad** | V | 🔴 4 sesiones | 🟢 Alto | Visión a largo plazo | ✅ Sesión 1 — página community.html creada + leaderboard expandido a 16 repos |

---

## Cron Job Audit (15-May-2026)

**Score:** 100.0% 🟢 EXCELENTE (sin regresiones)

### Hallazgos y Correcciones — Sesión 1 (06:00 AM)

En ejecución de fallback (sin tareas pendientes accionables), se auditó la consistencia estructural del sitio HTML:

| # | Problema | Severidad | Solución |
|---|----------|-----------|----------|
| 1 | **404.html** — Sidebar incompleto (solo 3 secciones de 5), sin toggle i18n, sin data-i18n attributes, sin js/i18n.js | 🟡 HIGH | Sidebar reescrito con 5 secciones completas, toggle ES\|EN añadido, data-i18n en todos los textos, js/i18n.js añadido |
| 2 | **Footer inconsistente** — 11 páginas con footers no estandarizados (custom text sin data-i18n) vs 4 páginas con footer estándar | 🟢 LOW | resources.html y templates.html actualizados al footer estándar con data-i18n |
| 3 | **Formateo HTML** — resources.html y templates.html con toggleSidebar en una línea | 🟢 LOW | Formateado a multi-línea |

### Hallazgos y Correcciones — Sesión 2 (06:00 AM)

| # | Problema | Severidad | Solución |
|---|----------|-----------|----------|
| 1 | **Footer i18n incompleto** — 12 páginas del sitio con footers sin data-i18n attributes | 🟡 HIGH | footers estandarizados con data-i18n en las 12 páginas restantes vía 3 subagentes paralelos. |
| 2 | **Leaderboard fecha desactualizada** — Mostraba "12-May-2026" | 🟢 LOW | Actualizado a "15-May-2026" |

### Hallazgos y Correcciones — Sesión 3 (12:00 PM)

| # | Descubrimiento | Severidad | Acción Tomada |
|---|---------------|-----------|--------------|
| 1 | **I.3 OpenClaw cosmetics** — La truncación de comandos a 100 ya estaba implementada en commit `fca9dae1` (25-Abr-2026). El plan lo marcaba pendiente por falta de acceso al repo, pero el fix ya existía. | 🟢 DONE | Marcado como completado en el plan |
| 2 | **Aider score verificado** — Re-escan confirmó 30.3% 🟠 (correcto en leaderboard). La discrepancia con 44.3% en el README del scanner es dato desactualizado del README, no del leaderboard. | 🟢 DONE | No se necesita cambio |
| 3 | **V.1 Extended — Leaderboard expandido** — 3 nuevos repos escaneados y agregados: context-mode (44.0%), learn-harness-engineering (29.4%), awesome-harness-engineering (11.9%). La tabla pasó de 10 a 13 repos. Promedios de subsistemas recalculados, conclusiones actualizadas. | 🟡 MEJORA | Leaderboard reordenado, promedios actualizados |

### Hallazgos y Correcciones — Sesión 4 (06:00 PM)

| # | Descubrimiento | Severidad | Acción Tomada |
|---|---------------|-----------|--------------|
| 1 | **V.4 Comunidad — Página community.html** | 🟡 MEJORA | Creada página community.html (303 líneas) con visión del registry público, instrucciones de submission (4 pasos: scan → issue → paste → listed), tabla de community scores, beneficios (4-card grid), botón de submit vía GitHub Issues. Diseño Linear Dark consistente con leaderboard.html. |
| 2 | **Sidebar — Enlace a Community añadido** | 🟡 MEJORA | Añadido enlace 🌐 Community a la sección Interactive del sidebar en las 17 páginas HTML del sitio (index.html + 404.html + 15 pages/). Traducciones EN/ES añadidas a i18n.js (`nav.community`). |
| 3 | **Leaderboard expandido a 16 repos** | 🟢 MEJORA | Añadidos: llama.cpp (41.3% 🟡, 100K★ C/C++), iberi22/skills (25.7% 🟠 Skills), iberi22/imported-skills (4.6% 🔴 CRÍTICO). Promedios de subsistemas recalculados. Separador visual entre original 13 y nuevos 3. |

|**Estado del plan:** V.4 Sesión 1 completada. Leaderboard ahora con 16 repos. Score del proyecto: 100.0% 🟢 (sin regresiones).

### Hallazgos y Correcciones — Sesión 5 (24-May-2026)

| # | Descubrimiento | Severidad | Acción Tomada |
|---|---------------|-----------|--------------|
| 1 | **score-submission.md template** — GitHub Issue template for community score submissions was missing (referenced by community.html but file didn't exist) | 🟡 MEJORA | Created `.github/ISSUE_TEMPLATE/score-submission.md` with bilingual EN/ES guided form |
| 2 | **FAQ section added to community.html** — Community page lacked FAQ section | 🟡 MEJORA | Added collapsible FAQ module with 5 questions + i18n keys in ES/EN |
| 3 | **Leaderboard expanded to 18 repos** — Added harness-course-site (1.8% 🔴) and local-models (0.0% 🔴) | 🟢 MEJORA | Leaderboard updated with separator, date updated to 24-May-2026, conclusions adjusted |
| 4 | **zeroclaw re-scan** — Score confirmed at 45.0% 🟡 (unchanged from prior scan) | 🟢 DONE | No change needed — leaderboard data current |

**Estado del plan:** V.4 Sesión 2 completada. Leaderboard ahora con 18 repos. Página community.html con FAQ. Score del proyecto: 100.0% 🟢 (sin regresiones).

### Hallazgos y Correcciones — Sesión 6 (24-May-2026 12:00 PM)

| # | Descubrimiento | Severidad | Acción Tomada |
|---|---------------|-----------|--------------|
| 1 | **Sidebar inconsistente** — `leaderboard.html` tenía una sección "Community" separada (correcta), pero las otras 16 páginas del sitio (index.html, 404.html, 14 pages/*.html) tenían el enlace Community dentro de la sección "Interactive" | 🟡 HIGH | Enlace Community extraído de Interactive en las 16 páginas y colocado en su propia sección nav (Community), consistente con leaderboard.html. +48 líneas netas, sin regresiones. |
| 2 | **Peligro: patch con fuzzy matching** — El primer intento usó un old_string demasiado genérico que matcheó la sección Resources en vez de Interactive, eliminando recursos de 16 páginas. Corregido usando old_string más específico (incluyendo `</nav>` para unicidad). | 🟢 DONE | Se recuperó con `git checkout` y se rehizo con patrón específico. Lección aprendida: siempre incluir contexto único en old_string. |

**Estado del plan:** V.4 Sesión 3 (sidebar fix). Score del proyecto: 100.0% 🟢 (sin regresiones). Sidebar unificado en las 17 páginas del sitio.

### Hallazgos y Correcciones — Sesión 7 (25-May-2026 06:00 AM)

| # | Descubrimiento | Severidad | Acción Tomada |
|---|---------------|-----------|--------------|
| 1 | **synapse-trading score actualizado** — Re-scan mostró 100.0% 🟢 (+18.1pp desde 81.9%). Commit `3e671b4` mejoró Dockerfile SKILLS path y commit `202f190` añadió Telegram bot commands y risk tuning. | 🟡 MEJORA | Leaderboard actualizado: synapse-trading 81.9% → 100.0%, rank #2 retenido. |
| 2 | **agent-recipes-repo score mejorado** — Re-scan mostró 48.6% 🟡 (+6.9pp desde 41.7%). Commit `eec5e54` de readiness assessment: AGENTS.md autocontenido, CLAUDE.md, badges, bash scripts. | 🟡 MEJORA | Leaderboard actualizado: 41.7% → 48.6%. Reordenado de rank #8 → #5 (ahora sobre zeroclaw 45.0%). |
| 3 | **swal-skills score bajó 1.5pp** — De 74.0% → 72.5% por cambios en skills directory (skills marcados como private). | 🟢 DONE | Leaderboard actualizado: 74.0% → 72.5%. Rank #3 retenido. |
| 4 | **Subsystem averages recalibrados** — Tras re-scan de 18 repos: Instructions 38%→46%, State 26%→30%, Verification 55%→50%, Scope 35%→30%, Skills 48%→36%. | 🟡 MEJORA | Averages actualizados en sección 📊 Comparativa por Subsistema. |

**Estado del plan:** V.5 Re-scan y leaderboard refresh. Leaderboard actualizado con datos frescos de 18 repos, reordenado, promedios recalculados. Score del proyecto: 100.0% 🟢 (sin regresiones).

### Hallazgos y Correcciones — Sesión 8 (25-May-2026 12:00 PM)

| # | Descubrimiento | Severidad | Acción Tomada |
|---|---------------|-----------|--------------|
| 1 | **mattpocock/skills escaneado** — 68K★ Shell, repo de skills para agentes. Score: 27.5% 🟠. Skills subsystem 73.3% (28 SKILL.md con frontmatter válido) pero Verification 0.0% y State 10.0%. | 🟡 MEJORA | Clonado + escaneado. Añadido al leaderboard como #15 con 27.5%. |
| 2 | **hummingbot/hummingbot escaneado** — 18K★ Python, popular trading bot. Score: 36.7% 🟠. Excelente Verification 94.4% (757 tests, CI/CD, linter) pero Instructions 10.0% y Skills 0.0%. | 🟡 MEJORA | Clonado + escaneado. Añadido al leaderboard como #12 con 36.7%. |
| 3 | **OpenHands/OpenHands escaneado** — 73K★ Python, AI-driven development platform. Score: 41.3% 🟡 REGULAR. Verification 83.3% (323 tests, CI/CD) pero Skills 0.0% y State 15.0%. | 🟡 MEJORA | Clonado + escaneado. Añadido al leaderboard como #10 con 41.3% (tie con llama.cpp). |
| 4 | **Leaderboard expandido a 21 repos** — 3 nuevos repos añadidos en orden correcto. Promedios recalculados: Inst 45%, State 28%, Verif 51%, Scope 29%, Lifecycle 45%, Skills 34%. Conclusiones actualizadas. | 🟢 MEJORA | Leaderboard actualizado, commit `d518716`. |

**Estado del plan:** V.5 Expansión — 3 nuevos repos escaneados del catálogo de starred repos. Leaderboard ahora con 21 repos. Score del proyecto: 100.0% 🟢 (sin regresiones).

### Hallazgos y Correcciones — Sesión 9 (25-May-2026 06:00 PM)

| # | Descubrimiento | Severidad | Acción Tomada |
|---|---------------|-----------|--------------|
| 1 | **github/awesome-copilot (32K★ Python)** — Escaneado: 34.9% 🟠 DÉBIL. Skills subsystem impresionante (73.3%, 360 SKILL.md con frontmatter válido), pero Verification 11.1% (sin tests, sin linter) y State 10.0% (sin task tracking ni memoria). Tiene AGENTS.md completo con estructura de proyecto. | 🟡 MEJORA | Clonado + escaneado. Añadido al leaderboard como #13 con 34.9%. |
| 2 | **langchain-ai/langgraph (31K★ Python)** — Escaneado: 23.9% 🟠 DÉBIL. Verification 33.3% (121 tests, CI/CD) y Lifecycle 40.0% (Makefile, .gitignore, LICENSE). Pero State 10.0% y Skills 0.0%. Tiene AGENTS.md con instrucciones de monorepo. | 🟡 MEJORA | Clonado + escaneado. Añadido al leaderboard como #18 con 23.9%. |
| 3 | **dzhng/deep-research (18K★ TypeScript)** — Escaneado: 14.7% 🔴 CRÍTICO. Lifecycle 50.0% (Docker, .env.example, .gitignore, LICENSE) es el único punto fuerte. Scope 0.0% (sin DoD, milestones, templates, ni ningún check de Scope). State 15.0%, Skills 0.0%. | 🟡 MEJORA | Clonado + escaneado. Añadido al leaderboard como #19 con 14.7%. |
| 4 | **Leaderboard expandido a 24 repos** — 3 nuevos repos añadidos: awesome-copilot (34.9%), langgraph (23.9%), deep-research (14.7%). Promedios recalculados: Inst 44%, State 26%, Verif 47%, Scope 27%, Lifecycle 45%, Skills 33%. Conclusiones actualizadas con menciones a los nuevos repos. | 🟢 MEJORA | Leaderboard actualizado con 24 repos, promedios y conclusiones actualizados. |

**Estado del plan:** V.5 Expansión — 3 nuevos repos escaneados. Leaderboard ahora con 24 repos. Score del proyecto: 100.0% 🟢 (sin regresiones).

### Hallazgos y Correcciones — Sesión 10 (26-May-2026 12:00 AM)

| # | Descubrimiento | Severidad | Acción Tomada |
|---|---------------|-----------|--------------|
| 1 | **VoltAgent/awesome-design-md (74K★ DESIGN)** — Escaneado: 9.2% 🔴 CRÍTICO. Solo README.md, CONTRIBUTING.md, .gitignore y LICENSE pasan. Verification 0.0% (sin tests ni CI/CD), Skills 0.0%. Es un repo de DESIGN.md files — no esperado tener harness completo, pero sorprende que no tenga ni AGENTS.md. | 🟡 MEJORA | Clonado + escaneado. Añadido al leaderboard como #24 con 9.2%. |
| 2 | **thedotmack/claude-mem (74K★ TypeScript)** — Escaneado: 37.6% 🟠 DÉBIL. Verification 72.2% (155 tests, CI/CD, tsconfig) es el punto más fuerte. Instructions 55% (CLAUDE.md completo + docs/ extenso). Lifecycle 55% (Docker, deps). Skills 0% (sin skills/). | 🟡 MEJORA | Clonado + escaneado. Añadido al leaderboard como #11 (empate con freqtrade) con 37.6%. |
| 3 | **earendil-works/pi (47K★ TypeScript)** — Escaneado: 26.6% 🟠 DÉBIL. Tiene AGENTS.md completo de 10K+ chars con reglas extensas (Instructions 40%). 251 tests encontrados pero no hay test directory (Verification 38.9%). Skills 0%. | 🟡 MEJORA | Clonado + escaneado. Añadido al leaderboard como #18 con 26.6%. |
| 4 | **Leaderboard expandido a 27 repos** — 3 nuevos repos añadidos: claude-mem (37.6%, #11), pi (26.6%, #18), awesome-design-md (9.2%, #24). Promedios recalculados: Inst 43%, State 25%, Verif 46%, Scope 27%, Lifecycle 44%, Skills 29%. Conclusiones actualizadas con menciones a los nuevos repos. | 🟢 MEJORA | Leaderboard actualizado con 27 repos, promedios y conclusiones actualizados. |

**Estado del plan:** V.5 Expansión — 3 nuevos repos escaneados del catálogo de starred repos. Leaderboard ahora con 27 repos. Score del proyecto: 100.0% 🟢 (sin regresiones).

### Hallazgos y Correcciones — Sesión 11 (26-May-2026 06:00 AM)

| # | Descubrimiento | Severidad | Acción Tomada |
|---|---------------|-----------|--------------|
| 1 | **Fosowl/agenticSeek (26K★ Python)** — Escaneado: 30.3% 🟠 DÉBIL. Verification 72.2% es decente (tests), pero Instructions 25%, State 15% y Skills 0%. Proyecto "Fully Local Manus AI" sin harness de agente. | 🟡 MEJORA | Clonado + escaneado. Añadido al leaderboard como #16 (tie con aider) con 30.3%. |
| 2 | **camel-ai/camel (16K★ Python)** — Escaneado: 39.4% 🟠 DÉBIL. Verification 83.3% (278 tests, CI/CD) y Lifecycle 75% son puntos fuertes. Pero Instructions 25% y Skills 0%. Framework multi-agente popular sin AGENTS.md ni skills/. | 🟡 MEJORA | Clonado + escaneado. Añadido al leaderboard como #11 con 39.4%. |
| 3 | **nanobrowser/nanobrowser (12K★ TypeScript)** — Escaneado: 20.2% 🔴 CRÍTICO. Tiene AGENTS.md completo (11K chars, Instructions 40%) pero Verification 11.1% (solo 1 test), State 10% y Skills 0%. Chrome extension multi-agente. | 🟡 MEJORA | Clonado + escaneado. Añadido al leaderboard como #23 con 20.2%. |
| 4 | **Leaderboard expandido a 30 repos** — 3 nuevos repos añadidos: camel (39.4%, #11), agenticSeek (30.3%, #16), nanobrowser (20.2%, #23). Promedios recalculados: Inst 42%, State 24%, Verif 47%, Scope 27%, Lifecycle 45%, Skills 26%. Conclusiones actualizadas con menciones a los nuevos repos. | 🟢 MEJORA | Leaderboard actualizado con 30 repos, promedios y conclusiones actualizados. |

**Estado del plan:** V.5 Expansión — 3 nuevos repos escaneados del catálogo de starred repos. Leaderboard ahora con 30 repos. Score del proyecto: 100.0% 🟢 (sin regresiones).

### Próxima Sesión Sugerida
- Scan more starred repos from the catalog (e.g., goose 44K★, GitNexus 37K★, or genai_agents 21K★)
- Re-scan existing leaderboard repos for score drift — especially swal-skills (72.5%), agents-flows-recipes (64.6%), and zeroclaw (45.0%)
- Consider re-scanning repos that may have improved since last scan (awesome-copilot at 34.9% — may have added more docs)
- Skills gap (26% average, 36/30 repos at 0%) remains the biggest universal weakness

## Timeline sugerido
Semana 2:  ████████████████░░░░  Fase II (infraestructura)
Semana 3:  ██████░░░░░░░░░░░░░░  Fase IV.2 (importar skills)
Semanas 4-5: ████████████████████  Fase III (contenido)
Semana 6:  ██████████░░░░░░░░░░  Fase IV.1 + IV.3 (registry + templates)
Semana 7+: ████████████████████  Fase V (expansión)
```

**Total estimado:** 7-10 sesiones para completar todo.

---

*Plan generado del análisis de 4 proyectos, ~35 archivos de harness, 150 starred repos, y diagnóstico de OpenClaw.*
