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

## Fase I: Fruta madura 🍎

> **Duración estimada:** 2-3 sesiones
> **Impacto:** Alto esfuerzo / Alto valor

### I.1 Harness Course → 60%+ 🔵

**Estado actual:** ~45% 🟡
**Objetivo:** ≥60% (azul)

| Sub-sistema | Actual | Target | Acción |
|---|---|---|---|
| Verification | 0% | 50% | Agregar test suite (HTML validation, link checker) |
| Skills & POML | 0% | 40% | Crear `skills/` directory + 1 receta POML |
| Lifecycle | ~40% | 60% | Mejorar init.sh, agregar requirements-dev.txt |
| Scope | ~30% | 50% | Mejorar templates .github/ |

**Archivos a crear:**
- `.github/workflows/test.yml` — HTML + link checker CI
- `tests/test_html.sh` — validador de HTML con `html-validator` o `tidy`
- `tests/test_links.sh` — link checker con `linkchecker` o `broken-link-checker`
- `skills/README.md` — catálogo de skills del proyecto
- `skills/harness-evaluator-skill/SKILL.md` — skill para usar el evaluador
- `poml/harness-scan.poml` — receta POML para escanear harness
- `requirements-dev.txt` — dependencias de desarrollo

**Criterio de éxito:** `harness scan . --ci --threshold 60` pasa.

### I.2 SynapseTrader — Issues críticos 🐛

**Estado actual:** ~50% 🟡
**Objetivo:** 55%+ y sin regresiones

