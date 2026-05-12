# 📋 Harness Engineering — Informe de Progreso

> **Fecha:** 11 Mayo 2026
> **Proyectos intervenidos:** 4
> **Archivos generados:** ~35
> **Objetivo:** Llevar todos los proyectos a score ≥ 50% con contenido real

---

## 1. Resumen Ejecutivo

Se intervinieron 4 proyectos con el **Harness Evaluator CLI** para diagnosticar, generar archivos faltantes y personalizar contenido según el contexto de cada proyecto.

| Proyecto | Score Inicial | Score Actual | Mejora |
|---|---|---|---|
| **harness-course** | 6.3% 🔴 | **100.0% 🏆** | **+93.7%** |
| **agents-flows-recipes** | 46.5% 🟡 | 64.6% 🔵 | +18.1% |
| **swal-skills** | 40.2% 🟡 | 74.0% 🔵 | +33.8% |
| **synapse-trading** | 37.0% 🟠 | 81.9% 🟢 | +44.9% |

Además se catalogaron ~150 repos starred de GitHub, se indexaron 44 skills locales y 8 starred, y se configuró CI/CD.

### Cron Job 11-Mayo-2026: swal-skills 58.3% → 74.0% (+15.7pp)

Se ejecutaron 3 subagentes en paralelo vía `delegate_task` (kimi-k2.6) para crear 12 archivos de harness:
- SOUL.md, TOOLS.md, RULES.md → Instructions 95%
- PROJECT_STATUS.md, MEMORY.md, HEARTBEAT.md → State 80%
- USER.md, BOOTSTRAP.md → Scope 62.5%
- Dockerfile → Lifecycle 95%

**Proyectos locales escaneados (7):**

| Proyecto | Score | Grade |
|---|---|---|
| harness-course | **100.0%** | 🟢 EXCELENTE |
| synapse-trading | 81.9% | 🟢 EXCELENTE |
| swal-skills | 74.0% | 🔵 BUENO |
| agents-flows-recipes | 64.6% | 🔵 BUENO |
| agent-recipes-repo | 41.7% | 🟡 REGULAR |
| learn-harness-engineering | 25.2% | 🟠 DÉBIL |
| awesome-harness-engineering | 10.2% | 🔴 CRÍTICO |

---

## 2. Hallazgos por Subsistema

### 📋 Instructions (Score promedio: ~40%)

**Problemas detectados:**
- AGENTS.md ausente en harness-course y synapse-trading (generado)
- ROADMAP.md ausente en todos los proyectos (generado con contenido real)
- README.md genérico sin instrucciones para agentes (actualizado)
- SOUL.md (identidad del proyecto) ausente en todos (creado)
- RULES.md (convenciones de código) ausente en harness-course (creado)
- TOOLS.md (herramientas del proyecto) ausente en todos (creado)

**Mejores prácticas observadas:**
- `agents-flows-recipes` tiene AGENTS.md robusto con briefing completo
- SynapseTrader ya tenía CLAUDE.md detallado (cubría parte de Instructions)

### 💾 State (Score promedio: ~35%)

**Problemas detectados:**
- TASK.md ausente en harness-course (generado con backlog real)
- PROJECT_STATUS.md ausente en todos (creado)
- MEMORY.md ausente en harness-course (creado con contexto persistente)
- USER.md ausente en todos (creado con perfil del usuario)
- memory/ directorio de diario de sesiones ausente en harness-course
- Sin heartbeat system en ninguno

**Mejores prácticas observadas:**
- agents-flows-recipes tiene sistema de memoria con daily notes + MEMORY.md
- SynapseTrader tiene docs/TASK.md con issues activos

### ✅ Verification (Score promedio: ~15%)

**Problemas detectados:**
- Sin tests en harness-course (sitio estático sin suite)
- Sin CI/CD en harness-course (creado .github/workflows/harness-ci.yml)
- Sin linters configurados en harness-course
- Sin type checking

