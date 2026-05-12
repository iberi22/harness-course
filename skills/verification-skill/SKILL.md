---
name: verification-skill
description: Aprende a configurar verification gates para agentes de IA — tests, linters, type checking, CI/CD y Definition of Done
version: 1.0.0
category: verification
tags: [verification, tests, ci-cd, linter, type-checking, harness]
---

# ✅ Verification Gates Skill

## Cuando Usarla

- Necesitas configurar tests para un proyecto de agente
- Quieres agregar linter + type checking
- El proyecto no tiene CI/CD pipeline
- Los agentes declaran tareas "listas" pero faltan validaciones

## Comandos Rápidos

```bash
# Escanear verification health
harness scan . --json | jq '.subsystems[] | select(.id=="verification")'

# Generar test stubs
harness fix . --all

# Ver gates
ls tests/ && ls .eslintrc* jsconfig* 2>/dev/null
```

## Qué Debe Tener un Buen Subsistema Verification

1. Tests que se ejecutan con un solo comando
2. Linter configurado (eslint, ruff, clippy, etc.)
3. Type checking (mypy, tsc, pyright)
4. CI/CD pipeline que corre tests + lint en cada PR
5. Definition of Done documentado en AGENTS.md o RULES.md
