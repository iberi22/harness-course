"""CLI entry point for Harness Evaluator."""
import argparse
import json
import os
import re
import sys
from dataclasses import asdict
from pathlib import Path

try:
    from importlib.resources import files as _resources_files
    _TEMPLATES_DIR = str(_resources_files('harness') / 'fix-templates')
except (ImportError, TypeError):
    _TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fix-templates')

from harness.models import VERSION, score_to_grade
from harness.scanner import HarnessScanner
from harness.poml import POMLValidator
from harness.report import build_json_report, generate_llm_prompt, print_report


# ── CLI: POML subcommand renderers ────────────────────────────────────

def cmd_poml_validate(args: argparse.Namespace) -> None:
    validator = POMLValidator(args.path, schema_path=getattr(args, "schema", None))
    issues = validator.validate()

    if not validator.poml_files:
        print(f"  ⚠️  No se encontraron archivos .poml en {args.path}")
        return

    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    infos = [i for i in issues if i.severity == "info"]

    print()
    print(f"  📋 POML Validate — {len(validator.poml_files)} archivos")
    print(f"     {len(errors)} errores, {len(warnings)} warnings, {len(infos)} informativos")
    print()

    if args.json:
        print(json.dumps({
            "total_files": len(validator.poml_files),
            "errors": [asdict(i) for i in errors],
            "warnings": [asdict(i) for i in warnings],
            "infos": [asdict(i) for i in infos],
        }, indent=2, ensure_ascii=False))
        return

    for issue_list, label in [(errors, "ERROR"), (warnings, "WARN"), (infos, "INFO")]:
        if not issue_list:
            continue
        for i in issue_list:
            print(f"  [{label}] {i.code} — {i.file}:{i.line}")
            print(f"         {i.message}")
        print()


def cmd_poml_lint(args: argparse.Namespace) -> None:
    validator = POMLValidator(args.path)
    issues = validator.lint()

    if not validator.poml_files:
        print(f"  ⚠️  No se encontraron archivos .poml en {args.path}")
        return

    warnings = [i for i in issues if i.severity == "warning"]
    infos = [i for i in issues if i.severity == "info"]

    print()
    print(f"  🔍 POML Lint — {len(validator.poml_files)} archivos")
    print(f"     {len(warnings)} warnings, {len(infos)} sugerencias")
    print()

    if args.json:
        print(json.dumps({
            "total_files": len(validator.poml_files),
            "warnings": [asdict(i) for i in warnings],
            "infos": [asdict(i) for i in infos],
        }, indent=2, ensure_ascii=False))
        return

    for label, issue_list in [("WARN", warnings), ("INFO", infos)]:
        if not issue_list:
            continue
        for i in issue_list:
            print(f"  [{label}] {i.code} — {i.file}:{i.line}")
            print(f"         {i.message}")
        print()

    if not warnings and not infos:
        print("  ✅ Sin issues de lint. Recetas limpias.")
        print()


def cmd_poml_coverage(args: argparse.Namespace) -> None:
    validator = POMLValidator(args.path)
    stats = validator.coverage()

    if stats.get("total", 0) == 0:
        print(f'{{"error":"{stats.get("message","No hay archivos .poml")}"}}' if args.json else f"  ⚠️  {stats.get('message', 'No hay archivos .poml')}")
        return

    if args.json:
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        return

    print()
    print(f"  📊 POML Coverage — {stats['total']} archivos .poml")
    print()

    if args.json:
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        return

    print(f"  Categorías: {len(stats['by_category'])}")
    for cat, count in stats["by_category"].items():
        bar = "█" * count
        print(f"    {cat}: {bar} ({count})")
    print()

    s = stats["sections"]
    print(f"  Secciones:")
    print(f"    <role>         {s['with_role']:>3}/{stats['total']} ({stats['pct_with_role']:>5.1f}%)")
    print(f"    <task>         {s['with_task']:>3}/{stats['total']} ({stats['pct_with_task']:>5.1f}%)")
    print(f"    <output-format> {s['with_output']:>3}/{stats['total']} ({stats['pct_with_output']:>5.1f}%)")
    print(f"    Completas      {s['with_all_sections']:>3}/{stats['total']} ({stats['pct_complete']:>5.1f}%)")
    print(f"    Con topology   {stats['pct_with_topology']}%")
    print(f"    Multi-provider {stats['multi_provider_recipes']} recetas")
    print()


# ── CLI: Fix command ───────────────────────────────────────────────────

