# 🚀 Bootstrap — Cómo empezar a trabajar en este proyecto

## Primeros pasos (para un agente nuevo)

```bash
# 1. Lee esta guía
cat BOOTSTRAP.md

# 2. Lee el briefing
cat AGENTS.md

# 3. Escanea el estado actual del harness
python3 scripts/harness_evaluator.py scan .

# 4. Si el score es bajo, genera archivos faltantes
python3 scripts/harness_evaluator.py fix .

# 5. Lee el backlog
cat TASK.md

# 6. Empieza con el primer ítem pendiente
```

## Flujo de trabajo diario
1. `git pull` — traer últimos cambios
2. `python3 scripts/harness_evaluator.py scan . --json | jq '.overall.score'` — ver score
3. Trabajar en una tarea a la vez (ver TASK.md)
4. `git push` al terminar

## Stack rápido
- **HTML/CSS/JS vanilla** — no instales nada
- **Editor:** cualquiera, previsualiza abriendo `index.html` en browser
- **Python 3** — solo para el evaluador, no para el sitio
- **GitHub Pages** — push a main despliega automáticamente
