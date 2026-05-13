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
from harness.report import build_json_report, generate_llm_prompt, print_report
from harness.project_detector import ProjectDetector, ProjectType


# ── CLI: Fix command ───────────────────────────────────────────────────

def cmd_fix(args: argparse.Namespace) -> None:
    """Generate missing harness files from POML templates."""
    templates_dir = Path(args.templates)

    if not templates_dir.is_dir():
        print(f"[ERROR] Directorio de templates no encontrado: {templates_dir}", file=sys.stderr)
        sys.exit(1)

    def _load_templates(tmpl_dir: Path) -> dict:
        """Load POML templates from a directory and return a dict indexed by output name."""
        loaded: dict = {}
        for tf in sorted(tmpl_dir.glob("*.poml")):
            content = tf.read_text(encoding="utf-8")
            m = re.search(r'<let\s+name="output">(.*?)</let>', content)
            if m:
                out_file = m.group(1).strip()
                out_m = re.search(r'<output>(.*?)</output>', content, re.DOTALL)
                if out_m:
                    ids_m = re.search(r'<let\s+name="check_ids">\[(.*?)\]</let>', content)
                    check_ids = [x.strip().strip('"') for x in ids_m.group(1).split(",")] if ids_m else []
                    trig_m = re.search(r'<let\s+name="triggers">\[(.*?)\]</let>', content)
                    triggers = [x.strip().strip('"') for x in trig_m.group(1).split(",")] if trig_m else []
                    loaded[out_file] = {
                        "content": out_m.group(1).strip(),
                        "check_ids": check_ids,
                        "triggers": triggers,
                    }
        return loaded

    # Load generic templates
    templates = _load_templates(templates_dir)
    if not templates:
        print(f"[ERROR] No hay templates POML en {templates_dir}", file=sys.stderr)
        sys.exit(1)

    # Auto-detect project type and load specific templates
    detected_name = None
    recommended: list[str] = []
    if getattr(args, "auto", False):
        try:
            detector = ProjectDetector()
            project_type, _evidence = detector.detect(args.path)
            detected_name = detector.get_project_type_name(project_type)
            print(f"  📋 Tipo detectado: {detected_name}")

            type_map = {
                ProjectType.RUST_PROJECT: "rust",
                ProjectType.PYTHON_PROJECT: "python",
                ProjectType.NODE_PROJECT: "node",
                ProjectType.TRADING_BOT: "trading",
            }
            type_key = type_map.get(project_type)
            if type_key:
                specific_dir = templates_dir / type_key
                if specific_dir.is_dir():
                    extra = _load_templates(specific_dir)
                    templates.update(extra)

            recommended = detector.get_recommended_templates(project_type)
        except Exception:
            pass

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

    if getattr(args, "auto", False) and detected_name and recommended:
        print(f"\n  💡 Recomendación: para este tipo ({detected_name}), considera crear: {', '.join(recommended)}")

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


# ── CLI: Audit command ──────────────────────────────────────────────────

def cmd_audit(args: argparse.Namespace) -> None:
    """Run the Harness Context Auditor."""
    import subprocess
    auditor_script = Path(__file__).resolve().parent.parent.parent / "scripts" / "harness_auditor.py"
    if not auditor_script.exists():
        print(f"[ERROR] Auditor script not found at {auditor_script}", file=sys.stderr)
        sys.exit(1)

    cmd = [sys.executable, str(auditor_script)]
    if args.prompt:
        cmd += ["--prompt", args.prompt]
    elif args.self or args.path == "--self":
        cmd += ["--self"]
    elif args.path and args.path != "--self":
        cmd += ["--path", args.path]
    else:
        cmd += ["--self"]

    if args.json:
        cmd += ["--json"]

    result = subprocess.run(cmd)
    sys.exit(result.returncode)


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

    # ── fix ─────────────────────────────────────────────────────────
    fix_p = subparsers.add_parser("fix", help="Genera archivos faltantes del harness desde templates")
    fix_p.add_argument("path", help="Ruta al proyecto a reparar")
    fix_p.add_argument("--templates", default=_TEMPLATES_DIR,
                       help="Directorio con templates")
    fix_p.add_argument("--auto", action="store_true", help="Auto-detectar tipo de proyecto y usar templates específicos")
    fix_p.add_argument("--dry-run", action="store_true", help="Mostrar qué generaría sin escribir")
    fix_p.add_argument("--all", action="store_true", help="Generar todos los archivos faltantes")
    fix_p.set_defaults(func=cmd_fix)

    # ── audit ────────────────────────────────────────────────────────
    audit_p = subparsers.add_parser("audit", help="Audita seguridad del harness — inyección, contexto, postura")
    audit_p.add_argument("path", nargs="?", default="--self",
                         help="Ruta al proyecto o --self para auto-auditar")
    audit_p.add_argument("--self", action="store_true", help="Auto-auditar el harness actual")
    audit_p.add_argument("--prompt", help="Analizar texto como system prompt")
    audit_p.add_argument("--json", action="store_true", help="Salida JSON")
    audit_p.set_defaults(func=cmd_audit)

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