def cmd_fix(args: argparse.Namespace) -> None:
    """Genera archivos faltantes del harness desde templates POML."""
    templates_dir = Path(args.templates)

    if not templates_dir.is_dir():
        print(f"[ERROR] Directorio de templates no encontrado: {templates_dir}", file=sys.stderr)
        sys.exit(1)

    # Load templates
    tmpl_files = sorted(templates_dir.glob("*.poml"))
    if not tmpl_files:
        print(f"[ERROR] No hay templates POML en {templates_dir}", file=sys.stderr)
        sys.exit(1)

    # Index templates by output file name and their check associations
    templates = {}
    for tf in tmpl_files:
        content = tf.read_text(encoding="utf-8")
        m = re.search(r'<let\s+name="output">(.*?)</let>', content)
        if m:
            out_file = m.group(1).strip()
            out_m = re.search(r'<output>(.*?)</output>', content, re.DOTALL)
            if out_m:
                # Extract check_ids or use fallback matching
                ids_m = re.search(r'<let\s+name="check_ids">\[(.*?)\]</let>', content)
                check_ids = [x.strip().strip('"') for x in ids_m.group(1).split(",")] if ids_m else []
                # Extract trigger keywords
                trig_m = re.search(r'<let\s+name="triggers">\[(.*?)\]</let>', content)
                triggers = [x.strip().strip('"') for x in trig_m.group(1).split(",")] if trig_m else []
                templates[out_file] = {
                    "content": out_m.group(1).strip(),
                    "check_ids": check_ids,
                    "triggers": triggers,
                }

    # Scan project
    try:
        scanner = HarnessScanner(args.path)
        subsystems = scanner.scan()
    except NotADirectoryError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    # Find failed checks that match templates
    project_root = Path(args.path).resolve()
    generated = 0

    print()
    print(f"  🔧 Harness Fix — {project_root.name}")
    print()

    for s in subsystems:
        for c in s.checks:
            if c.passed:
                continue
            for out_file, tmpl in templates.items():
                content = tmpl["content"]
                check_ids = tmpl["check_ids"]
                triggers = tmpl["triggers"]
                target = project_root / out_file
                if target.exists() and not args.all:
                    continue
                match = c.id in check_ids
                if not match:
                    cname_lower = c.name.lower()
                    for trig in triggers:
                        if trig.lower() in cname_lower:
                            match = True
                            break
                if match:
                    if args.dry_run:
                        print(f"  📄 Generaría: {out_file} (fix: {c.id} {c.name})")
                        generated += 1
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_text(content + "\n")
                        print(f"  ✅ {out_file} — generado ({c.id} {c.name})")
                        generated += 1
                    break

    if generated == 0:
        print("  ✨ No hay archivos que generar. El harness está completo.")
    elif args.dry_run:
        print(f"\n  📋 {generated} archivo(s) listos para generar. Usa --all para escribirlos.")
    else:
        print(f"\n  ✅ {generated} archivo(s) generados. Vuelve a escanear para ver el nuevo score.")
    print()


# ── CLI: Scan command ──────────────────────────────────────────────────

def cmd_scan(args: argparse.Namespace) -> None:
    try:
        scanner = HarnessScanner(args.path)
        subsystems = scanner.scan()
    except NotADirectoryError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    report = build_json_report(subsystems)
    overall = report["overall"]["score"]

    if getattr(args, "llm", False):
        print(generate_llm_prompt(subsystems))
        return

    print_report(subsystems, json_output=args.json)

    if getattr(args, "ci", False) and overall < args.threshold:
        print(f"[CI FAIL] Overall: {overall}% < threshold: {args.threshold}%", file=sys.stderr)
        sys.exit(1)


# ── CLI Entry Point ───────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Harness Evaluator v2 — Evalúa la madurez del harness para agentes de IA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--json", action="store_true", help="Salida en formato JSON")
    parser.add_argument("--version", action="version", version=f"Harness Evaluator v{VERSION}")

    subparsers = parser.add_subparsers(dest="command", help="Subcomandos")

    # ── scan (default) ─────────────────────────────────────────────
    scan_p = subparsers.add_parser("scan", help="Escanea un proyecto (por defecto)")
    scan_p.add_argument("path", help="Ruta al proyecto a escanear")
    scan_p.add_argument("--json", action="store_true", help="Salida en formato JSON")
    scan_p.add_argument("--llm", action="store_true", help="Generar prompt LLM para recomendaciones")
    scan_p.add_argument("--ci", action="store_true", help="Modo CI: exit 1 si no pasa threshold")
    scan_p.add_argument("--threshold", type=int, default=50, help="Threshold mínimo para CI")
    scan_p.set_defaults(func=cmd_scan)

    # ── poml validate ──────────────────────────────────────────────
    pv = subparsers.add_parser("poml", help="Comandos para recetas POML")
    pv_sub = pv.add_subparsers(dest="poml_command", help="Subcomando POML")

    pv_validate = pv_sub.add_parser("validate", help="Valida recetas POML contra schema")
    pv_validate.add_argument("path", help="Ruta al proyecto con archivos .poml")
    pv_validate.add_argument("--schema", help="Ruta al recipe.schema.yaml")
    pv_validate.add_argument("--json", action="store_true", help="Salida JSON")
    pv_validate.set_defaults(func=cmd_poml_validate)

    pv_lint = pv_sub.add_parser("lint", help="Analiza calidad de recetas POML")
    pv_lint.add_argument("path", help="Ruta al proyecto con archivos .poml")
    pv_lint.add_argument("--json", action="store_true", help="Salida JSON")
    pv_lint.set_defaults(func=cmd_poml_lint)

    pv_coverage = pv_sub.add_parser("coverage", help="Estadísticas de cobertura POML")
    pv_coverage.add_argument("path", help="Ruta al proyecto con archivos .poml")
    pv_coverage.add_argument("--json", action="store_true", help="Salida JSON")
    pv_coverage.set_defaults(func=cmd_poml_coverage)

    # ── fix ─────────────────────────────────────────────────────────
    fix_p = subparsers.add_parser("fix", help="Genera archivos faltantes del harness desde templates POML")
    fix_p.add_argument("path", help="Ruta al proyecto a reparar")
    fix_p.add_argument("--templates", default=_TEMPLATES_DIR,
                       help="Directorio con templates POML")
    fix_p.add_argument("--dry-run", action="store_true", help="Mostrar qué generaría sin escribir")
    fix_p.add_argument("--all", action="store_true", help="Generar todos los archivos faltantes")
    fix_p.set_defaults(func=cmd_fix)

    # ── Backwards compat: if no subcommand, treat first arg as path ─
    args = parser.parse_args()

    if args.command is None:
        # Legacy mode: python3 script.py path [--json --llm --ci]
        argv = sys.argv[1:]
        if not argv or argv[0].startswith("-"):
            parser.print_help()
            sys.exit(0)
        # Re-parse as scan
        scan_args = scan_p.parse_args(argv)
        cmd_scan(scan_args)
        return

    if hasattr(args, "func"):
        args.func(args)