| Issue | Prioridad | Acción |
|---|---|---|
| Accountant agent no crea dirs (#7) | Alta | Fix en `accountant.rs` — validar permisos de directorio |
| OpsAnalyzer BraveAI símbolos (#9) | Alta | Alinear símbolos entre config y restart script |
| restart-daemon.sh apunta a debug/ | Media | Cambiar `debug/` → `release/` |
| Skills & POML en 0% | Media | Agregar skills/ directory básico |

**Criterio de éxito:** Los 3 bugs cerrados, daemon estable post-fix.

### I.3 OpenClaw — setMyCommands cosmetics 🧹

**Estado:** 147 comandos > 100 límite Telegram API
**Acción:** Reducir skills visibles en menú o desactivar comandos nativos

**Opciones:**
1. Desactivar `channels.telegram.commands.native: false` — oculta el menú, los comandos siguen funcionando vía texto
2. Reducir skills a los 100 más usados
3. Configurar por-bot: bots principales tienen los comandos, bots secundarios no

**Criterio de éxito:** Logs sin errores `setMyCommands` después del restart.

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

## Fase III: Contenido educativo 📚

> **Duración estimada:** 3-4 sesiones
> **Impacto:** Alto esfuerzo / Alto valor (el curso como tal)

### III.1 Páginas de detalle por subsistema

**Estado actual:** 5 páginas genéricas (course, fundamentals, design-patterns, resources, templates)
**Objetivo:** 6 páginas nuevas — una por subsistema del harness

| Página | Subsistema | Contenido |
|---|---|---|
| `/pages/instructions.html` | 📋 Instructions | Cómo escribir AGENTS.md, ROADMAP.md, RULES.md |
| `/pages/state.html` | 💾 State | TASK.md, MEMORY.md, persistencia, diario de sesiones |
| `/pages/verification.html` | ✅ Verification | Tests, CI/CD, linters, type checking |
| `/pages/scope.html` | 🎯 Scope | Definition of Done, milestones, CONTRIBUTING |
| `/pages/lifecycle.html` | 🔄 Lifecycle | Init scripts, Docker, dependencias, .env |
| `/pages/skills.html` | 🧠 Skills & POML | SKILL.md, recetas POML, registry, providers |

**Cada página debe incluir:**
- Checklist de lo que un agente debe verificar
- Ejemplo de archivo bien hecho
- Enlace al evaluador (`harness scan . --json`)

### III.2 Tutorial interactivo: "De 45% a 80% en 10 minutos"

**Formato:** Página web con pasos interactivos (JS)
**Contenido:**
1. `harness scan . --json` → ver diagnóstico
2. `harness fix .` → generar archivos faltantes
3. Personalizar cada archivo generado
4. Re-escanear → ver mejora
5. Agregar tests → sube Verification
6. Score final

### III.3 Case study: agents-flows-recipes

**Contenido:**
- Por qué este proyecto tiene el mejor score (64.6%)
- Qué hace bien: POML recetas, _registry, skills con frontmatter
- Qué se puede aprender para otros proyectos

**Criterio de éxito:** El curso tiene contenido práctico que un agente puede seguir y aplicar.

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

### IV.3 POML template generator mejorado 🏗️

**Estado actual:** 6 templates POML en `scripts/harness-fix/templates/`
**Mejora:** Auto-detección del tipo de proyecto

| Tipo de proyecto | Templates a generar |
|---|---|
| Static site (HTML/CSS/JS) | AGENTS.md, ROADMAP.md, .gitignore, LICENSE |
| Rust project (Cargo.toml) | + Dockerfile, Makefile, rust-toolchain.toml |
| Python project | + pyproject.toml, pytest.ini, .venv |
| Node project | + package.json, .npmrc, .nvmrc |
| Trading bot | + .env.example con Binance keys, restart script |

**Criterio de éxito:** `harness fix . --auto` genera contenido específico del tipo de proyecto.

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

### V.2 Agente evaluador autónomo 🤖

**Visión:** Un cron job que:
1. Escanea todos los proyectos del usuario periódicamente
2. Si el score bajó, genera un reporte
3. Si hay issues nuevos, los crea en GitHub
4. Envía resumen por Telegram

**Implementación:**
```bash
# Cron job semanal
hermes cron create \
  --schedule "0 9 * * 1" \
  --prompt "Escanea todos los proyectos en ~/projects/ con harness scan . --json
            y reporta cambios de score comparado con la semana anterior" \
  --deliver telegram
```

### V.3 Multi-lenguaje 🌐

**Estado actual:** Solo español
**Mejora:**
1. README en inglés
2. Páginas del curso con toggle ES/EN
3. Comentarios en código en inglés (convención)
4. AGENTS.md bilingüe

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

| # | Item | Fase | Esfuerzo | Impacto | Por qué ahora |
|---|---|---|---|---|---|
| 1 | **I.2 SynapseTrader bugs** | I | 🟡 1 sesión | 🟢 Alto | Issues activos afectando trading |
| 2 | **I.3 OpenClaw cosmetics** | I | 🟢 30 min | 🟢 Alto | Logs limpios = debugging más rápido |
| 3 | **I.1 Harness Course 60%** | I | 🟡 2 sesiones | 🟢 Alto | Sube credibilidad del sistema |
| 4 | **II.2 CI/CD badge + tests** | II | 🟡 1 sesión | 🟢 Alto | Visibilidad + calidad |
| 5 | **II.1 context-mode** | II | 🟡 1 sesión | 🟢 Alto | 98% menos tokens = $ |
| 6 | **IV.2 Importar skills** | IV | 🟡 2 sesiones | 🟡 Medio | + skills = agente más capaz |
| 7 | **IV.1 Registry unificado** | IV | 🔴 2 sesiones | 🟢 Alto | Elimina duplicación |
| 8 | **III.1 Páginas subsistema** | III | 🔴 3 sesiones | 🟢 Alto | El curso como tal |
| 9 | **II.3 Package CLI** | II | 🟡 1 sesión | 🟡 Medio | Instalación más fácil |
| 10 | **IV.3 POML templates** | IV | 🟡 1 sesión | 🟡 Medio | Fix más inteligente |
| 11 | **III.2 Tutorial interactivo** | III | 🔴 3 sesiones | 🟢 Alto | Valor educativo |
| 12 | **V.1 Starred scanner** | V | 🟡 1 sesión | 🟡 Medio | Contenido para el sitio |
| 13 | **V.2 Agente autónomo** | V | 🔴 2 sesiones | 🟢 Alto | Automatización total |
| 14 | **III.3 Case study** | III | 🟡 1 sesión | 🟡 Medio | Ejemplo concreto |
| 15 | **V.3 Multi-lenguaje** | V | 🔴 2 sesiones | 🟢 Medio | Alcance global |
| 16 | **V.4 Comunidad** | V | 🔴 4 sesiones | 🟢 Alto | Visión a largo plazo |

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
