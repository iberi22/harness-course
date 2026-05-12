# 🤖 Autonomous Evaluator Agent

> **Fase:** V.2
> **Versión:** 1.0.0
> **Propósito:** Escaneo periódico de todos los proyectos del ecosistema Harness Engineering

---

## Visión

Un cron job que:
1. **Escanea** todos los proyectos del usuario periódicamente
2. **Reporta** cambios de score comparado con la ejecución anterior
3. **Alerta** si el score de algún proyecto bajó o cruza un umbral crítico
4. **Envía** resumen por el canal de delivery configurado (consola, archivo o notificación)

---

## System Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Cron Job  │────▶│ evaluator-cron.sh │────▶│ auto-evaluate.sh │
│  (diario)   │     │  (registro)       │     │  (orquestador)  │
└─────────────┘     └──────────────────┘     └────────┬────────┘
                                                      │
                              ┌───────────────────────┼───────────────────────┐
                              ▼                       ▼                       ▼
                        ┌──────────┐           ┌──────────┐           ┌──────────┐
                        │ harness  │           │ harness  │           │ harness  │
                        │ scan .   │           │ scan .   │           │ scan .   │
                        │ --json   │           │ --json   │           │ --json   │
                        │proj-1    │           │proj-2    │           │proj-n    │
                        └────┬─────┘           └────┬─────┘           └────┬─────┘
                             │                      │                      │
                             └──────────────────────┼──────────────────────┘
                                                    ▼
                                           ┌─────────────────┐
                                           │   index.json    │
                                           │  (scores +      │
                                           │   timestamps)   │
                                           └────────┬────────┘
                                                    │
                              ┌─────────────────────┼─────────────────────┐
                              ▼                     ▼                     ▼
                        ┌──────────┐        ┌──────────┐         ┌──────────┐
                        │ --report │        │ --compare│         │ --alert  │
                        │  (nuevo) │        │  (delta) │         │  (exit 1)│
                        └──────────┘        └──────────┘         └──────────┘
```

### Flujo de ejecución

1. `evaluator-cron.sh` registra o actualiza el cron job en el sistema (idempotente).
2. El cron dispara `auto-evaluate.sh` a la hora programada.
3. `auto-evaluate.sh` detecta proyectos en `~/projects/` que contengan archivos Harness conocidos (`AGENTS.md`, `ROADMAP.md`, `SKILL.md`, etc.).
4. Por cada proyecto encontrado, ejecuta `harness scan . --json`.
4. Los resultados se acumulan en `data/evaluations/index.json`.
6. Si se invoca con `--compare`, calcula delta contra la corrida anterior.
7. Si se invoca con `--alert-below <N>`, retorna exit code 1 si algún proyecto está por debajo.

---

## Setup

### Requisitos previos

- `harness` CLI instalado y en PATH (`pip install -e ~/projects/harness-course`)
- Python ≥ 3.10
- `crontab` disponible (Linux/macOS) o `hermes cron` (si se ejecuta dentro de Hermes Agent)

### Pasos de instalación

```bash
# 1. Ir al directorio del repositorio
cd ~/projects/harness-course

# 2. Primer scan — establece baseline
./scripts/auto-evaluate.sh

# 3. Ver comparación (delta contra baseline)
./scripts/auto-evaluate.sh --compare

# 4. Chequear alertas (exit 1 si algún proyecto < 50%)
./scripts/auto-evaluate.sh --alert-below 50

# 5. Registrar cron job diario (9 AM)
./scripts/evaluator-cron.sh
```

---

## Cron Job

### Opción A: hermes cron (preferido, si está disponible)

```bash
# Registra un cron job diario a las 9:00 AM
hermes cron create \
  --schedule "0 9 * * *" \
  --command "cd ~/projects/harness-course && ./scripts/auto-evaluate.sh --compare --alert-below 50" \
  --name "harness-evaluator-v2"
```

### Opción B: crontab del sistema (fallback)

```bash
# El script evaluator-cron.sh hace esto automáticamente:
(crontab -l 2>/dev/null | grep -v "auto-evaluate.sh"; \
 echo "0 9 * * * cd ~/projects/harness-course && ./scripts/auto-evaluate.sh --compare --alert-below 50 >> data/evaluator.log 2>&1") | crontab -