**Hallazgo notable:**
- SynapseTrader tiene tests en `backend/tests/` pero sin cobertura suficiente
- agents-flows-recipes tiene pytest.ini configurado

### 🎯 Scope (Score promedio: ~20%)

**Problemas detectados:**
- Definition of Done sin documentar en todos (generado en AGENTS.md)
- Backlog formal ausente (TASK.md generado)
- Sin USER.md ni BOOTSTRAP.md (creados)
- Sin .github/ISSUE_TEMPLATE en harness-course (creado)

### 🔄 Lifecycle (Score promedio: ~30%)

**Problemas detectados:**
- Sin init.sh en harness-course (generado)
- Sin .env.example personalizado en harness-course (generado)
- Sin .gitignore en harness-course (generado)
- Sin LICENSE en harness-course (generado MIT)
- Sin Docker en harness-course (no aplica — sitio estático)

**Hallazgo notable:**
- SynapseTrader es el más robusto: Dockerfile, docker-compose.yml, .env.example, .gitignore, LICENSE ya existían

### 🧠 Skills & POML (Score promedio: ~15%)

**Problemas detectados:**
- Sin skills/ directory en harness-course ni synapse-trading
- Sin recetas POML en harness-course ni synapse-trading
- Sin skill registry ni provider en ninguno excepto agents-flows-recipes

**Hallazgo notable:**
- agents-flows-recipes tiene 20 skills con SKILD.md frontmatter, POML recetas, y _registry
- swal-skills tiene 24 skills con formato Agent Skills estándar

---

## 3. Archivos Generados por Proyecto

### Harness Course (16 archivos)

