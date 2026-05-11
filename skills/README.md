# 🧠 Harness Course — Skills Catalog

> Skills para agentes de IA que trabajan en este proyecto.

## Skills incluidas

| Skill | Descripción | Uso |
|---|---|---|
| **harness-evaluator** | Cómo usar el evaluador CLI para escanear, fix y validar POML | Cualquier agente que llegue al proyecto |

## Cómo usar una skill

```bash
# Leer la skill
cat skills/harness-evaluator-skill/SKILL.md

# O desde el CLI
harness scan . --json | jq '.overall.score'
```
