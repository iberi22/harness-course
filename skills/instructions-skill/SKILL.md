---
name: instructions-skill
description: Crea sistemas de instrucciones efectivos para agentes de IA — AGENTS.md, ROADMAP.md, SOUL.md y progressive disclosure
version: 1.0.0
category: instructions
tags: [instructions, agents, briefing, progressive-disclosure, harness]
---

# 📋 Instructions Design Skill

## Cuando Usarla

- Un agente nuevo no sabe por dónde empezar
- El proyecto no tiene AGENTS.md o CLAUDE.md
- Necesitas progressive disclosure (de lo general a lo específico)
- El agente ignora convenciones del proyecto

## Comandos Rápidos

```bash
# Ver archivos de instrucciones
ls AGENTS.md CLAUDE.md SOUL.md TOOLS.md RULES.md ROADMAP.md README.md 2>/dev/null

# Ver briefings
ls briefings/ 2>/dev/null
```

## Pirámide de Progressive Disclosure

1. README.md — Qué hace el proyecto (1 párrafo)
2. AGENTS.md — Briefing completo para agentes
3. SOUL.md — Identidad y personalidad del agente
4. ROADMAP.md — Visión a largo plazo
5. RULES.md — Convenciones de código
6. TOOLS.md — Herramientas del proyecto
7. briefings/ — Documentos de contexto específicos