```

### Opción C: systemd timer (Linux avanzado)

Ver `docs/systemd-timer-setup.md` (documento separado) para configuración de servicio systemd.

---

## Project Status

| Proyecto | Score | Delta | Estado |
|----------|-------|-------|--------|
| harness-course | 100% | — | 🟢 |
| synapse-trading | 81.9% | — | 🟢 |
| swal-skills | 75.0% | — | 🟡 |
| agents-flows-recipes | 61.5% | — | 🟡 |
| openclaw | 45.0% | — | 🔴 |
| ... | ... | ... | ... |

**Leyenda:**
- 🟢 ≥ 80% — Excelente
- 🟡 60-79% — Aceptable, mejoras posibles
- 🔴 < 60% — Necesita atención
- 🔻 ↓ — Score bajó respecto a la corrida anterior
- 🔺 ↑ — Score subió respecto a la corrida anterior

---

## CLI Reference

### `auto-evaluate.sh`

```bash
./scripts/auto-evaluate.sh [OPTIONS]
```

| Opción | Descripción |
|--------|-------------|
| (sin flags) | Ejecuta scan completo y guarda resultados en `data/evaluations/index.json` |
| `--compare` | Muestra tabla comparativa con la corrida anterior |
| `--alert-below N` | Retorna exit code 1 si algún proyecto está debajo de N% |
| `--help` | Muestra ayuda |

### `evaluator-cron.sh`

```bash
./scripts/evaluator-cron.sh [OPTIONS]
```

| Opción | Descripción |
|--------|-------------|
| (sin flags) | Registra cron job diario a las 9:00 AM (idempotente) |
| `--remove` | Elimina el cron job registrado |
| `--status` | Muestra si el cron job está registrado y cuándo corre |
| `--schedule "CRON"` | Usa una expresión cron custom (default: `0 9 * * *`) |
| `--help` | Muestra ayuda |

---

## Estructura de datos

### `data/evaluations/index.json`

```json
{
  "last_updated": "2026-05-12T09:00:00+00:00",
  "projects": {
    "harness-course": {
      "path": "/home/belal/projects/harness-course",
      "latest_score": 100.0,
      "latest_file": "2026-05-12T09-00-00.json",
      "previous_score": 100.0,
      "delta": 0.0,
      "status": "ok",
      "error_msg": null
    },
    "synapse-trading": {
      "path": "/home/belal/projects/synapse-trading",
      "latest_score": 81.9,
      "latest_file": "2026-05-12T09-00-00.json",
      "previous_score": 78.5,
      "delta": 3.4,
      "status": "ok",
      "error_msg": null
    }
  }
}
```

---

## Troubleshooting

### Script fails: `harness: command not found`

- Verificar que `harness` está instalado: `pip install -e ~/projects/harness-course`
- Verificar que `~/.local/bin` está en PATH
- Alternativa: usar `python3 -m harness` en lugar del binario

### No se encuentran proyectos

- Asegurarse de que los proyectos en `~/projects/` tengan al menos un archivo Harness (`AGENTS.md`, `ROADMAP.md`, `TASK.md`, etc.)
- Probar con `--projects /ruta/a/proyectos` explícitamente

### Resultados vacíos o corruptos en JSON

- Ejecutar manualmente `harness scan . --json` en uno de los proyectos para ver si hay errores
- Revisar permisos de escritura en `data/evaluations/`
- Borrar `data/evaluations/index.json` y re-correr para regenerar baseline

### Cron job no corre

- Verificar que el cron job está registrado: `./scripts/evaluator-cron.sh --status`
- Revisar logs: `tail -f ~/projects/harness-course/data/evaluations/evaluator.log`
- Asegurarse de que el shell del cron tiene PATH completo (el script se encarga de esto)

### Scores inconsistentes entre corridas

- Algunos evaluadores verifican archivos generados dinámicamente (ej. `memory/`, `data/`)
- Agregar `.harnessignore` en los proyectos si hay archivos que no deben contar

---

## Roadmap

- [ ] V.2.1 — Soporte de notificaciones por Telegram (`--notify telegram`)
- [ ] V.2.2 — Integración con GitHub Issues (crear issue automático si score baja)
- [ ] V.2.3 — Dashboard HTML embebido en el sitio del curso
- [ ] V.2.4 — Soporte multi-usuario (escanear proyectos de múltiples workspaces)

---

*Documento generado para el ecosistema Harness Engineering — Fase V.2*