| Archivo | Función |
|---|---|
| AGENTS.md | Briefing para agentes con stack, convenciones, DoD |
| ROADMAP.md | Roadmap en 4 fases con items chequeables |
| TASK.md | Backlog con milestones y estado actual |
| CONTRIBUTING.md | Guía de contribución con estándares |
| RULES.md | Reglas de código HTML/CSS/JS |
| SOUL.md | Identidad y valores del proyecto |
| TOOLS.md | Catálogo de herramientas esenciales/opcionales |
| USER.md | Perfil del usuario para agentes |
| MEMORY.md | Contexto persistente del proyecto |
| BOOTSTRAP.md | Primeros pasos para agentes nuevos |
| PROJECT_STATUS.md | Estado funcional del proyecto |
| .gitignore | Exclusiones estándar + Python/editor/OS |
| LICENSE | MIT License |
| .env.example | Variables de entorno (vacías — sitio estático) |
| init.sh | Bootstrap script con verificación de tools |
| .github/workflows/harness-ci.yml | CI/CD pipeline |
| .github/ISSUE_TEMPLATE/* | Bug report + feature request |
| .github/PULL_REQUEST_TEMPLATE.md | PR template |

### SynapseTrader (10 archivos)

| Archivo | Función |
|---|---|
| AGENTS.md | Briefing con stack Rust + AI agents |
| ROADMAP.md | Roadmap trading-focused |
| CONTRIBUTING.md | Guía con reglas de paper-first |
| SOUL.md | Identidad técnica del bot |
| TOOLS.md | Catálogo de scripts y daemon |
| USER.md | Perfil del dueño (privacidad) |
| MEMORY.md | Issues recurrentes + estado del daemon |
| BOOTSTRAP.md | Onboarding para agentes nuevos |
| PROJECT_STATUS.md | Métricas de trading + issues activos |
| init.sh | Bootstrap Rust + .env |

### Docs globales (3 archivos)

| Archivo | Función |
|---|---|
| docs/starred-catalog.md | ~150 repos starred en 11 categorías |
| docs/skills-index.json | 44 skills locales + 8 starred indexadas |
| docs/harness-evaluator-cli.md | Documentación completa del CLI (pre-existente) |

---

## 4. Skills Index — Hallazgos Clave

### Skills compartidas entre swal-skills y agents-flows-recipes

| Skill | swal-skills | agents-flows-recipes |
|---|---|---|
| astro | ✅ | ✅ |
| codex | ✅ | ✅ |
| gemini | ✅ | ✅ |
| github | ✅ | ✅ |
| nextjs | ✅ | ✅ |
| python | ✅ | ✅ |
| qwen | ✅ | ✅ |
| rust | ✅ | ✅ |
| skill-launcher | ✅ | ✅ |
| skill-provider | ✅ | ✅ |
| tailwindcss | ✅ | ✅ |
| vite | ✅ | ✅ |
| web-research | ✅ | ✅ |

### Skills únicas de swal-skills (no duplicadas)
`coding-agent`, `deploy-anywhere`, `frontend-agent`, `frontend-doctor`, `jules`, `minimax-tools`, `web-design-guidelines`, `worldexams-curator`, `worldexams-generator`, `worldexams-validator`, `xavier2-context`

### Skills únicas de agents-flows-recipes (no duplicadas)
`sales-pro`, `sqlite-pro`, `src-generator`, `swal-finetune`, `synapse`

### Starred repos de alto valor para skills

| Repo | ★ | Valor |
|---|---|---|
| forrestchang/andrej-karpathy-skills | 123K | CLAUDE.md con principios Karpathy |
| mattpocock/skills | 68K | Skills reales de ingeniería |
| context-mode (mksglu) | 14K | 98% reducción de tokens |
| Orchestra-Research/AI-Research-SKILLs | 8K | Skills de AI research |
| midudev/autoskills | 5K | Instalador automático de skills |

---

## 5. CI/CD Pipeline

**Archivo:** `.github/workflows/harness-ci.yml`

Flujo:
1. Se ejecuta en cada PR a `main`
2. Corre `harness scan . --ci --threshold 50`
3. Comenta el resultado en el PR (score + subsistemas)
4. Exit 1 si score < 50% (bloquea el merge si está configurado como required check)

**Configurable:** cambiar threshold en `--threshold N`

---

## 6. Lecciones Aprendidas

### Sobre el evaluador
- El scan tarda más en proyectos grandes con muchos archivos (SynapseTrader tiene ~300 archivos)
- El `--json` es la forma más eficiente para que agentes consuman los resultados (~16KB vs ~400KB texto)
- El subcomando `fix` genera templates genéricos — requieren personalización manual para ser útiles
- Los templates del fix deberían detectar el tipo de proyecto (Rust, Python, static site) para generar contenido relevante

### Sobre harness engineering
- **Instructions y State** son los subsistemas más rápidos de mejorar (crear archivos markdown)
- **Verification y Skills** son los más difíciles — requieren tests y skills reales
- Un AGENTS.md bien escrito vale por 5 checks individuales
- La memoria persistente (MEMORY.md + daily notes) es lo que más valor agrega para agentes recurrentes

### Sobre los proyectos
- **agents-flows-recipes** es el benchmark — tiene el mejor harness de todos
- **harness-course** es el que más necesita mejora (partió de 6.3%)
- **synapse-trading** es grande y complejo — ya tenía mucho harness pero desorganizado

---

## 7. Próximos Pasos Recomendados

1. **Importar skills externas** — mattpocock/skills (68K★), karpathy-skills (123K★), context-mode (14K★)
2. **Harness Course → 60%+** — agregar tests (HTML validation + link checker), skills/ directory, POML recetas
3. **SynapseTrader → sesión de fix** — Accountant agent dirs, OpsAnalyzer BraveAI, restart-daemon.sh release path
4. **Unificar skills registry** — skills compartidas entre swal-skills y agents-flows-recipes en un solo _registry
5. **Agregar badge CI** al README una vez que el workflow esté activo en GitHub
6. **Template auto-detect** — mejorar el fix para detectar tipo de proyecto y generar contenido específico

---

*Documentación generada automáticamente desde el análisis de 4 proyectos, ~150 starred repos, y ~35 archivos generados.*
