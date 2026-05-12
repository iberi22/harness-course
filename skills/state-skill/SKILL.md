---
name: state-skill
description: Diseña sistemas de estado persistente para agentes — TASK.md, MEMORY.md, daily notes, heartbeat y session handoff
version: 1.0.0
category: state
tags: [state, persistence, task-tracking, memory, session, harness]
---

# 💾 State Management Skill

## Cuando Usarla

- El agente no recuerda lo que hizo en la sesión anterior
- No hay un backlog visible de tareas pendientes
- Necesitas session handoff entre agentes
- Quieres heartbeat system para monitoreo periódico

## Comandos Rápidos

```bash
# Ver estado actual
ls TASK.md MEMORY.md PROJECT_STATUS.md HEARTBEAT.md 2>/dev/null
ls memory/ 2>/dev/null

# Crear daily note
echo "# Daily Notes — $(date +%F)" > memory/$(date +%F).md
```

## Componentes Esenciales

- TASK.md con backlog, milestones y progreso visible
- MEMORY.md con contexto curado (no raw logs)
- memory/YYYY-MM-DD.md para notas de sesión
- HEARTBEAT.md para checks periódicos
- PROJECT_STATUS.md para estado funcional
