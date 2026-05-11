"""Reporting utilities for Harness Evaluator."""
import json
import os
import sys

from harness.models import Subsystem, VERSION, score_to_grade


def generate_llm_prompt(subsystems: list[Subsystem]) -> str:
    total_w = sum(s.total_weight for s in subsystems)
    earned_w = sum(s.earned_weight for s in subsystems)
    overall = round((earned_w / total_w * 100), 1) if total_w > 0 else 0.0

    prompt_parts = [
        "# Harness Evaluation Report — LLM Recommendations\n",
        f"Overall Score: {overall}%\n",
        "## Subsystem Scores\n",
    ]
    for s in subsystems:
        prompt_parts.append(f"- {s.name}: {s.percentage}% ({s.summary()})")

    prompt_parts.append("\n## Failed Checks (Needs Attention)\n")
    for s in subsystems:
        failed = [c for c in s.checks if not c.passed]
        if failed:
            prompt_parts.append(f"### {s.name}\n")
            for c in failed:
                prompt_parts.append(f"- [{c.id}] {c.name}: {c.detail}")

    prompt_parts.append("""
## Your Task
Eres un experto en Harness Engineering para agentes de IA. Basado en los resultados del scan:

1. **Prioriza** las 3-5 acciones más impactantes
2. **Recomienda** pasos concretos y accionables
3. **Sugiere** qué skills o archivos crear primero
4. **Identifica** riesgos si no se abordan

Responde en español, concreto, sin rodeos.
""")
    return "\n".join(prompt_parts)


def build_json_report(subsystems: list[Subsystem]) -> dict:
    total_w = sum(s.total_weight for s in subsystems)
    earned_w = sum(s.earned_weight for s in subsystems)
    overall = round((earned_w / total_w * 100), 1) if total_w > 0 else 0.0
    grade, _ = score_to_grade(overall)

    return {
        "version": VERSION,
        "overall": {"score": overall, "grade": grade},
        "subsystems": [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "percentage": s.percentage,
                "passed": s.passed,
                "summary": s.summary(),
                "checks": [
                    {
                        "id": c.id,
                        "name": c.name,
                        "passed": c.passed,
                        "weight": c.weight,
                        "detail": c.detail,
                        "files_found": c.files_found,
                    }
                    for c in s.checks
                ],
            }
            for s in subsystems
        ],
        "recommendations": {
            "llm_prompt": generate_llm_prompt(subsystems),
        },
    }


def print_report(subsystems: list[Subsystem], json_output: bool = False) -> None:
    report = build_json_report(subsystems)

    if json_output:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    W = os.get_terminal_size().columns if sys.stdout.isatty() else 80
    print()
    print("=" * W)
    print("  🔧  HARNESS EVALUATOR v2  🔧".center(W))
    print("=" * W)
    print()

    overall = report["overall"]
    print(f"  Puntuación Global: {overall['score']}%  —  {overall['grade']}".center(W))
    print()

    for sub in report["subsystems"]:
        status_icon = "✅" if sub["passed"] else "⚠️"
        bar_len = W - 42
        filled = int(bar_len * sub["percentage"] / 100)
        bar = "█" * filled + "░" * (bar_len - filled)

        print(f"  {status_icon}  {sub['name']}")
        print(f"     {sub['description']}")
        print(f"     [{bar}] {sub['percentage']:>5.1f}%  —  {sub['summary']}")
        print()

        for c in sub["checks"]:
            ok = "✓" if c["passed"] else "✗"
            print(f"     {ok}  {c['id']} {c['name']}")
            print(f"        {c['detail']}")
            if c["files_found"]:
                print(f"        📁 {', '.join(c['files_found'][:3])}")
                if len(c["files_found"]) > 3:
                    print(f"           ... y {len(c['files_found']) - 3} más")
            print()

    print("─" * W)
    print(f"  PUNTUACIÓN GLOBAL: {overall['score']}%  —  {overall['grade']}".center(W))

    failed_subs = [s for s in report["subsystems"] if not s["passed"]]
    if failed_subs:
        print()
        print("  🎯 Prioridades sugeridas:")
        for s in sorted(failed_subs, key=lambda x: x["percentage"]):
            print(f"     • {s['name']} ({s['percentage']}%)")
        print()
        print("  💡 Usa --llm para generar recomendaciones IA contextuales")
    print("=" * W)
    print()
