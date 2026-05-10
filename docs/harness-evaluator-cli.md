# Harness Evaluator v2 — CLI Reference

> 🔧 Agent Workspace Maturity Scanner
> Versión: 2.1.0 · CLI puro · Sin dependencias externas · Sin servidores

---

## Instalación

```bash
# El script es standalone, no necesita instalación
python3 scripts/harness_evaluator.py --version
```

## Subcomandos

### `scan` — Escanear proyecto (por defecto)

```bash
# Reporte humano
python3 harness_evaluator.py ~/proyecto

# Modo legacy (sin subcomando)
python3 harness_evaluator.py ~/proyecto

# JSON estructurado (para pipelines/agentes)
python3 harness_evaluator.py scan ~/proyecto --json

# Prompt LLM para recomendaciones contextuales
python3 harness_evaluator.py scan ~/proyecto --llm

# Modo CI (exit 1 si no pasa threshold)
python3 harness_evaluator.py scan ~/proyecto --ci --threshold 60
```

**Flags:**
| Flag | Default | Descripción |
|---|---|---|
| `--json` | — | Salida JSON estructurada |
| `--llm` | — | Genera prompt para LLM (recomendaciones IA) |
| `--ci` | — | Modo CI: exit code 1 si no pasa |
| `--threshold` | 50 | Score mínimo para CI |

---

### `poml validate` — Validar recetas POML

Valida archivos `.poml` contra reglas estructurales:

```bash
python3 harness_evaluator.py poml validate ~/proyecto
python3 harness_evaluator.py poml validate ~/proyecto --schema schema/recipe.schema.yaml
python3 harness_evaluator.py poml validate ~/proyecto --json
```

**Chequea:**
| Código | Severidad | Regla |
|---|---|---|
| P001 | error | Debe comenzar con `<poml>` |
| P002 | error | Debe terminar con `</poml>` |
| P010 | error | Topology inválida (solo/multi/rag/tools-first) |
| P011 | warning | tool_mode inválido |
| P012 | warning | Provider no estándar |
| P013 | error | providers no es JSON válido |
| P020 | error | Falta `<let name="...">` requerido |
| P030 | warning | Falta sección `<role>` |
| P031 | warning | Falta sección `<task>` |
| P040 | warning | Tags desbalanceados |

---

### `poml lint` — Analizar calidad POML

Análisis más profundo de calidad de recetas:

```bash
python3 harness_evaluator.py poml lint ~/proyecto
python3 harness_evaluator.py poml lint ~/proyecto --json
```

**Chequea:**
| Código | Severidad | Regla |
|---|---|---|
| L010 | info | Tool sin alias en tool_aliases |
| L020 | info | Topology 'solo' en proyecto grande |
| L030 | warning | Sección `<role>` vacía |
| L031 | warning | Sección `<task>` vacía |
| L040 | info | Falta `<output-format>` |
| L050 | info | temperature=0.0 (sin creatividad) |
| L051 | info | temperature>1.0 (muy alta para codegen) |

---

### `poml coverage` — Estadísticas POML

Reporte de cobertura y calidad de recetas:

```bash
python3 harness_evaluator.py poml coverage ~/proyecto
python3 harness_evaluator.py poml coverage ~/proyecto --json
```

**Muestra:**
- Total de archivos .poml
- Distribución por categoría (engineering, marketing, design, etc.)
- % con `<role>`, `<task>`, `<output-format>`
- % completas (role + task + output-format)
- % con topology definida
- Recetas multi-provider

---

## 6 Subsistemas del Scan

| # | Subsistema | Checks | Peso total |
|---|---|---|---|
| 1 | 📋 Instructions | 8 | 10.0 |
| 2 | 💾 State | 7 | 10.0 |
| 3 | ✅ Verification | 6 | 9.0 |
| 4 | 🎯 Scope | 7 | 8.0 |
| 5 | 🔄 Lifecycle | 8 | 10.0 |
| 6 | 🧠 Skills & POML | 12 | 16.5 |

**Total: 48 checks · 63.5 puntos ponderados**

---

## Scores y Grades

| Score | Grade |
|---|---|
| ≥ 80% | 🟢 EXCELENTE |
| ≥ 60% | 🔵 BUENO |
| ≥ 40% | 🟡 REGULAR |
| ≥ 20% | 🟠 DÉBIL |
| < 20% | 🔴 CRÍTICO |

---

## Arquitectura

```
harness_evaluator.py
├── HarnessScanner      # 48 checks en 6 subsistemas
│   ├── _scan_instructions()  # S1: AGENTS.md, docs/, SOUL.md
│   ├── _scan_state()         # S2: TASK.md, MEMORY.md, git
│   ├── _scan_verification()  # S3: tests, CI/CD, linters
│   ├── _scan_scope()         # S4: DoD, milestones, templates
│   ├── _scan_lifecycle()     # S5: init, Docker, handoff
│   └── _scan_skills()        # S6: skills/, poml/, registry
│
├── POMLValidator       # Validación + lint + coverage POML
│   ├── validate()      # 12 reglas estructurales (P001-P040)
│   ├── lint()          # 7 reglas de calidad (L010-L051)
│   └── coverage()      # Estadísticas de recetas
│
├── Reporting           # JSON + humano + LLM prompt
│   ├── build_json_report()
│   ├── print_report()
│   └── generate_llm_prompt()
│
└── CLI (argparse)      # scan, poml validate/lint/coverage
```

---

## Integración con CI/CD

```yaml
# .github/workflows/harness-check.yml
- name: Harness Evaluation
  run: |
    python3 scripts/harness_evaluator.py . --ci --threshold 50
```

```bash
# Pipeline
python3 harness_evaluator.py . --json | jq '.overall.score'
```

---

## Integración con LLM

```bash
# Generar prompt y pasarlo a cualquier LLM
python3 harness_evaluator.py . --llm | hermes run --stdin
python3 harness_evaluator.py . --llm | opencode run --stdin
python3 harness_evaluator.py . --llm | gemini run --stdin
```

---

## Ejemplos de uso

```bash
# Escanear proyecto actual
python3 harness_evaluator.py .

# Escanear agents-flows-recipes
python3 harness_evaluator.py ~/projects/agents-flows-recipes

# Solo validación POML
python3 harness_evaluator.py poml validate ~/projects/agents-flows-recipes

# Coverage POML
python3 harness_evaluator.py poml coverage ~/projects/agents-flows-recipes

# Escanear + recomendar con IA
python3 harness_evaluator.py ~/projects/synapse-trading --llm | opencode run
```
