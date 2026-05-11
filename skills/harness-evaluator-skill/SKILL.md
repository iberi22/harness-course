---
name: harness-evaluator
description: Cómo usar el Harness Evaluator CLI para escanear, diagnosticar y corregir proyectos
trigger: cuando un agente necesita evaluar el estado del harness de un proyecto
---

# Harness Evaluator Skill

## Comandos principales

```bash
# Escanear proyecto (formato humano)
python3 scripts/harness_evaluator.py scan /ruta/al/proyecto

# JSON compacto para agentes (~16KB)
python3 scripts/harness_evaluator.py scan /ruta/al/proyecto --json

# CI mode (exit 1 si score < threshold)
python3 scripts/harness_evaluator.py scan . --ci --threshold 50

# Generar archivos faltantes
python3 scripts/harness_evaluator.py fix /ruta/al/proyecto

# Validar recetas POML
python3 scripts/harness_evaluator.py poml validate /ruta/al/proyecto

# Si el CLI global está instalado
harness scan . --json
```

## Interpretación de scores

| Score | Color | Significado |
|---|---|---|
| ≥80% | 🟢 Excelente | Proyecto maduro para agentes |
| ≥60% | 🔵 Bueno | Harness sólido, mejoras puntuales |
| ≥40% | 🟡 Regular | Falta trabajo en varios subsistemas |
| ≥20% | 🟠 Bajo | Múltiples carencias críticas |
| <20% | 🔴 Crítico | Proyecto no orquestable por agentes |

## Flujo recomendado

1. `scan . --json` → ver diagnóstico
2. Revisar subsistemas con menor score
3. `fix .` → generar archivos faltantes
4. Personalizar contenido generado
5. `scan . --json` → ver mejora
6. Repetir hasta score ≥ 80%

## 6 subsistemas evaluados

| ID | Subsistema | Propósito |
|---|---|---|
| instructions | 📋 Instructions | Briefings, reglas, roadmap |
| state | 💾 State | Task tracking, memoria |
| verification | ✅ Verification | Tests, CI/CD |
| scope | 🎯 Scope | DoD, milestones |
| lifecycle | 🔄 Lifecycle | Init, Docker, .env |
| skills | 🧠 Skills & POML | Skills, recetas, registry |
